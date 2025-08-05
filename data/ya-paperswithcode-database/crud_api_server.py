#!/usr/bin/env python3
"""
Enhanced FastAPI server with full CRUD operations for PapersWithCode data
"""

import json
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException, Query, Path as PathParam, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Configuration
DB_PATH = "paperswithcode.db"
API_VERSION = "v1"
DEFAULT_PORT = 8080  # Changed from 8000

# Create FastAPI app
app = FastAPI(
    title="PapersWithCode CRUD API",
    description="Full CRUD API for managing PapersWithCode data",
    version="2.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for CRUD operations
class PaperCreate(BaseModel):
    id: str
    arxiv_id: Optional[str] = None
    title: str
    abstract: Optional[str] = None
    url_abs: Optional[str] = None
    url_pdf: Optional[str] = None
    proceeding: Optional[str] = None
    authors: List[str] = []
    tasks: List[str] = []
    date: Optional[str] = None
    methods: List[str] = []
    year: Optional[int] = None
    month: Optional[int] = None

class PaperUpdate(BaseModel):
    arxiv_id: Optional[str] = None
    title: Optional[str] = None
    abstract: Optional[str] = None
    url_abs: Optional[str] = None
    url_pdf: Optional[str] = None
    proceeding: Optional[str] = None
    authors: Optional[List[str]] = None
    tasks: Optional[List[str]] = None
    date: Optional[str] = None
    methods: Optional[List[str]] = None
    year: Optional[int] = None
    month: Optional[int] = None

class RepositoryCreate(BaseModel):
    paper_id: Optional[str] = None
    paper_arxiv_id: Optional[str] = None
    paper_title: Optional[str] = None
    paper_url_abs: Optional[str] = None
    paper_url_pdf: Optional[str] = None
    repo_url: str
    framework: Optional[str] = None
    mentioned_in_paper: bool = False
    mentioned_in_github: bool = False
    stars: int = 0
    is_official: bool = False

class RepositoryUpdate(BaseModel):
    paper_id: Optional[str] = None
    paper_arxiv_id: Optional[str] = None
    paper_title: Optional[str] = None
    paper_url_abs: Optional[str] = None
    paper_url_pdf: Optional[str] = None
    repo_url: Optional[str] = None
    framework: Optional[str] = None
    mentioned_in_paper: Optional[bool] = None
    mentioned_in_github: Optional[bool] = None
    stars: Optional[int] = None
    is_official: Optional[bool] = None

class MethodCreate(BaseModel):
    id: str
    name: str
    full_name: Optional[str] = None
    description: Optional[str] = None
    source_title: Optional[str] = None
    source_url: Optional[str] = None
    code_snippet: Optional[str] = None
    intro_year: Optional[int] = None
    categories: List[str] = []

class MethodUpdate(BaseModel):
    name: Optional[str] = None
    full_name: Optional[str] = None
    description: Optional[str] = None
    source_title: Optional[str] = None
    source_url: Optional[str] = None
    code_snippet: Optional[str] = None
    intro_year: Optional[int] = None
    categories: Optional[List[str]] = None

class DatasetCreate(BaseModel):
    id: str
    name: str
    full_name: Optional[str] = None
    homepage: Optional[str] = None
    description: Optional[str] = None
    paper_title: Optional[str] = None
    paper_url: Optional[str] = None
    subtasks: List[str] = []
    modalities: List[str] = []
    languages: List[str] = []

class DatasetUpdate(BaseModel):
    name: Optional[str] = None
    full_name: Optional[str] = None
    homepage: Optional[str] = None
    description: Optional[str] = None
    paper_title: Optional[str] = None
    paper_url: Optional[str] = None
    subtasks: Optional[List[str]] = None
    modalities: Optional[List[str]] = None
    languages: Optional[List[str]] = None

class EvaluationCreate(BaseModel):
    task: str
    dataset: str
    sota_rows: List[Dict[str, Any]] = []
    metrics: List[Dict[str, Any]] = []
    subdataset: Optional[str] = None

class EvaluationUpdate(BaseModel):
    task: Optional[str] = None
    dataset: Optional[str] = None
    sota_rows: Optional[List[Dict[str, Any]]] = None
    metrics: Optional[List[Dict[str, Any]]] = None
    subdataset: Optional[str] = None


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


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "PapersWithCode CRUD API",
        "version": API_VERSION,
        "port": DEFAULT_PORT,
        "endpoints": {
            "papers": f"/api/{API_VERSION}/papers",
            "repositories": f"/api/{API_VERSION}/repositories",
            "methods": f"/api/{API_VERSION}/methods",
            "datasets": f"/api/{API_VERSION}/datasets",
            "evaluations": f"/api/{API_VERSION}/evaluations",
            "docs": "/docs"
        }
    }


