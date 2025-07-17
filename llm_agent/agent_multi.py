import os
import json
from typing import Tuple, List, Any
from langchain_openai import AzureChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.callbacks import UsageMetadataCallbackHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from llm_agent.prompts_multi import SIMPLE_PROMPT
from llm_agent.tools_multi import generate_pinescript, exa_search, exa_find_similar

# ─────────── CONFIG ───────────
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# ─────────── NO MEMORY - STATELESS ───────────

# ─────────── LLM ───────────
llm = AzureChatOpenAI(
    azure_deployment=AZURE_OPENAI_DEPLOYMENT,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    openai_api_version=AZURE_OPENAI_API_VERSION,
    temperature=0,
    model_version="0125",  # Ensure we use a version that supports tools
)

# ─────────── LANGGRAPH AGENT ───────────
# We need to use the EXACT same state as before - no changes!
# But LangGraph expects messages, so we'll convert internally

# Extract system prompt for the agent
system_prompt_content = SIMPLE_PROMPT.messages[0].prompt.template

# Create a custom prompt that works with LangGraph's tool calling
# We need to tell it to use tools, not return JSON directly
tool_calling_prompt = """You are an expert trading and financial markets consultant who helps users with market analysis, trading strategies, and financial research.

You have access to the following tools:

1. **exa_search**: Search the web for current financial news, market analysis, earnings reports, and other financial information.
2. **exa_find_similar**: Find similar articles or content to a given URL.
3. **generate_pinescript**: Generate PineScript code for trading strategies.

When answering questions:

1. For market analysis, news, or research questions:
   - Use exa_search to find current information
   - Provide comprehensive analysis based on the search results
   - Include relevant data points, trends, and insights

2. For trading strategy questions:
   - Provide a text-only explanation first
   - Focus on strategy concept, market conditions, indicators, risk management
   - If user needs PineScript code, use the generate_pinescript tool

3. Your response should be clear, data-driven, and actionable.
   - Use markdown formatting for better readability
   - Cite sources when using search results
   - Provide balanced analysis with both opportunities and risks

IMPORTANT: 
- Use exa_search for ANY current market data or news requests
- Use generate_pinescript for ANY PineScript code requests
- Keep explanations separate from code
- Focus on providing valuable insights based on current data"""

# Create LangGraph agent with tool-friendly prompt
agent = create_react_agent(
    model=llm,
    tools=[generate_pinescript, exa_search, exa_find_similar],
    prompt=tool_calling_prompt
)

