#!/usr/bin/env python3
"""
Comprehensive test suite for PapersWithCode API.
Tests all endpoints with various scenarios.
"""
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

import requests

# API Configuration
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"
API_URL = f"{BASE_URL}{API_PREFIX}"


class APITester:
    def __init__(self, base_url: str = API_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log(self, message: str, level: str = "INFO") -> None:
        """Log test message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def test_endpoint(
        self,
        name: str,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        expected_status: int = 200
    ) -> Optional[requests.Response]:
        """Test a single endpoint."""
        url = f"{self.base_url}{endpoint}"
        self.log(f"Testing {name}: {method} {url}")
        
        try:
            if method == "GET":
                response = self.session.get(url, params=params)
            elif method == "POST":
                response = self.session.post(url, json=data, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Check status code
            if response.status_code == expected_status:
                self.log(f"✅ {name}: Status {response.status_code} (Expected: {expected_status})", "SUCCESS")
                result = "PASSED"
            else:
                self.log(f"❌ {name}: Status {response.status_code} (Expected: {expected_status})", "ERROR")
                result = "FAILED"
            
            # Log response
            try:
                response_data = response.json()
                self.log(f"Response preview: {json.dumps(response_data, indent=2)[:500]}...")
            except json.JSONDecodeError:
                self.log(f"Response: {response.text[:500]}...")
            
            self.test_results.append({
                "name": name,
                "endpoint": endpoint,
                "method": method,
                "status": response.status_code,
                "expected": expected_status,
                "result": result
            })
            
            return response
            
        except Exception as e:
            self.log(f"❌ {name}: Exception - {str(e)}", "ERROR")
            self.test_results.append({
                "name": name,
                "endpoint": endpoint,
                "method": method,
                "error": str(e),
                "result": "ERROR"
            })
            return None
    
    def run_all_tests(self) -> None:
        """Run all API tests."""
        self.log("="*60)
        self.log("Starting PapersWithCode API Test Suite")
        self.log("="*60)
        
        # Test 1: Root endpoint
        self.test_endpoint(
            name="Root Endpoint",
            method="GET",
            endpoint="/"
        )
        
        # Test 2: SQLite Search
        self.test_endpoint(
            name="SQLite Search - Basic",
            method="POST",
            endpoint="/search/sqlite",
            data={
                "query": "machine learning",
                "page": 1,
                "per_page": 10
            }
        )
        
        # Test 3: SQLite Search with filters
        self.test_endpoint(
            name="SQLite Search - With Filters",
            method="POST",
            endpoint="/search/sqlite",
            data={
                "query": "neural",
                "page": 1,
                "per_page": 5,
                "filters": {
                    "year": 2023,
                    "has_code": True
                }
            }
        )
        
        # Test 4: AI Agent Search
        self.test_endpoint(
            name="AI Agent Search",
            method="POST",
            endpoint="/search/agent",
            data={
                "query": "transformer models for NLP",
                "max_results": 10,
                "similarity_threshold": 0.7
            }
        )
        
        # Test 5: Get Papers
        self.test_endpoint(
            name="Get Papers - Basic",
            method="GET",
            endpoint="/papers",
            params={"page": 1, "per_page": 10}
        )
        
        # Test 6: Get Papers with filters
        self.test_endpoint(
            name="Get Papers - With Year Filter",
            method="GET",
            endpoint="/papers",
            params={"page": 1, "per_page": 5, "year": 2023}
        )
        
        # Test 7: Get Repositories
        self.test_endpoint(
            name="Get Repositories",
            method="GET",
            endpoint="/repositories",
            params={"page": 1, "per_page": 10}
        )
        
        # Test 8: Get Methods
        self.test_endpoint(
            name="Get Methods",
            method="GET",
            endpoint="/methods",
            params={"page": 1, "per_page": 10}
        )
        
        # Test 9: Get Datasets
        self.test_endpoint(
            name="Get Datasets",
            method="GET",
            endpoint="/datasets",
            params={"page": 1, "per_page": 10}
        )
        
        # Test 10: Statistics
        self.test_endpoint(
            name="Statistics",
            method="GET",
            endpoint="/statistics"
        )
        
        # Test 11: Data Import (Papers)
        self.test_endpoint(
            name="Import Papers",
            method="POST",
            endpoint="/import",
            data={
                "data_type": "papers",
                "data": [
                    {
                        "id": "test_paper_001",
                        "title": "Test Paper for API Testing",
                        "abstract": "This is a test paper for API testing purposes",
                        "authors": ["Test Author 1", "Test Author 2"],
                        "year": 2024,
                        "tasks": ["testing", "api-development"]
                    }
                ],
                "update_existing": False
            }
        )
        
        # Test 12: Data Export
        self.test_endpoint(
            name="Export Papers",
            method="POST",
            endpoint="/export",
            data={
                "data_type": "papers",
                "format": "json"
            }
        )
        
        # Test 13: Export with compression
        self.test_endpoint(
            name="Export Papers (Compressed)",
            method="POST",
            endpoint="/export",
            data={
                "data_type": "papers",
                "format": "json.gz"
            }
        )
        
        # Test 14: Invalid endpoint (should return 404)
        self.test_endpoint(
            name="Invalid Endpoint",
            method="GET",
            endpoint="/invalid_endpoint",
            expected_status=404
        )
        
        # Test 15: Search with empty query (should return 422)
        self.test_endpoint(
            name="Search with Empty Query",
            method="POST",
            endpoint="/search/sqlite",
            data={
                "query": "",
                "page": 1,
                "per_page": 10
            },
            expected_status=422
        )
        
        self.print_summary()
    
    def print_summary(self) -> None:
        """Print test results summary."""
        self.log("="*60)
        self.log("Test Results Summary")
        self.log("="*60)
        
        passed = sum(1 for r in self.test_results if r["result"] == "PASSED")
        failed = sum(1 for r in self.test_results if r["result"] == "FAILED")
        errors = sum(1 for r in self.test_results if r["result"] == "ERROR")
        
        total = len(self.test_results)
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Errors: {errors}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if failed > 0 or errors > 0:
            print("\nFailed/Error Tests:")
            for result in self.test_results:
                if result["result"] in ["FAILED", "ERROR"]:
                    print(f"  - {result['name']}: {result.get('error', 'Status mismatch')}")
        
        # Save detailed results
        with open("test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\nDetailed results saved to test_results.json")


def main() -> None:
    """Main test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test PapersWithCode API")
    parser.add_argument("--url", default=BASE_URL, help="API base URL")
    parser.add_argument("--wait", type=int, default=0, help="Wait N seconds before starting tests")
    args = parser.parse_args()
    
    if args.wait > 0:
        print(f"Waiting {args.wait} seconds for server to start...")
        time.sleep(args.wait)
    
    # Check if server is running
    try:
        response = requests.get(f"{args.url}/")
        print(f"✅ Server is running at {args.url}")
    except requests.RequestException:
        print(f"❌ Server is not running at {args.url}")
        print("Please start the server with: python api_server.py")
        return
    
    # Run tests
    tester = APITester(f"{args.url}{API_PREFIX}")
    tester.run_all_tests()


if __name__ == "__main__":
    main()