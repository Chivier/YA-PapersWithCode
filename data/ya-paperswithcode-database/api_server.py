#!/usr/bin/env python3
"""
PapersWithCode API Server
Clean and organized FastAPI server with SQLite and AI search capabilities
"""

import json
import sqlite3
import os
import gzip
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file"""
    # Try multiple possible locations for .env file
    possible_paths = [
        Path(__file__).parent.parent.parent / '.env',  # Project root
        Path(__file__).parent.parent / '.env',  # data directory
        Path(__file__).parent / '.env',  # Current directory
        Path.cwd() / '.env'  # Working directory
    ]
    
    for env_path in possible_paths:
        if env_path.exists():
            print(f"Loading .env from: {env_path}")
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        # Remove quotes if present
                        value = value.strip().strip('"').strip("'")
                        os.environ.setdefault(key, value)
            break

# Load .env file
load_env_file()

from fastapi import FastAPI, HTTPException, Query, Body, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Database configuration
DB_PATH = "paperswithcode.db"
API_PREFIX = "/api/v1"
DEFAULT_PORT = 8000
EXPORT_DIR = Path("exports")

# Ensure directories exist
EXPORT_DIR.mkdir(exist_ok=True)

# Create FastAPI app
app = FastAPI(
    title="PapersWithCode API",
    description="API with SQLite search and AI agent search capabilities",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Pydantic Models ====================

class SQLiteSearchRequest(BaseModel):
    """Request model for SQLite-based search"""
    query: str = Field(..., min_length=1, description="Search query string")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(50, ge=1, le=200, description="Results per page")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")

class AISearchRequest(BaseModel):
    """Request model for AI agent-based search"""
    query: str = Field(..., min_length=1, description="Natural language query for AI search")
    model: Optional[str] = Field("default", description="AI model to use")
    max_results: int = Field(20, ge=1, le=100, description="Maximum results to return")
    similarity_threshold: Optional[float] = Field(0.7, ge=0, le=1, description="Similarity threshold")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")

class SearchResponse(BaseModel):
    """Unified search response model"""
    results: List[Dict[str, Any]]
    total: int
    page: Optional[int] = None
    per_page: Optional[int] = None
    search_type: str
    query: str
    execution_time: float

class ImportRequest(BaseModel):
    """Request model for data import"""
    data_type: str = Field(..., description="Type: papers, repositories, methods, datasets, evaluations")
    data: List[Dict[str, Any]] = Field(..., description="Data to import")
    update_existing: bool = Field(False, description="Update existing records")

class ImportResponse(BaseModel):
    """Response model for data import"""
    imported: int
    updated: int
    failed: int
    errors: List[str]
    execution_time: float

class ExportRequest(BaseModel):
    """Request model for data export"""
    data_type: str = Field(..., description="Type: papers, repositories, methods, datasets, evaluations, all")
    format: str = Field("json", description="Export format: json or json.gz")


# ==================== Database Helpers ====================

@contextmanager
def get_db():
    """Get database connection with context manager."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def parse_json_field(value: str, default: list = None) -> list:
    """Parse JSON field from database."""
    if not value:
        return default or []
    try:
        return json.loads(value)
    except:
        return default or []

def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert database row to dictionary."""
    return dict(row)

def row_to_dataset(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert database row to dataset dictionary with parsed JSON fields."""
    dataset = dict(row)
    # Parse JSON fields
    dataset["subtasks"] = parse_json_field(dataset.get("subtasks"))
    dataset["modalities"] = parse_json_field(dataset.get("modalities"))
    dataset["languages"] = parse_json_field(dataset.get("languages"))
    return dataset

