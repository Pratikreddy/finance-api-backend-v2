#!/usr/bin/env python3
"""Test script for Exa search queries"""

import json
from llm_agent.agent_multi import run_pinescript_agent

# Test queries
queries = [
    "Give me a detailed report on HDFC Bank's Q4 earnings",
    "What sectors are gaining strength after RBI's latest policy?",
    "Is it a good time to buy auto stocks before the budget?",
    "Compare Reliance and Adani Green fundamentals for the last 2 years",
    "What's the market sentiment around NIFTY this week?",
    "Break down the US Fed's statement and its impact on Indian IT stocks",
    "Summarize top 5 news that could affect options expiry tomorrow"
]

print("Testing Exa search integration with financial queries...\n")

# Test first query only (to avoid rate limits)
query = queries[0]
print(f"Testing query: {query}")
print("-" * 80)

try:
    # Run the agent
    result_json, tokens, cost, _, _ = run_pinescript_agent(query)
    
    # Parse the result
    result = json.loads(result_json)
    
    print("\nResponse:")
    print(result.get("answer", "No answer provided"))
    print(f"\nTokens used: {tokens}")
    print(f"Cost: ${cost:.4f}")
    print(f"\nSummary: {result.get('chatsummary', 'No summary')}")
    
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("Note: Only testing one query to avoid rate limits. Modify script to test more.")