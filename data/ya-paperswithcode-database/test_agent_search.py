#!/usr/bin/env python3
"""
Test script for Agent Search functionality
"""
import sys
import os
import asyncio
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Load .env file
def load_env_file():
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        print(f"Loading .env from: {env_path}")
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key, value)
                    if key == 'USE_MOCK_MODELS':
                        print(f"  {key}={value}")

load_env_file()

import importlib.util
import sys

# Import the manager module with dashes in the directory name
spec = importlib.util.spec_from_file_location("manager", "agent-search/manager.py")
manager_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manager_module)
SearchManager = manager_module.SearchManager

async def test_agent_search():
    """Test the Agent Search functionality"""
    print("=" * 60)
    print("🧪 Testing Agent Search")
    print("=" * 60)
    
    try:
        print("\n1. Initializing SearchManager...")
        manager = SearchManager()
        print("✓ SearchManager initialized successfully!")
        
        # Get agent info
        info = manager.get_agent_info()
        print(f"\nAvailable agents: {info['available_agents']}")
        
        use_mock_models = info['model_settings'].get('use_mock_models', True)
        print(f"Using mock models: {use_mock_models}")
        
        print("\n2. Testing basic paper search...")
        result = await manager.search(
            query='neural networks', 
            search_type='papers', 
            agent_type='basic',
            limit=3
        )
        
        print(f"✓ Search completed!")
        print(f"  Results found: {result.get('total', 0)}")
        print(f"  Execution time: {result.get('execution_time', 0):.3f}s")
        print(f"  Search type: {result.get('metadata', {}).get('search_type', 'unknown')}")
        
        # Show first result if available
        results = result.get('results', [])
        if results:
            first = results[0] if hasattr(results[0], 'title') else results[0]
            title = getattr(first, 'title', first.get('title', 'No title'))
            print(f"  First result: {title[:100]}...")
        
        print("\n3. Testing advanced paper search with expansion...")
        result = await manager.search(
            query='transformer models',
            search_type='papers',
            agent_type='advanced',
            limit=2,
            expand=True
        )
        
        print(f"✓ Advanced search completed!")
        print(f"  Results found: {result.get('total', 0)}")
        print(f"  Execution time: {result.get('execution_time', 0):.3f}s")
        print(f"  Agent type: {result.get('metadata', {}).get('agent_type', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent_search())