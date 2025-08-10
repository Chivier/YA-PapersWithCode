#!/usr/bin/env python3
"""
Database initialization script with enhanced indexing and optimization
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime
import gzip

DB_PATH = "paperswithcode.db"
SCHEMA_PATH = "schema.sql"

def create_enhanced_schema(conn):
    """Create enhanced database schema with optimized indexes."""
    cursor = conn.cursor()
    
    # Read and execute base schema
    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, 'r') as f:
            schema_sql = f.read()
        cursor.executescript(schema_sql)
    
    # Additional indexes for search optimization
    print("Creating additional indexes for search optimization...")
    
    # Composite indexes for common query patterns
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_papers_year_month 
        ON papers(year, month)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_papers_date_year 
        ON papers(date, year)
    """)
    
    # Index for abstract search (partial index for non-null abstracts)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_papers_abstract_not_null 
        ON papers(id) WHERE abstract IS NOT NULL
    """)
    
    # Repository composite indexes
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_repos_paper_stars 
        ON repositories(paper_id, stars DESC)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_repos_official_stars 
        ON repositories(is_official, stars DESC)
    """)
    
    # Task frequency index
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_paper_tasks_task_paper 
        ON paper_tasks(task_name, paper_id)
    """)
    
    # Custom sort index for datasets (Numbers -> Letters -> Special chars)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_datasets_custom_sort 
        ON datasets(
            CASE 
                WHEN substr(name, 1, 1) GLOB '[0-9]' THEN 1
                WHEN substr(name, 1, 1) GLOB '[A-Za-z]' THEN 2
                ELSE 3
            END,
            name COLLATE NOCASE
        )
    """)
    
    # Custom sort index for methods (Numbers -> Letters -> Special chars)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_methods_custom_sort 
        ON methods(
            CASE 
                WHEN substr(name, 1, 1) GLOB '[0-9]' THEN 1
                WHEN substr(name, 1, 1) GLOB '[A-Za-z]' THEN 2
                ELSE 3
            END,
            name COLLATE NOCASE
        )
    """)
    
    # Create views for common queries
    print("Creating optimized views...")
    
    # View for papers with code
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS papers_with_code AS
        SELECT DISTINCT p.*, 
               (SELECT COUNT(*) FROM repositories r WHERE r.paper_id = p.id) as repo_count,
               (SELECT MAX(stars) FROM repositories r WHERE r.paper_id = p.id) as max_stars
        FROM papers p
        WHERE EXISTS (SELECT 1 FROM repositories r WHERE r.paper_id = p.id)
    """)
    
    # View for recent papers
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS recent_papers AS
        SELECT * FROM papers
        WHERE date IS NOT NULL
        ORDER BY date DESC
        LIMIT 1000
    """)
    
    # View for task statistics
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS task_statistics AS
        SELECT t.name,
               t.description,
               COUNT(DISTINCT pt.paper_id) as paper_count,
               COUNT(DISTINCT r.id) as repo_count
        FROM tasks t
        LEFT JOIN paper_tasks pt ON t.name = pt.task_name
        LEFT JOIN papers p ON pt.paper_id = p.id
        LEFT JOIN repositories r ON p.id = r.paper_id
        GROUP BY t.name
        ORDER BY paper_count DESC
    """)
    
    conn.commit()
    print("Enhanced schema with custom sort indexes created successfully!")


def load_json_data(file_path):
    """Load JSON data from file (supports .gz files)."""
    if file_path.endswith('.gz'):
        try:
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                return json.load(f)
        except gzip.BadGzipFile:
            # File might be corrupted or contain error message, check content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content.startswith('Not Found') or content.startswith('404'):
                    raise FileNotFoundError(f"File {file_path} contains download error: {content}")
                else:
                    raise ValueError(f"File {file_path} is not a valid gzip file: {content[:50]}")
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)