def row_to_paper(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert database row to paper dictionary with parsed JSON fields."""
    paper = dict(row)
    paper["authors"] = parse_json_field(paper.get("authors"))
    paper["tasks"] = parse_json_field(paper.get("tasks"))
    paper["methods"] = parse_json_field(paper.get("methods"))
    return paper


# ==================== Root Endpoint ====================

@app.get("/")
async def root():
    """API information and available endpoints."""
    return {
        "name": "PapersWithCode API",
        "version": "1.0.0",
        "endpoints": {
            "search": {
                "papers": f"{API_PREFIX}/papers/search",
                "papers_agent": f"{API_PREFIX}/papers/search/agent",
                "datasets": f"{API_PREFIX}/datasets/search",
                "datasets_agent": f"{API_PREFIX}/datasets/search/agent"
            },
            "data": {
                "import": f"{API_PREFIX}/import",
                "export": f"{API_PREFIX}/export"
            },
            "resources": {
                "papers": f"{API_PREFIX}/papers",
                "repositories": f"{API_PREFIX}/repositories",
                "methods": f"{API_PREFIX}/methods",
                "datasets": f"{API_PREFIX}/datasets"
            },
            "statistics": f"{API_PREFIX}/statistics",
            "documentation": "/docs"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint for monitoring."""
    try:
        # Check database connection
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM papers")
            paper_count = cursor.fetchone()[0]
        
        return {
            "status": "healthy",
            "database": "connected",
            "papers_count": paper_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# ==================== Search Endpoints ====================

@app.post(f"{API_PREFIX}/search/unified")
async def unified_search(request: Dict[str, Any]):
    """
    Unified search endpoint using the modular agent system.
    Automatically detects search type and selects appropriate agent.
    
    Request body:
    {
        "query": "search query",
        "type": "auto|papers|datasets|methods",  # optional, default: auto
        "agent": "auto|basic|advanced",  # optional, default: auto
        "options": {
            "expand": bool,  # whether to expand results
            "limit": int,  # max results
            "filters": dict  # additional filters
        }
    }
    """
    try:
        # Import the modular agent search system
        import sys
        sys.path.append(str(Path(__file__).parent))
        from agent_search.manager import SearchManager
        
        # Extract parameters
        query = request.get('query', '')
        search_type = request.get('type', 'auto')
        agent_type = request.get('agent', 'auto')
        options = request.get('options', {})
        
        # Initialize search manager
        manager = SearchManager()
        
        # Perform unified search
        result = await manager.search(
            query=query,
            search_type=search_type,
            agent_type=agent_type,
            **options
        )
        
        return result
    
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail="Unified search not available. Agent search module not installed."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unified search failed: {str(e)}")

@app.post(f"{API_PREFIX}/search/multi")
async def multi_search(request: Dict[str, Any]):
    """
    Search across multiple data types simultaneously.
    
    Request body:
    {
        "query": "search query",
        "types": ["papers", "datasets", "methods"],  # optional, default: all
        "options": {
            "limit": int,  # max results per type
            "filters": dict  # additional filters
        }
    }
    """
    try:
        # Import the modular agent search system
        import sys
        sys.path.append(str(Path(__file__).parent))
        from agent_search.manager import SearchManager
        
        # Extract parameters
        query = request.get('query', '')
        search_types = request.get('types', None)
        
        # Initialize search manager
        manager = SearchManager()
        
        # Perform multi-type search
        result = await manager.multi_search(
            query=query,
            search_types=search_types
        )
        
        return result
    
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail="Multi-search not available. Agent search module not installed."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-search failed: {str(e)}")

@app.post(f"{API_PREFIX}/papers/search", response_model=SearchResponse)
async def search_papers(request: SQLiteSearchRequest):
    """
    Search papers using SQLite full-text search.
    Searches in paper titles and abstracts.
    """
    start_time = datetime.now()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Build search query
        base_query = """
            SELECT * FROM papers 
            WHERE (title LIKE ? OR abstract LIKE ?)
        """
        search_pattern = f"%{request.query}%"
        params = [search_pattern, search_pattern]
        
        # Apply filters
        if request.filters:
            if "year" in request.filters:
                base_query += " AND year = ?"
                params.append(request.filters["year"])
            if "task" in request.filters:
                base_query += " AND tasks LIKE ?"
                params.append(f'%"{request.filters["task"]}"%')
            if "has_code" in request.filters and request.filters["has_code"]:
                base_query += " AND id IN (SELECT DISTINCT paper_id FROM repositories)"
        
        # Count total results
        count_query = f"SELECT COUNT(*) FROM ({base_query})"
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Add pagination
        base_query += " ORDER BY date DESC LIMIT ? OFFSET ?"
        params.extend([request.per_page, (request.page - 1) * request.per_page])
        
        # Execute search
        cursor.execute(base_query, params)
        papers = [row_to_paper(row) for row in cursor.fetchall()]
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return SearchResponse(
            results=papers,
            total=total,
            page=request.page,
            per_page=request.per_page,
            search_type="papers",
            query=request.query,
            execution_time=execution_time
        )

@app.post(f"{API_PREFIX}/datasets/search", response_model=SearchResponse)
async def search_datasets(request: SQLiteSearchRequest):
    """
    Search datasets using SQLite.
    Searches in dataset names and descriptions.
    """
    start_time = datetime.now()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Build search query for datasets
        base_query = """
            SELECT * FROM datasets 
            WHERE (name LIKE ? OR description LIKE ?)
        """
        search_pattern = f"%{request.query}%"
        params = [search_pattern, search_pattern]
        
        # Apply filters
        if request.filters:
            if "modality" in request.filters:
                base_query += " AND modalities LIKE ?"
                params.append(f'%"{request.filters["modality"]}"%')
            if "language" in request.filters:
                base_query += " AND languages LIKE ?"
                params.append(f'%"{request.filters["language"]}"%')
        
        # Count total results
        count_query = f"SELECT COUNT(*) FROM ({base_query})"
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Add pagination with custom sorting
        base_query += """ 
            ORDER BY 
                CASE 
                    WHEN substr(name, 1, 1) GLOB '[0-9]' THEN 1
                    WHEN substr(name, 1, 1) GLOB '[A-Za-z]' THEN 2
                    ELSE 3
                END,
                name COLLATE NOCASE ASC
            LIMIT ? OFFSET ?
        """
        params.extend([request.per_page, (request.page - 1) * request.per_page])
        
        # Execute search
        cursor.execute(base_query, params)
        datasets = [row_to_dataset(row) for row in cursor.fetchall()]
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return SearchResponse(
            results=datasets,
            total=total,
            page=request.page,
            per_page=request.per_page,
            search_type="datasets",
            query=request.query,
            execution_time=execution_time
        )

@app.post(f"{API_PREFIX}/papers/search/agent", response_model=SearchResponse)
async def ai_agent_search_papers(request: AISearchRequest):
    """
    AI agent-based semantic search for papers.
    Uses modular agent system for intelligent paper discovery and ranking.
    """
    start_time = datetime.now()
    
    try:
        # Import the modular agent search system
        import sys
        sys.path.append(str(Path(__file__).parent))
        from agent_search.manager import SearchManager
        
        # Initialize search manager
        manager = SearchManager()
        
        # Prepare search parameters
        search_params = {
            'limit': request.max_results,
            'expand': request.filters.get('expand', False) if request.filters else False,
            'filters': request.filters or {}
        }
        
        # Determine agent type based on request
        agent_type = 'advanced' if request.filters and request.filters.get('use_advanced', False) else 'basic'
        
        # Perform search using the modular system
        result = await manager.search(
            query=request.query,
            search_type='papers',
            agent_type=agent_type,
            **search_params
        )
        
        # AGENT_SEARCH - Once the advanced search is implemented, remove this fallback
        # For now, if no results from agent, fallback to simple search
        if not result.get('results'):
            with get_db() as conn:
                cursor = conn.cursor()
                
                search_pattern = f"%{request.query}%"
                cursor.execute("""
                    SELECT * FROM papers 
                    WHERE title LIKE ? OR abstract LIKE ?
                    ORDER BY date DESC
                    LIMIT ?
                """, [search_pattern, search_pattern, request.max_results])
                
                papers = [row_to_paper(row) for row in cursor.fetchall()]
                result = {
                    'results': papers,
                    'total': len(papers),
                    'query': request.query,
                    'search_type': 'fallback',
                    'execution_time': (datetime.now() - start_time).total_seconds()
                }
        
        return SearchResponse(
            results=result.get('results', []),
            total=result.get('total', 0),
            search_type="ai_agent_papers",
            query=request.query,
            execution_time=result.get('execution_time', (datetime.now() - start_time).total_seconds())
        )
    
    except ImportError as e:
        # If agent search module not available, use fallback
        with get_db() as conn:
            cursor = conn.cursor()
            
            search_pattern = f"%{request.query}%"
            cursor.execute("""
                SELECT * FROM papers 
                WHERE title LIKE ? OR abstract LIKE ?
                ORDER BY date DESC
                LIMIT ?
            """, [search_pattern, search_pattern, request.max_results])
            
            papers = [row_to_paper(row) for row in cursor.fetchall()]
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return SearchResponse(
                results=papers,
                total=len(papers),
                search_type="ai_agent_papers_fallback",
                query=request.query,
                execution_time=execution_time
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI agent search failed: {str(e)}")

@app.post(f"{API_PREFIX}/datasets/search/agent", response_model=SearchResponse)
async def ai_agent_search_datasets(request: AISearchRequest):
    """
    AI agent-based semantic search for datasets.
    Uses modular agent system for natural language dataset discovery.
    """
    start_time = datetime.now()
    
    try:
        # Import the modular agent search system
        import sys
        sys.path.append(str(Path(__file__).parent))
        from agent_search.manager import SearchManager
        
        # Initialize search manager
        manager = SearchManager()
        
        # Prepare search parameters
        search_params = {
            'limit': request.max_results,
            'expand': request.filters.get('expand', False) if request.filters else False,
            'filters': request.filters or {}
        }
        
        # Determine agent type based on request
        agent_type = 'advanced' if request.filters and request.filters.get('use_advanced', False) else 'basic'
        
        # Perform search using the modular system
        result = await manager.search(
            query=request.query,
            search_type='datasets',
            agent_type=agent_type,
            **search_params
        )
        
        # AGENT_SEARCH - Once the advanced search is implemented, remove this fallback
        # For now, if no results from agent, fallback to simple search
        if not result.get('results'):
            with get_db() as conn:
                cursor = conn.cursor()
                
                search_pattern = f"%{request.query}%"
                cursor.execute("""
                    SELECT * FROM datasets 
                    WHERE name LIKE ? OR description LIKE ?
                    ORDER BY 
                        CASE 
                            WHEN substr(name, 1, 1) GLOB '[0-9]' THEN 1
                            WHEN substr(name, 1, 1) GLOB '[A-Za-z]' THEN 2
                            ELSE 3
                        END,
                        name COLLATE NOCASE ASC
                    LIMIT ?
                """, [search_pattern, search_pattern, request.max_results])
                
                datasets = [row_to_dataset(row) for row in cursor.fetchall()]
                result = {
                    'results': datasets,
                    'total': len(datasets),
                    'query': request.query,
                    'search_type': 'fallback',
                    'execution_time': (datetime.now() - start_time).total_seconds()
                }
        
        return SearchResponse(
            results=result.get('results', []),
            total=result.get('total', 0),
            search_type="ai_agent_datasets",
            query=request.query,
            execution_time=result.get('execution_time', (datetime.now() - start_time).total_seconds())
        )
    
    except ImportError as e:
        # If agent search module not available, use fallback
        with get_db() as conn:
            cursor = conn.cursor()
            
            search_pattern = f"%{request.query}%"
            cursor.execute("""
                SELECT * FROM datasets 
                WHERE name LIKE ? OR description LIKE ?
                ORDER BY 
                    CASE 
                        WHEN substr(name, 1, 1) GLOB '[0-9]' THEN 1
                        WHEN substr(name, 1, 1) GLOB '[A-Za-z]' THEN 2
                        ELSE 3
                    END,
                    name COLLATE NOCASE ASC
                LIMIT ?
            """, [search_pattern, search_pattern, request.max_results])
            
            datasets = [row_to_dataset(row) for row in cursor.fetchall()]
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return SearchResponse(
                results=datasets,
                total=len(datasets),
                search_type="ai_agent_datasets_fallback",
                query=request.query,
                execution_time=execution_time
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dataset search failed: {str(e)}")


# ==================== Data Import/Export Endpoints ====================

@app.post(f"{API_PREFIX}/import", response_model=ImportResponse)
async def import_data(request: ImportRequest):
    """
    Import data into SQLite database.
    Supports papers, repositories, methods, datasets, and evaluations.
    """
    start_time = datetime.now()
    imported = 0
    updated = 0
    failed = 0
    errors = []
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        try:
            if request.data_type == "papers":
                for item in request.data:
                    try:
                        # Check if exists
                        cursor.execute("SELECT id FROM papers WHERE id = ?", (item["id"],))
                        exists = cursor.fetchone()
                        
                        if exists and request.update_existing:
                            cursor.execute("""
                                UPDATE papers SET
                                    arxiv_id=?, title=?, abstract=?, url_abs=?, url_pdf=?,
                                    proceeding=?, authors=?, tasks=?, date=?, methods=?, year=?, month=?
                                WHERE id = ?
                            """, (
                                item.get("arxiv_id"), item.get("title"), item.get("abstract"),
                                item.get("url_abs"), item.get("url_pdf"), item.get("proceeding"),
                                json.dumps(item.get("authors", [])), json.dumps(item.get("tasks", [])),
                                item.get("date"), json.dumps(item.get("methods", [])),
                                item.get("year"), item.get("month"), item["id"]
                            ))
                            updated += 1
                        elif not exists:
                            cursor.execute("""
                                INSERT INTO papers (
                                    id, arxiv_id, title, abstract, url_abs, url_pdf,
                                    proceeding, authors, tasks, date, methods, year, month
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                item["id"], item.get("arxiv_id"), item.get("title"),
                                item.get("abstract"), item.get("url_abs"), item.get("url_pdf"),
                                item.get("proceeding"), json.dumps(item.get("authors", [])),
                                json.dumps(item.get("tasks", [])), item.get("date"),
                                json.dumps(item.get("methods", [])), item.get("year"), item.get("month")
                            ))
                            imported += 1
                    except Exception as e:
                        failed += 1
                        errors.append(f"Paper {item.get('id')}: {str(e)}")
            
            elif request.data_type == "repositories":
                for item in request.data:
                    try:
                        cursor.execute("""
                            INSERT OR REPLACE INTO repositories (
                                paper_id, paper_arxiv_id, paper_title, paper_url_abs,
                                paper_url_pdf, repo_url, framework, mentioned_in_paper,
                                mentioned_in_github, stars, is_official
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            item.get("paper_id"), item.get("paper_arxiv_id"),
                            item.get("paper_title"), item.get("paper_url_abs"),
                            item.get("paper_url_pdf"), item.get("repo_url"),
                            item.get("framework"), item.get("mentioned_in_paper", 0),
                            item.get("mentioned_in_github", 0), item.get("stars", 0),
                            item.get("is_official", 0)
                        ))
                        imported += 1
                    except Exception as e:
                        failed += 1
                        errors.append(f"Repository: {str(e)}")
            
            # Similar implementations for methods, datasets, evaluations...
            else:
                raise ValueError(f"Unsupported data type: {request.data_type}")
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
    
    execution_time = (datetime.now() - start_time).total_seconds()
    
    return ImportResponse(
        imported=imported,
        updated=updated,
        failed=failed,
        errors=errors[:10],  # Limit to first 10 errors
        execution_time=execution_time
    )

@app.post(f"{API_PREFIX}/export")
async def export_data(request: ExportRequest):
    """
    Export data from SQLite database to JSON file.
    File will be saved as {data_type}_{timestamp}.json
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with get_db() as conn:
        cursor = conn.cursor()
        data = {}
        
        try:
            if request.data_type in ["papers", "all"]:
                cursor.execute("SELECT * FROM papers")
                data["papers"] = [row_to_paper(row) for row in cursor.fetchall()]
            
            if request.data_type in ["repositories", "all"]:
                cursor.execute("SELECT * FROM repositories")
                data["repositories"] = [row_to_dict(row) for row in cursor.fetchall()]
            
            if request.data_type in ["methods", "all"]:
                cursor.execute("SELECT * FROM methods")
                data["methods"] = [row_to_dict(row) for row in cursor.fetchall()]
            
            if request.data_type in ["datasets", "all"]:
                cursor.execute("SELECT * FROM datasets")
                data["datasets"] = [row_to_dict(row) for row in cursor.fetchall()]
            
            if request.data_type in ["evaluations", "all"]:
                cursor.execute("SELECT * FROM evaluation_results")
                data["evaluations"] = [row_to_dict(row) for row in cursor.fetchall()]
            
            # Add metadata
            data["_metadata"] = {
                "exported_at": timestamp,
                "data_type": request.data_type,
                "total_records": sum(len(v) for v in data.values() if isinstance(v, list))
            }
            
            # Save to file
            filename = f"{request.data_type}_{timestamp}.json"
            filepath = EXPORT_DIR / filename
            
            if request.format == "json.gz":
                filename += ".gz"
                filepath = EXPORT_DIR / filename
                with gzip.open(filepath, "wt", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            return {
                "message": "Export successful",
                "filename": filename,
                "path": str(filepath.absolute()),
                "records": data["_metadata"]["total_records"],
                "format": request.format
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


# ==================== Resource Endpoints ====================

@app.get(f"{API_PREFIX}/papers")
async def get_papers(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    year: Optional[int] = None,
    task: Optional[str] = None
):
    """Get papers with pagination and optional filters."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = "SELECT * FROM papers WHERE 1=1"
        params = []
        
        if year:
            query += " AND year = ?"
            params.append(year)
        
        if task:
            query += " AND tasks LIKE ?"
            params.append(f'%"{task}"%')
        
        # Count total
        count_query = f"SELECT COUNT(*) FROM ({query})"
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Add pagination
        query += " ORDER BY date DESC LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])
        
        cursor.execute(query, params)
        papers = [row_to_paper(row) for row in cursor.fetchall()]
        
        return {
            "results": papers,
            "total": total,
            "page": page,
            "per_page": per_page
        }

@app.get(f"{API_PREFIX}/papers/count")
async def get_papers_count():
    """Get total count of papers."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM papers")
        count = cursor.fetchone()[0]
        
        return {"count": count, "table": "papers"}

@app.get(f"{API_PREFIX}/papers/{{paper_id}}")
async def get_paper(paper_id: str):
    """Get specific paper by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM papers WHERE id = ?", (paper_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        return row_to_paper(row)

@app.get(f"{API_PREFIX}/repositories")
async def get_repositories(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    paper_id: Optional[str] = None
):
    """Get repositories with pagination."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = "SELECT * FROM repositories WHERE 1=1"
        params = []
        
        if paper_id:
            query += " AND paper_id = ?"
            params.append(paper_id)
        
        query += " ORDER BY stars DESC LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])
        
        cursor.execute(query, params)
        repos = [row_to_dict(row) for row in cursor.fetchall()]
        
        return {
            "results": repos,
            "page": page,
            "per_page": per_page
        }

@app.get(f"{API_PREFIX}/methods")
async def get_methods(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200)
):
    """Get methods with pagination."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM methods")
        total = cursor.fetchone()[0]
        
        query = """SELECT * FROM methods 
        ORDER BY 
            CASE 
                WHEN substr(name, 1, 1) GLOB '[0-9]' THEN 1  -- Numbers first
                WHEN substr(name, 1, 1) GLOB '[A-Za-z]' THEN 2  -- Letters second
                ELSE 3  -- Special characters last
            END,
            name COLLATE NOCASE ASC 
        LIMIT ? OFFSET ?"""
        params = [per_page, (page - 1) * per_page]
        
        cursor.execute(query, params)
        methods = [row_to_dict(row) for row in cursor.fetchall()]
        
        return {
            "results": methods,
            "total": total,
            "page": page,
            "per_page": per_page
        }

@app.get(f"{API_PREFIX}/methods/count")
async def get_methods_count():
    """Get total count of methods."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM methods")
        count = cursor.fetchone()[0]
        
        return {"count": count, "table": "methods"}

@app.get(f"{API_PREFIX}/datasets")
async def get_datasets(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    modalities: Optional[str] = Query(None, description="Comma-separated modalities filter"),
    languages: Optional[str] = Query(None, description="Comma-separated languages filter")
):
    """Get datasets with pagination and filtering."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Build filter conditions
        where_conditions = []
        params = []
        
        # Filter by modalities (JSON array contains check)
        # Multiple modalities: AND logic (dataset must have ALL selected modalities)
        if modalities:
            modality_list = [m.strip() for m in modalities.split(',')]
            for modality in modality_list:
                # Each modality must exist in the dataset's modalities array
                where_conditions.append(
                    "EXISTS (SELECT 1 FROM json_each(datasets.modalities) WHERE json_each.value = ?)"
                )
                params.append(modality)
        
        # Filter by languages (JSON array contains check)
        # Multiple languages: AND logic (dataset must have ALL selected languages)
        if languages:
            language_list = [l.strip() for l in languages.split(',')]
            for language in language_list:
                # Each language must exist in the dataset's languages array
                where_conditions.append(
                    "EXISTS (SELECT 1 FROM json_each(datasets.languages) WHERE json_each.value = ?)"
                )
                params.append(language)
        
        # Build WHERE clause - different filter types are combined with AND
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Get filtered count
        count_query = f"SELECT COUNT(*) FROM datasets WHERE {where_clause}"
        cursor.execute(count_query, params.copy())  # Use a copy for count query
        total = cursor.fetchone()[0]
        
        # Get filtered results with pagination
        query = f"""SELECT * FROM datasets 
        WHERE {where_clause} 
        ORDER BY 
            CASE 
                WHEN substr(name, 1, 1) GLOB '[0-9]' THEN 1  -- Numbers first
                WHEN substr(name, 1, 1) GLOB '[A-Za-z]' THEN 2  -- Letters second
                ELSE 3  -- Special characters last
            END,
            name COLLATE NOCASE ASC 
        LIMIT ? OFFSET ?"""
        # Create new params list for pagination query
        page_params = params.copy()
        page_params.extend([per_page, (page - 1) * per_page])
        
        cursor.execute(query, page_params)
        datasets = [row_to_dataset(row) for row in cursor.fetchall()]
        
        return {
            "results": datasets,
            "total": total,
            "page": page,
            "per_page": per_page,
            "filters": {
                "modalities": modalities,
                "languages": languages
            }
        }

@app.get(f"{API_PREFIX}/datasets/count")
async def get_datasets_count():
    """Get total count of datasets."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM datasets")
        count = cursor.fetchone()[0]
        
        return {"count": count, "table": "datasets"}

@app.get(f"{API_PREFIX}/datasets/{{dataset_id}}")
async def get_dataset(dataset_id: str):
    """Get specific dataset by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        return row_to_dataset(row)


# ==================== Statistics Endpoint ====================

@app.get(f"{API_PREFIX}/statistics")
async def get_statistics():
    """Get database statistics."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        stats = {}
        
        # Papers statistics
        cursor.execute("SELECT COUNT(*) FROM papers")
        stats["total_papers"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT arxiv_id) FROM papers WHERE arxiv_id IS NOT NULL")
        stats["papers_with_arxiv"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM papers WHERE abstract IS NOT NULL AND abstract != ''")
        stats["papers_with_abstract"] = cursor.fetchone()[0]
        
        # Repository statistics
        cursor.execute("SELECT COUNT(*) FROM repositories")
        stats["total_repositories"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT paper_id) FROM repositories")
        stats["papers_with_code"] = cursor.fetchone()[0]
        
        # Other statistics
        cursor.execute("SELECT COUNT(*) FROM methods")
        stats["total_methods"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM datasets")
        stats["total_datasets"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks")
        stats["total_tasks"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM evaluation_results")
        stats["total_evaluations"] = cursor.fetchone()[0]
        
        # Year distribution
        cursor.execute("""
            SELECT year, COUNT(*) as count 
            FROM papers 
            WHERE year IS NOT NULL 
            GROUP BY year 
            ORDER BY year DESC 
            LIMIT 10
        """)
        stats["papers_by_year"] = [
            {"year": row[0], "count": row[1]} for row in cursor.fetchall()
        ]
        
        return stats

@app.get(f"{API_PREFIX}/counts")
async def get_table_counts():
    """Get count of records in each table."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        counts = {}
        
        # Get counts for all main tables
        tables = ['papers', 'datasets', 'methods', 'repositories', 'tasks', 'evaluation_results']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cursor.fetchone()[0]
        
        return counts


# ==================== Main Entry Point ====================

def main():
    """Run the API server."""
    import sys
    
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        print("Please run the database initialization script first.")
        sys.exit(1)
    
    # Support both PORT and BACKEND_PORT for flexibility
    port = int(os.getenv("BACKEND_PORT", os.getenv("PORT", DEFAULT_PORT)))
    host = os.getenv("BACKEND_HOST", os.getenv("HOST", "0.0.0.0"))
    
    print(f"Starting PapersWithCode API Server")
    print(f"Database: {DB_PATH}")
    print(f"Server: http://{host}:{port}")
    print(f"API Docs: http://{host}:{port}/docs")
    print(f"API Base: http://{host}:{port}{API_PREFIX}")
    print("-" * 50)
    
    uvicorn.run("api_server:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    main()