"""
Paper Search Agent Implementation
"""
import re
import threading
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseSearchAgent
from .api_client import SearchAPIClient
from .paper_node import PaperNode
from .utils import local_search_arxiv_id, search_paper_by_arxiv_id, get_similar_papers, init_semantic_search

class PaperSearchAgent(BaseSearchAgent):
    """Agent for searching academic papers with advanced expansion capabilities"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the paper search agent
        
        Args:
            config: Configuration dictionary with options like:
                - data_source: 'api' or 'json'
                - search_strategy: 'basic' or 'advanced'
                - expand_layers: Number of expansion layers (default: 2)
                - search_queries: Number of search queries to generate (default: 5)
                - search_papers: Number of papers to search per query (default: 10)
                - expand_papers: Number of papers to expand (default: 20)
                - threads_num: Number of threads for parallel processing (default: 20)
        """
        super().__init__(config)
        
        # Paper-specific configuration
        self.expand_layers = self.config.get('expand_layers', 2)
        self.search_queries = self.config.get('search_queries', 5)
        self.search_papers = self.config.get('search_papers', 10)
        self.expand_papers = self.config.get('expand_papers', 20)
        self.threads_num = self.config.get('threads_num', 20)
        self.semantic_model_name = self.config.get('semantic_model_name', 'all-MiniLM-L6-v2')
        self.selector = self.config.get('selector', None)
        self.crawler = self.config.get('crawler', None)
        
        # Initialize API client
        self.api_client = SearchAPIClient()
        
        self.prompts = {
            "generate_query": "Please generate some mutually exclusive queries in a list to search the relevant papers according to the User Query. Searching for survey papers would be better.\nUser Query: {user_query}",
            "select_section": "You are conducting research on `{user_query}`. You need to predict which sections to look at for getting more relevant papers. Title: {title}\nAbstract: {abstract}\nSections: {sections}",
            "get_selected": "You are an elite researcher in the field of AI, conducting research on {user_query}. Evaluate whether the following paper fully satisfies the detailed requirements of the user query and provide your reasoning. Ensure that your decision and reasoning are consistent.\n\nSearched Paper:\nTitle: {title}\nAbstract: {abstract}\n\nUser Query: {user_query}\n\nOutput format: Decision: True/False\nReason:... \nDecision:",
            "get_value": "You are conducting research on {user_query}. Evaluate whether the following paper fully satisfies the detailed requirements of the user query and provide your reasoning. Ensure that your decision and reasoning are consistent.\n\nSearched Paper:\nTitle: {title}\nAbstract: {abstract}\n\nUser Query: {user_query}\n\nOutput format: Decision: True/False\nReason:... \nDecision:"
        }
        self.templates       = {
            "cite_template":   r"~\\cite\{(.*?)\}",
            "search_template": r"Search\](.*?)\[",
            "expand_template": r"Expand\](.*?)\["
        }
        self.papers_queue = []
        self.expand_start = 0
        self.papers_path = self.config.get('papers_path', None)
        
    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Search for papers based on query
        
        Args:
            query: Search query string
            **kwargs: Additional parameters:
                - limit: Maximum number of results
                - filters: Filter criteria
                - expand: Whether to expand results
                
        Returns:
            Search results dictionary
        """
        start_time = datetime.now()
        
        limit = kwargs.get('limit', 50)
        filters = kwargs.get('filters', {})
        expand = kwargs.get('expand', False)
        
        # Get initial results based on data source
        if self.data_source == 'json':
            results = await self._search_json(query, limit, filters)
        else:
            results = await self._search_api(query, limit, filters)
        
        # Expand results if requested and using advanced strategy
        if expand and self.search_strategy == 'advanced':
            # TODO:AGENT_SEARCH - Implement paper expansion using run_search_agent.py logic
            # This should:
            # 1. Use the PaperAgent from paper_agent.py
            # 2. Implement multi-layer expansion
            # 3. Use crawler and selector models
            # 4. Handle citation graphs and related papers
            expand_papers = results
            for depth in range(self.expand_layers):
                if depth != 0:
                    expand_results = self.expand_search(expand_papers[:self.expand_papers])
                else:
                    expand_results = self.expand_search(expand_papers)
                results.extend(expand_results)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return self.format_response(
            results=results,
            query=query,
            execution_time=execution_time,
            metadata={
                'data_source': self.data_source,
                'search_strategy': self.search_strategy,
                'expanded': expand
            }
        )
    
    async def _search_api(self, query: str, limit: int, filters: Dict) -> List[Dict]:
        """
        Search using database API
        
        Args:
            query: Search query
            limit: Result limit
            filters: Filter criteria
            
        Returns:
            List of paper dictionaries
        """
        search_filters = filters.copy()
        search_filters['search'] = query
        
        return self.api_client.get_papers(filters=search_filters, limit=limit)
    
    async def _search_json(self, query: str, limit: int, filters: Dict) -> List[Dict]:
        """
        Search using JSON data
        
        Args:
            query: Search query
            limit: Result limit
            filters: Filter criteria
            
        Returns:
            List of paper dictionaries
        """
        self.root = PaperNode({
            "title": query,
            "extra": {
                "touch_ids": [],
                "crawler_recall_papers": [],
                "recall_papers": [],
            }
        })
        
        all_papers = self.api_client.get_papers_json()
        
        # TODO:AGENT_SEARCH - Implement semantic search on JSON data
        # This should:
        # 1. Use semantic_search.py for vector similarity
        # 2. Filter by query relevance
        # 3. Apply additional filters
        # 4. Sort by relevance score
        
        init_semantic_search(papers=all_papers, model_name=self.semantic_model_name)
        queries = self.generate_search_queries(query)
        results = self.search_paper(queries)
        
        filtered_papers = []
        
        for paper in results:
            if filters:
                if 'year' in filters:
                    date = paper.get('date', '')
                    try:
                        year = int(date.split('-')[0])
                        if filters['year'] != year:
                            continue
                    except:
                        continue
                if 'task' in filters:
                    tasks = paper.get('tasks', [])
                    if not any(filters['task'].lower() in task.lower() for task in tasks):
                        continue
                if 'conference' in filters:
                    proceeding = paper.get('proceeding', '')
                    if not filters['conference'].lower() in proceeding.lower():
                        continue
            
            filtered_papers.append(paper)
        
        ranked_results = self.rank_results(filtered_papers, query)
        
        return ranked_results
    
    async def expand_search(self, initial_results: List[Dict], **kwargs) -> List[Dict]:
        """
        Expand search results using citation graphs and related papers
        
        Args:
            initial_results: Initial search results
            **kwargs: Expansion parameters
            
        Returns:
            Expanded search results
        """
        # TODO:AGENT_SEARCH - Implement multi-layer paper expansion
        # This should:
        # 1. Build citation graph from initial results
        # 2. Find related papers through citations
        # 3. Find papers by same authors
        # 4. Find papers from same venues/conferences
        # 5. Use parallel processing with threads_num
        # 6. Rank and filter expanded results
        expand_papers = initial_results
        extend_results = []
        while expand_papers:
            if not expand_papers:
                break
            paper = expand_papers.pop(0)
            
            # Get similar papers
            similar_papers = get_similar_papers(paper.arxiv_id, num=10)
            
            select_prompts = []
            valid_papers = []
            
            for similar_paper in similar_papers:
                arxiv_id = similar_paper.get("arxiv_id", "")
                if not arxiv_id:
                    continue
                    
                if arxiv_id not in self.root.extra["touch_ids"]:
                    self.root.extra["touch_ids"].append(arxiv_id)
                    prompt = self.prompts["get_selected"].format(
                        title=similar_paper["title"], 
                        abstract=similar_paper["abstract"], 
                        user_query=self.user_query
                    )
                    select_prompts.append(prompt)
                    valid_papers.append(similar_paper)
            
            if select_prompts:
                scores = self.selector.infer_score(select_prompts)
                
                for score, ref_paper in zip(scores, valid_papers):
                    self.root.extra["crawler_recall_papers"].append(ref_paper["title"])
                    if score > 0.5:
                        self.root.extra["recall_papers"].append(ref_paper["title"])
                    
                    paper_node = PaperNode({
                        "title": ref_paper["title"],
                        "depth": paper.depth + 1,
                        "arxiv_id": ref_paper["arxiv_id"],
                        "abstract": ref_paper["abstract"],
                        "authors": ref_paper.get("authors", []),
                        "tasks": ref_paper.get("tasks", []),
                        "date": ref_paper.get("date", ""),
                        "url_pdf": ref_paper.get("url_pdf", ""),
                        "url_abs": ref_paper.get("url_abs", ""),
                        "search_source": f"Similar to: {paper.title}",
                        "select_score": score,
                        "extra": {"similarity_score": ref_paper.get("similarity_score", 0)}
                    })
                    if "similar" not in paper.child:
                        paper.child["similar"] = []
                    paper.child["similar"].append(paper_node)
                    paper.extra["expand"] = "success"
                    extend_results.append(paper_node)
        extend_results = sorted(extend_results, key=PaperNode.sort_paper, reverse=True)
        return extend_results
    
    async def generate_search_queries(self, user_query: str) -> List[str]:
        """
        Generate multiple search queries from user input
        
        Args:
            user_query: Original user query
            
        Returns:
            List of generated search queries
        """
        # TODO:AGENT_SEARCH - Implement query generation using LLM
        # This should:
        # 1. Use the crawler model to generate variations
        # 2. Create queries for different aspects of the search
        # 3. Generate queries for citation exploration
        prompt = self.prompts["generate_query"].format(user_query=user_query).strip()
        queries = self.crawler.infer(prompt)
        queries = [q.strip() for q in re.findall(self.templates["search_template"], user_query, flags=re.DOTALL)][:self.search_queries]
        
        
        return queries
    
    async def rank_results(self, results: List[Dict], query: str) -> List[Dict]:
        """
        Rank search results by relevance
        
        Args:
            results: Search results to rank
            query: Original query
            
        Returns:
            Ranked results
        """
        # TODO:AGENT_SEARCH - Implement result ranking using selector model
        # This should:
        # 1. Use the selector model to score relevance
        # 2. Consider citation count
        # 3. Consider recency
        # 4. Apply personalization if available
        select_prompts = [self.prompts["get_selected"].format(title=paper["title"], abstract=paper["abstract"], user_query=query) for paper in results]
        scores = self.selector.infer_score(select_prompts)
        
        ranked_papers = []
        for score, paper in zip(scores, results):
            self.root.extra["crawler_recall_papers"].append(paper["title"])
            if score > 0.5:
                self.root.extra["recall_papers"].append(paper["title"])
            paper_node = PaperNode({
                "title": paper["title"],
                "arxiv_id": paper["arxiv_id"],
                "depth": 0,
                "abstract": paper["abstract"],
                "authors": paper["authors"],
                "tasks": paper["tasks"],
                "date": paper["date"],
                "url_pdf": paper["url_pdf"],
                "url_abs": paper["url_abs"],
                "search_source": f"Query: {query}",
                "select_score": score,
                "extra": {}
            })
            self.root.child[query].append(paper_node)
            ranked_papers.append(paper_node)
        ranked_papers = sorted(ranked_papers, key=PaperNode.sort_paper, reverse=True)
        
        return ranked_papers
    
    async def search_paper(self, queries):
        while queries:
            query, self.root.child[query] = queries.pop(), []
            pre_arxiv_ids, searched_papers = local_search_arxiv_id(query, self.search_papers), []
            for arxiv_id in pre_arxiv_ids:
                arxiv_id = arxiv_id.split('v')[0]
                if arxiv_id not in self.root.extra["touch_ids"]:
                    self.root.extra["touch_ids"].append(arxiv_id)
                    paper = search_paper_by_arxiv_id(arxiv_id)
                    if paper is not None:
                        searched_papers.append(paper)
        return searched_papers   
    
            