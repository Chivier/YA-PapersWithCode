#!/usr/bin/env python3
"""
Download and setup model checkpoints for AI Agent Search
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Optional

def create_model_directories():
    """Create necessary directories for model checkpoints"""
    base_dir = Path(__file__).parent
    checkpoints_dir = base_dir / "checkpoints"
    
    # Create directories
    crawler_dir = checkpoints_dir / "pasa-7b-crawler"
    selector_dir = checkpoints_dir / "pasa-7b-selector"
    
    for dir_path in [checkpoints_dir, crawler_dir, selector_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {dir_path}")
    
    return crawler_dir, selector_dir

def check_huggingface_models():
    """Check if models are available on HuggingFace"""
    models_to_check = [
        "bytedance-research/pasa-7b-crawler",
        "bytedance-research/pasa-7b-selector",
        "sentence-transformers/all-MiniLM-L6-v2"
    ]
    
    print("\n🔍 Checking model availability...")
    available_models = []
    
    for model_name in models_to_check:
        # Check HuggingFace API
        url = f"https://huggingface.co/api/models/{model_name}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"  ✓ Found on HuggingFace: {model_name}")
                available_models.append(model_name)
            else:
                print(f"  ✗ Not found on HuggingFace: {model_name}")
        except:
            print(f"  ? Could not check: {model_name}")
    
    return available_models

def download_from_huggingface(model_name: str, target_dir: Path):
    """Download model from HuggingFace"""
    try:
        from huggingface_hub import snapshot_download
        
        print(f"\n📥 Downloading {model_name} from HuggingFace...")
        snapshot_download(
            repo_id=model_name,
            local_dir=target_dir,
            local_dir_use_symlinks=False,
            resume_download=True
        )
        print(f"  ✓ Downloaded to {target_dir}")
        return True
    except ImportError:
        print("  ✗ Please install huggingface_hub: pip install huggingface_hub")
        return False
    except Exception as e:
        print(f"  ✗ Download failed: {e}")
        return False

def create_mock_models(crawler_dir: Path, selector_dir: Path):
    """Create mock model configurations for testing"""
    print("\n⚠️  Creating mock model configurations for testing...")
    print("    Note: These are NOT real models and won't provide actual AI functionality")
    
    # Mock config for both models
    mock_config = {
        "architectures": ["LlamaForCausalLM"],
        "model_type": "llama",
        "vocab_size": 32000,
        "hidden_size": 4096,
        "intermediate_size": 11008,
        "num_hidden_layers": 32,
        "num_attention_heads": 32,
        "num_key_value_heads": 32,
        "max_position_embeddings": 2048,
        "rms_norm_eps": 1e-6,
        "initializer_range": 0.02,
        "use_cache": True,
        "tie_word_embeddings": False,
        "rope_theta": 10000.0,
        "attention_bias": False,
        "attention_dropout": 0.0,
        "_name_or_path": "mock-model"
    }
    
    # Mock tokenizer config
    mock_tokenizer_config = {
        "tokenizer_class": "LlamaTokenizer",
        "model_max_length": 2048,
        "padding_side": "left",
        "bos_token": "<s>",
        "eos_token": "</s>",
        "unk_token": "<unk>",
        "pad_token": "<pad>"
    }
    
    for dir_path, model_name in [(crawler_dir, "pasa-7b-crawler"), (selector_dir, "pasa-7b-selector")]:
        # Save config.json
        config_path = dir_path / "config.json"
        with open(config_path, 'w') as f:
            json.dump(mock_config, f, indent=2)
        print(f"  ✓ Created mock config: {config_path}")
        
        # Save tokenizer_config.json
        tokenizer_config_path = dir_path / "tokenizer_config.json"
        with open(tokenizer_config_path, 'w') as f:
            json.dump(mock_tokenizer_config, f, indent=2)
        print(f"  ✓ Created mock tokenizer config: {tokenizer_config_path}")
        
        # Create README
        readme_path = dir_path / "README.md"
        with open(readme_path, 'w') as f:
            f.write(f"""# Mock Model: {model_name}

This is a mock model configuration for testing purposes only.

