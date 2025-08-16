#!/usr/bin/env python3
"""
Debug why SearchManager returns 0 results.
"""
import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
os.environ['USE_MOCK_MODELS'] = 'false'

async def test_manager() -> None:
    """Test SearchManager to debug result issues."""
    from agent_search.manager import SearchManager
    from agent_search.dataset_search import DatasetSearchAgent
    
    print("Testing SearchManager issue")
    print("=" * 60)
    
    # Initialize manager
    manager = SearchManager()
    
    # Get the dataset agent
    agent = manager._select_agent('datasets', 'basic')
    print(f"Selected agent: {type(agent)}")
    print(f"Agent config: {agent.config}")
    
    # Test search directly on agent
    print("\n1. Direct agent search:")
    result1 = await agent.search("mnist related", limit=5)
    print(f"   Results: {result1.get('total', 0)}")
    if result1.get('results'):
        print(f"   First: {result1['results'][0].get('name', 'N/A')}")
    
    # Test through manager
    print("\n2. Through manager search:")
    result2 = await manager.search("mnist related", search_type='datasets', limit=5)
    print(f"   Results: {result2.get('total', 0)}")
    print(f"   Metadata: {result2.get('metadata', {})}")
    if result2.get('results'):
        print(f"   First: {result2['results'][0].get('name', 'N/A')}")
    
    # Check if manager is modifying results
    print("\n3. Checking result structure:")
    print(f"   Direct result keys: {result1.keys()}")
    print(f"   Manager result keys: {result2.keys()}")
    
    # Check format_response
    print("\n4. Checking format_response:")
    from agent_search.base import BaseSearchAgent
    base_agent = BaseSearchAgent({})
    formatted = base_agent.format_response(
        results=[{"name": "test"}],
        query="test",
        execution_time=0.1,
        metadata={}
    )
    print(f"   Formatted result keys: {formatted.keys()}")
    print(f"   Formatted total: {formatted.get('total', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(test_manager())