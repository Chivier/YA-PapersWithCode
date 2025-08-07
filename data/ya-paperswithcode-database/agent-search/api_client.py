"""
API Client for accessing database and JSON data
"""

import sqlite3
import json
import gzip
from typing import List, Dict, Any, Optional
from pathlib import Path


class SearchAPIClient:
    """Client for accessing data through SQL queries or JSON files"""
    
    def __init__(self, db_path: str = "paperswithcode.db", json_dir: str = "."):
        """
        Initialize the API client
        
        Args:
            db_path: Path to SQLite database
            json_dir: Directory containing JSON files
        """
        self.db_path = db_path
        self.json_dir = Path(json_dir)
        
    def query_database(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of result dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            return results
            
        finally:
            conn.close()
    
    def get_papers(self, filters: Optional[Dict[str, Any]] = None, 
                   limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get papers from database with optional filters
        
        Args:
            filters: Filter criteria
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of paper dictionaries
        """
        base_query = "SELECT * FROM papers WHERE 1=1"
        params = []
        
        if filters:
            if 'year' in filters:
                base_query += " AND year = ?"
                params.append(filters['year'])
            if 'search' in filters:
                base_query += " AND (title LIKE ? OR abstract LIKE ?)"
                search_pattern = f"%{filters['search']}%"
                params.extend([search_pattern, search_pattern])
        
        base_query += f" ORDER BY date DESC LIMIT {limit} OFFSET {offset}"
        
        return self.query_database(base_query, tuple(params) if params else None)
    
    def get_datasets(self, filters: Optional[Dict[str, Any]] = None,
                    limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get datasets from database with optional filters
        
        Args:
            filters: Filter criteria
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of dataset dictionaries
        """
        base_query = "SELECT * FROM datasets WHERE 1=1"
        params = []
        
        if filters:
            if 'modality' in filters:
                base_query += " AND modalities LIKE ?"
                params.append(f'%"{filters["modality"]}"%')
            if 'language' in filters:
                base_query += " AND languages LIKE ?"
                params.append(f'%"{filters["language"]}"%')
            if 'search' in filters:
                base_query += " AND (name LIKE ? OR description LIKE ?)"
                search_pattern = f"%{filters['search']}%"
                params.extend([search_pattern, search_pattern])
        
        base_query += """ 
            ORDER BY 
                CASE 
                    WHEN substr(name, 1, 1) GLOB '[0-9]' THEN 1
                    WHEN substr(name, 1, 1) GLOB '[A-Za-z]' THEN 2
                    ELSE 3
                END,
                name COLLATE NOCASE ASC
        """
        base_query += f" LIMIT {limit} OFFSET {offset}"
        
        return self.query_database(base_query, tuple(params) if params else None)
    
    def get_methods(self, filters: Optional[Dict[str, Any]] = None,
                   limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get methods from database with optional filters
        
        Args:
            filters: Filter criteria
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of method dictionaries
        """
        base_query = "SELECT * FROM methods WHERE 1=1"
        params = []
        
        if filters and 'search' in filters:
            base_query += " AND (name LIKE ? OR description LIKE ?)"
            search_pattern = f"%{filters['search']}%"
            params.extend([search_pattern, search_pattern])
        
        base_query += """ 
            ORDER BY 
                CASE 
                    WHEN substr(name, 1, 1) GLOB '[0-9]' THEN 1
                    WHEN substr(name, 1, 1) GLOB '[A-Za-z]' THEN 2
                    ELSE 3
                END,
                name COLLATE NOCASE ASC
        """
        base_query += f" LIMIT {limit} OFFSET {offset}"
        
        return self.query_database(base_query, tuple(params) if params else None)
    
    def load_json_file(self, filename: str) -> List[Dict[str, Any]]:
        """
        Load data from a JSON file (handles gzipped files)
        
        Args:
            filename: Name of the JSON file
            
        Returns:
            List of data dictionaries
        """
        file_path = self.json_dir / filename
        
        # Try gzipped version first
        gz_path = self.json_dir / f"{filename}.gz"
        if gz_path.exists():
            with gzip.open(gz_path, 'rt') as f:
                data = json.load(f)
                return data if isinstance(data, list) else [data]
        
        # Try regular JSON file
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data if isinstance(data, list) else [data]
        
        raise FileNotFoundError(f"Cannot find {filename} or {filename}.gz")
    
    def get_papers_json(self) -> List[Dict[str, Any]]:
        """Load all papers from JSON file"""
        return self.load_json_file("papers-with-abstracts.json")
    
    def get_datasets_json(self) -> List[Dict[str, Any]]:
        """Load all datasets from JSON file"""
        return self.load_json_file("datasets.json")
    
    def get_methods_json(self) -> List[Dict[str, Any]]:
        """Load all methods from JSON file"""
        return self.load_json_file("methods.json")