def import_papers(conn, papers_file):
    """Import papers into database."""
    if not os.path.exists(papers_file):
        print(f"Papers file not found: {papers_file}")
        return 0
    
    print(f"Loading papers from {papers_file}...")
    papers = load_json_data(papers_file)
    
    cursor = conn.cursor()
    imported = 0
    
    for paper in papers:
        try:
            # Extract year and month from date
            year = month = None
            if paper.get('date'):
                try:
                    date_obj = datetime.strptime(paper['date'], '%Y-%m-%d')
                    year = date_obj.year
                    month = date_obj.month
                except:
                    pass
            
            cursor.execute("""
                INSERT OR IGNORE INTO papers (
                    id, arxiv_id, title, abstract, url_abs, url_pdf,
                    proceeding, authors, tasks, date, methods, year, month
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                paper.get('paper_id', paper.get('id')),
                paper.get('arxiv_id'),
                paper.get('title'),
                paper.get('abstract'),
                paper.get('url_abs'),
                paper.get('url_pdf'),
                paper.get('proceeding'),
                json.dumps(paper.get('authors', [])),
                json.dumps(paper.get('tasks', [])),
                paper.get('date'),
                json.dumps(paper.get('methods', [])),
                year,
                month
            ))
            
            # Add tasks
            for task in paper.get('tasks', []):
                cursor.execute("INSERT OR IGNORE INTO tasks (name) VALUES (?)", (task,))
                cursor.execute(
                    "INSERT OR IGNORE INTO paper_tasks (paper_id, task_name) VALUES (?, ?)",
                    (paper.get('paper_id', paper.get('id')), task)
                )
            
            imported += 1
            
            if imported % 1000 == 0:
                print(f"  Imported {imported} papers...")
                conn.commit()
        
        except Exception as e:
            print(f"  Error importing paper {paper.get('id')}: {e}")
    
    conn.commit()
    print(f"Successfully imported {imported} papers!")
    return imported


def import_repositories(conn, repos_file):
    """Import repositories into database."""
    if not os.path.exists(repos_file):
        print(f"Repositories file not found: {repos_file}")
        return 0
    
    print(f"Loading repositories from {repos_file}...")
    repos = load_json_data(repos_file)
    
    cursor = conn.cursor()
    imported = 0
    
    for repo in repos:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO repositories (
                    paper_id, paper_arxiv_id, paper_title, paper_url_abs,
                    paper_url_pdf, repo_url, framework, mentioned_in_paper,
                    mentioned_in_github, stars, is_official
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            imported += 1
            
            if imported % 1000 == 0:
                print(f"  Imported {imported} repositories...")
                conn.commit()
        
        except Exception as e:
            print(f"  Error importing repository: {e}")
    
    conn.commit()
    print(f"Successfully imported {imported} repositories!")
    return imported


def import_methods(conn, methods_file):
    """Import methods into database."""
    if not os.path.exists(methods_file):
        print(f"Methods file not found: {methods_file}")
        return 0
    
    print(f"Loading methods from {methods_file}...")
    methods = load_json_data(methods_file)
    
    cursor = conn.cursor()
    imported = 0
    
    for method in methods:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO methods (
                    id, name, full_name, description, source_title,
                    source_url, code_snippet, intro_year, categories
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                method.get('id'),
                method.get('name'),
                method.get('full_name'),
                method.get('description'),
                method.get('source_title'),
                method.get('source_url'),
                method.get('code_snippet'),
                method.get('intro_year'),
                json.dumps(method.get('categories', []))
            ))
            imported += 1
        
        except Exception as e:
            print(f"  Error importing method {method.get('id')}: {e}")
    
    conn.commit()
    print(f"Successfully imported {imported} methods!")
    return imported


def import_datasets(conn, datasets_file):
    """Import datasets into database."""
    if not os.path.exists(datasets_file):
        print(f"Datasets file not found: {datasets_file}")
        return 0
    
    print(f"Loading datasets from {datasets_file}...")
    datasets = load_json_data(datasets_file)
    
    cursor = conn.cursor()
    imported = 0
    
    for dataset in datasets:
        try:
            # Generate ID from URL slug, fallback to name if URL is missing
            dataset_id = dataset.get('url', '').split('/')[-1] if dataset.get('url') else dataset.get('name')
            
            cursor.execute("""
                INSERT OR IGNORE INTO datasets (
                    id, name, full_name, homepage, description,
                    paper_title, paper_url, subtasks, modalities, languages
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dataset_id,
                dataset.get('name'),
                dataset.get('full_name'),
                dataset.get('homepage'),
                dataset.get('description'),
                dataset.get('paper_title'),
                dataset.get('paper_url'),
                json.dumps(dataset.get('subtasks', [])),
                json.dumps(dataset.get('modalities', [])),
                json.dumps(dataset.get('languages', []))
            ))
            imported += 1
        
        except Exception as e:
            print(f"  Error importing dataset {dataset.get('name')}: {e}")
    
    conn.commit()
    print(f"Successfully imported {imported} datasets!")
    return imported


