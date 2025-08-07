"""
Base class for search agents
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


class BaseSearchAgent(ABC):
    """Abstract base class for all search agents"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the search agent
        
        Args:
            config: Configuration dictionary for the agent
        """
        self.config = config or {}
        self.api_client = None
        self.data_source = self.config.get('data_source', 'api')  # 'api' or 'json'
        self.search_strategy = self.config.get('search_strategy', 'basic')  # 'basic' or 'advanced'
        
    @abstractmethod
    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Perform a search based on the query
        
        Args:
            query: Search query string
            **kwargs: Additional search parameters
            
        Returns:
            Search results dictionary
        """
        pass
    
    @abstractmethod
    async def expand_search(self, initial_results: List[Dict], **kwargs) -> List[Dict]:
        """
        Expand search results using various strategies
        
        Args:
            initial_results: Initial search results
            **kwargs: Additional expansion parameters
            
        Returns:
            Expanded search results
        """
        pass
    
    def set_api_client(self, api_client):
        """Set the API client for data access"""
        self.api_client = api_client
        
    async def load_json_data(self, file_path: str) -> List[Dict]:
        """
        Load data from JSON file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            List of data records
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data if isinstance(data, list) else [data]
        except Exception as e:
            print(f"Error loading JSON data: {e}")
            return []
    
    def format_response(self, results: List[Dict], query: str, 
                       execution_time: float, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Format the search response
        
        Args:
            results: Search results
            query: Original query
            execution_time: Time taken for search
            metadata: Additional metadata
            
        Returns:
            Formatted response dictionary
        """
        return {
            "results": results,
            "total": len(results),
            "query": query,
            "search_type": f"{self.__class__.__name__}",
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }