#!/usr/bin/env python3
"""
Test all API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_endpoint(method, path, data=None, params=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{path}"
    
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            return None
            
        return {
            "status": response.status_code,
            "success": response.status_code == 200,
            "data": response.json() if response.status_code == 200 else response.text
        }
    except Exception as e:
        return {
            "status": 0,
            "success": False,
            "data": str(e)
        }

def main():
    print("Testing PapersWithCode API Endpoints")
    print("=" * 60)
    
    # Test cases
    tests = [
        # Basic search endpoints
        {
            "name": "Search Papers (SQLite)",
            "method": "POST",
            "path": "/papers/search",
            "data": {"query": "deep learning", "page": 1, "per_page": 5}
        },
        {
            "name": "Search Datasets (SQLite)",
            "method": "POST",
            "path": "/datasets/search",
            "data": {"query": "mnist", "page": 1, "per_page": 5}
        },
        
        # AI Agent search endpoints
        {
            "name": "Search Papers (AI Agent)",
            "method": "POST",
            "path": "/papers/search/agent",
            "data": {"query": "transformer models", "max_results": 5}
        },
        {
            "name": "Search Datasets (AI Agent)",
            "method": "POST",
            "path": "/datasets/search/agent",
            "data": {"query": "image classification", "max_results": 5}
        },
        
        # Get endpoints
        {
            "name": "Get Papers",
            "method": "GET",
            "path": "/papers",
            "params": {"page": 1, "per_page": 5}
        },
        {
            "name": "Get Datasets",
            "method": "GET",
            "path": "/datasets",
            "params": {"page": 1, "per_page": 5}
        }
    ]
    
    # Run tests
    results = []
    for test in tests:
        print(f"\nTesting: {test['name']}")
        print("-" * 40)
        
        result = test_endpoint(
            test["method"],
            test["path"],
            test.get("data"),
            test.get("params")
        )
        
        if result["success"]:
            print(f"✓ Success (Status: {result['status']})")
            if isinstance(result["data"], dict):
                if "results" in result["data"]:
                    print(f"  Results: {len(result['data']['results'])}")
                if "total" in result["data"]:
                    print(f"  Total: {result['data']['total']}")
                if "search_type" in result["data"]:
                    print(f"  Search Type: {result['data']['search_type']}")
        else:
            print(f"✗ Failed (Status: {result['status']})")
            if result["status"] != 0:
                try:
                    error_data = json.loads(result["data"])
                    print(f"  Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"  Error: {result['data'][:200]}")
            else:
                print(f"  Error: {result['data']}")
        
        results.append({
            "test": test["name"],
            "success": result["success"],
            "status": result["status"]
        })
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    
    for r in results:
        status = "✓" if r["success"] else "✗"
        print(f"{status} {r['test']}: {r['status']}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed < total:
        print("\n⚠ Some endpoints are failing. Please restart the API server after code changes.")

if __name__ == "__main__":
    main()