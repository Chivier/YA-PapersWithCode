#!/usr/bin/env python3
"""
Enhanced FastAPI server with unified search APIs and data import/export functionality
"""

import json
import sqlite3
import os
import gzip
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager
import traceback

from fastapi import FastAPI, HTTPException, Query, Path as PathParam, Body, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Import semantic search components
try:
    from semantic_search import SemanticSearchEngine
    SEMANTIC_SEARCH_AVAILABLE = True
except ImportError:
    SEMANTIC_SEARCH_AVAILABLE = False
    print("Warning: Semantic search not available. Install required packages.")

# Import AI agent components
try:
    from paper_agent import PaperAgent
    from models import Agent
    AI_AGENT_AVAILABLE = True
except ImportError:
    AI_AGENT_AVAILABLE = False
    print("Warning: AI agent search not available. Install required packages.")

# Configuration
DB_PATH = "paperswithcode.db"
API_VERSION = "v1"
DEFAULT_PORT = 8000
EXPORT_DIR = Path("exports")
IMPORT_DIR = Path("imports")

# Ensure directories exist
EXPORT_DIR.mkdir(exist_ok=True)
IMPORT_DIR.mkdir(exist_ok=True)

# Create FastAPI app
app = FastAPI(
    title="PapersWithCode Enhanced API",
    description="Comprehensive API with SQLite matching and AI semantic search",
    version="3.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize semantic search engine if available
semantic_engine = None
if SEMANTIC_SEARCH_AVAILABLE and os.path.exists("papers-with-abstracts.json"):
    try:
        semantic_engine = SemanticSearchEngine("papers-with-abstracts.json")
        print("Semantic search engine initialized successfully")
    except Exception as e:
        print(f"Failed to initialize semantic search: {e}")


# Pydantic models
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query string")
    search_type: str = Field("sqlite", description="Search type: 'sqlite' for keyword matching or 'semantic' for AI-based search")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(50, ge=1, le=200, description="Results per page")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total: int
    page: int
    per_page: int
    search_type: str
    query: str
    execution_time: float

class AIAgentSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User query for AI agent search")
    end_date: Optional[str] = Field(None, description="End date for paper filtering (YYYYMMDD)")
    expand_layers: int = Field(2, ge=1, le=5, description="Number of expansion layers")
    search_queries: int = Field(5, ge=1, le=20, description="Number of search queries to generate")
    search_papers: int = Field(10, ge=1, le=50, description="Papers per query")
    expand_papers: int = Field(20, ge=1, le=100, description="Papers to expand per layer")

class ImportRequest(BaseModel):
    data_type: str = Field(..., description="Type of data: papers, repositories, methods, datasets, evaluations")
    data: List[Dict[str, Any]] = Field(..., description="Data to import")
    update_existing: bool = Field(False, description="Update existing records if found")

class ImportResponse(BaseModel):
    imported: int
    updated: int
    failed: int
    errors: List[str]
    execution_time: float

class ExportRequest(BaseModel):
    data_type: str = Field(..., description="Type of data: papers, repositories, methods, datasets, evaluations, all")
    format: str = Field("json", description="Export format: json or json.gz")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters to apply")

class Paper(BaseModel):
    id: str
    arxiv_id: Optional[str]
    title: str
    abstract: Optional[str]
    url_abs: Optional[str]
    url_pdf: Optional[str]
    proceeding: Optional[str]
    authors: List[str]
    tasks: List[str]
    date: Optional[str]
    methods: List[str]
    year: Optional[int]
    month: Optional[int]


# Database connection manager
@contextmanager
def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# Helper functions
def parse_json_field(value: str, default: list = None) -> list:
    """Parse JSON field from database."""
    if not value:
        return default or []
    try:
        return json.loads(value)
    except:
        return default or []


def row_to_paper(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert database row to paper dict."""
    return {
        "id": row["id"],
        "arxiv_id": row["arxiv_id"],
        "title": row["title"],
        "abstract": row["abstract"],
        "url_abs": row["url_abs"],
        "url_pdf": row["url_pdf"],
        "proceeding": row["proceeding"],
        "authors": parse_json_field(row["authors"]),
        "tasks": parse_json_field(row["tasks"]),
        "date": row["date"],
        "methods": parse_json_field(row["methods"]),
        "year": row["year"],
        "month": row["month"]
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "PapersWithCode Enhanced API",
        "version": API_VERSION,
        "features": {
            "sqlite_search": True,
            "semantic_search": SEMANTIC_SEARCH_AVAILABLE and semantic_engine is not None,
            "ai_agent_search": AI_AGENT_AVAILABLE,
            "data_import": True,
            "data_export": True
        },
        "endpoints": {
            "search": f"/api/{API_VERSION}/search",
            "ai_agent_search": f"/api/{API_VERSION}/search/agent",
            "import": f"/api/{API_VERSION}/import",
            "export": f"/api/{API_VERSION}/export",
            "papers": f"/api/{API_VERSION}/papers",
            "repositories": f"/api/{API_VERSION}/repositories",
            "methods": f"/api/{API_VERSION}/methods",
            "datasets": f"/api/{API_VERSION}/datasets",
            "statistics": f"/api/{API_VERSION}/statistics",
            "docs": "/docs"
        }
    }


# Unified Search API
@app.post(f"/api/{API_VERSION}/search", response_model=SearchResponse)
async def unified_search(request: SearchRequest):
    """
    Unified search endpoint supporting both SQLite matching and semantic search.
    
    Search types:
    - 'sqlite': Traditional keyword matching using SQLite FTS5
    - 'semantic': AI-based semantic similarity search using embeddings
    """
    start_time = datetime.now()
    
    if request.search_type == "sqlite":
        # SQLite FTS5 search
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Build search query with FTS5
            search_query = """
                SELECT p.* 
                FROM papers p
                JOIN papers_fts ON p.rowid = papers_fts.rowid
                WHERE papers_fts MATCH ?
            """
            params = [request.query]
            
            # Apply additional filters if provided
            if request.filters:
                if "year" in request.filters:
                    search_query += " AND p.year = ?"
                    params.append(request.filters["year"])
                if "task" in request.filters:
                    search_query += " AND p.id IN (SELECT paper_id FROM paper_tasks WHERE task_name = ?)"
                    params.append(request.filters["task"])
                if "has_code" in request.filters and request.filters["has_code"]:
                    search_query += " AND p.id IN (SELECT DISTINCT paper_id FROM repositories)"
            
            # Count total results
            count_query = f"SELECT COUNT(*) FROM ({search_query})"
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]
            
            # Add pagination and ordering
            search_query += " ORDER BY rank LIMIT ? OFFSET ?"
            params.extend([request.per_page, (request.page - 1) * request.per_page])
            
            # Execute search
            cursor.execute(search_query, params)
            papers = [row_to_paper(row) for row in cursor.fetchall()]
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return SearchResponse(
                results=papers,
                total=total,
                page=request.page,
                per_page=request.per_page,
                search_type="sqlite",
                query=request.query,
                execution_time=execution_time
            )
    
    elif request.search_type == "semantic":
        # Semantic similarity search
        if not semantic_engine:
            raise HTTPException(
                status_code=503,
                detail="Semantic search is not available. Please ensure the semantic search engine is properly initialized."
            )
        
        try:
            # Perform semantic search
            arxiv_ids = semantic_engine.search_by_query(
                request.query,
                num_results=request.per_page * request.page,
                end_date=request.filters.get("end_date") if request.filters else None
            )
            
            # Fetch paper details from database
            papers = []
            with get_db() as conn:
                cursor = conn.cursor()
                
                # Get papers for the current page
                start_idx = (request.page - 1) * request.per_page
                end_idx = start_idx + request.per_page
                page_arxiv_ids = arxiv_ids[start_idx:end_idx]
                
                for arxiv_id in page_arxiv_ids:
                    cursor.execute("SELECT * FROM papers WHERE arxiv_id = ?", (arxiv_id,))
                    row = cursor.fetchone()
                    if row:
                        papers.append(row_to_paper(row))
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return SearchResponse(
                results=papers,
                total=len(arxiv_ids),
                page=request.page,
                per_page=request.per_page,
                search_type="semantic",
                query=request.query,
                execution_time=execution_time
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Semantic search failed: {str(e)}")
    
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid search type: {request.search_type}. Must be 'sqlite' or 'semantic'."
        )


# AI Agent Search API
@app.post(f"/api/{API_VERSION}/search/agent")
async def ai_agent_search(request: AIAgentSearchRequest, background_tasks: BackgroundTasks):
    """
    Advanced AI agent-based search that expands and explores related papers.
    This endpoint uses AI agents to intelligently search and expand the paper graph.
    """
    if not AI_AGENT_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="AI agent search is not available. Please ensure required packages are installed."
        )
    
    try:
        # Initialize AI agents (this would need proper model initialization)
        # For now, returning a placeholder response
        return {
            "message": "AI agent search initiated",
            "query": request.query,
            "status": "processing",
            "note": "Full AI agent implementation requires model configuration"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI agent search failed: {str(e)}")


# Data Import API
@app.post(f"/api/{API_VERSION}/import", response_model=ImportResponse)
async def import_data(request: ImportRequest):
    """
    Import data into the SQLite database.
    Supports importing papers, repositories, methods, datasets, and evaluations.
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
                        # Check if paper exists
                        cursor.execute("SELECT id FROM papers WHERE id = ?", (item["id"],))
                        exists = cursor.fetchone()
                        
                        if exists and request.update_existing:
                            # Update existing paper
                            cursor.execute("""
                                UPDATE papers SET
                                    arxiv_id = ?, title = ?, abstract = ?,
                                    url_abs = ?, url_pdf = ?, proceeding = ?,
                                    authors = ?, tasks = ?, date = ?,
                                    methods = ?, year = ?, month = ?
                                WHERE id = ?
                            """, (
                                item.get("arxiv_id"),
                                item.get("title"),
                                item.get("abstract"),
                                item.get("url_abs"),
                                item.get("url_pdf"),
                                item.get("proceeding"),
                                json.dumps(item.get("authors", [])),
                                json.dumps(item.get("tasks", [])),
                                item.get("date"),
                                json.dumps(item.get("methods", [])),
                                item.get("year"),
                                item.get("month"),
                                item["id"]
                            ))
                            updated += 1
                        elif not exists:
                            # Insert new paper
                            cursor.execute("""
                                INSERT INTO papers (
                                    id, arxiv_id, title, abstract, url_abs, url_pdf,
                                    proceeding, authors, tasks, date, methods, year, month
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                item["id"],
                                item.get("arxiv_id"),
                                item.get("title"),
                                item.get("abstract"),
                                item.get("url_abs"),
                                item.get("url_pdf"),
                                item.get("proceeding"),
                                json.dumps(item.get("authors", [])),
                                json.dumps(item.get("tasks", [])),
                                item.get("date"),
                                json.dumps(item.get("methods", [])),
                                item.get("year"),
                                item.get("month")
                            ))
                            
                            # Add tasks
                            for task in item.get("tasks", []):
                                cursor.execute("INSERT OR IGNORE INTO tasks (name) VALUES (?)", (task,))
                                cursor.execute(
                                    "INSERT OR IGNORE INTO paper_tasks (paper_id, task_name) VALUES (?, ?)",
                                    (item["id"], task)
                                )
                            
                            imported += 1
                        
                    except Exception as e:
                        failed += 1
                        errors.append(f"Paper {item.get('id', 'unknown')}: {str(e)}")
            
            elif request.data_type == "repositories":
                for item in request.data:
                    try:
                        cursor.execute("""
                            INSERT INTO repositories (
                                paper_id, paper_arxiv_id, paper_title, paper_url_abs,
                                paper_url_pdf, repo_url, framework, mentioned_in_paper,
                                mentioned_in_github, stars, is_official
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            item.get("paper_id"),
                            item.get("paper_arxiv_id"),
                            item.get("paper_title"),
                            item.get("paper_url_abs"),
                            item.get("paper_url_pdf"),
                            item.get("repo_url"),
                            item.get("framework"),
                            1 if item.get("mentioned_in_paper") else 0,
                            1 if item.get("mentioned_in_github") else 0,
                            item.get("stars", 0),
                            1 if item.get("is_official") else 0
                        ))
                        imported += 1
                    except Exception as e:
                        failed += 1
                        errors.append(f"Repository: {str(e)}")
            
            elif request.data_type == "methods":
                for item in request.data:
                    try:
                        cursor.execute("SELECT id FROM methods WHERE id = ?", (item["id"],))
                        exists = cursor.fetchone()
                        
                        if exists and request.update_existing:
                            cursor.execute("""
                                UPDATE methods SET
                                    name = ?, full_name = ?, description = ?,
                                    source_title = ?, source_url = ?, code_snippet = ?,
                                    intro_year = ?, categories = ?
                                WHERE id = ?
                            """, (
                                item.get("name"),
                                item.get("full_name"),
                                item.get("description"),
                                item.get("source_title"),
                                item.get("source_url"),
                                item.get("code_snippet"),
                                item.get("intro_year"),
                                json.dumps(item.get("categories", [])),
                                item["id"]
                            ))
                            updated += 1
                        elif not exists:
                            cursor.execute("""
                                INSERT INTO methods (
                                    id, name, full_name, description, source_title,
                                    source_url, code_snippet, intro_year, categories
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                item["id"],
                                item.get("name"),
                                item.get("full_name"),
                                item.get("description"),
                                item.get("source_title"),
                                item.get("source_url"),
                                item.get("code_snippet"),
                                item.get("intro_year"),
                                json.dumps(item.get("categories", []))
                            ))
                            imported += 1
                    except Exception as e:
                        failed += 1
                        errors.append(f"Method {item.get('id', 'unknown')}: {str(e)}")
            
            elif request.data_type == "datasets":
                for item in request.data:
                    try:
                        cursor.execute("SELECT id FROM datasets WHERE id = ?", (item["id"],))
                        exists = cursor.fetchone()
                        
                        if exists and request.update_existing:
                            cursor.execute("""
                                UPDATE datasets SET
                                    name = ?, full_name = ?, homepage = ?,
                                    description = ?, paper_title = ?, paper_url = ?,
                                    subtasks = ?, modalities = ?, languages = ?
                                WHERE id = ?
                            """, (
                                item.get("name"),
                                item.get("full_name"),
                                item.get("homepage"),
                                item.get("description"),
                                item.get("paper_title"),
                                item.get("paper_url"),
                                json.dumps(item.get("subtasks", [])),
                                json.dumps(item.get("modalities", [])),
                                json.dumps(item.get("languages", [])),
                                item["id"]
                            ))
                            updated += 1
                        elif not exists:
                            cursor.execute("""
                                INSERT INTO datasets (
                                    id, name, full_name, homepage, description,
                                    paper_title, paper_url, subtasks, modalities, languages
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                item["id"],
                                item.get("name"),
                                item.get("full_name"),
                                item.get("homepage"),
                                item.get("description"),
                                item.get("paper_title"),
                                item.get("paper_url"),
                                json.dumps(item.get("subtasks", [])),
                                json.dumps(item.get("modalities", [])),
                                json.dumps(item.get("languages", []))
                            ))
                            imported += 1
                    except Exception as e:
                        failed += 1
                        errors.append(f"Dataset {item.get('id', 'unknown')}: {str(e)}")
            
            elif request.data_type == "evaluations":
                for item in request.data:
                    try:
                        cursor.execute("""
                            INSERT INTO evaluation_results (
                                task, dataset, sota_rows, metrics, subdataset
                            ) VALUES (?, ?, ?, ?, ?)
                        """, (
                            item.get("task"),
                            item.get("dataset"),
                            json.dumps(item.get("sota_rows", [])),
                            json.dumps(item.get("metrics", [])),
                            item.get("subdataset")
                        ))
                        imported += 1
                    except Exception as e:
                        failed += 1
                        errors.append(f"Evaluation: {str(e)}")
            
            else:
                raise HTTPException(status_code=400, detail=f"Invalid data type: {request.data_type}")
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
    
    execution_time = (datetime.now() - start_time).total_seconds()
    
    return ImportResponse(
        imported=imported,
        updated=updated,
        failed=failed,
        errors=errors[:10],  # Limit errors to first 10
        execution_time=execution_time
    )


# Data Export API
@app.post(f"/api/{API_VERSION}/export")
async def export_data(request: ExportRequest):
    """
    Export data from the SQLite database.
    Supports exporting to JSON or compressed JSON.gz format.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with get_db() as conn:
        cursor = conn.cursor()
        data = {}
        
        try:
            if request.data_type in ["papers", "all"]:
                cursor.execute("SELECT * FROM papers")
                papers = []
                for row in cursor.fetchall():
                    papers.append(row_to_paper(row))
                data["papers"] = papers
            
            if request.data_type in ["repositories", "all"]:
                cursor.execute("SELECT * FROM repositories")
                repos = []
                for row in cursor.fetchall():
                    repos.append({
                        "id": row["id"],
                        "paper_id": row["paper_id"],
                        "paper_arxiv_id": row["paper_arxiv_id"],
                        "paper_title": row["paper_title"],
                        "paper_url_abs": row["paper_url_abs"],
                        "paper_url_pdf": row["paper_url_pdf"],
                        "repo_url": row["repo_url"],
                        "framework": row["framework"],
                        "mentioned_in_paper": bool(row["mentioned_in_paper"]),
                        "mentioned_in_github": bool(row["mentioned_in_github"]),
                        "stars": row["stars"],
                        "is_official": bool(row["is_official"])
                    })
                data["repositories"] = repos
            
            if request.data_type in ["methods", "all"]:
                cursor.execute("SELECT * FROM methods")
                methods = []
                for row in cursor.fetchall():
                    methods.append({
                        "id": row["id"],
                        "name": row["name"],
                        "full_name": row["full_name"],
                        "description": row["description"],
                        "source_title": row["source_title"],
                        "source_url": row["source_url"],
                        "code_snippet": row["code_snippet"],
                        "intro_year": row["intro_year"],
                        "categories": parse_json_field(row["categories"])
                    })
                data["methods"] = methods
            
            if request.data_type in ["datasets", "all"]:
                cursor.execute("SELECT * FROM datasets")
                datasets = []
                for row in cursor.fetchall():
                    datasets.append({
                        "id": row["id"],
                        "name": row["name"],
                        "full_name": row["full_name"],
                        "homepage": row["homepage"],
                        "description": row["description"],
                        "paper_title": row["paper_title"],
                        "paper_url": row["paper_url"],
                        "subtasks": parse_json_field(row["subtasks"]),
                        "modalities": parse_json_field(row["modalities"]),
                        "languages": parse_json_field(row["languages"])
                    })
                data["datasets"] = datasets
            
            if request.data_type in ["evaluations", "all"]:
                cursor.execute("SELECT * FROM evaluation_results")
                evaluations = []
                for row in cursor.fetchall():
                    evaluations.append({
                        "id": row["id"],
                        "task": row["task"],
                        "dataset": row["dataset"],
                        "subdataset": row["subdataset"],
                        "sota_rows": parse_json_field(row["sota_rows"]),
                        "metrics": parse_json_field(row["metrics"])
                    })
                data["evaluations"] = evaluations
            
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
                "path": str(filepath),
                "records_exported": data["_metadata"]["total_records"],
                "format": request.format
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


# Import from file endpoint
@app.post(f"/api/{API_VERSION}/import/file")
async def import_from_file(
    file: UploadFile = File(...),
    data_type: str = Query(..., description="Type of data in the file"),
    update_existing: bool = Query(False, description="Update existing records")
):
    """Import data from an uploaded JSON file."""
    try:
        # Read and parse the file
        content = await file.read()
        
        # Handle gzipped files
        if file.filename.endswith(".gz"):
            import gzip
            content = gzip.decompress(content)
        
        data = json.loads(content)
        
        # Extract the actual data based on type
        if isinstance(data, dict) and data_type in data:
            items = data[data_type]
        elif isinstance(data, list):
            items = data
        else:
            raise ValueError("Invalid file format")
        
        # Use the import_data function
        request = ImportRequest(
            data_type=data_type,
            data=items,
            update_existing=update_existing
        )
        
        return await import_data(request)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File import failed: {str(e)}")


# Statistics endpoint
@app.get(f"/api/{API_VERSION}/statistics")
async def get_statistics():
    """Get comprehensive database statistics."""
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
        
        cursor.execute("SELECT COUNT(DISTINCT paper_id) FROM repositories WHERE paper_id IS NOT NULL")
        stats["papers_with_code"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(stars) FROM repositories")
        stats["total_stars"] = cursor.fetchone()[0] or 0
        
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
        
        # Top tasks
        cursor.execute("""
            SELECT task_name, COUNT(*) as count 
            FROM paper_tasks 
            GROUP BY task_name 
            ORDER BY count DESC 
            LIMIT 10
        """)
        stats["top_tasks"] = [
            {"task": row[0], "count": row[1]} for row in cursor.fetchall()
        ]
        
        return stats


# Keep existing endpoints for backward compatibility
@app.get(f"/api/{API_VERSION}/search")
async def search_papers_get(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200)
):
    """Legacy GET search endpoint for backward compatibility."""
    request = SearchRequest(
        query=q,
        search_type="sqlite",
        page=page,
        per_page=per_page
    )
    return await unified_search(request)


# Papers endpoints
@app.get(f"/api/{API_VERSION}/papers", response_model=List[Paper])
async def get_papers(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    year: Optional[int] = None,
    task: Optional[str] = None
):
    """Get papers with pagination and filters."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = "SELECT * FROM papers WHERE 1=1"
        params = []
        
        if year:
            query += " AND year = ?"
            params.append(year)
        
        if task:
            query += " AND id IN (SELECT paper_id FROM paper_tasks WHERE task_name = ?)"
            params.append(task)
        
        query += " ORDER BY date DESC LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])
        
        cursor.execute(query, params)
        papers = [row_to_paper(row) for row in cursor.fetchall()]
        
        return papers


@app.get(f"/api/{API_VERSION}/papers/{{paper_id}}")
async def get_paper(paper_id: str = PathParam(...)):
    """Get specific paper by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM papers WHERE id = ?", (paper_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        return row_to_paper(row)


def main():
    """Run the enhanced API server."""
    print(f"Starting PapersWithCode Enhanced API server on port {DEFAULT_PORT}...")
    print(f"Semantic search available: {SEMANTIC_SEARCH_AVAILABLE and semantic_engine is not None}")
    print(f"AI agent search available: {AI_AGENT_AVAILABLE}")
    uvicorn.run(app, host="0.0.0.0", port=DEFAULT_PORT)


if __name__ == "__main__":
    main()