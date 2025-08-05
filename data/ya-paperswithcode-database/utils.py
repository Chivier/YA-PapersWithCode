# local_utils.py
import re
from typing import List, Dict, Optional
from semantic_search import SemanticSearchEngine

# Initialize semantic search engine globally
semantic_engine = None

def init_semantic_search(papers_path: str):
    """Initialize the semantic search engine"""
    global semantic_engine
    semantic_engine = SemanticSearchEngine(papers_path)

def local_search_arxiv_id(query: str, num: int = 10, end_date: Optional[str] = None) -> List[str]:
    """Local semantic search replacement for google_search_arxiv_id"""
    if semantic_engine is None:
        raise ValueError("Semantic search engine not initialized. Call init_semantic_search first.")
    
    return semantic_engine.search_by_query(query, num, end_date)

def search_paper_by_arxiv_id(arxiv_id: str) -> Optional[Dict]:
    """Get paper details by arxiv ID from local database"""
    if semantic_engine is None:
        raise ValueError("Semantic search engine not initialized. Call init_semantic_search first.")
    
    return semantic_engine.search_by_arxiv_id(arxiv_id)

def search_paper_by_title(title: str) -> Optional[Dict]:
    """Search paper by title in local database"""
    if semantic_engine is None:
        raise ValueError("Semantic search engine not initialized. Call init_semantic_search first.")
    
    return semantic_engine.search_by_title(title)

def get_similar_papers(arxiv_id: str, num: int = 10) -> List[Dict]:
    """Get similar papers based on content similarity"""
    if semantic_engine is None:
        raise ValueError("Semantic search engine not initialized. Call init_semantic_search first.")
    
    return semantic_engine.search_similar_papers(arxiv_id, num)