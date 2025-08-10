#!/usr/bin/env python3
"""Test script to verify frontend integration with fixed dataset IDs"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_dataset_search_with_ids():
    """Test that dataset search returns proper IDs for frontend"""
    print("=" * 60)
    print("Testing Dataset Search API - Frontend Integration")
    print("=" * 60)
    
    endpoint = f"{BASE_URL}/api/v1/datasets/search/agent"
    
    test_cases = [
        {
            "name": "MNIST Related",
            "query": {"query": "mnist related", "limit": 5}
        },
        {
            "name": "Image Classification",
            "query": {"query": "image classification", "limit": 5}
        },
        {
            "name": "NLP Datasets",
            "query": {"query": "natural language processing", "limit": 5}
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"\n📝 Test: {test_case['name']}")
        print("-" * 40)
        
        try:
            response = requests.post(endpoint, json=test_case['query'])
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                print(f"✓ Status: 200 OK")
                print(f"✓ Found {len(results)} results")
                
                # Check each result has required fields for frontend
                missing_ids = []
                for result in results:
                    required_fields = ['id', 'name', 'description']
                    missing_fields = [field for field in required_fields if field not in result or not result[field]]
                    
                    if 'id' not in result or not result['id']:
                        missing_ids.append(result.get('name', 'Unknown'))
                
                if missing_ids:
                    print(f"❌ Missing IDs for: {', '.join(missing_ids)}")
                    all_passed = False
                else:
                    print(f"✓ All {len(results)} datasets have valid IDs")
                    
                    # Show sample results
                    if results:
                        print("\n  Sample results:")
                        for i, dataset in enumerate(results[:3], 1):
                            print(f"    {i}. {dataset['name']}")
                            print(f"       ID: {dataset['id']}")
                            print(f"       URL: /datasets/{dataset['id']}")
            else:
                print(f"❌ Error: Status {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            all_passed = False
    
    return all_passed

def test_dataset_detail_urls():
    """Test that dataset detail URLs would work"""
    print("\n" + "=" * 60)
    print("Testing Dataset Detail URL Formation")
    print("=" * 60)
    
    # Get some datasets
    endpoint = f"{BASE_URL}/api/v1/datasets/search/agent"
    response = requests.post(endpoint, json={"query": "popular datasets", "limit": 10})
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        
        print(f"Checking {len(results)} dataset URLs...")
        
        valid_ids = []
        invalid_ids = []
        
        for dataset in results:
            dataset_id = dataset.get('id', '')
            dataset_name = dataset.get('name', 'Unknown')
            
            # Check if ID is valid for URL
            if dataset_id and dataset_id.replace('-', '').replace('_', '').isalnum():
                valid_ids.append((dataset_name, dataset_id))
            else:
                invalid_ids.append((dataset_name, dataset_id))
        
        print(f"\n✓ Valid IDs: {len(valid_ids)}")
        for name, id in valid_ids[:5]:
            print(f"   {name}: /datasets/{id}")
            
        if invalid_ids:
            print(f"\n❌ Invalid IDs: {len(invalid_ids)}")
            for name, id in invalid_ids[:5]:
                print(f"   {name}: {id}")
            return False
        else:
            print("\n✅ All dataset IDs are valid for frontend routing")
            return True
    else:
        print(f"❌ Failed to fetch datasets: {response.status_code}")
        return False

def main():
    """Run all tests"""
    print("\n🚀 Frontend Integration Test Suite\n")
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL)
        if response.status_code != 200:
            print("❌ API server is not responding properly")
            return
    except:
        print("❌ Cannot connect to API server at", BASE_URL)
        print("   Please ensure the server is running")
        return
    
    # Run tests
    test1_passed = test_dataset_search_with_ids()
    test2_passed = test_dataset_detail_urls()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    if test1_passed and test2_passed:
        print("✅ All tests passed! Frontend should display datasets correctly.")
        print("\nThe frontend DatasetCard component should now work properly:")
        print("  - Each dataset has a valid 'id' field")
        print("  - Dataset URLs are properly formed: /datasets/{id}")
        print("  - No console warnings about missing IDs")
    else:
        print("❌ Some tests failed. Please review the errors above.")
        print("\nIssues that may affect frontend:")
        if not test1_passed:
            print("  - Some datasets missing ID fields")
        if not test2_passed:
            print("  - Some dataset IDs invalid for URL routing")

if __name__ == "__main__":
    main()