def update_statistics(conn):
    """Update database statistics."""
    cursor = conn.cursor()
    
    print("Updating statistics...")
    
    # Clear old statistics
    cursor.execute("DELETE FROM statistics")
    
    # Papers statistics
    cursor.execute("SELECT COUNT(*) FROM papers")
    total_papers = cursor.fetchone()[0]
    cursor.execute("INSERT INTO statistics (stat_type, stat_value) VALUES (?, ?)",
                   ("total_papers", total_papers))
    
    cursor.execute("SELECT COUNT(DISTINCT arxiv_id) FROM papers WHERE arxiv_id IS NOT NULL")
    papers_with_arxiv = cursor.fetchone()[0]
    cursor.execute("INSERT INTO statistics (stat_type, stat_value) VALUES (?, ?)",
                   ("papers_with_arxiv", papers_with_arxiv))
    
    # Repository statistics
    cursor.execute("SELECT COUNT(*) FROM repositories")
    total_repos = cursor.fetchone()[0]
    cursor.execute("INSERT INTO statistics (stat_type, stat_value) VALUES (?, ?)",
                   ("total_repositories", total_repos))
    
    cursor.execute("SELECT COUNT(DISTINCT paper_id) FROM repositories WHERE paper_id IS NOT NULL")
    papers_with_code = cursor.fetchone()[0]
    cursor.execute("INSERT INTO statistics (stat_type, stat_value) VALUES (?, ?)",
                   ("papers_with_code", papers_with_code))
    
    # Other statistics
    cursor.execute("SELECT COUNT(*) FROM methods")
    total_methods = cursor.fetchone()[0]
    cursor.execute("INSERT INTO statistics (stat_type, stat_value) VALUES (?, ?)",
                   ("total_methods", total_methods))
    
    cursor.execute("SELECT COUNT(*) FROM datasets")
    total_datasets = cursor.fetchone()[0]
    cursor.execute("INSERT INTO statistics (stat_type, stat_value) VALUES (?, ?)",
                   ("total_datasets", total_datasets))
    
    cursor.execute("SELECT COUNT(*) FROM tasks")
    total_tasks = cursor.fetchone()[0]
    cursor.execute("INSERT INTO statistics (stat_type, stat_value) VALUES (?, ?)",
                   ("total_tasks", total_tasks))
    
    conn.commit()
    
    print(f"Statistics updated:")
    print(f"  Total papers: {total_papers}")
    print(f"  Papers with arXiv ID: {papers_with_arxiv}")
    print(f"  Total repositories: {total_repos}")
    print(f"  Papers with code: {papers_with_code}")
    print(f"  Total methods: {total_methods}")
    print(f"  Total datasets: {total_datasets}")
    print(f"  Total tasks: {total_tasks}")


def optimize_database(conn):
    """Optimize database performance."""
    cursor = conn.cursor()
    
    print("Optimizing database...")
    
    # Analyze tables for query optimization
    cursor.execute("ANALYZE")
    
    # Vacuum to reclaim space and defragment
    conn.execute("VACUUM")
    
    print("Database optimized!")


def main():
    """Main initialization function."""
    print("Initializing PapersWithCode database...")
    
    # Create or connect to database
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    try:
        # Create enhanced schema
        create_enhanced_schema(conn)
        
        # Import data files if they exist
        papers_imported = import_papers(conn, "papers-with-abstracts.json")
        if papers_imported == 0:
            papers_imported = import_papers(conn, "papers-with-abstracts.json.gz")
        
        repos_imported = import_repositories(conn, "links-between-papers-and-code.json")
        if repos_imported == 0:
            repos_imported = import_repositories(conn, "links-between-papers-and-code.json.gz")
        
        methods_imported = import_methods(conn, "methods.json")
        if methods_imported == 0:
            methods_imported = import_methods(conn, "methods.json.gz")
        
        datasets_imported = import_datasets(conn, "datasets.json")
        if datasets_imported == 0:
            datasets_imported = import_datasets(conn, "datasets.json.gz")
        
        # Update statistics
        update_statistics(conn)
        
        # Optimize database
        optimize_database(conn)
        
        print("\nDatabase initialization complete!")
        print(f"Database file: {DB_PATH}")
        
    except Exception as e:
        print(f"Error during initialization: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()


if __name__ == "__main__":
    main()