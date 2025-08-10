#!/usr/bin/env python3
"""
Test API endpoint and get detailed error information
"""
import requests
import json
import traceback

def test_api_endpoint():
    """Test the dataset search API endpoint"""
    
    url = "http://localhost:8000/api/v1/datasets/search/agent"
    
    test_queries = [
        {"query": "mnist", "max_results": 5},
        {"query": "image classification datasets", "max_results": 5}
    ]
    
    for test_data in test_queries:
        print(f"\n{'='*60}")
        print(f"Testing query: {test_data['query']}")
        print(f"{'='*60}")
        
        try:
            response = requests.post(url, json=test_data, timeout=30)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Success! Results: {data.get('total', 0)}")
                if data.get('results'):
                    print(f"First result: {data['results'][0].get('name', 'N/A')}")
            else:
                print(f"Error Response:")
                print(f"Headers: {dict(response.headers)}")
                print(f"Content: {response.text}")
                
                # Try to parse as JSON
                try:
                    error_data = response.json()
                    print(f"Error detail: {error_data.get('detail', 'No detail')}")
                except:
                    print("Could not parse error as JSON")
                    
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            traceback.print_exc()
        except Exception as e:
            print(f"Unexpected error: {e}")
            traceback.print_exc()

def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get("http://localhost:8000/docs")
        if response.status_code == 200:
            print("✓ API server is running")
            return True
    except:
        print("✗ API server is not responding")
        return False
    return False

if __name__ == "__main__":
    print("Testing PapersWithCode API")
    
    if check_api_health():
        test_api_endpoint()
    else:
        print("Please start the API server first")