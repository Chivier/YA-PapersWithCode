"""
Local Model Provider for PASA Models

Implements the model provider interface for locally hosted PASA models.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from .base import BaseModelProvider, ModelProviderConfig, ModelType, ProviderType

logger = logging.getLogger(__name__)


class LocalModelProvider(BaseModelProvider):
    """
    Provider for locally hosted PASA models.
    
    This provider loads and runs PASA-7B models directly on the local machine.
    Requires the models to be downloaded and available in the checkpoints directory.
    """
    
    def __init__(self, config: ModelProviderConfig):
        """
        Initialize the local model provider.
        
        Args:
            config: Configuration for the local provider
        """
        super().__init__(config)
        self.checkpoints_dir = Path(config.model_path or "checkpoints")
        extra_params = config.extra_params or {}
        self.device = extra_params.get("device", "cpu")
        self.torch_dtype = extra_params.get("torch_dtype", "float32")
        
    async def initialize(self) -> bool:
        """
        Initialize and load PASA models from local checkpoints.
        
        Returns:
            bool: True if models loaded successfully
        """
        try:
            # Check if transformers is available
            try:
                import torch
                import transformers
                from transformers import AutoModelForCausalLM, AutoTokenizer
            except ImportError as e:
                logger.error(f"Required packages not installed: {e}")
                logger.info("Please install: pip install torch transformers")
                return False
            
            # Load PASA-7B Crawler model
            crawler_path = self.checkpoints_dir / "pasa-7b-crawler"
            if crawler_path.exists():
                try:
                    logger.info(f"Loading PASA-7B Crawler from {crawler_path}")
                    
                    # Check if model files exist
                    config_file = crawler_path / "config.json"
                    if not config_file.exists():
                        logger.warning(f"Model config not found at {config_file}")
                        logger.info("Using mock configuration for development")
                        self._models[ModelType.CRAWLER.value] = None
                    else:
                        # Load the actual model
                        tokenizer = AutoTokenizer.from_pretrained(
                            str(crawler_path),
                            local_files_only=True
                        )
                        model = AutoModelForCausalLM.from_pretrained(
                            str(crawler_path),
                            local_files_only=True,
                            torch_dtype=getattr(torch, self.torch_dtype, torch.float32),
                            device_map=self.device
                        )
                        self._models[ModelType.CRAWLER.value] = {
                            "model": model,
                            "tokenizer": tokenizer
                        }
                        logger.info("PASA-7B Crawler loaded successfully")
                except Exception as e:
                    logger.warning(f"Failed to load PASA-7B Crawler: {e}")
                    self._models[ModelType.CRAWLER.value] = None
            else:
                logger.warning(f"PASA-7B Crawler not found at {crawler_path}")
                
            # Load PASA-7B Selector model
            selector_path = self.checkpoints_dir / "pasa-7b-selector"
            if selector_path.exists():
                try:
                    logger.info(f"Loading PASA-7B Selector from {selector_path}")
                    
                    # Check if model files exist
                    config_file = selector_path / "config.json"
                    if not config_file.exists():
                        logger.warning(f"Model config not found at {config_file}")
                        logger.info("Using mock configuration for development")
                        self._models[ModelType.SELECTOR.value] = None
                    else:
                        # Load the actual model
                        tokenizer = AutoTokenizer.from_pretrained(
                            str(selector_path),
                            local_files_only=True
                        )
                        model = AutoModelForCausalLM.from_pretrained(
                            str(selector_path),
                            local_files_only=True,
                            torch_dtype=getattr(torch, self.torch_dtype, torch.float32),
                            device_map=self.device
                        )
                        self._models[ModelType.SELECTOR.value] = {
                            "model": model,
                            "tokenizer": tokenizer
                        }
                        logger.info("PASA-7B Selector loaded successfully")
                except Exception as e:
                    logger.warning(f"Failed to load PASA-7B Selector: {e}")
                    self._models[ModelType.SELECTOR.value] = None
            else:
                logger.warning(f"PASA-7B Selector not found at {selector_path}")
                
            # Load embedding model (using sentence-transformers)
            try:
                from sentence_transformers import SentenceTransformer
                
                extra_params = self.config.extra_params or {}
                embedding_model_name = extra_params.get(
                    "embedding_model",
                    "sentence-transformers/all-MiniLM-L6-v2"
                )
                
                logger.info(f"Loading embedding model: {embedding_model_name}")
                self._models[ModelType.EMBEDDING.value] = SentenceTransformer(
                    embedding_model_name,
                    device=self.device
                )
                logger.info("Embedding model loaded successfully")
            except ImportError:
                logger.warning("sentence-transformers not installed")
                logger.info("Please install: pip install sentence-transformers")
                self._models[ModelType.EMBEDDING.value] = None
            except Exception as e:
                logger.warning(f"Failed to load embedding model: {e}")
                self._models[ModelType.EMBEDDING.value] = None
                
            self._initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize local model provider: {e}")
            return False
    
    async def generate(
        self,
        prompt: str,
        model_type: ModelType = ModelType.CRAWLER,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        Generate text using PASA models.
        
        Args:
            prompt: Input prompt
            model_type: Type of model to use (CRAWLER or SELECTOR)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional generation parameters
            
        Returns:
            str: Generated text
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            model_data = self._models.get(model_type.value)
            if not model_data:
                # Fallback to mock response for development
                logger.warning(f"Model {model_type.value} not available, using mock response")
                return f"[Mock {model_type.value} response for: {prompt[:50]}...]"
            
            model = model_data["model"]
            tokenizer = model_data["tokenizer"]
            
            # Tokenize input
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
            
            # Generate
            import torch
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=max_tokens or self.config.max_tokens,
                    temperature=temperature or self.config.temperature,
                    do_sample=True,
                    top_p=kwargs.get("top_p", 0.9),
                    pad_token_id=tokenizer.pad_token_id,
                    eos_token_id=tokenizer.eos_token_id
                )
            
            # Decode output
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the input prompt from the output
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
                
            return generated_text
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return await self._handle_fallback("generate", e, prompt, model_type, max_tokens, temperature, **kwargs)
    
    async def embed(
        self,
        text: Union[str, List[str]],
        model_type: ModelType = ModelType.EMBEDDING,
        **kwargs
    ) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings for text.
        
        Args:
            text: Single text or list of texts to embed
            model_type: Type of embedding model to use
            **kwargs: Additional parameters
            
        Returns:
            List of floats for single text, list of lists for multiple texts
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            model = self._models.get(ModelType.EMBEDDING.value)
            if not model:
                # Return mock embeddings for development
                logger.warning("Embedding model not available, using mock embeddings")
                import random
                if isinstance(text, str):
                    return [random.random() for _ in range(384)]  # Mock 384-dim embedding
                else:
                    return [[random.random() for _ in range(384)] for _ in text]
            
            # Generate embeddings
            embeddings = model.encode(text, **kwargs)
            
            # Convert to list format
            if isinstance(text, str):
                return embeddings.tolist()
            else:
                return embeddings.tolist()
                
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return await self._handle_fallback("embed", e, text, model_type, **kwargs)
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health status of the local provider.
        
        Returns:
            Dict containing health status information
        """
        try:
            models_loaded = {
                ModelType.CRAWLER.value: self._models.get(ModelType.CRAWLER.value) is not None,
                ModelType.SELECTOR.value: self._models.get(ModelType.SELECTOR.value) is not None,
                ModelType.EMBEDDING.value: self._models.get(ModelType.EMBEDDING.value) is not None
            }
            
            # Check if at least one model is loaded
            healthy = any(models_loaded.values())
            
            # Get device info
            device_info = {"device": self.device}
            try:
                import torch
                if torch.cuda.is_available():
                    device_info["cuda_available"] = True
                    device_info["cuda_device_count"] = torch.cuda.device_count()
                    if self.device != "cpu":
                        device_info["gpu_name"] = torch.cuda.get_device_name()
                        device_info["gpu_memory"] = {
                            "allocated": torch.cuda.memory_allocated() / 1024**3,
                            "reserved": torch.cuda.memory_reserved() / 1024**3
                        }
                else:
                    device_info["cuda_available"] = False
            except ImportError:
                device_info["torch_available"] = False
            
            return {
                "healthy": healthy,
                "models_loaded": models_loaded,
                "error": None if healthy else "No models loaded",
                "metadata": {
                    "provider": "local",
                    "checkpoints_dir": str(self.checkpoints_dir),
                    **device_info
                }
            }
        except Exception as e:
            return {
                "healthy": False,
                "models_loaded": {},
                "error": str(e),
                "metadata": {"provider": "local"}
            }
    
    async def cleanup(self) -> None:
        """
        Clean up loaded models and free memory.
        """
        try:
            # Clear CUDA cache if using GPU
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
        
        await super().cleanup()
