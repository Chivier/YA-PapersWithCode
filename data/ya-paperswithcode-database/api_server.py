#!/usr/bin/env python3
"""
FastAPI server to serve PapersWithCode data from SQLite database
"""

import json
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException, Query, Path as PathParam
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Configuration
DB_PATH = "paperswithcode.db"
API_VERSION = "v1"

# Create FastAPI app
app = FastAPI(
    title="PapersWithCode API",
    description="API for accessing PapersWithCode data",
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


# Pydantic models
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
    
class Repository(BaseModel):
    id: int
    paper_id: Optional[str]
    paper_arxiv_id: Optional[str]
    paper_title: Optional[str]
    paper_url_abs: Optional[str]
    paper_url_pdf: Optional[str]
    repo_url: str
    framework: Optional[str]
    mentioned_in_paper: bool
    mentioned_in_github: bool
    stars: int
    is_official: bool
    
class Method(BaseModel):
    id: str
    name: str
    full_name: Optional[str]
    description: Optional[str]
    source_title: Optional[str]
    source_url: Optional[str]
    code_snippet: Optional[str]
    intro_year: Optional[int]
    categories: List[str]
    
class Dataset(BaseModel):
    id: str
    name: str
    full_name: Optional[str]
    homepage: Optional[str]
    description: Optional[str]
    paper_title: Optional[str]
    paper_url: Optional[str]
    subtasks: List[str]
    modalities: List[str]
    languages: List[str]
    
class SearchResult(BaseModel):
    papers: List[Paper]
    total: int
    page: int
    per_page: int
    

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


# API endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "PapersWithCode API",
        "version": API_VERSION,
        "endpoints": {
            "papers": f"/api/{API_VERSION}/papers",
            "search": f"/api/{API_VERSION}/search",
            "repositories": f"/api/{API_VERSION}/repositories",
            "methods": f"/api/{API_VERSION}/methods",
            "datasets": f"/api/{API_VERSION}/datasets",
            "statistics": f"/api/{API_VERSION}/statistics"
        }
    }


@app.get(f"/api/{API_VERSION}/statistics")
async def get_statistics():
    """Get database statistics."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT stat_type, stat_value FROM statistics")
        
        stats = {}
        for row in cursor.fetchall():
            stats[row["stat_type"]] = row["stat_value"]
            
        return stats


@app.get(f"/api/{API_VERSION}/papers", response_model=SearchResult)
async def get_papers(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    year: Optional[int] = None,
    task: Optional[str] = None
):
    """Get papers with pagination."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Build query
        query = "SELECT * FROM papers WHERE 1=1"
        params = []
        
        if year:
            query += " AND year = ?"
            params.append(year)
            
        if task:
            query += " AND id IN (SELECT paper_id FROM paper_tasks WHERE task_name = ?)"
            params.append(task)
            
        # Count total
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Add pagination
        query += " ORDER BY date DESC LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])
        
        cursor.execute(query, params)
        papers = [row_to_paper(row) for row in cursor.fetchall()]
        
        return {
            "papers": papers,
            "total": total,
            "page": page,
            "per_page": per_page
        }


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


@app.get(f"/api/{API_VERSION}/papers/arxiv/{{arxiv_id}}")
async def get_paper_by_arxiv(arxiv_id: str = PathParam(...)):
    """Get paper by arXiv ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM papers WHERE arxiv_id = ?", (arxiv_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Paper not found")
            
        return row_to_paper(row)


@app.get(f"/api/{API_VERSION}/search")
async def search_papers(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200)
):
    """Full-text search in papers."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Use FTS5 for search
        search_query = """
            SELECT p.* 
            FROM papers p
            JOIN papers_fts ON p.rowid = papers_fts.rowid
            WHERE papers_fts MATCH ?
            ORDER BY rank
            LIMIT ? OFFSET ?
        """
        
        # Count query
        count_query = """
            SELECT COUNT(*) 
            FROM papers p
            JOIN papers_fts ON p.rowid = papers_fts.rowid
            WHERE papers_fts MATCH ?
        """
        
        # Execute count
        cursor.execute(count_query, (q,))
        total = cursor.fetchone()[0]
        
        # Execute search
        cursor.execute(search_query, (q, per_page, (page - 1) * per_page))
        papers = [row_to_paper(row) for row in cursor.fetchall()]
        
        return {
            "papers": papers,
            "total": total,
            "page": page,
            "per_page": per_page,
            "query": q
        }


@app.get(f"/api/{API_VERSION}/repositories")
async def get_repositories(
    paper_id: Optional[str] = None,
    framework: Optional[str] = None,
    min_stars: int = Query(0, ge=0),
    official_only: bool = False,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200)
):
    """Get code repositories."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = "SELECT * FROM repositories WHERE stars >= ?"
        params = [min_stars]
        
        if paper_id:
            query += " AND paper_id = ?"
            params.append(paper_id)
            
        if framework:
            query += " AND framework = ?"
            params.append(framework)
            
        if official_only:
            query += " AND is_official = 1"
            
        # Count total
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Add ordering and pagination
        query += " ORDER BY stars DESC LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])
        
        cursor.execute(query, params)
        
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
            
        return {
            "repositories": repos,
            "total": total,
            "page": page,
            "per_page": per_page
        }


@app.get(f"/api/{API_VERSION}/methods")
async def get_methods(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    year: Optional[int] = None
):
    """Get methods."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = "SELECT * FROM methods WHERE 1=1"
        params = []
        
        if year:
            query += " AND intro_year = ?"
            params.append(year)
            
        # Count total
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Add pagination
        query += " ORDER BY name LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])
        
        cursor.execute(query, params)
        
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
            
        return {
            "methods": methods,
            "total": total,
            "page": page,
            "per_page": per_page
        }


@app.get(f"/api/{API_VERSION}/datasets")
async def get_datasets(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    modality: Optional[str] = None,
    language: Optional[str] = None
):
    """Get datasets."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = "SELECT * FROM datasets WHERE 1=1"
        params = []
        
        if modality:
            query += " AND modalities LIKE ?"
            params.append(f'%"{modality}"%')
            
        if language:
            query += " AND languages LIKE ?"
            params.append(f'%"{language}"%')
            
        # Count total
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Add pagination
        query += " ORDER BY name LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])
        
        cursor.execute(query, params)
        
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
            
        return {
            "datasets": datasets,
            "total": total,
            "page": page,
            "per_page": per_page
        }


@app.get(f"/api/{API_VERSION}/tasks")
async def get_tasks():
    """Get all tasks."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.name, t.description, COUNT(pt.paper_id) as paper_count
            FROM tasks t
            LEFT JOIN paper_tasks pt ON t.name = pt.task_name
            GROUP BY t.name
            ORDER BY paper_count DESC
        """)
        
        tasks = []
        for row in cursor.fetchall():
            tasks.append({
                "name": row["name"],
                "description": row["description"],
                "paper_count": row["paper_count"]
            })
            
        return {"tasks": tasks}


@app.get(f"/api/{API_VERSION}/evaluations")
async def get_evaluations(
    task: Optional[str] = None,
    dataset: Optional[str] = None
):
    """Get evaluation results."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = "SELECT * FROM evaluation_results WHERE 1=1"
        params = []
        
        if task:
            query += " AND task = ?"
            params.append(task)
            
        if dataset:
            query += " AND dataset = ?"
            params.append(dataset)
            
        cursor.execute(query, params)
        
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
            
        return {"evaluations": evaluations}


def main():
    """Run the API server."""
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()