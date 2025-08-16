#!/usr/bin/env python3
"""
Final test script for API endpoints after all fixes.
"""
import json
from typing import Dict, Any

import requests

def test_api() -> None:
    """Test all API endpoints."""
    print("=" * 60)
    print("Final API Test - After All Fixes")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api/v1"
    
    # Test cases for dataset search
    dataset_tests = [
        {"query": "mnist", "max_results": 5},
        {"query": "mnist related", "max_results": 5},
        {"query": "image classification", "max_results": 5},
        {"query": "computer vision datasets", "max_results": 5}
    ]
    
    print("\n📊 Testing Dataset Search (AI Agent)")
    print("-" * 40)
    
    for test in dataset_tests:
        print(f"\nQuery: '{test['query']}'")
        
        try:
            response = requests.post(
                f"{base_url}/datasets/search/agent",
                json=test,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Success!")
                print(f"    Total results: {data.get('total', 0)}")
                print(f"    Search type: {data.get('search_type', 'N/A')}")
                
                if data.get('results'):
                    print(f"    Results found:")
                    for i, result in enumerate(data['results'][:3], 1):
                        name = result.get('name', result.get('id', 'N/A'))
                        print(f"      {i}. {name}")
                else:
                    print(f"    ⚠ No results returned")
            else:
                print(f"  ✗ Error {response.status_code}")
                try:
                    error = response.json()
                    print(f"    {error.get('detail', 'Unknown error')}")
                except json.JSONDecodeError:
                    print(f"    {response.text[:200]}")
                    
        except requests.RequestException as e:
            print(f"  ✗ Request failed: {e}")
    
    # Test paper search
    print("\n📄 Testing Paper Search (AI Agent)")
    print("-" * 40)
    
    paper_tests = [
        {"query": "transformer models", "max_results": 5},
        {"query": "deep learning", "max_results": 5}
    ]
    
    for test in paper_tests:
        print(f"\nQuery: '{test['query']}'")
        
        try:
            response = requests.post(
                f"{base_url}/papers/search/agent",
                json=test,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Success!")
                print(f"    Total results: {data.get('total', 0)}")
                
                if data.get('results'):
                    print(f"    First result: {data['results'][0].get('title', 'N/A')[:60]}...")
            else:
                print(f"  ✗ Error {response.status_code}")
                
        except requests.RequestException as e:
            print(f"  ✗ Request failed: {e}")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("\nIf you see errors above, please:")
    print("1. Stop the API server (Ctrl+C)")
    print("2. Restart it: ./start_backend.sh")
    print("3. Run this test again: python final_test.py")

if __name__ == "__main__":
    test_api()