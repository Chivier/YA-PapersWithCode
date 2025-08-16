#!/usr/bin/env python3
"""Test script to debug the search flow."""
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agent_search.manager import SearchManager
from agent_search.dataset_search import DatasetSearchAgent

async def test_dataset_search() -> None:
    """Test dataset search functionality."""
    print("=" * 60)
    print("Testing Dataset Search")
    print("=" * 60)
    
    # Test query
    query = "mnist related"
    
    # Create dataset search agent directly
    config = {
        'data_source': 'json',
        'search_strategy': 'basic',
        'use_llm': False,  # Disable LLM to avoid loading models
        'enable_filters': True,
        'recommend_similar': False
    }
    
    print(f"\nCreating DatasetSearchAgent with config:")
    print(json.dumps(config, indent=2))
    
    agent = DatasetSearchAgent(config)
    
    print(f"\nSearching for: '{query}'")
    
    # Test the search
    try:
        result = await agent.search(query, limit=10)
        
        print(f"\nSearch completed. Found {len(result.get('results', []))} results")
        
        if result.get('results'):
            print("\nFirst 3 results:")
            for i, dataset in enumerate(result['results'][:3]):
                print(f"\n{i+1}. {dataset.get('name', 'Unknown')}")
                print(f"   ID: {dataset.get('id', 'N/A')}")
                print(f"   Description: {dataset.get('description', 'N/A')[:100]}...")
        else:
            print("\nNo results found!")
            
            # Debug: Check if datasets are loaded
            from agent_search.api_client import SearchAPIClient
            client = SearchAPIClient()
            all_datasets = client.get_datasets_json()
            print(f"\nTotal datasets loaded: {len(all_datasets)}")
            
            # Check if any dataset contains 'mnist'
            mnist_datasets = [
                d for d in all_datasets
                if 'mnist' in d.get('name', '').lower() or 'mnist' in d.get('description', '').lower()
            ]
            print(f"Datasets containing 'mnist': {len(mnist_datasets)}")
            
            if mnist_datasets:
                print("\nExample MNIST datasets found:")
                for d in mnist_datasets[:3]:
                    print(f"  - {d.get('name')}: {d.get('id')}")
                    
    except Exception as e:
        print(f"\nError during search: {e}")
        import traceback
        traceback.print_exc()
        
    print("\n" + "=" * 60)

async def test_manager_search() -> None:
    """Test search through manager."""
    print("\nTesting Search Manager")
    print("=" * 60)
    
    query = "mnist related"
    
    # Create search manager
    manager = SearchManager()
    
    print(f"Manager initialized with mock models: {manager.use_mock_models}")
    print(f"\nSearching for: '{query}'")
    
    try:
        result = await manager.search(
            query=query,
            search_type='datasets',
            agent_type='basic',
            limit=10
        )
        
        print(f"\nSearch completed. Found {len(result.get('results', []))} results")
        
        if result.get('results'):
            print("\nFirst 3 results:")
            for i, dataset in enumerate(result['results'][:3]):
                print(f"\n{i+1}. {dataset.get('name', 'Unknown')}")
                print(f"   ID: {dataset.get('id', 'N/A')}")
        else:
            print("\nNo results found through manager!")
            
    except Exception as e:
        print(f"\nError during manager search: {e}")
        import traceback
        traceback.print_exc()

async def test_semantic_search() -> None:
    """Test semantic search functionality."""
    print("\n" + "=" * 60)
    print("Testing Semantic Search")
    print("=" * 60)
    
    try:
        from agent_search.utils import get_semantic_results, init_semantic_search
        from agent_search.api_client import SearchAPIClient
        
        # Load datasets
        client = SearchAPIClient()
        all_datasets = client.get_datasets_json()
        
        print(f"Initializing semantic search with {len(all_datasets)} datasets...")
        init_semantic_search(datasets=all_datasets, model_name='all-MiniLM-L6-v2')
        
        # Test semantic search
        query = "mnist handwritten digits"
        print(f"\nSearching semantically for: '{query}'")
        
        results = get_semantic_results(query, 10)
        print(f"Found {len(results)} semantic results")
        
        if results:
            print("\nTop 3 semantic results:")
            for i, dataset in enumerate(results[:3]):
                print(f"\n{i+1}. {dataset.get('name', 'Unknown')}")
                print(f"   Description: {dataset.get('description', 'N/A')[:100]}...")
                
    except Exception as e:
        print(f"\nError in semantic search: {e}")
        import traceback
        traceback.print_exc()

async def main() -> None:
    """Run all tests."""
    await test_dataset_search()
    await test_manager_search()
    await test_semantic_search()

if __name__ == "__main__":
    asyncio.run(main())