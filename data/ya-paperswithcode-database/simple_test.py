#!/usr/bin/env python3
"""
Simple test to check if models are loading
"""
import os
import sys
from pathlib import Path

# Load .env file
def load_env_file():
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        print(f"Loading .env from: {env_path}")
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    # Force set the environment variable (don't use setdefault)
                    os.environ[key] = value
                    if key in ['USE_MOCK_MODELS', 'MODEL_PATH']:
                        print(f"  {key}={value}")
    else:
        print(f"⚠ .env file not found at: {env_path}")

load_env_file()

# Test model loading
try:
    print("\n" + "="*50)
    print("Testing Model Loading")
    print("="*50)
    
    use_mock_models = os.getenv('USE_MOCK_MODELS', 'true').lower() in ('true', '1', 'yes')
    model_path = os.getenv('MODEL_PATH', 'checkpoints')
    
    print(f"USE_MOCK_MODELS: {use_mock_models}")
    print(f"MODEL_PATH: {model_path}")
    
    if not use_mock_models:
        crawler_path = f"{model_path}/pasa-7b-crawler"
        selector_path = f"{model_path}/pasa-7b-selector"
        
        print(f"\nCrawler model path: {crawler_path}")
        print(f"Selector model path: {selector_path}")
        
        # Check if paths exist
        if Path(crawler_path).exists():
            print("✓ Crawler model directory exists")
            # Check for model files
            if Path(f"{crawler_path}/config.json").exists():
                print("✓ Crawler config.json found")
            if (Path(f"{crawler_path}/model.safetensors").exists() or 
                list(Path(crawler_path).glob("model-*.safetensors"))):
                print("✓ Crawler model files found")
        else:
            print("✗ Crawler model directory not found")
            
        if Path(selector_path).exists():
            print("✓ Selector model directory exists")
            if Path(f"{selector_path}/config.json").exists():
                print("✓ Selector config.json found")
            if Path(f"{selector_path}/model.safetensors").exists():
                print("✓ Selector model files found")
        else:
            print("✗ Selector model directory not found")
            
        # Try to load models
        print("\nAttempting to load models...")
        try:
            # Import here to avoid issues with package structure
            sys.path.insert(0, str(Path(__file__).parent / "agent-search"))
            from models import Agent
            
            print("Loading crawler...")
            crawler = Agent(crawler_path)
            print("✓ Crawler loaded successfully!")
            
            print("Loading selector...")  
            selector = Agent(selector_path)
            print("✓ Selector loaded successfully!")
            
            # Test a simple inference
            print("\nTesting inference...")
            test_prompt = "This is a test prompt."
            try:
                response = crawler.infer(test_prompt)
                print(f"✓ Crawler inference works! Response length: {len(response)}")
                print(f"  Sample response: {response[:100]}...")
            except Exception as e:
                print(f"✗ Crawler inference failed: {e}")
            
            try:
                scores = selector.infer_score([test_prompt])
                print(f"✓ Selector scoring works! Score: {scores[0] if scores else 'None'}")
            except Exception as e:
                print(f"✗ Selector scoring failed: {e}")
                
        except Exception as e:
            print(f"✗ Failed to load models: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\nUsing mock models - skipping real model loading")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()