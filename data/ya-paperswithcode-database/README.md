# PapersWithCode SQLite Database

This module provides SQLite database storage and API server for PapersWithCode data.

## Features

- SQLite database with optimized schema
- Full-text search capabilities
- FastAPI server for data access
- Pagination support
- Advanced filtering options

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### 1. Download Data

First, download the data using the download script:
```bash
cd ../download_scripts
python download.py
```

### 2. Initialize Database

Create and populate the SQLite database:
```bash
# Initialize database with schema and load data
python init_database.py
```

### 3. Start API Server

Start the API server:
```bash
python api_server.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Papers
- `GET /api/v1/papers` - List papers with pagination
- `GET /api/v1/papers/{paper_id}` - Get specific paper
- `GET /api/v1/papers/arxiv/{arxiv_id}` - Get paper by arXiv ID
- `GET /api/v1/search?q={query}` - Full-text search

#### Other Resources
- `GET /api/v1/repositories` - List code repositories
- `GET /api/v1/methods` - List methods
- `GET /api/v1/datasets` - List datasets
- `GET /api/v1/tasks` - List all tasks
- `GET /api/v1/evaluations` - Get evaluation results
- `GET /api/v1/statistics` - Database statistics

## Database Schema

The database includes the following tables:
- `papers` - Research papers with abstracts
- `repositories` - Code implementations
- `methods` - ML methods and algorithms
- `datasets` - Datasets used in research
- `evaluation_results` - Benchmark results
- `tasks` - Research tasks/problems
- `paper_tasks` - Many-to-many relationship

Full-text search is enabled on papers for efficient searching.

## Examples

### Search for papers
```bash
curl "http://localhost:8000/api/v1/search?q=transformer"
```

#### Get papers by year
```bash
curl "http://localhost:8000/api/v1/papers?year=2023&per_page=10"
```

### Find repositories with many stars
```bash
curl "http://localhost:8000/api/v1/repositories?min_stars=100"
```

### Interactive API Documentation
Visit `http://localhost:8000/docs` for interactive Swagger UI documentation.
