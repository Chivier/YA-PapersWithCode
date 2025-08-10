#!/usr/bin/env python3
"""
Test lazy loading of models
"""
import os
import sys
sys.path.insert(0, '.')

# Set environment to use real models
os.environ['USE_MOCK_MODELS'] = 'false'
os.environ['MODEL_PATH'] = 'checkpoints'

from agent_search.model_manager import model_manager
import torch
import gc

def print_gpu_memory():
    """Print current GPU memory usage"""
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / 1024**3
        reserved = torch.cuda.memory_reserved() / 1024**3
        print(f"GPU Memory: Allocated={allocated:.2f}GB, Reserved={reserved:.2f}GB")
    else:
        print("GPU not available")

def test_lazy_loading():
    print("=" * 60)
    print("Testing Lazy Model Loading")
    print("=" * 60)
    
    print("\n1. Initial state:")
    print_gpu_memory()
    print(f"Model manager status: {model_manager.get_status()}")
    
    print("\n2. Loading crawler model:")
    crawler_path = 'checkpoints/pasa-7b-crawler'
    crawler = model_manager.get_model(crawler_path, 'agent')
    print_gpu_memory()
    print(f"Model manager status: {model_manager.get_status()}")
    
    print("\n3. Testing crawler inference:")
    try:
        result = crawler.infer("Test prompt", sample=False)
        print(f"Inference successful, result length: {len(result)}")
    except Exception as e:
        print(f"Inference failed: {e}")
    
    print("\n4. Loading selector model (should unload crawler):")
    selector_path = 'checkpoints/pasa-7b-selector'
    selector = model_manager.get_model(selector_path, 'agent')
    print_gpu_memory()
    print(f"Model manager status: {model_manager.get_status()}")
    
    print("\n5. Testing selector inference:")
    try:
        scores = selector.infer_score(["Test prompt"])
        print(f"Scoring successful, scores: {scores}")
    except Exception as e:
        print(f"Scoring failed: {e}")
    
    print("\n6. Unloading all models:")
    model_manager.unload_all()
    print_gpu_memory()
    print(f"Model manager status: {model_manager.get_status()}")
    
    print("\n✓ Test completed!")

if __name__ == "__main__":
    test_lazy_loading()