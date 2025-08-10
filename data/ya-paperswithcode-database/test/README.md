# Test Directory

This directory contains all test scripts for the YA-PapersWithCode backend.

## Test Files

### API Tests
- `test_api.py` - Basic API endpoint tests
- `test_api_comprehensive.py` - Comprehensive API test suite
- `test_api_agent.py` - Agent search API tests
- `test_api_error.py` - API error handling tests
- `test_all_endpoints.py` - Tests for all API endpoints
- `test_frontend_integration.py` - Frontend integration tests

### Search Tests
- `test_search_flow.py` - Complete search flow tests
- `test_agent_search.py` - Agent search functionality tests
- `test_manager_issue.py` - Search manager issue tests
- `test_lazy_loading.py` - Lazy loading tests

### Other Tests
- `simple_test.py` - Simple test cases
- `test_individual.py` - Individual component tests
- `final_test.py` - Final integration tests

## Running Tests

To run the tests, first activate the virtual environment:

```bash
source ../.venv/bin/activate
```

Then run individual test files:

```bash
python test/test_api_comprehensive.py
python test/test_frontend_integration.py
```

Or use the test runner script:

```bash
cd test
bash run_tests.sh
```

## Requirements

Make sure the API server is running before executing tests:

```bash
# From the data/ya-paperswithcode-database directory
source .venv/bin/activate
python api_server.py
```