# CRUD operations for Papers
@app.post(f"/api/{API_VERSION}/papers", status_code=201)
async def create_paper(paper: PaperCreate):
    """Create a new paper."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO papers 
                (id, arxiv_id, title, abstract, url_abs, url_pdf, proceeding,
                 authors, tasks, date, methods, year, month)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                paper.id,
                paper.arxiv_id,
                paper.title,
                paper.abstract,
                paper.url_abs,
                paper.url_pdf,
                paper.proceeding,
                json.dumps(paper.authors),
                json.dumps(paper.tasks),
                paper.date,
                json.dumps(paper.methods),
                paper.year,
                paper.month
            ))
            
            # Add tasks
            for task in paper.tasks:
                cursor.execute("INSERT OR IGNORE INTO tasks (name) VALUES (?)", (task,))
                cursor.execute(
                    "INSERT OR IGNORE INTO paper_tasks (paper_id, task_name) VALUES (?, ?)",
                    (paper.id, task)
                )
            
            conn.commit()
            return {"message": "Paper created successfully", "id": paper.id}
            
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Paper with this ID already exists")


@app.get(f"/api/{API_VERSION}/papers/{{paper_id}}")
async def get_paper(paper_id: str = PathParam(...)):
    """Get a specific paper by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM papers WHERE id = ?", (paper_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Paper not found")
        
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


