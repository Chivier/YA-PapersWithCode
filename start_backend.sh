#!/bin/bash

# Backend startup script for YA-PapersWithCode
# This script sets up the Python environment, downloads data, initializes the database, and starts the API server

set -e  # Exit on error

echo "=== YA-PapersWithCode Backend Setup ==="
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
BACKEND_DIR="$SCRIPT_DIR/data/ya-paperswithcode-database"

# Change to backend directory
cd "$BACKEND_DIR"
log_info "Working directory: $BACKEND_DIR"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    log_warn "uv is not installed. Installing uv..."
    
    # Detect OS and install uv
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            log_info "Installing uv using Homebrew..."
            brew install uv
        else
            log_info "Installing uv using curl..."
            curl -LsSf https://astral.sh/uv/install.sh | sh
            # Add to PATH for current session
            export PATH="$HOME/.cargo/bin:$PATH"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        log_info "Installing uv using curl..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        # Add to PATH for current session
        export PATH="$HOME/.cargo/bin:$PATH"
    else
        log_error "Unsupported OS: $OSTYPE"
        log_info "Please install uv manually: https://github.com/astral-sh/uv"
        exit 1
    fi
    
    # Verify installation
    if ! command -v uv &> /dev/null; then
        log_error "Failed to install uv. Please install it manually."
        exit 1
    fi
    log_info "uv installed successfully!"
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    log_info "Creating Python virtual environment..."
    uv venv
fi

# Activate virtual environment
log_info "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
log_info "Installing Python dependencies..."
uv pip install fastapi uvicorn pydantic python-multipart aiofiles python-dotenv

# Install AI model dependencies
log_info "Installing AI model dependencies..."
uv pip install requests sentence-transformers torch transformers huggingface_hub || {
    log_warn "Some AI dependencies could not be installed. AI features may be limited."
}

# Check required Python files
REQUIRED_FILES=("api_server.py" "init_database.py" "schema.sql")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        log_error "Required file $file is missing!"
        log_info "Please ensure all backend files are present."
        exit 1
    fi
done

# Check if JSON data files exist
DATA_FILES=("papers-with-abstracts.json" "datasets.json" "methods.json" "evaluation-tables.json" "links-between-papers-and-code.json")
NEED_DOWNLOAD=false

for file in "${DATA_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        NEED_DOWNLOAD=true
        break
    fi
done

# Download data if needed
if [ "$NEED_DOWNLOAD" = true ]; then
    log_info "Data files not found. Downloading PapersWithCode data..."
    
    # Download compressed files
    BASE_URL="https://github.com/paperswithcode/paperswithcode-data/releases/download/v1.93.2/"
    
    for file in "${DATA_FILES[@]}"; do
        if [ ! -f "$file" ]; then
            GZ_FILE="${file}.gz"
            if [ ! -f "$GZ_FILE" ]; then
                log_info "Downloading $GZ_FILE..."
                curl -L -o "$GZ_FILE" "${BASE_URL}${GZ_FILE}"
            fi
            
            log_info "Extracting $GZ_FILE..."
            gunzip -k "$GZ_FILE" || true
        fi
    done
else
    log_info "Data files already exist."
fi

# Database initialization with duplicate checking
if [ ! -f "paperswithcode.db" ]; then
    log_info "Database not found. Creating new database..."
    python init_database.py
    
    # Remove duplicates after initial load
    log_info "Removing duplicate entries..."
    python -c "
import sqlite3
conn = sqlite3.connect('paperswithcode.db')
cursor = conn.cursor()

# Remove duplicate papers (keeping the first occurrence)
cursor.execute('''
    DELETE FROM papers
    WHERE rowid NOT IN (
        SELECT MIN(rowid)
        FROM papers
        GROUP BY id
    )
''')
papers_removed = cursor.rowcount

# Remove duplicate datasets (keeping the first occurrence)
cursor.execute('''
    DELETE FROM datasets
    WHERE rowid NOT IN (
        SELECT MIN(rowid)
        FROM datasets
        GROUP BY id
    )
''')
datasets_removed = cursor.rowcount

