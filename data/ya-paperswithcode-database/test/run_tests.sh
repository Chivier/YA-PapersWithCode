#!/bin/bash

# Run tests for PapersWithCode API
# This script starts the API server and runs all tests

echo "=========================================="
echo "PapersWithCode API Test Runner"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# API server configuration
API_DIR="../"
API_SCRIPT="api_server.py"
API_PORT=8000
API_URL="http://localhost:${API_PORT}"

# Function to check if server is running
check_server() {
    curl -s "${API_URL}/" > /dev/null 2>&1
    return $?
}

# Function to start API server
start_server() {
    echo -e "${YELLOW}Starting API server...${NC}"
    cd "$API_DIR"
    python "$API_SCRIPT" &
    SERVER_PID=$!
    cd - > /dev/null
    
    # Wait for server to start
    echo "Waiting for server to start..."
    for i in {1..30}; do
        if check_server; then
            echo -e "${GREEN}✅ Server started successfully (PID: $SERVER_PID)${NC}"
            return 0
        fi
        sleep 1
    done
    
    echo -e "${RED}❌ Failed to start server${NC}"
    return 1
}

# Function to stop API server
stop_server() {
    if [ ! -z "$SERVER_PID" ]; then
        echo -e "${YELLOW}Stopping API server (PID: $SERVER_PID)...${NC}"
        kill $SERVER_PID 2>/dev/null
        wait $SERVER_PID 2>/dev/null
        echo -e "${GREEN}✅ Server stopped${NC}"
    fi
}

# Trap to ensure server is stopped on exit
trap stop_server EXIT

# Main execution
echo "Checking if server is already running..."
if check_server; then
    echo -e "${YELLOW}⚠️  Server is already running on port ${API_PORT}${NC}"
    echo "Please stop it first or use the existing server"
    read -p "Continue with existing server? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    # Start the server
    if ! start_server; then
        exit 1
    fi
fi

# Run tests
echo ""
echo "=========================================="
echo "Running API Tests"
echo "=========================================="

# Run comprehensive test suite
echo -e "\n${YELLOW}1. Running comprehensive test suite...${NC}"
python test_api.py --wait 2

# Run individual endpoint tests
echo -e "\n${YELLOW}2. Running individual endpoint tests...${NC}"
python test_individual.py

# Summary
echo ""
echo "=========================================="
echo -e "${GREEN}All tests completed!${NC}"
echo "=========================================="
echo ""
echo "Test results have been saved to:"
echo "  - test_results.json (comprehensive test results)"
echo ""

# Ask if user wants to keep server running
if [ ! -z "$SERVER_PID" ]; then
    read -p "Keep API server running? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        trap - EXIT
        echo -e "${GREEN}Server is still running on ${API_URL}${NC}"
        echo "To stop it later, run: kill $SERVER_PID"
    fi
fi