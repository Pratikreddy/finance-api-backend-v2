#!/usr/bin/env python3
"""Test Exa integration via API"""

import requests
import json

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

# API endpoint
url = "http://localhost:8000/chat/invoke"
headers = {
    "Content-Type": "application/json",
    "x-user-uuid": "test-user-exa"
}

print("Testing Exa search integration via API...\n")

# Test first query
query = queries[0]
print(f"Query: {query}")
print("-" * 80)

try:
    response = requests.post(
        url,
        headers=headers,
        json={"input": {"query": query}},
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        output = result.get("output", {})
        
        print("\nResponse:")
        print(output.get("answer", "No answer provided"))
        print(f"\nTokens used: {output.get('tokens_used', 'N/A')}")
        print(f"Cost: ${output.get('cost', 0):.4f}")
        print(f"\nSummary: {output.get('chatsummary', 'No summary')}")
    else:
        print(f"Error: HTTP {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("Error: Could not connect to API. Make sure the server is running:")
    print("uvicorn main:app --reload")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)}")

print("\n" + "="*80)
print("Note: Make sure the API server is running before testing.")