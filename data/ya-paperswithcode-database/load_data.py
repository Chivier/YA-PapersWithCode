#!/usr/bin/env python3
"""
Load PapersWithCode JSON data into SQLite database
"""

import json
import sqlite3
import argparse
import gzip
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PapersWithCodeLoader:
    """Load PapersWithCode data into SQLite database."""
    
    def __init__(self, db_path: str = "paperswithcode.db"):
        """Initialize the loader with database connection."""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        
    def connect(self):
        """Connect to the database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        # Enable foreign keys
        self.cursor.execute("PRAGMA foreign_keys = ON")
        logger.info(f"Connected to database: {self.db_path}")
        
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
            
    def init_database(self, schema_file: str = "schema.sql"):
        """Initialize database with schema."""
        logger.info("Initializing database schema...")
        with open(schema_file, 'r') as f:
            schema = f.read()
        self.cursor.executescript(schema)
        self.conn.commit()
        logger.info("Database schema initialized")
        
    def load_json_file(self, filepath: Path) -> List[Dict[str, Any]]:
        """Load JSON file, handling gzip compression."""
        logger.info(f"Loading {filepath}...")
        
        if filepath.suffix == '.gz':
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                data = json.load(f)
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
        logger.info(f"Loaded {len(data)} records from {filepath}")
        return data
        
    def load_papers(self, filepath: Path):
        """Load papers data into database."""
        papers = self.load_json_file(filepath)
        
        logger.info("Loading papers into database...")
        inserted = 0
        skipped = 0
        
        for paper in tqdm(papers, desc="Loading papers"):
            try:
                # Extract year and month from date if available
                year = None
                month = None
                if paper.get('date'):
                    try:
                        date_obj = datetime.strptime(paper['date'], '%Y-%m-%d')
                        year = date_obj.year
                        month = date_obj.month
                    except:
                        pass
                
                # Convert lists to JSON strings
                authors_json = json.dumps(paper.get('authors', []))
                tasks_json = json.dumps(paper.get('tasks', []))
                methods_json = json.dumps(paper.get('methods', []))
                
                self.cursor.execute("""
                    INSERT OR IGNORE INTO papers 
                    (id, arxiv_id, title, abstract, url_abs, url_pdf, proceeding, 
                     authors, tasks, date, methods, year, month)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    paper.get('paper_id'),
                    paper.get('arxiv_id'),
                    paper.get('title'),
                    paper.get('abstract'),
                    paper.get('url_abs'),
                    paper.get('url_pdf'),
                    paper.get('proceeding'),
                    authors_json,
                    tasks_json,
                    paper.get('date'),
                    methods_json,
                    year,
                    month
                ))
                
                if self.cursor.rowcount > 0:
                    inserted += 1
                    
                    # Extract and store tasks
                    for task in paper.get('tasks', []):
                        self.cursor.execute("""
                            INSERT OR IGNORE INTO tasks (name) VALUES (?)
                        """, (task,))
                        
                        self.cursor.execute("""
                            INSERT OR IGNORE INTO paper_tasks (paper_id, task_name)
                            VALUES (?, ?)
                        """, (paper.get('paper_id'), task))
                else:
                    skipped += 1
                    
            except Exception as e:
                logger.error(f"Error loading paper {paper.get('paper_id')}: {e}")
                continue
                
        self.conn.commit()
        logger.info(f"Papers loaded: {inserted} inserted, {skipped} skipped")
        
    def load_repositories(self, filepath: Path):
        """Load code repositories data into database."""
        repos_data = self.load_json_file(filepath)
        
        logger.info("Loading repositories into database...")
        inserted = 0
        
        for repo in tqdm(repos_data, desc="Loading repositories"):
            try:
                self.cursor.execute("""
                    INSERT INTO repositories 
                    (paper_id, paper_arxiv_id, paper_title, paper_url_abs, 
                     paper_url_pdf, repo_url, framework, mentioned_in_paper, 
                     mentioned_in_github, stars, is_official)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    repo.get('paper_id'),
                    repo.get('paper_arxiv_id'),
                    repo.get('paper_title'),
                    repo.get('paper_url_abs'),
                    repo.get('paper_url_pdf'),
                    repo.get('repo_url'),
                    repo.get('framework'),
                    1 if repo.get('mentioned_in_paper') else 0,
                    1 if repo.get('mentioned_in_github') else 0,
                    repo.get('stars', 0),
                    1 if repo.get('is_official') else 0
                ))
                inserted += 1
            except Exception as e:
                logger.error(f"Error loading repository: {e}")
                continue
                
        self.conn.commit()
        logger.info(f"Repositories loaded: {inserted} inserted")
        
    def load_methods(self, filepath: Path):
        """Load methods data into database."""
        methods = self.load_json_file(filepath)
        
        logger.info("Loading methods into database...")
        inserted = 0
        
        for method in tqdm(methods, desc="Loading methods"):
            try:
                categories_json = json.dumps(method.get('categories', []))
                
                self.cursor.execute("""
                    INSERT OR IGNORE INTO methods 
                    (id, name, full_name, description, source_title, 
                     source_url, code_snippet, intro_year, categories)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    method.get('id'),
                    method.get('name'),
                    method.get('full_name'),
                    method.get('description'),
                    method.get('source_title'),
                    method.get('source_url'),
                    method.get('code_snippet'),
                    method.get('introduced_year'),
                    categories_json
                ))
                
                if self.cursor.rowcount > 0:
                    inserted += 1
            except Exception as e:
                logger.error(f"Error loading method {method.get('id')}: {e}")
                continue
                
        self.conn.commit()
        logger.info(f"Methods loaded: {inserted} inserted")
        
    def load_datasets(self, filepath: Path):
        """Load datasets data into database."""
        datasets = self.load_json_file(filepath)
        
        logger.info("Loading datasets into database...")
        inserted = 0
        
        for dataset in tqdm(datasets, desc="Loading datasets"):
            try:
                subtasks_json = json.dumps(dataset.get('subtasks', []))
                modalities_json = json.dumps(dataset.get('modalities', []))
                languages_json = json.dumps(dataset.get('languages', []))
                
                self.cursor.execute("""
                    INSERT OR IGNORE INTO datasets 
                    (id, name, full_name, homepage, description, 
                     paper_title, paper_url, subtasks, modalities, languages)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    dataset.get('id'),
                    dataset.get('dataset'),
                    dataset.get('dataset_full_name'),
                    dataset.get('homepage'),
                    dataset.get('description'),
                    dataset.get('paper_title'),
                    dataset.get('paper_url'),
                    subtasks_json,
                    modalities_json,
                    languages_json
                ))
                
                if self.cursor.rowcount > 0:
                    inserted += 1
            except Exception as e:
                logger.error(f"Error loading dataset {dataset.get('id')}: {e}")
                continue
                
        self.conn.commit()
        logger.info(f"Datasets loaded: {inserted} inserted")
        
    def load_evaluations(self, filepath: Path):
        """Load evaluation results data into database."""
        evaluations = self.load_json_file(filepath)
        
        logger.info("Loading evaluation results into database...")
        inserted = 0
        
        for eval_data in tqdm(evaluations, desc="Loading evaluations"):
            try:
                # Store the entire SOTA rows and metrics as JSON
                sota_rows_json = json.dumps(eval_data.get('sota_rows', []))
                metrics_json = json.dumps(eval_data.get('metrics', []))
                
                self.cursor.execute("""
                    INSERT INTO evaluation_results 
                    (task, dataset, sota_rows, metrics, subdataset)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    eval_data.get('task'),
                    eval_data.get('dataset'),
                    sota_rows_json,
                    metrics_json,
                    eval_data.get('subdataset')
                ))
                inserted += 1
            except Exception as e:
                logger.error(f"Error loading evaluation: {e}")
                continue
                
        self.conn.commit()
        logger.info(f"Evaluation results loaded: {inserted} inserted")
        
    def update_statistics(self):
        """Update statistics table with current counts."""
        logger.info("Updating statistics...")
        
        stats = [
            ('total_papers', "SELECT COUNT(*) FROM papers"),
            ('total_repositories', "SELECT COUNT(*) FROM repositories"),
            ('total_methods', "SELECT COUNT(*) FROM methods"),
            ('total_datasets', "SELECT COUNT(*) FROM datasets"),
            ('total_evaluations', "SELECT COUNT(*) FROM evaluation_results"),
            ('total_tasks', "SELECT COUNT(*) FROM tasks"),
            ('papers_with_code', "SELECT COUNT(DISTINCT paper_id) FROM repositories"),
        ]
        
        for stat_type, query in stats:
            self.cursor.execute(query)
            count = self.cursor.fetchone()[0]
            
            self.cursor.execute("""
                INSERT OR REPLACE INTO statistics (stat_type, stat_value)
                VALUES (?, ?)
            """, (stat_type, count))
            
        self.conn.commit()
        logger.info("Statistics updated")
        
    def load_all(self, data_dir: Path):
        """Load all data files from directory."""
        # Define file mappings
        file_mappings = {
            'papers-with-abstracts.json': self.load_papers,
            'links-between-papers-and-code.json': self.load_repositories,
            'methods.json': self.load_methods,
            'datasets.json': self.load_datasets,
            'evaluation-tables.json': self.load_evaluations,
        }
        
        # Try both compressed and uncompressed versions
        for filename, load_func in file_mappings.items():
            filepath = data_dir / filename
            filepath_gz = data_dir / f"{filename}.gz"
            
            if filepath_gz.exists():
                load_func(filepath_gz)
            elif filepath.exists():
                load_func(filepath)
            else:
                logger.warning(f"File not found: {filename}")
                
        # Update statistics after loading all data
        self.update_statistics()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Load PapersWithCode data into SQLite")
    parser.add_argument(
        '--data-dir',
        default='.',
        help='Directory containing the JSON data files'
    )
    parser.add_argument(
        '--db-path',
        default='paperswithcode.db',
        help='Path to SQLite database file'
    )
    parser.add_argument(
        '--schema-file',
        default='schema.sql',
        help='Path to schema SQL file'
    )
    parser.add_argument(
        '--init-db',
        action='store_true',
        help='Initialize database with schema'
    )
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    
    with PapersWithCodeLoader(args.db_path) as loader:
        if args.init_db:
            loader.init_database(args.schema_file)
            
        loader.load_all(data_dir)
        
    logger.info("Data loading complete!")


if __name__ == "__main__":
    main()