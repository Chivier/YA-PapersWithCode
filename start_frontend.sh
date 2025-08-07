#!/bin/bash

# Frontend startup script for YA-PapersWithCode
# This script sets up the Node.js environment and starts the React development server

set -e  # Exit on error

echo "=== YA-PapersWithCode Frontend Setup ==="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
FRONTEND_DIR="$SCRIPT_DIR/frontend/ya-paperswithcode"

# Change to frontend directory
cd "$FRONTEND_DIR"
log_info "Working directory: $FRONTEND_DIR"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    log_error "Node.js is not installed!"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        log_info "Please install Node.js using one of the following methods:"
        echo "  1. Using Homebrew: brew install node"
        echo "  2. Download from: https://nodejs.org/"
        echo "  3. Using nvm: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        log_info "Please install Node.js using one of the following methods:"
        echo "  1. Using apt: sudo apt update && sudo apt install nodejs npm"
        echo "  2. Using snap: sudo snap install node --classic"
        echo "  3. Download from: https://nodejs.org/"
    fi
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v)
log_info "Node.js version: $NODE_VERSION"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    log_error "npm is not installed!"
    log_info "Please install npm: https://www.npmjs.com/get-npm"
    exit 1
fi

NPM_VERSION=$(npm -v)
log_info "npm version: $NPM_VERSION"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    log_info "Installing dependencies (this may take a few minutes)..."
    npm install
else
    log_info "Dependencies already installed. Checking for updates..."
    # Check if package.json is newer than node_modules
    if [ "package.json" -nt "node_modules" ]; then
        log_warn "package.json has been modified. Updating dependencies..."
        npm install
    else
        log_info "Dependencies are up to date."
    fi
fi

# Check if the backend is running
if ! curl -s http://localhost:8000/health >/dev/null 2>&1; then
    log_warn "Backend API server is not running at http://localhost:8000"
    log_warn "Please run ./start_backend.sh in another terminal first!"
    echo
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    log_info "Backend API server is running at http://localhost:8000"
fi

# Check if another dev server is already running
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    log_warn "Port 5173 is already in use. Stopping existing process..."
    kill $(lsof -Pi :5173 -sTCP:LISTEN -t) 2>/dev/null || true
    sleep 2
fi

# Build CSS if needed
if [ -f "tailwind.config.js" ]; then
    log_info "Building Tailwind CSS..."
    npx tailwindcss -i ./src/index.css -o ./src/output.css --minify 2>/dev/null || true
fi

# Start the development server
log_info "Starting React development server..."
echo
echo "=== Frontend Development Server ==="
echo "Local:    http://localhost:5173"
echo "Network:  http://$(ipconfig getifaddr en0 2>/dev/null || hostname -I | awk '{print $1}'):5173"
echo
echo "Press Ctrl+C to stop the server"
echo

# Run the development server
npm run dev