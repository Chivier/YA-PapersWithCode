# YA-PapersWithCode Setup Guide

## Quick Start

This project consists of a Python FastAPI backend and a React frontend. Use the provided scripts to set up and run both components.

### Prerequisites

- **macOS** or **Linux** operating system
- **Python 3.8+** (backend will install `uv` if not present)
- **Node.js 16+** and **npm** (for frontend)

### Installation & Running

#### 1. Start the Backend

Open a terminal and run:
```bash
./start_backend.sh
```

This script will:
- ✅ Check and install `uv` (Python package manager) if needed
- ✅ Create a Python virtual environment
- ✅ Install all Python dependencies
- ✅ Download PapersWithCode data files (first run only)
- ✅ Initialize the SQLite database
- ✅ Start the API server on http://localhost:8000

#### 2. Start the Frontend

Open another terminal and run:
```bash
./start_frontend.sh
```

This script will:
- ✅ Check Node.js and npm installation
- ✅ Install npm dependencies
- ✅ Check if backend is running
- ✅ Start the React dev server on http://localhost:5173

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Stopping the Services

Press `Ctrl+C` in each terminal to stop the respective service.

### Troubleshooting

#### Backend Issues

1. **Port 8000 already in use**: The script will automatically try to stop the existing process.
2. **uv installation fails**: Install manually from https://github.com/astral-sh/uv
3. **Database errors**: Delete `paperswithcode.db` and `.initialized` files, then restart

#### Frontend Issues

1. **Node.js not installed**: 
   - macOS: `brew install node`
   - Linux: `sudo apt install nodejs npm`
2. **Port 5173 already in use**: The script will automatically try to stop the existing process.
3. **Backend not running**: Start the backend first using `./start_backend.sh`

### Manual Setup (Alternative)

If the scripts don't work for your environment, you can set up manually:

#### Backend
```bash
cd data/ya-paperswithcode-database
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install fastapi uvicorn pydantic python-multipart aiofiles
python init_database.py
python api_server.py
```

#### Frontend
```bash
cd frontend/ya-paperswithcode
npm install
npm run dev
```

### Development Notes

- The backend uses SQLite for data storage
- Data files are downloaded from the official PapersWithCode repository
- The frontend is built with React, TypeScript, and Tailwind CSS
- Both services support hot-reloading for development