To use real AI functionality, you need to:
1. Obtain the actual {model_name} model files
2. Place them in this directory
3. Ensure the model files include:
   - pytorch_model.bin or model.safetensors
   - config.json
   - tokenizer files (tokenizer.json, tokenizer_config.json, etc.)

For now, the agent search will fall back to basic search without AI enhancement.
""")
        print(f"  ✓ Created README: {readme_path}")

def update_agent_config():
    """Update agent configuration to handle missing models gracefully"""
    base_dir = Path(__file__).parent
    agent_config_path = base_dir / "agent-search" / "config.json"
    
    if agent_config_path.exists():
        with open(agent_config_path, 'r') as f:
            config = json.load(f)
        
        # Add fallback configuration
        config["model_settings"]["fallback_enabled"] = True
        config["model_settings"]["use_mock_models"] = True
        
        with open(agent_config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"  ✓ Updated agent config: {agent_config_path}")

def setup_embedding_model():
    """Setup the embedding model for semantic search"""
    print("\n📦 Setting up embedding model...")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        print(f"  Downloading {model_name}...")
        
        # This will download and cache the model
        model = SentenceTransformer(model_name)
        print(f"  ✓ Embedding model ready: {model_name}")
        return True
    except ImportError:
        print("  ✗ Please install sentence-transformers: pip install sentence-transformers")
        return False
    except Exception as e:
        print(f"  ✗ Failed to setup embedding model: {e}")
        return False

def check_requirements():
    """Check if required packages are installed"""
    print("\n📋 Checking requirements...")
    
    required_packages = {
        "transformers": "pip install transformers",
        "torch": "pip install torch",
        "sentence_transformers": "pip install sentence-transformers",
        "huggingface_hub": "pip install huggingface_hub"
    }
    
    missing_packages = []
    
    for package, install_cmd in required_packages.items():
        try:
            __import__(package)
            print(f"  ✓ {package} is installed")
        except ImportError:
            print(f"  ✗ {package} is NOT installed")
            missing_packages.append(install_cmd)
    
    if missing_packages:
        print("\n⚠️  Please install missing packages:")
        for cmd in missing_packages:
            print(f"    {cmd}")
        print("\n  Or install all at once:")
        print("    pip install transformers torch sentence-transformers huggingface_hub")
        return False
    
    return True

def main():
    """Main setup function"""
    print("=" * 60)
    print("🚀 YA-PapersWithCode Model Setup")
    print("=" * 60)
    
    # Check requirements
    requirements_ok = check_requirements()
    
    # Create directories
    crawler_dir, selector_dir = create_model_directories()
    
    # Check if models exist on HuggingFace
    available_models = check_huggingface_models()
    
    # Try to download models if available
    if "sentence-transformers/all-MiniLM-L6-v2" in available_models:
        setup_embedding_model()
    
    # Try to download PASA models if available
    models_downloaded = False
    if "bytedance-research/pasa-7b-crawler" in available_models:
        if download_from_huggingface("bytedance-research/pasa-7b-crawler", crawler_dir):
            models_downloaded = True
    
    if "bytedance-research/pasa-7b-selector" in available_models:
        if download_from_huggingface("bytedance-research/pasa-7b-selector", selector_dir):
            models_downloaded = True
    
    # If models weren't downloaded, create mock versions
    if not models_downloaded:
        print("\n📝 Setting up model configurations...")
        print("   Note: PASA-7B models will use mock configurations for development/testing.")
        create_mock_models(crawler_dir, selector_dir)
    else:
        print("\n✅ Real PASA-7B models successfully downloaded!")
    
    # Update agent configuration
    update_agent_config()
    
    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    
    print("\n📌 Next Steps:")
    print("1. If you have access to PASA-7B models:")
    print(f"   - Place pasa-7b-crawler files in: {crawler_dir}")
    print(f"   - Place pasa-7b-selector files in: {selector_dir}")
    print("\n2. For now, the system will work with:")
    print("   - Basic SQL/JSON search (no AI enhancement)")
    print("   - Semantic search using sentence-transformers")
    print("   - Standard filtering and sorting")
    
    if not requirements_ok:
        print("\n⚠️  Remember to install missing packages first!")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