@app.put(f"/api/{API_VERSION}/papers/{{paper_id}}")
async def update_paper(paper_id: str, paper: PaperUpdate):
    """Update an existing paper."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if paper exists
        cursor.execute("SELECT * FROM papers WHERE id = ?", (paper_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Paper not found")
        
        # Build update query
        update_fields = []
        params = []
        
        for field, value in paper.dict(exclude_unset=True).items():
            if value is not None:
                if isinstance(value, list):
                    update_fields.append(f"{field} = ?")
                    params.append(json.dumps(value))
                else:
                    update_fields.append(f"{field} = ?")
                    params.append(value)
        
        if not update_fields:
            return {"message": "No fields to update"}
        
        params.append(paper_id)
        query = f"UPDATE papers SET {', '.join(update_fields)} WHERE id = ?"
        
        cursor.execute(query, params)
        
        # Update tasks if provided
        if paper.tasks is not None:
            # Remove old tasks
            cursor.execute("DELETE FROM paper_tasks WHERE paper_id = ?", (paper_id,))
            
            # Add new tasks
            for task in paper.tasks:
                cursor.execute("INSERT OR IGNORE INTO tasks (name) VALUES (?)", (task,))
                cursor.execute(
                    "INSERT INTO paper_tasks (paper_id, task_name) VALUES (?, ?)",
                    (paper_id, task)
                )
        
        conn.commit()
        return {"message": "Paper updated successfully"}


@app.delete(f"/api/{API_VERSION}/papers/{{paper_id}}")
async def delete_paper(paper_id: str):
    """Delete a paper."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if paper exists
        cursor.execute("SELECT * FROM papers WHERE id = ?", (paper_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Paper not found")
        
        # Delete paper (cascade will handle related records)
        cursor.execute("DELETE FROM papers WHERE id = ?", (paper_id,))
        cursor.execute("DELETE FROM paper_tasks WHERE paper_id = ?", (paper_id,))
        
        conn.commit()
        return {"message": "Paper deleted successfully"}


# CRUD operations for Repositories
@app.post(f"/api/{API_VERSION}/repositories", status_code=201)
async def create_repository(repo: RepositoryCreate):
    """Create a new repository."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO repositories 
            (paper_id, paper_arxiv_id, paper_title, paper_url_abs, paper_url_pdf,
             repo_url, framework, mentioned_in_paper, mentioned_in_github, stars, is_official)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            repo.paper_id,
            repo.paper_arxiv_id,
            repo.paper_title,
            repo.paper_url_abs,
            repo.paper_url_pdf,
            repo.repo_url,
            repo.framework,
            1 if repo.mentioned_in_paper else 0,
            1 if repo.mentioned_in_github else 0,
            repo.stars,
            1 if repo.is_official else 0
        ))
        
        repo_id = cursor.lastrowid
        conn.commit()
        return {"message": "Repository created successfully", "id": repo_id}


@app.get(f"/api/{API_VERSION}/repositories/{{repo_id}}")
async def get_repository(repo_id: int):
    """Get a specific repository by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM repositories WHERE id = ?", (repo_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        return {
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
        }


@app.put(f"/api/{API_VERSION}/repositories/{{repo_id}}")
async def update_repository(repo_id: int, repo: RepositoryUpdate):
    """Update an existing repository."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if repository exists
        cursor.execute("SELECT * FROM repositories WHERE id = ?", (repo_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Repository not found")
        
        # Build update query
        update_fields = []
        params = []
        
        for field, value in repo.dict(exclude_unset=True).items():
            if value is not None:
                if field in ['mentioned_in_paper', 'mentioned_in_github', 'is_official']:
                    update_fields.append(f"{field} = ?")
                    params.append(1 if value else 0)
                else:
                    update_fields.append(f"{field} = ?")
                    params.append(value)
        
        if not update_fields:
            return {"message": "No fields to update"}
        
        params.append(repo_id)
        query = f"UPDATE repositories SET {', '.join(update_fields)} WHERE id = ?"
        
        cursor.execute(query, params)
        conn.commit()
        return {"message": "Repository updated successfully"}


@app.delete(f"/api/{API_VERSION}/repositories/{{repo_id}}")
async def delete_repository(repo_id: int):
    """Delete a repository."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM repositories WHERE id = ?", (repo_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Repository not found")
        
        cursor.execute("DELETE FROM repositories WHERE id = ?", (repo_id,))
        conn.commit()
        return {"message": "Repository deleted successfully"}


# CRUD operations for Methods
@app.post(f"/api/{API_VERSION}/methods", status_code=201)
async def create_method(method: MethodCreate):
    """Create a new method."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO methods 
                (id, name, full_name, description, source_title, source_url,
                 code_snippet, intro_year, categories)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                method.id,
                method.name,
                method.full_name,
                method.description,
                method.source_title,
                method.source_url,
                method.code_snippet,
                method.intro_year,
                json.dumps(method.categories)
            ))
            
            conn.commit()
            return {"message": "Method created successfully", "id": method.id}
            
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Method with this ID already exists")


@app.get(f"/api/{API_VERSION}/methods/{{method_id}}")
async def get_method(method_id: str):
    """Get a specific method by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM methods WHERE id = ?", (method_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Method not found")
        
        return {
            "id": row["id"],
            "name": row["name"],
            "full_name": row["full_name"],
            "description": row["description"],
            "source_title": row["source_title"],
            "source_url": row["source_url"],
            "code_snippet": row["code_snippet"],
            "intro_year": row["intro_year"],
            "categories": parse_json_field(row["categories"])
        }


@app.put(f"/api/{API_VERSION}/methods/{{method_id}}")
async def update_method(method_id: str, method: MethodUpdate):
    """Update an existing method."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM methods WHERE id = ?", (method_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Method not found")
        
        update_fields = []
        params = []
        
        for field, value in method.dict(exclude_unset=True).items():
            if value is not None:
                if isinstance(value, list):
                    update_fields.append(f"{field} = ?")
                    params.append(json.dumps(value))
                else:
                    update_fields.append(f"{field} = ?")
                    params.append(value)
        
        if not update_fields:
            return {"message": "No fields to update"}
        
        params.append(method_id)
        query = f"UPDATE methods SET {', '.join(update_fields)} WHERE id = ?"
        
        cursor.execute(query, params)
        conn.commit()
        return {"message": "Method updated successfully"}


@app.delete(f"/api/{API_VERSION}/methods/{{method_id}}")
async def delete_method(method_id: str):
    """Delete a method."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM methods WHERE id = ?", (method_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Method not found")
        
        cursor.execute("DELETE FROM methods WHERE id = ?", (method_id,))
        conn.commit()
        return {"message": "Method deleted successfully"}


# CRUD operations for Datasets
@app.post(f"/api/{API_VERSION}/datasets", status_code=201)
async def create_dataset(dataset: DatasetCreate):
    """Create a new dataset."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO datasets 
                (id, name, full_name, homepage, description, paper_title,
                 paper_url, subtasks, modalities, languages)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dataset.id,
                dataset.name,
                dataset.full_name,
                dataset.homepage,
                dataset.description,
                dataset.paper_title,
                dataset.paper_url,
                json.dumps(dataset.subtasks),
                json.dumps(dataset.modalities),
                json.dumps(dataset.languages)
            ))
            
            conn.commit()
            return {"message": "Dataset created successfully", "id": dataset.id}
            
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Dataset with this ID already exists")


@app.get(f"/api/{API_VERSION}/datasets/{{dataset_id}}")
async def get_dataset(dataset_id: str):
    """Get a specific dataset by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        return {
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
        }


@app.put(f"/api/{API_VERSION}/datasets/{{dataset_id}}")
async def update_dataset(dataset_id: str, dataset: DatasetUpdate):
    """Update an existing dataset."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        update_fields = []
        params = []
        
        for field, value in dataset.dict(exclude_unset=True).items():
            if value is not None:
                if isinstance(value, list):
                    update_fields.append(f"{field} = ?")
                    params.append(json.dumps(value))
                else:
                    update_fields.append(f"{field} = ?")
                    params.append(value)
        
        if not update_fields:
            return {"message": "No fields to update"}
        
        params.append(dataset_id)
        query = f"UPDATE datasets SET {', '.join(update_fields)} WHERE id = ?"
        
        cursor.execute(query, params)
        conn.commit()
        return {"message": "Dataset updated successfully"}


@app.delete(f"/api/{API_VERSION}/datasets/{{dataset_id}}")
async def delete_dataset(dataset_id: str):
    """Delete a dataset."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        cursor.execute("DELETE FROM datasets WHERE id = ?", (dataset_id,))
        conn.commit()
        return {"message": "Dataset deleted successfully"}


# CRUD operations for Evaluations
@app.post(f"/api/{API_VERSION}/evaluations", status_code=201)
async def create_evaluation(evaluation: EvaluationCreate):
    """Create a new evaluation result."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO evaluation_results 
            (task, dataset, sota_rows, metrics, subdataset)
            VALUES (?, ?, ?, ?, ?)
        """, (
            evaluation.task,
            evaluation.dataset,
            json.dumps(evaluation.sota_rows),
            json.dumps(evaluation.metrics),
            evaluation.subdataset
        ))
        
        eval_id = cursor.lastrowid
        conn.commit()
        return {"message": "Evaluation created successfully", "id": eval_id}


@app.get(f"/api/{API_VERSION}/evaluations/{{eval_id}}")
async def get_evaluation(eval_id: int):
    """Get a specific evaluation by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM evaluation_results WHERE id = ?", (eval_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        
        return {
            "id": row["id"],
            "task": row["task"],
            "dataset": row["dataset"],
            "subdataset": row["subdataset"],
            "sota_rows": parse_json_field(row["sota_rows"]),
            "metrics": parse_json_field(row["metrics"])
        }


@app.put(f"/api/{API_VERSION}/evaluations/{{eval_id}}")
async def update_evaluation(eval_id: int, evaluation: EvaluationUpdate):
    """Update an existing evaluation."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM evaluation_results WHERE id = ?", (eval_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Evaluation not found")
        
        update_fields = []
        params = []
        
        for field, value in evaluation.dict(exclude_unset=True).items():
            if value is not None:
                if isinstance(value, list):
                    update_fields.append(f"{field} = ?")
                    params.append(json.dumps(value))
                else:
                    update_fields.append(f"{field} = ?")
                    params.append(value)
        
        if not update_fields:
            return {"message": "No fields to update"}
        
        params.append(eval_id)
        query = f"UPDATE evaluation_results SET {', '.join(update_fields)} WHERE id = ?"
        
        cursor.execute(query, params)
        conn.commit()
        return {"message": "Evaluation updated successfully"}


@app.delete(f"/api/{API_VERSION}/evaluations/{{eval_id}}")
async def delete_evaluation(eval_id: int):
    """Delete an evaluation."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM evaluation_results WHERE id = ?", (eval_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Evaluation not found")
        
        cursor.execute("DELETE FROM evaluation_results WHERE id = ?", (eval_id,))
        conn.commit()
        return {"message": "Evaluation deleted successfully"}


# List endpoints with filtering
@app.get(f"/api/{API_VERSION}/papers")
async def list_papers(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    year: Optional[int] = None,
    task: Optional[str] = None,
    search: Optional[str] = None
):
    """List papers with filtering and pagination."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        if search:
            # Use FTS for search
            query = """
                SELECT p.* 
                FROM papers p
                JOIN papers_fts ON p.rowid = papers_fts.rowid
                WHERE papers_fts MATCH ?
            """
            params = [search]
        else:
            query = "SELECT * FROM papers WHERE 1=1"
            params = []
        
        if year:
            query += " AND year = ?"
            params.append(year)
            
        if task:
            query += " AND id IN (SELECT paper_id FROM paper_tasks WHERE task_name = ?)"
            params.append(task)
        
        # Count total
        count_query = f"SELECT COUNT(*) FROM ({query})"
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Add pagination
        query += " ORDER BY date DESC LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])
        
        cursor.execute(query, params)
        
        papers = []
        for row in cursor.fetchall():
            papers.append({
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
            })
        
        return {
            "papers": papers,
            "total": total,
            "page": page,
            "per_page": per_page
        }


@app.get(f"/api/{API_VERSION}/repositories")
async def list_repositories(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    paper_id: Optional[str] = None,
    framework: Optional[str] = None,
    min_stars: int = Query(0, ge=0)
):
    """List repositories with filtering and pagination."""
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
        
        # Count total
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Add pagination
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


def main():
    """Run the CRUD API server."""
    print(f"Starting PapersWithCode CRUD API server on port {DEFAULT_PORT}...")
    uvicorn.run(app, host="0.0.0.0", port=DEFAULT_PORT)


if __name__ == "__main__":
    main()