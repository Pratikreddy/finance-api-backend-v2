#!/usr/bin/env python3
"""Comprehensive test script for Exa search integration"""

import json
import time
import subprocess
import sys

# Test queries
test_queries = [
    "Give me a detailed report on HDFC Bank's Q4 earnings",
    "What sectors are gaining strength after RBI's latest policy?",
    "Is it a good time to buy auto stocks before the budget?",
    "Compare Reliance and Adani Green fundamentals for the last 2 years",
    "What's the market sentiment around NIFTY this week?",
    "Break down the US Fed's statement and its impact on Indian IT stocks",
    "Summarize top 5 news that could affect options expiry tomorrow"
]

def test_query(query, index):
    """Test a single query against the API"""
    print(f"\n{'='*80}")
    print(f"Test {index+1}: {query}")
    print(f"{'='*80}")
    
    cmd = [
        'curl', '-X', 'POST', 'http://localhost:8001/chat/invoke',
        '-H', 'Content-Type: application/json',
        '-H', 'x-user-uuid: test-user-exa',
        '-d', json.dumps({"query": query}),
        '--silent', '--show-error'
    ]
    
    try:
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        elapsed_time = time.time() - start_time
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            output = response.get('output', {})
            
            print(f"\nStatus: SUCCESS")
            print(f"Response Time: {elapsed_time:.2f} seconds")
            print(f"Tokens Used: {output.get('tokens_used', 'N/A')}")
            print(f"Cost: ${output.get('cost', 0):.4f}")
            
            print(f"\nAnswer Preview (first 500 chars):")
            answer = output.get('answer', 'No answer')
            print(answer[:500] + "..." if len(answer) > 500 else answer)
            
            print(f"\nWhatsApp Summary:")
            print(output.get('whatsapp_summary', 'No summary'))
            
            return True, elapsed_time, output.get('tokens_used', 0), output.get('cost', 0)
        else:
            print(f"\nStatus: FAILED")
            print(f"Error: {result.stderr}")
            return False, elapsed_time, 0, 0
            
    except subprocess.TimeoutExpired:
        print(f"\nStatus: TIMEOUT")
        return False, 60, 0, 0
    except Exception as e:
        print(f"\nStatus: ERROR")
        print(f"Exception: {str(e)}")
        return False, 0, 0, 0

def main():
    print("EXA SEARCH INTEGRATION TEST SUITE")
    print("=================================")
    print(f"Testing {len(test_queries)} queries...")
    
    # Test results summary
    results = []
    total_time = 0
    total_tokens = 0
    total_cost = 0
    successful = 0
    
    for i, query in enumerate(test_queries):
        success, time_taken, tokens, cost = test_query(query, i)
        results.append({
            'query': query,
            'success': success,
            'time': time_taken,
            'tokens': tokens,
            'cost': cost
        })
        
        if success:
            successful += 1
            total_time += time_taken
            total_tokens += tokens
            total_cost += cost
        
        # Small delay between requests
        time.sleep(2)
    
    # Print summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Total Tests: {len(test_queries)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(test_queries) - successful}")
    print(f"Success Rate: {(successful/len(test_queries)*100):.1f}%")
    print(f"\nPerformance Metrics:")
    print(f"Total Time: {total_time:.2f} seconds")
    print(f"Average Response Time: {(total_time/successful if successful > 0 else 0):.2f} seconds")
    print(f"Total Tokens: {total_tokens:,}")
    print(f"Total Cost: ${total_cost:.4f}")
    
    # Save results to JSON
    with open('exa_test_results.json', 'w') as f:
        json.dump({
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_tests': len(test_queries),
                'successful': successful,
                'failed': len(test_queries) - successful,
                'total_time': total_time,
                'total_tokens': total_tokens,
                'total_cost': total_cost
            },
            'results': results
        }, f, indent=2)
    
    print(f"\nResults saved to exa_test_results.json")

if __name__ == "__main__":
    # Check if server is running
    try:
        subprocess.run(['curl', 'http://localhost:8001/health', '--silent'], 
                      check=True, capture_output=True, timeout=2)
        main()
    except:
        print("ERROR: Server not running on port 8001")
        print("Please start the server with:")
        print("  source venv/bin/activate && python3 -m uvicorn main:app --port 8001")
        sys.exit(1)