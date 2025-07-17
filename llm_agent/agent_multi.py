import os
import json
from typing import Tuple, List, Any
from langchain_openai import AzureChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.callbacks import UsageMetadataCallbackHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from llm_agent.prompts_multi import SIMPLE_PROMPT, TOOL_CALLING_PROMPT
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
# Create LangGraph agent with tool-friendly prompt from prompts file
agent = create_react_agent(
    model=llm,
    tools=[generate_pinescript, exa_search, exa_find_similar],
    prompt=TOOL_CALLING_PROMPT
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
    
    # The agent should return properly formatted JSON
    # Get the final response from the last assistant message
    final_response = assistant_messages[-1].content
    
    
    # Try to parse the response as JSON
    try:
        parsed = json.loads(final_response)
        
        # Ensure all required fields exist
        if "answer" not in parsed:
            parsed["answer"] = final_response
        
        # Ensure whatsapp_summary exists
        if "whatsapp_summary" not in parsed:
            parsed["whatsapp_summary"] = f"*{user_input}*\n\nSee full response for details."
            
        # Clean up the answer text - replace escape sequences properly for Markdown
        if isinstance(parsed.get("answer"), str):
            # Replace \n with actual newlines for Markdown
            parsed["answer"] = parsed["answer"].replace("\\n", "\n").replace("\\t", "  ").strip()
            
        # Ensure chatsummary exists
        if "chatsummary" not in parsed:
            parsed["chatsummary"] = f"User asked: {user_input}"
        
        json_str = json.dumps(parsed)
        
    except json.JSONDecodeError:
        # If it's not valid JSON, create proper structure from the response
        response = {
            "answer": final_response.replace("\\n", "\n").replace("\\t", "  ").strip(),
            "chatsummary": f"User asked: {user_input}",
            "whatsapp_summary": f"*{user_input}*\n\nSee full response for details."
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