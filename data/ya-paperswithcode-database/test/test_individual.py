#!/usr/bin/env python3
"""
Individual API endpoint test scripts.
Each function tests a specific endpoint in detail.
"""
import json
from typing import Dict, Any, List, Optional

import requests

BASE_URL = "http://localhost:8000/api/v1"


def test_sqlite_search() -> None:
    """Test SQLite search endpoint."""
    print("\n" + "="*50)
    print("Testing SQLite Search Endpoint")
    print("="*50)
    
    endpoint = f"{BASE_URL}/search/sqlite"
    
    # Test cases
    test_cases = [
        {
            "name": "Basic search",
            "data": {
                "query": "deep learning",
                "page": 1,
                "per_page": 5
            }
        },
        {
            "name": "Search with year filter",
            "data": {
                "query": "transformer",
                "page": 1,
                "per_page": 10,
                "filters": {"year": 2023}
            }
        },
        {
            "name": "Search with task filter",
            "data": {
                "query": "neural",
                "page": 1,
                "per_page": 5,
                "filters": {"task": "image-classification"}
            }
        },
        {
            "name": "Search papers with code",
            "data": {
                "query": "bert",
                "page": 1,
                "per_page": 10,
                "filters": {"has_code": True}
            }
        },
        {
            "name": "Pagination test",
            "data": {
                "query": "model",
                "page": 2,
                "per_page": 20
            }
        }
    ]
    
    for test in test_cases:
        print(f"\n📝 Test: {test['name']}")
        print(f"Request: {json.dumps(test['data'], indent=2)}")
        
        try:
            response = requests.post(endpoint, json=test['data'])
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Results found: {data.get('total', 0)}")
                print(f"Page: {data.get('page', 0)}/{(data.get('total', 0) - 1) // data.get('per_page', 1) + 1}")
                print(f"Execution time: {data.get('execution_time', 0):.3f}s")
                
                if data.get('results'):
                    print(f"First result: {data['results'][0].get('title', 'N/A')[:80]}...")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Exception: {str(e)}")


def test_ai_search() -> None:
    """Test AI agent search endpoint."""
    print("\n" + "="*50)
    print("Testing AI Agent Search Endpoint")
    print("="*50)
    
    endpoint = f"{BASE_URL}/search/agent"
    
    test_cases = [
        {
            "name": "Natural language query",
            "data": {
                "query": "papers about using transformers for computer vision tasks",
                "max_results": 10
            }
        },
        {
            "name": "Query with similarity threshold",
            "data": {
                "query": "recent advances in federated learning",
                "max_results": 15,
                "similarity_threshold": 0.8
            }
        },
        {
            "name": "Specific model request",
            "data": {
                "query": "BERT improvements for multilingual NLP",
                "model": "default",
                "max_results": 20
            }
        }
    ]
    
    for test in test_cases:
        print(f"\n📝 Test: {test['name']}")
        print(f"Request: {json.dumps(test['data'], indent=2)}")
        
        try:
            response = requests.post(endpoint, json=test['data'])
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Results found: {data.get('total', 0)}")
                print(f"Search type: {data.get('search_type', 'N/A')}")
                print(f"Execution time: {data.get('execution_time', 0):.3f}s")
                
                if data.get('results'):
                    print(f"Top results:")
                    for i, paper in enumerate(data['results'][:3], 1):
                        print(f"  {i}. {paper.get('title', 'N/A')[:70]}...")
            else:
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"Exception: {str(e)}")


