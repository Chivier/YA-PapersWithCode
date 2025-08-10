#!/usr/bin/env python3
"""
Test Agent Search API endpoint
"""
import requests
import json

# Test the agent search endpoint
url = "http://localhost:8000/api/v1/datasets/search/agent"

test_queries = [
    "image classification datasets",
    "natural language processing datasets",
    "computer vision benchmarks",
    "ImageNet CIFAR"
]

print("Testing Agent Search API Endpoint")
print("=" * 60)

for query in test_queries:
    print(f"\nQuery: {query}")
    print("-" * 40)
    
    response = requests.post(url, json={"query": query})
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: ✓ Success")
        print(f"Search type: {data.get('search_type', 'N/A')}")
        print(f"Results found: {data.get('total', 0)}")
        print(f"Execution time: {data.get('execution_time', 'N/A')}s")
        
        if data.get('results'):
            print(f"\nFirst result:")
            result = data['results'][0]
            print(f"  - Name: {result.get('name', 'N/A')}")
            print(f"  - Task: {result.get('task', 'N/A')}")
            if 'description' in result:
                desc = result['description'][:100] + "..." if len(result.get('description', '')) > 100 else result.get('description', '')
                print(f"  - Description: {desc}")
    else:
        print(f"Status: ✗ Error {response.status_code}")
        print(f"Error: {response.text}")