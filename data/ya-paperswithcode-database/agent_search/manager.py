"""
Agent Search Manager - Orchestrates different search agents
"""

import json
import asyncio
import os
from typing import Dict, Any, Optional
from pathlib import Path
from .paper_search import PaperSearchAgent
from .dataset_search import DatasetSearchAgent
from .models import Agent
from .model_manager import model_manager


class LazyModelWrapper:
    """Wrapper for lazy-loaded models"""
    def __init__(self, model_path: str, model_type: str):
        self.model_path = model_path
        self.model_type = model_type
        self._model = None
    
    def get_model(self):
        """Get the actual model, loading if necessary"""
        return model_manager.get_model(self.model_path, self.model_type)
    
    def __getattr__(self, name):
        """Delegate attribute access to the actual model"""
        model = self.get_model()
        return getattr(model, name)


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
        self.crawler_path = None  # Store path to crawler model
        self.selector_path = None  # Store path to selector model
        self.use_mock_models = True  # Default to mock
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all search agents with their configurations"""
        
        # Load AI models configuration from .env
        # First try to load from .env file
        env_path = Path(__file__).parent.parent.parent / '.env'
        use_mock_models = True  # Default to mock models
        
        if env_path.exists():
            # Read .env file
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('USE_MOCK_MODELS='):
                        use_mock_models = line.split('=')[1].lower() in ('true', '1', 'yes')
                        break
        
        # Also check environment variables
        if 'USE_MOCK_MODELS' in os.environ:
            use_mock_models = os.environ['USE_MOCK_MODELS'].lower() in ('true', '1', 'yes')
        
        self.use_mock_models = use_mock_models
        crawler = None
        selector = None
        
        if not use_mock_models:
            # Get model paths from .env or use defaults
            self.crawler_path = os.getenv('MODEL_PATH', 'checkpoints') + '/pasa-7b-crawler'
            self.selector_path = os.getenv('MODEL_PATH', 'checkpoints') + '/pasa-7b-selector'
            
            print(f"Model paths configured:")
            print(f"  Crawler: {self.crawler_path}")
            print(f"  Selector: {self.selector_path}")
            print("Models will be loaded on-demand to save memory")
            
            # Create lazy-loaded wrapper objects
            crawler = LazyModelWrapper(self.crawler_path, 'crawler')
            selector = LazyModelWrapper(self.selector_path, 'selector')
        else:
            print("Using mock models - AI features disabled")
        
        # Initialize paper search agents
        paper_configs = self.config.get('agents', {}).get('paper_search', {})
        
        # Add models to configurations
        basic_config = paper_configs.get('default', {}).copy()
        advanced_config = paper_configs.get('advanced', {}).copy()
        
        basic_config['crawler'] = crawler
        basic_config['selector'] = selector
        advanced_config['crawler'] = crawler
        advanced_config['selector'] = selector
        
        self.agents['paper_basic'] = PaperSearchAgent(basic_config)
        self.agents['paper_advanced'] = PaperSearchAgent(advanced_config)
        
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
        
        # Always unload models after use to prevent GPU OOM
        # Models will be reloaded on next use thanks to lazy loading
        if not self.use_mock_models:
            self.unload_models()
        
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
    
    def unload_models(self):
        """Unload AI models from GPU memory to free resources"""
        # Use the global model manager to unload all models
        model_manager.unload_all()


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