# Remove duplicate methods (keeping the first occurrence)
cursor.execute('''
    DELETE FROM methods
    WHERE rowid NOT IN (
        SELECT MIN(rowid)
        FROM methods
        GROUP BY id
    )
''')
methods_removed = cursor.rowcount

# Remove duplicate repositories (keeping the first occurrence based on paper_id and repo_url)
cursor.execute('''
    DELETE FROM repositories
    WHERE rowid NOT IN (
        SELECT MIN(rowid)
        FROM repositories
        GROUP BY paper_id, repo_url
    )
''')
repos_removed = cursor.rowcount

conn.commit()
conn.close()

if papers_removed > 0:
    print(f'Removed {papers_removed} duplicate papers')
if datasets_removed > 0:
    print(f'Removed {datasets_removed} duplicate datasets')
if methods_removed > 0:
    print(f'Removed {methods_removed} duplicate methods')
if repos_removed > 0:
    print(f'Removed {repos_removed} duplicate repositories')
" || log_warn "Could not check for duplicates"
    
    log_info "Database initialized successfully!"
else
    log_info "Database already exists."
    
    # Check if database has data
    log_info "Checking database contents..."
    PAPER_COUNT=$(python -c "
import sqlite3
try:
    conn = sqlite3.connect('paperswithcode.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM papers')
    count = cursor.fetchone()[0]
    print(count)
    conn.close()
except:
    print(0)
" 2>/dev/null)
    
    DATASET_COUNT=$(python -c "
import sqlite3
try:
    conn = sqlite3.connect('paperswithcode.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM datasets')
    count = cursor.fetchone()[0]
    print(count)
    conn.close()
except:
    print(0)
" 2>/dev/null)
    
    if [ "$PAPER_COUNT" -eq "0" ] || [ "$DATASET_COUNT" -eq "0" ]; then
        log_warn "Database exists but is empty. Loading data..."
        python init_database.py
        
        # After loading, remove duplicates
        log_info "Removing duplicate entries..."
        python -c "
import sqlite3
conn = sqlite3.connect('paperswithcode.db')
cursor = conn.cursor()

# Remove duplicate papers (keeping the first occurrence)
cursor.execute('''
    DELETE FROM papers
    WHERE rowid NOT IN (
        SELECT MIN(rowid)
        FROM papers
        GROUP BY id
    )
''')
papers_removed = cursor.rowcount

# Remove duplicate datasets (keeping the first occurrence)
cursor.execute('''
    DELETE FROM datasets
    WHERE rowid NOT IN (
        SELECT MIN(rowid)
        FROM datasets
        GROUP BY id
    )
''')
datasets_removed = cursor.rowcount

# Remove duplicate methods (keeping the first occurrence)
cursor.execute('''
    DELETE FROM methods
    WHERE rowid NOT IN (
        SELECT MIN(rowid)
        FROM methods
        GROUP BY id
    )
''')
methods_removed = cursor.rowcount

# Remove duplicate repositories (keeping the first occurrence based on paper_id and repo_url)
cursor.execute('''
    DELETE FROM repositories
    WHERE rowid NOT IN (
        SELECT MIN(rowid)
        FROM repositories
        GROUP BY paper_id, repo_url
    )
''')
repos_removed = cursor.rowcount

conn.commit()
conn.close()

if papers_removed > 0:
    print(f'Removed {papers_removed} duplicate papers')
if datasets_removed > 0:
    print(f'Removed {datasets_removed} duplicate datasets')
if methods_removed > 0:
    print(f'Removed {methods_removed} duplicate methods')
if repos_removed > 0:
    print(f'Removed {repos_removed} duplicate repositories')
" || log_warn "Could not check for duplicates"
        
        log_info "Data loading complete!"
    else
        log_info "Database already contains data:"
        log_info "  Papers: $PAPER_COUNT"
        log_info "  Datasets: $DATASET_COUNT"
        log_info "Skipping data load - database is already populated."
    fi
fi

# Display database statistics
log_info "Database Statistics:"
python -c "
import sqlite3
conn = sqlite3.connect('paperswithcode.db')
cursor = conn.cursor()

# Get counts
cursor.execute('SELECT COUNT(*) FROM papers')
papers = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM datasets')
datasets = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM methods')
methods = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM repositories')
repos = cursor.fetchone()[0]

print(f'  • Papers: {papers:,}')
print(f'  • Datasets: {datasets:,}')
print(f'  • Methods: {methods:,}')
print(f'  • Repositories: {repos:,}')

conn.close()
" 2>/dev/null || log_warn "Could not retrieve database statistics"

# Setup AI models for Agent Search
log_info "Setting up AI models for Agent Search..."
if [ -f "download_models.py" ]; then
    # Check if models are already set up
    if [ ! -d "checkpoints" ]; then
        log_info "Downloading and configuring models..."
        python download_models.py || {
            log_warn "Model setup encountered issues, but continuing with basic search capabilities."
        }
    else
        log_info "Model directories already exist."
        # Verify config is up to date
        if [ -f "agent-search/config.json" ]; then
            # Check if fallback mode is enabled in config
            if ! grep -q "fallback_enabled" "agent-search/config.json"; then
                log_info "Updating model configuration..."
                python download_models.py || {
                    log_warn "Model configuration update failed, but continuing."
                }
            fi
        fi
    fi
else
    log_warn "download_models.py not found. AI Agent Search will use basic mode only."
fi

# Display model status
if [ -d "checkpoints/pasa-7b-crawler" ] && [ -d "checkpoints/pasa-7b-selector" ]; then
    log_info "Model directories found:"
    if [ -f "checkpoints/pasa-7b-crawler/pytorch_model.bin" ] || [ -f "checkpoints/pasa-7b-crawler/model.safetensors" ]; then
        log_info "  ✓ PASA-7B Crawler model found"
    else
        log_warn "  ✗ PASA-7B Crawler model not found (using mock configuration)"
    fi
    if [ -f "checkpoints/pasa-7b-selector/pytorch_model.bin" ] || [ -f "checkpoints/pasa-7b-selector/model.safetensors" ]; then
        log_info "  ✓ PASA-7B Selector model found"
    else
        log_warn "  ✗ PASA-7B Selector model not found (using mock configuration)"
    fi
fi

# Check if another instance is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    log_warn "Port 8000 is already in use. Stopping existing process..."
    kill $(lsof -Pi :8000 -sTCP:LISTEN -t) 2>/dev/null || true
    sleep 2
fi

# Start the API server
log_info "Starting API server on http://localhost:8000"
log_info "Press Ctrl+C to stop the server"
echo
echo "=== API Server is starting ==="
echo "API Documentation: http://localhost:8000/docs"
echo "Available Features:"
echo "  • Basic SQL/JSON search: ✓ Enabled"
echo "  • Standard filtering: ✓ Enabled"
echo "  • Full-text search: ✓ Enabled"

# Check for AI capabilities
if python -c "import sentence_transformers" 2>/dev/null; then
    echo "  • Semantic search: ✓ Enabled"
else
    echo "  • Semantic search: ✗ Disabled (install sentence-transformers)"
fi

if [ -f "checkpoints/pasa-7b-crawler/config.json" ] && [ -f "checkpoints/pasa-7b-selector/config.json" ]; then
    if [ -f "checkpoints/pasa-7b-crawler/pytorch_model.bin" ] || [ -f "checkpoints/pasa-7b-crawler/model.safetensors" ]; then
        echo "  • AI-powered query expansion: ✓ Enabled"
        echo "  • Multi-layer paper expansion: ✓ Enabled"
    else
        echo "  • AI-powered search: ✗ Using fallback mode"
    fi
else
    echo "  • AI-powered search: ✗ Not configured"
fi

echo

# Run the API server
python api_server.py