# ─────────── MAIN FUNCTION ───────────
def run_pinescript_agent(
    user_input: str,
    previous_summary: str = "No previous conversation."
) -> Tuple[str, int, float, List[Any], List[Any]]:
    """Trading strategy chat with PineScript generation using LangGraph"""
    
    # Create token usage callback
    token_callback = UsageMetadataCallbackHandler()
    
    # Build the EXACT same user prompt format as the original
    # This matches what SIMPLE_PROMPT expects: "Previous conversation summary: {previous_summary}\n\nCurrent query: {input}"
    user_message = f"Previous conversation summary: {previous_summary}\n\nCurrent query: {user_input}"
    
    # Run the LangGraph agent - it expects messages internally
    result = agent.invoke(
        {
            "messages": [
                ("human", user_message)
            ]
        },
        config={
            "callbacks": [token_callback],
            "recursion_limit": 10
        }
    )
    
    # Extract the final assistant message
    messages = result.get("messages", [])
    if not messages:
        raise ValueError("No messages returned from agent")
    
    # Get the last assistant message
    assistant_messages = [msg for msg in messages if hasattr(msg, 'type') and msg.type == 'ai']
    if not assistant_messages:
        raise ValueError("No assistant messages found")
    
    # Check if tools were called
    tool_messages = [msg for msg in messages if hasattr(msg, 'type') and msg.type == 'tool']
    
    # Build the JSON response based on tool outputs
    if tool_messages:
        # Get the final assistant message that explains the strategy
        final_message = assistant_messages[-1].content
        
        # Check if this is a PineScript tool call (returns JSON) or other tools
        last_tool_content = tool_messages[-1].content if tool_messages else ""
        tool_output = {}
        
        try:
            # Try to parse as JSON (for PineScript tool)
            tool_output = json.loads(last_tool_content)
        except (json.JSONDecodeError, TypeError):
            # Not JSON - this is from Exa or other tools
            # The assistant message will contain the analysis
            pass
        
        # Build the integrated answer
        integrated_answer = final_message
        
        # Only add code sections if we have PineScript output
        if tool_output.get('pinescript_code'):
            integrated_answer += "\n\n---\n\n"
        
        # Add PineScript code if available
        if tool_output.get('pinescript_code'):
            integrated_answer += "## PineScript Implementation\n\n"
            integrated_answer += f"```pinescript\n{tool_output['pinescript_code']}\n```\n\n"
        
        # Add visualizations if available
        if tool_output.get('visualizations'):
            viz = tool_output['visualizations']
            if viz.get('shadcn'):
                integrated_answer += "---\n\n## Visualization Component\n\n" + viz['shadcn'] + "\n\n"
            if viz.get('apexcharts'):
                integrated_answer += "---\n\n## Chart Configuration\n\n" + viz['apexcharts'] + "\n\n"
        
        # Add usage notes if available
        if tool_output.get('usage_notes'):
            integrated_answer += "---\n\n## Usage Notes\n\n" + tool_output['usage_notes']
        
        # Build WhatsApp summary with actual strategy details
        whatsapp_summary = f"*{user_input[:50]}*\n\n"
        
        # Extract key points from the tool output
        if tool_output.get('parameters'):
            whatsapp_summary += "Key Parameters:\n"
            for param in tool_output['parameters'][:4]:
                whatsapp_summary += f"• {param}\n"
        
        # Add a brief summary from explanation if available
        if tool_output.get('explanation'):
            # Take first 150 chars of explanation
            brief = tool_output['explanation'][:150].strip()
            if not brief.endswith('.'):
                brief = brief[:brief.rfind(' ')] + '...'
            whatsapp_summary += f"\n{brief}"
        
        whatsapp_summary += "\n\n_PineScript code included in full response_"
        
        # Build the expected JSON format
        output_json = {
            "answer": integrated_answer,
            "chatsummary": f"User asked: {user_input}. Provided PineScript strategy with implementation.",
            "whatsapp_summary": whatsapp_summary
        }
        
        output = json.dumps(output_json)
    else:
        # No tool was called - format as basic response
        # Extract key points from the answer for WhatsApp summary
        answer_text = assistant_messages[-1].content
        # Take first 200 chars or first paragraph
        first_para = answer_text.split('\n\n')[0] if '\n\n' in answer_text else answer_text[:200]
        if len(first_para) > 200:
            first_para = first_para[:197] + '...'
        
        whatsapp_summary = f"*{user_input[:50]}*\n\n{first_para}\n\n_Full explanation in main response_"
        
        output_json = {
            "answer": answer_text,
            "chatsummary": f"User asked: {user_input}. Provided explanation.",
            "whatsapp_summary": whatsapp_summary
        }
        output = json.dumps(output_json)
    
    # Verify and enhance the JSON response
    try:
        parsed = json.loads(output)
        
        # Ensure all required fields exist
        if "answer" not in parsed:
            parsed["answer"] = output
        
        # Ensure whatsapp_summary exists
        if "whatsapp_summary" not in parsed:
            parsed["whatsapp_summary"] = f"📱 *Response Generated*\\n\\n{user_input[:100]}...\\n\\n_See details above_ 📋"
            
        # Clean up the answer text - replace escape sequences properly for Markdown
        if isinstance(parsed.get("answer"), str):
            # Replace \n with actual newlines for Markdown
            parsed["answer"] = parsed["answer"].replace("\\n", "\n").replace("\\t", "  ").strip()
            
        # Ensure chatsummary exists
        if "chatsummary" not in parsed:
            parsed["chatsummary"] = f"User asked: {user_input}"
        
        json_str = json.dumps(parsed)
        
    except json.JSONDecodeError:
        # If it's not valid JSON, create proper structure
        response = {
            "answer": output.replace("\\n", "\n").replace("\\t", "  ").strip(),
            "chatsummary": f"User asked: {user_input}",
            "whatsapp_summary": f"📱 *Response Generated*\\n\\n{user_input[:100]}...\\n\\n_See details above_ 📋"
        }
        json_str = json.dumps(response)
    
    # Extract token usage from callback
    token_usage = token_callback.usage_metadata
    total_tokens = 0
    total_cost = 0.0
    
    if token_usage:
        # Sum tokens across all models (usually just one)
        for model_name, usage in token_usage.items():
            total_tokens += usage.get('total_tokens', 0)
            
            # Calculate cost based on Azure OpenAI pricing (approximate)
            # GPT-4o: $0.005 per 1K input tokens, $0.015 per 1K output tokens
            input_tokens = usage.get('input_tokens', 0)
            output_tokens = usage.get('output_tokens', 0)
            model_cost = (input_tokens * 0.005 / 1000) + (output_tokens * 0.015 / 1000)
            total_cost += model_cost
    
    # Return response with actual token usage
    return json_str, total_tokens, total_cost, [], []