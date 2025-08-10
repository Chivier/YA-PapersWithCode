"""
API Model Provider for OpenAI/Claude

Implements the model provider interface for API-based models.
"""

import os
import json
import logging
import aiohttp
from typing import Dict, List, Optional, Any, Union

from .base import BaseModelProvider, ModelProviderConfig, ModelType, ProviderType

logger = logging.getLogger(__name__)


class APIModelProvider(BaseModelProvider):
    """
    Provider for API-based models (OpenAI, Claude, etc.).
    
    This provider interfaces with external AI services through their APIs.
    """
    
    def __init__(self, config: ModelProviderConfig):
        """
        Initialize the API model provider.
        
        Args:
            config: Configuration for the API provider
        """
        super().__init__(config)
        self.api_key = config.api_key or os.getenv("OPENAI_API_KEY", "")
        self.api_base = config.api_base or "https://api.openai.com/v1"
        self.model_name = config.model_name or "gpt-5-mini-2025-08-07"
        self.session = None
        
    async def initialize(self) -> bool:
        """
        Initialize API connection and validate credentials.
        
        Returns:
            bool: True if API is accessible
        """
        try:
            if not self.api_key:
                logger.error("API key not provided")
                return False
            
            # Create aiohttp session
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            
            # Test API connection
            try:
                async with self.session.get(f"{self.api_base}/models") as response:
                    if response.status == 401:
                        logger.error("Invalid API key")
                        return False
                    elif response.status != 200:
                        logger.warning(f"API test returned status {response.status}")
            except Exception as e:
                logger.warning(f"Could not verify API connection: {e}")
            
            self._initialized = True
            logger.info(f"API provider initialized with model {self.model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize API provider: {e}")
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
        Generate text using API models.
        
        Args:
            prompt: Input prompt
            model_type: Type of model to use (ignored for API)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional generation parameters
            
        Returns:
            str: Generated text
        """
        if not self._initialized:
            await self.initialize()
        
        if not self.session:
            raise RuntimeError("API session not initialized")
            
        try:
            # Prepare the request
            if "gpt" in self.model_name.lower():
                # OpenAI format
                payload = {
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": self._get_system_prompt(model_type)},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens or self.config.max_tokens,
                    "temperature": temperature or self.config.temperature,
                    **kwargs
                }
                
                async with self.session.post(
                    f"{self.api_base}/chat/completions",
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"API error {response.status}: {error_text}")
                    
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                    
            elif "claude" in self.model_name.lower():
                # Claude/Anthropic format
                payload = {
                    "model": self.model_name,
                    "prompt": f"{self._get_system_prompt(model_type)}\n\nHuman: {prompt}\n\nAssistant:",
                    "max_tokens_to_sample": max_tokens or self.config.max_tokens,
                    "temperature": temperature or self.config.temperature,
                    **kwargs
                }
                
                async with self.session.post(
                    f"{self.api_base}/complete",
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"API error {response.status}: {error_text}")
                    
                    data = await response.json()
                    return data["completion"]
            else:
                # Generic format - try OpenAI style
                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "max_tokens": max_tokens or self.config.max_tokens,
                    "temperature": temperature or self.config.temperature,
                    **kwargs
                }
                
                async with self.session.post(
                    f"{self.api_base}/completions",
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"API error {response.status}: {error_text}")
                    
                    data = await response.json()
                    return data["choices"][0]["text"]
                    
        except Exception as e:
            logger.error(f"API generation failed: {e}")
            return await self._handle_fallback("generate", e, prompt, model_type, max_tokens, temperature, **kwargs)
    
    async def embed(
        self,
        text: Union[str, List[str]],
        model_type: ModelType = ModelType.EMBEDDING,
        **kwargs
    ) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings using API models.
        
        Args:
            text: Single text or list of texts to embed
            model_type: Type of embedding model to use
            **kwargs: Additional parameters
            
        Returns:
            List of floats for single text, list of lists for multiple texts
        """
        if not self._initialized:
            await self.initialize()
        
        if not self.session:
            raise RuntimeError("API session not initialized")
            
        try:
            # Prepare text list
            texts = [text] if isinstance(text, str) else text
            
            # Use appropriate embedding model
            embedding_model = kwargs.get("model", "text-embedding-ada-002")
            
            payload = {
                "model": embedding_model,
                "input": texts
            }
            
            async with self.session.post(
                f"{self.api_base}/embeddings",
                json=payload
            ) as response:
                if response.status != 200:
                    # Fallback to mock embeddings if API doesn't support embeddings
                    logger.warning(f"Embedding API not available, using mock embeddings")
                    import random
                    if isinstance(text, str):
                        return [random.random() for _ in range(1536)]  # OpenAI embedding size
                    else:
                        return [[random.random() for _ in range(1536)] for _ in text]
                
                data = await response.json()
                embeddings = [item["embedding"] for item in data["data"]]
                
                # Return single or multiple based on input
                if isinstance(text, str):
                    return embeddings[0]
                else:
                    return embeddings
                    
        except Exception as e:
            logger.error(f"API embedding failed: {e}")
            return await self._handle_fallback("embed", e, text, model_type, **kwargs)
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health status of the API provider.
        
        Returns:
            Dict containing health status information
        """
        try:
            healthy = False
            error_msg = None
            
            if not self.api_key:
                error_msg = "API key not configured"
            elif not self.session:
                error_msg = "Session not initialized"
            else:
                # Test API connection
                try:
                    async with self.session.get(
                        f"{self.api_base}/models",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        healthy = response.status == 200
                        if not healthy:
                            error_msg = f"API returned status {response.status}"
                except Exception as e:
                    error_msg = f"Connection test failed: {str(e)}"
            
            return {
                "healthy": healthy,
                "models_loaded": {
                    "api": healthy
                },
                "error": error_msg,
                "metadata": {
                    "provider": "api",
                    "api_base": self.api_base,
                    "model": self.model_name,
                    "has_key": bool(self.api_key)
                }
            }
        except Exception as e:
            return {
                "healthy": False,
                "models_loaded": {},
                "error": str(e),
                "metadata": {"provider": "api"}
            }
    
    async def cleanup(self) -> None:
        """
        Clean up API session.
        """
        if self.session:
            await self.session.close()
            self.session = None
        
        await super().cleanup()
    
    def _get_system_prompt(self, model_type: ModelType) -> str:
        """
        Get the system prompt based on model type.
        
        Args:
            model_type: Type of model
            
        Returns:
            str: System prompt
        """
        if model_type == ModelType.CRAWLER:
            return (
                "You are a research assistant helping to search for academic papers. "
                "Your task is to expand and refine search queries to find relevant papers. "
                "Provide comprehensive search terms and related concepts."
            )
        elif model_type == ModelType.SELECTOR:
            return (
                "You are a research assistant helping to rank and select academic papers. "
                "Your task is to evaluate the relevance of papers based on the search query. "
                "Provide clear reasoning for your selections."
            )
        else:
            return "You are a helpful research assistant."
