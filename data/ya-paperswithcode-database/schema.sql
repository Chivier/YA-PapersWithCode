-- PapersWithCode Database Schema

-- Papers table
CREATE TABLE IF NOT EXISTS papers (
    id TEXT PRIMARY KEY,
    arxiv_id TEXT UNIQUE,
    title TEXT NOT NULL,
    abstract TEXT,
    url_abs TEXT,
    url_pdf TEXT,
    proceeding TEXT,
    authors TEXT, -- JSON array stored as text
    tasks TEXT, -- JSON array stored as text
    date TEXT,
    methods TEXT, -- JSON array stored as text
    year INTEGER,
    month INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_papers_arxiv_id ON papers(arxiv_id);
CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(year);
CREATE INDEX IF NOT EXISTS idx_papers_date ON papers(date);
CREATE INDEX IF NOT EXISTS idx_papers_title ON papers(title);

-- Full-text search virtual table for papers
CREATE VIRTUAL TABLE IF NOT EXISTS papers_fts USING fts5(
    title, 
    abstract,
    authors,
    content=papers,
    content_rowid=rowid
);

-- Triggers to keep FTS index in sync
CREATE TRIGGER IF NOT EXISTS papers_ai AFTER INSERT ON papers BEGIN
    INSERT INTO papers_fts(rowid, title, abstract, authors)
    VALUES (new.rowid, new.title, new.abstract, new.authors);
END;

CREATE TRIGGER IF NOT EXISTS papers_ad AFTER DELETE ON papers BEGIN
    INSERT INTO papers_fts(papers_fts, rowid, title, abstract, authors)
    VALUES ('delete', old.rowid, old.title, old.abstract, old.authors);
END;

CREATE TRIGGER IF NOT EXISTS papers_au AFTER UPDATE ON papers BEGIN
    INSERT INTO papers_fts(papers_fts, rowid, title, abstract, authors)
    VALUES ('delete', old.rowid, old.title, old.abstract, old.authors);
    INSERT INTO papers_fts(rowid, title, abstract, authors)
    VALUES (new.rowid, new.title, new.abstract, new.authors);
END;

-- Code repositories table
CREATE TABLE IF NOT EXISTS repositories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id TEXT,
    paper_arxiv_id TEXT,
    paper_title TEXT,
    paper_url_abs TEXT,
    paper_url_pdf TEXT,
    repo_url TEXT NOT NULL,
    framework TEXT,
    mentioned_in_paper INTEGER DEFAULT 0,
    mentioned_in_github INTEGER DEFAULT 0,
    stars INTEGER DEFAULT 0,
    is_official INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers(id)
);

CREATE INDEX IF NOT EXISTS idx_repos_paper_id ON repositories(paper_id);
CREATE INDEX IF NOT EXISTS idx_repos_paper_arxiv_id ON repositories(paper_arxiv_id);
CREATE INDEX IF NOT EXISTS idx_repos_stars ON repositories(stars);
CREATE INDEX IF NOT EXISTS idx_repos_framework ON repositories(framework);

-- Methods table
CREATE TABLE IF NOT EXISTS methods (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    full_name TEXT,
    description TEXT,
    source_title TEXT,
    source_url TEXT,
    code_snippet TEXT,
    intro_year INTEGER,
    categories TEXT, -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_methods_name ON methods(name);
CREATE INDEX IF NOT EXISTS idx_methods_year ON methods(intro_year);

-- Datasets table
CREATE TABLE IF NOT EXISTS datasets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    full_name TEXT,
    homepage TEXT,
    description TEXT,
    paper_title TEXT,
    paper_url TEXT,
    subtasks TEXT, -- JSON array
    modalities TEXT, -- JSON array
    languages TEXT, -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_datasets_name ON datasets(name);

-- Evaluation results table
CREATE TABLE IF NOT EXISTS evaluation_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL,
    dataset TEXT NOT NULL,
    sota_rows TEXT, -- JSON array of SOTA entries
    metrics TEXT, -- JSON array of metric definitions
    subdataset TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_eval_task ON evaluation_results(task);
CREATE INDEX IF NOT EXISTS idx_eval_dataset ON evaluation_results(dataset);

-- Tasks table (extracted from papers and evaluations)
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    paper_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tasks_name ON tasks(name);

-- Many-to-many relationship between papers and tasks
CREATE TABLE IF NOT EXISTS paper_tasks (
    paper_id TEXT,
    task_name TEXT,
    PRIMARY KEY (paper_id, task_name),
    FOREIGN KEY (paper_id) REFERENCES papers(id),
    FOREIGN KEY (task_name) REFERENCES tasks(name)
);

-- Statistics table for tracking data
CREATE TABLE IF NOT EXISTS statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stat_type TEXT NOT NULL,
    stat_value INTEGER NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);