def test_import_export() -> None:
    """Test data import and export endpoints."""
    print("\n" + "="*50)
    print("Testing Import/Export Endpoints")
    print("="*50)
    
    # Test Import
    print("\n📥 Testing Data Import")
    import_endpoint = f"{BASE_URL}/import"
    
    test_data = {
        "data_type": "papers",
        "data": [
            {
                "id": f"test_paper_{i}",
                "title": f"Test Paper {i}: Advanced Machine Learning Techniques",
                "abstract": f"This is test paper {i} about ML techniques and algorithms.",
                "authors": [f"Author {j}" for j in range(1, 4)],
                "year": 2023 + (i % 2),
                "month": (i % 12) + 1,
                "tasks": ["machine-learning", "deep-learning"],
                "methods": ["neural-network", "transformer"],
                "arxiv_id": f"2024.{1000+i}"
            }
            for i in range(1, 4)
        ],
        "update_existing": True
    }
    
    print(f"Importing {len(test_data['data'])} test papers...")
    
    try:
        response = requests.post(import_endpoint, json=test_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Imported: {data.get('imported', 0)}")
            print(f"Updated: {data.get('updated', 0)}")
            print(f"Failed: {data.get('failed', 0)}")
            print(f"Execution time: {data.get('execution_time', 0):.3f}s")
            
            if data.get('errors'):
                print(f"Errors: {data['errors'][:3]}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {str(e)}")
    
    # Test Export
    print("\n📤 Testing Data Export")
    export_endpoint = f"{BASE_URL}/export"
    
    export_tests = [
        {
            "name": "Export papers as JSON",
            "data": {
                "data_type": "papers",
                "format": "json"
            }
        },
        {
            "name": "Export all data compressed",
            "data": {
                "data_type": "all",
                "format": "json.gz"
            }
        }
    ]
    
    for test in export_tests:
        print(f"\n📝 {test['name']}")
        
        try:
            response = requests.post(export_endpoint, json=test['data'])
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Filename: {data.get('filename', 'N/A')}")
                print(f"Path: {data.get('path', 'N/A')}")
                print(f"Records exported: {data.get('records', 0)}")
                print(f"Format: {data.get('format', 'N/A')}")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Exception: {str(e)}")


def test_resource_endpoints() -> None:
    """Test resource endpoints (papers, repos, methods, datasets)."""
    print("\n" + "="*50)
    print("Testing Resource Endpoints")
    print("="*50)
    
    endpoints = [
        {
            "name": "Papers",
            "url": f"{BASE_URL}/papers",
            "params": {"page": 1, "per_page": 5}
        },
        {
            "name": "Papers with year filter",
            "url": f"{BASE_URL}/papers",
            "params": {"page": 1, "per_page": 5, "year": 2023}
        },
        {
            "name": "Repositories",
            "url": f"{BASE_URL}/repositories",
            "params": {"page": 1, "per_page": 5}
        },
        {
            "name": "Methods",
            "url": f"{BASE_URL}/methods",
            "params": {"page": 1, "per_page": 5}
        },
        {
            "name": "Datasets",
            "url": f"{BASE_URL}/datasets",
            "params": {"page": 1, "per_page": 5}
        }
    ]
    
    for endpoint in endpoints:
        print(f"\n📝 Testing: {endpoint['name']}")
        print(f"URL: {endpoint['url']}")
        print(f"Params: {endpoint['params']}")
        
        try:
            response = requests.get(endpoint['url'], params=endpoint['params'])
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                print(f"Results: {len(results)}")
                print(f"Total available: {data.get('total', 'N/A')}")
                
                if results:
                    first = results[0]
                    if 'title' in first:
                        print(f"First item: {first.get('title', 'N/A')[:60]}...")
                    elif 'name' in first:
                        print(f"First item: {first.get('name', 'N/A')}")
                    elif 'repo_url' in first:
                        print(f"First item: {first.get('repo_url', 'N/A')}")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Exception: {str(e)}")


def test_statistics() -> None:
    """Test statistics endpoint."""
    print("\n" + "="*50)
    print("Testing Statistics Endpoint")
    print("="*50)
    
    endpoint = f"{BASE_URL}/statistics"
    
    try:
        response = requests.get(endpoint)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            stats = response.json()
            
            print("\n📊 Database Statistics:")
            print(f"  Total Papers: {stats.get('total_papers', 0):,}")
            print(f"  Papers with ArXiv ID: {stats.get('papers_with_arxiv', 0):,}")
            print(f"  Papers with Abstract: {stats.get('papers_with_abstract', 0):,}")
            print(f"  Papers with Code: {stats.get('papers_with_code', 0):,}")
            print(f"  Total Repositories: {stats.get('total_repositories', 0):,}")
            print(f"  Total Methods: {stats.get('total_methods', 0):,}")
            print(f"  Total Datasets: {stats.get('total_datasets', 0):,}")
            print(f"  Total Tasks: {stats.get('total_tasks', 0):,}")
            print(f"  Total Evaluations: {stats.get('total_evaluations', 0):,}")
            
            if stats.get('papers_by_year'):
                print("\n📅 Papers by Year (Top 5):")
                for item in stats['papers_by_year'][:5]:
                    print(f"  {item['year']}: {item['count']:,} papers")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {str(e)}")


def test_error_handling() -> None:
    """Test API error handling."""
    print("\n" + "="*50)
    print("Testing Error Handling")
    print("="*50)
    
    test_cases = [
        {
            "name": "Invalid endpoint",
            "method": "GET",
            "url": f"{BASE_URL}/invalid_endpoint",
            "expected_status": 404
        },
        {
            "name": "Empty search query",
            "method": "POST",
            "url": f"{BASE_URL}/search/sqlite",
            "data": {"query": "", "page": 1, "per_page": 10},
            "expected_status": 422
        },
        {
            "name": "Invalid page number",
            "method": "POST",
            "url": f"{BASE_URL}/search/sqlite",
            "data": {"query": "test", "page": 0, "per_page": 10},
            "expected_status": 422
        },
        {
            "name": "Invalid data type for import",
            "method": "POST",
            "url": f"{BASE_URL}/import",
            "data": {"data_type": "invalid_type", "data": []},
            "expected_status": 500
        },
        {
            "name": "Missing required field",
            "method": "POST",
            "url": f"{BASE_URL}/search/sqlite",
            "data": {"page": 1, "per_page": 10},
            "expected_status": 422
        }
    ]
    
    for test in test_cases:
        print(f"\n📝 Test: {test['name']}")
        print(f"Expected status: {test['expected_status']}")
        
        try:
            if test['method'] == 'GET':
                response = requests.get(test['url'])
            else:
                response = requests.post(test['url'], json=test.get('data', {}))
            
            print(f"Actual status: {response.status_code}")
            
            if response.status_code == test['expected_status']:
                print("✅ Error handled correctly")
            else:
                print("❌ Unexpected status code")
                print(f"Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"Exception: {str(e)}")


def main() -> None:
    """Run individual tests."""
    import sys
    
    # Check if server is running
    try:
        response = requests.get(f"http://localhost:8000/")
        print("✅ Server is running")
    except requests.RequestException:
        print("❌ Server is not running. Please start with: python api_server.py")
        sys.exit(1)
    
    # Run all test functions
    test_functions = [
        test_sqlite_search,
        test_ai_search,
        test_import_export,
        test_resource_endpoints,
        test_statistics,
        test_error_handling
    ]
    
    for func in test_functions:
        func()
    
    print("\n" + "="*50)
    print("All tests completed!")
    print("="*50)


if __name__ == "__main__":
    main()