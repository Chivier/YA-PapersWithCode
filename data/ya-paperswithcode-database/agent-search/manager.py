"""
Agent Search Manager - Orchestrates different search agents
"""

import json
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from .paper_search import PaperSearchAgent
from .dataset_search import DatasetSearchAgent


class SearchManager:
    """Manager for coordinating different search agents"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the search manager
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            # Load default config
            default_config_path = Path(__file__).parent / 'config.json'
            if default_config_path.exists():
                with open(default_config_path, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {}
        
        # Initialize agents
        self.agents = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all search agents with their configurations"""
        
        # Initialize paper search agents
        paper_configs = self.config.get('agents', {}).get('paper_search', {})
        self.agents['paper_basic'] = PaperSearchAgent(paper_configs.get('default', {}))
        self.agents['paper_advanced'] = PaperSearchAgent(paper_configs.get('advanced', {}))
        
        # Initialize dataset search agents
        dataset_configs = self.config.get('agents', {}).get('dataset_search', {})
        self.agents['dataset_basic'] = DatasetSearchAgent(dataset_configs.get('default', {}))
        self.agents['dataset_advanced'] = DatasetSearchAgent(dataset_configs.get('advanced', {}))
    
    async def search(self, query: str, search_type: str = 'auto', 
                    agent_type: str = 'auto', **kwargs) -> Dict[str, Any]:
        """
        Perform a search using the appropriate agent
        
        Args:
            query: Search query string
            search_type: Type of search ('papers', 'datasets', 'methods', 'auto')
            agent_type: Agent type ('basic', 'advanced', 'auto')
            **kwargs: Additional search parameters
            
        Returns:
            Search results dictionary
        """
        # Determine search type if auto
        if search_type == 'auto':
            search_type = self._detect_search_type(query)
        
        # Determine agent type if auto
        if agent_type == 'auto':
            agent_type = self._detect_agent_type(query, kwargs)
        
        # Select appropriate agent
        agent = self._select_agent(search_type, agent_type)
        
        # Perform search
        results = await agent.search(query, **kwargs)
        
        # Add manager metadata
        results['metadata']['search_type'] = search_type
        results['metadata']['agent_type'] = agent_type
        
        return results
    
    def _detect_search_type(self, query: str) -> str:
        """
        Detect the type of search from the query
        
        Args:
            query: Search query
            
        Returns:
            Search type ('papers', 'datasets', 'methods')
        """
        query_lower = query.lower()
        
        # Dataset indicators
        dataset_keywords = ['dataset', 'corpus', 'benchmark', 'samples', 'data']
        if any(keyword in query_lower for keyword in dataset_keywords):
            return 'datasets'
        
        # Method indicators
        method_keywords = ['method', 'algorithm', 'model', 'architecture', 'approach']
        if any(keyword in query_lower for keyword in method_keywords):
            return 'methods'
        
        # Default to papers
        return 'papers'
    
    def _detect_agent_type(self, query: str, kwargs: Dict) -> str:
        """
        Detect whether to use basic or advanced agent
        
        Args:
            query: Search query
            kwargs: Additional parameters
            
        Returns:
            Agent type ('basic' or 'advanced')
        """
        # Use advanced if expansion is requested
        if kwargs.get('expand', False):
            return 'advanced'
        
        # Use advanced for complex queries
        if len(query.split()) > 10:
            return 'advanced'
        
        # Use advanced if specific advanced features are requested
        if kwargs.get('use_semantic', False) or kwargs.get('multi_layer', False):
            return 'advanced'
        
        # Default to basic for simple queries
        return 'basic'
    
    def _select_agent(self, search_type: str, agent_type: str):
        """
        Select the appropriate agent
        
        Args:
            search_type: Type of search
            agent_type: Type of agent
            
        Returns:
            Selected agent instance
        """
        if search_type == 'papers':
            return self.agents[f'paper_{agent_type}']
        elif search_type == 'datasets':
            return self.agents[f'dataset_{agent_type}']
        else:
            # Default to paper search for methods and others
            return self.agents[f'paper_{agent_type}']
    
    async def multi_search(self, query: str, search_types: list = None) -> Dict[str, Any]:
        """
        Perform search across multiple types
        
        Args:
            query: Search query
            search_types: List of search types (default: all)
            
        Returns:
            Combined search results
        """
        if search_types is None:
            search_types = ['papers', 'datasets', 'methods']
        
        # Run searches in parallel
        tasks = []
        for search_type in search_types:
            task = self.search(query, search_type=search_type)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # Combine results
        combined = {
            'query': query,
            'results': {},
            'metadata': {
                'search_types': search_types
            }
        }
        
        for search_type, result in zip(search_types, results):
            combined['results'][search_type] = result
        
        return combined
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about available agents"""
        return {
            'available_agents': list(self.agents.keys()),
            'configurations': self.config.get('agents', {}),
            'api_settings': self.config.get('api_settings', {}),
            'model_settings': self.config.get('model_settings', {})
        }


# Convenience function for quick searches
async def quick_search(query: str, **kwargs) -> Dict[str, Any]:
    """
    Perform a quick search using default settings
    
    Args:
        query: Search query
        **kwargs: Additional parameters
        
    Returns:
        Search results
    """
    manager = SearchManager()
    return await manager.search(query, **kwargs)