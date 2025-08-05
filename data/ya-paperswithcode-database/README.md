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
# Initialize schema and load data
python load_data.py --init-db

# Or load specific files
python load_data.py --data-dir . --db-path paperswithcode.db
```

### 3. Start API Server

Choose one of the following API servers:

#### Basic API Server (Read-only, port 8000):
```bash
python api_server.py
```

#### CRUD API Server (Full CRUD operations, port 8080):
```bash
python crud_api_server.py
```

The CRUD API will be available at `http://localhost:8080`

## API Endpoints

### Basic API (Read-only, Port 8000)

#### Papers
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

### CRUD API (Full CRUD, Port 8080)

#### Papers
- `POST /api/v1/papers` - Create a new paper
- `GET /api/v1/papers` - List papers with filtering
- `GET /api/v1/papers/{paper_id}` - Get specific paper
- `PUT /api/v1/papers/{paper_id}` - Update paper
- `DELETE /api/v1/papers/{paper_id}` - Delete paper

#### Repositories
- `POST /api/v1/repositories` - Create a new repository
- `GET /api/v1/repositories` - List repositories
- `GET /api/v1/repositories/{repo_id}` - Get specific repository
- `PUT /api/v1/repositories/{repo_id}` - Update repository
- `DELETE /api/v1/repositories/{repo_id}` - Delete repository

#### Methods
- `POST /api/v1/methods` - Create a new method
- `GET /api/v1/methods` - List methods
- `GET /api/v1/methods/{method_id}` - Get specific method
- `PUT /api/v1/methods/{method_id}` - Update method
- `DELETE /api/v1/methods/{method_id}` - Delete method

#### Datasets
- `POST /api/v1/datasets` - Create a new dataset
- `GET /api/v1/datasets` - List datasets
- `GET /api/v1/datasets/{dataset_id}` - Get specific dataset
- `PUT /api/v1/datasets/{dataset_id}` - Update dataset
- `DELETE /api/v1/datasets/{dataset_id}` - Delete dataset

#### Evaluations
- `POST /api/v1/evaluations` - Create a new evaluation
- `GET /api/v1/evaluations/{eval_id}` - Get specific evaluation
- `PUT /api/v1/evaluations/{eval_id}` - Update evaluation
- `DELETE /api/v1/evaluations/{eval_id}` - Delete evaluation

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

### Basic API (Read-only)

#### Search for papers
```bash
curl "http://localhost:8000/api/v1/search?q=transformer"
```

#### Get papers by year
```bash
curl "http://localhost:8000/api/v1/papers?year=2023&per_page=10"
```

#### Find repositories with many stars
```bash
curl "http://localhost:8000/api/v1/repositories?min_stars=100"
```

### CRUD API Examples

#### Create a new paper
```bash
curl -X POST "http://localhost:8080/api/v1/papers" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "new-paper-001",
    "title": "A New Approach to Machine Learning",
    "abstract": "We present a novel method...",
    "authors": ["John Doe", "Jane Smith"],
    "tasks": ["Image Classification"],
    "year": 2024
  }'
```

#### Update a paper
```bash
curl -X PUT "http://localhost:8080/api/v1/papers/new-paper-001" \
  -H "Content-Type: application/json" \
  -d '{
    "abstract": "Updated abstract text...",
    "tasks": ["Image Classification", "Object Detection"]
  }'
```

#### Delete a paper
```bash
curl -X DELETE "http://localhost:8080/api/v1/papers/new-paper-001"
```

#### Create a repository
```bash
curl -X POST "http://localhost:8080/api/v1/repositories" \
  -H "Content-Type: application/json" \
  -d '{
    "paper_id": "paper-123",
    "repo_url": "https://github.com/user/repo",
    "framework": "pytorch",
    "stars": 150,
    "is_official": true
  }'
```

#### Interactive API Documentation
Visit `http://localhost:8080/docs` for interactive Swagger UI documentation.
