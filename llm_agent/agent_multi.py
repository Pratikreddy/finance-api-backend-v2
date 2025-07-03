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
from llm_agent.tools_multi import generate_pinescript

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
tool_calling_prompt = """You are an expert trading strategy consultant who helps users design and implement trading strategies.

When answering questions about trading strategies:

1. ALWAYS provide a text-only explanation without any code. Focus on:
   - Strategy concept and how it works
   - Market conditions where it's effective
   - Key indicators or patterns involved
   - Risk management considerations
   - Entry and exit rules
   - Advantages and limitations

2. If the user needs PineScript code, ALWAYS use the generate_pinescript tool:
   - Call the tool with a clear description
   - The tool will return the code separately
   - DO NOT include any code in your explanation

3. Your response should be a clear, comprehensive explanation in plain text or markdown.
   DO NOT include PineScript code blocks in your response - let the tool handle that.

IMPORTANT: 
- Use the generate_pinescript tool for ANY PineScript code requests
- Keep your explanation separate from the code
- Focus on strategy explanation, not implementation details"""

# Create LangGraph agent with tool-friendly prompt
agent = create_react_agent(
    model=llm,
    tools=[generate_pinescript],
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
        # Tool was called - extract the PineScript output
        tool_output = json.loads(tool_messages[-1].content) if tool_messages else {}
        
        # Get the final assistant message that explains the strategy
        final_message = assistant_messages[-1].content
        
        # Build the expected JSON format
        output_json = {
            "answer": final_message,
            "code": f"```pinescript\\n{tool_output.get('pinescript_code', '')}\\n```" if tool_output.get('pinescript_code') else None,
            "visualizations": {
                "shadcn": None,
                "apexcharts": None
            },
            "chatsummary": f"User asked: {user_input}. Provided PineScript strategy with implementation."
        }
        
        # Get visualizations from tool output - they should already be in markdown format
        if tool_output.get('visualizations') and isinstance(tool_output['visualizations'], dict):
            viz = tool_output['visualizations']
            output_json['visualizations']['shadcn'] = viz.get('shadcn')
            output_json['visualizations']['apexcharts'] = viz.get('apexcharts')
        
        output = json.dumps(output_json)
    else:
        # No tool was called - format as basic response
        output_json = {
            "answer": assistant_messages[-1].content,
            "code": None,
            "visualizations": {
                "shadcn": None,
                "apexcharts": None
            },
            "chatsummary": f"User asked: {user_input}. Awaiting more specific requirements."
        }
        output = json.dumps(output_json)
    
    # Verify and enhance the JSON response
    try:
        parsed = json.loads(output)
        
        # Ensure all required fields exist
        if "answer" not in parsed:
            parsed["answer"] = output
        
        # Ensure visualizations is an object with shadcn and apexcharts keys
        if "visualizations" not in parsed or not isinstance(parsed["visualizations"], dict):
            parsed["visualizations"] = {
                "shadcn": None,
                "apexcharts": None
            }
        else:
            # Ensure both keys exist
            if "shadcn" not in parsed["visualizations"]:
                parsed["visualizations"]["shadcn"] = None
            if "apexcharts" not in parsed["visualizations"]:
                parsed["visualizations"]["apexcharts"] = None
            
        # Format code field as Markdown if present
        if "code" in parsed and parsed["code"]:
            # Only wrap in markdown if not already wrapped
            if not parsed["code"].startswith("```"):
                parsed["code"] = f"```pinescript\n{parsed['code']}\n```"
        else:
            parsed["code"] = None
            
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
            "code": None,
            "visualizations": {
                "shadcn": None,
                "apexcharts": None
            },
            "chatsummary": f"User asked: {user_input}"
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