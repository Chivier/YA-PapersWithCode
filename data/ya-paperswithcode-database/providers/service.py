"""
Service Model Provider for Remote PASA

Implements the model provider interface for remote PASA service.
"""

import os
import json
import logging
import aiohttp
from typing import Dict, List, Optional, Any, Union

from .base import BaseModelProvider, ModelProviderConfig, ModelType, ProviderType

logger = logging.getLogger(__name__)


class ServiceModelProvider(BaseModelProvider):
    """
    Provider for remote PASA service.
    
    This provider connects to a remote PASA service endpoint.
    """
    
    def __init__(self, config: ModelProviderConfig):
        """
        Initialize the service model provider.
        
        Args:
            config: Configuration for the service provider
        """
        super().__init__(config)
        self.service_url = config.api_base or os.getenv("PASA_SERVICE_URL", "http://localhost:8080")
        self.api_key = config.api_key or os.getenv("PASA_API_KEY", "")
        self.session = None
        
    async def initialize(self) -> bool:
        """
        Initialize service connection.
        
        Returns:
            bool: True if service is accessible
        """
        try:
            # Create aiohttp session
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
                
            self.session = aiohttp.ClientSession(headers=headers)
            
            # Test service connection
            try:
                async with self.session.get(
                    f"{self.service_url}/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status != 200:
                        logger.warning(f"Service health check returned status {response.status}")
                        return False
            except Exception as e:
                logger.error(f"Could not connect to PASA service: {e}")
                return False
            
            self._initialized = True
            logger.info(f"Service provider initialized at {self.service_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize service provider: {e}")
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
        Generate text using remote PASA service.
        
        Args:
            prompt: Input prompt
            model_type: Type of model to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional generation parameters
            
        Returns:
            str: Generated text
        """
        if not self._initialized:
            await self.initialize()
        
        if not self.session:
            raise RuntimeError("Service session not initialized")
            
        try:
            payload = {
                "prompt": prompt,
                "model_type": model_type.value,
                "max_tokens": max_tokens or self.config.max_tokens,
                "temperature": temperature or self.config.temperature,
                **kwargs
            }
            
            async with self.session.post(
                f"{self.service_url}/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Service error {response.status}: {error_text}")
                
                data = await response.json()
                return data.get("text", "")
                
        except Exception as e:
            logger.error(f"Service generation failed: {e}")
            return await self._handle_fallback("generate", e, prompt, model_type, max_tokens, temperature, **kwargs)
    
    async def embed(
        self,
        text: Union[str, List[str]],
        model_type: ModelType = ModelType.EMBEDDING,
        **kwargs
    ) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings using remote service.
        
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
            raise RuntimeError("Service session not initialized")
            
        try:
            texts = [text] if isinstance(text, str) else text
            
            payload = {
                "texts": texts,
                "model_type": model_type.value,
                **kwargs
            }
            
            async with self.session.post(
                f"{self.service_url}/embed",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    # Fallback to mock embeddings
                    logger.warning("Service embedding not available, using mock embeddings")
                    import random
                    if isinstance(text, str):
                        return [random.random() for _ in range(384)]
                    else:
                        return [[random.random() for _ in range(384)] for _ in text]
                
                data = await response.json()
                embeddings = data.get("embeddings", [])
                
                # Return single or multiple based on input
                if isinstance(text, str):
                    return embeddings[0] if embeddings else []
                else:
                    return embeddings
                    
        except Exception as e:
            logger.error(f"Service embedding failed: {e}")
            return await self._handle_fallback("embed", e, text, model_type, **kwargs)
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health status of the service provider.
        
        Returns:
            Dict containing health status information
        """
        try:
            healthy = False
            error_msg = None
            models_info = {}
            
            if not self.session:
                error_msg = "Session not initialized"
            else:
                try:
                    async with self.session.get(
                        f"{self.service_url}/health",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        healthy = response.status == 200
                        if healthy:
                            data = await response.json()
                            models_info = data.get("models", {})
                        else:
                            error_msg = f"Service returned status {response.status}"
                except Exception as e:
                    error_msg = f"Health check failed: {str(e)}"
            
            return {
                "healthy": healthy,
                "models_loaded": models_info,
                "error": error_msg,
                "metadata": {
                    "provider": "service",
                    "service_url": self.service_url,
                    "has_auth": bool(self.api_key)
                }
            }
        except Exception as e:
            return {
                "healthy": False,
                "models_loaded": {},
                "error": str(e),
                "metadata": {"provider": "service"}
            }
    
    async def cleanup(self) -> None:
        """
        Clean up service session.
        """
        if self.session:
            await self.session.close()
            self.session = None
        
        await super().cleanup()
