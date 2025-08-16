#!/usr/bin/env python3
"""Comprehensive API test script."""
import json
import time
from typing import Dict, Any, List

import requests

BASE_URL = "http://localhost:8000"

def test_agent_search() -> None:
    """Test various agent search queries."""
    print("=" * 60)
    print("Testing Agent Search API")
    print("=" * 60)
    
    test_queries = [
        {"query": "mnist related", "limit": 3},
        {"query": "image classification dataset", "limit": 3},
        {"query": "nlp text dataset", "limit": 3},
        {"query": "computer vision benchmark", "limit": 3},
    ]
    
    endpoint = f"{BASE_URL}/api/v1/datasets/search/agent"
    
    for test_data in test_queries:
        print(f"\nQuery: {test_data['query']}")
        print("-" * 40)
        
        try:
            response = requests.post(endpoint, json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                print(f"✓ Status: 200 OK")
                print(f"✓ Found {len(results)} results")
                print(f"✓ Execution time: {data.get('execution_time', 'N/A')}s")
                
                if results:
                    print("\nTop results:")
                    for i, item in enumerate(results[:3], 1):
                        print(f"  {i}. {item.get('name', 'Unknown')}")
                        desc = item.get('short_description', item.get('description', 'No description'))
                        if desc:
                            print(f"     {desc[:80]}...")
            else:
                print(f"✗ Error: Status {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"✗ Request failed: {e}")
        
        time.sleep(0.5)  # Small delay between requests

def test_regular_search() -> None:
    """Test regular dataset search."""
    print("\n" + "=" * 60)
    print("Testing Regular Dataset Search API")
    print("=" * 60)
    
    endpoint = f"{BASE_URL}/api/v1/datasets/search"
    
    test_data = {
        "search": "mnist",
        "limit": 5
    }
    
    try:
        response = requests.get(endpoint, params=test_data)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            print(f"✓ Regular search working")
            print(f"✓ Found {len(results)} results for 'mnist'")
            
            if results:
                print("\nTop results:")
                for i, item in enumerate(results[:3], 1):
                    print(f"  {i}. {item.get('name', 'Unknown')}")
        else:
            print(f"✗ Error: Status {response.status_code}")
            
    except Exception as e:
        print(f"✗ Request failed: {e}")

def test_api_health() -> bool:
    """Test API health endpoints."""
    print("\n" + "=" * 60)
    print("Testing API Health")
    print("=" * 60)
    
    # Test root endpoint
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print(f"✓ API root accessible")
        else:
            print(f"✗ API root error: {response.status_code}")
    except Exception as e:
        print(f"✗ Cannot connect to API: {e}")
        return False
        
    # Test API docs
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print(f"✓ API documentation accessible at {BASE_URL}/docs")
        else:
            print(f"✗ API docs error: {response.status_code}")
    except Exception as e:
        print(f"✗ Cannot access API docs: {e}")
        
    return True

def main() -> None:
    """Run all tests."""
    print("\n🚀 Starting Comprehensive API Tests\n")
    
    if not test_api_health():
        print("\n❌ API is not accessible. Please ensure the server is running.")
        return
        
    test_agent_search()
    test_regular_search()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()