"""
Base Model Provider Interface

Defines the abstract interface that all model providers must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
from enum import Enum


class ProviderType(Enum):
    """Types of model providers"""
    LOCAL = "local"       # Local PASA models
    API = "api"          # OpenAI/Claude API
    SERVICE = "service"  # Remote PASA service


class ModelType(Enum):
    """Types of models used in the system"""
    CRAWLER = "crawler"    # For query expansion/refinement
    SELECTOR = "selector"  # For result ranking/selection
    EMBEDDING = "embedding"  # For semantic search


@dataclass
class ModelProviderConfig:
    """Configuration for a model provider"""
    provider_type: ProviderType
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    model_name: Optional[str] = None
    model_path: Optional[str] = None
    service_url: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30
    retry_count: int = 3
    fallback_provider: Optional['ModelProviderConfig'] = None
    extra_params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.extra_params is None:
            self.extra_params = {}


class BaseModelProvider(ABC):
    """
    Abstract base class for all model providers.
    
    This class defines the interface that all model providers must implement,
    ensuring consistent behavior across different deployment modes.
    """
    
    def __init__(self, config: ModelProviderConfig):
        """
        Initialize the model provider with configuration.
        
        Args:
            config: Configuration for the model provider
        """
        self.config = config
        self._models = {}  # Cache for loaded models
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the provider and load necessary models.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model_type: ModelType = ModelType.CRAWLER,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        Generate text using the specified model.
        
        Args:
            prompt: Input prompt for generation
            model_type: Type of model to use
            max_tokens: Maximum tokens to generate (overrides config)
            temperature: Sampling temperature (overrides config)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            str: Generated text
        """
        pass
    
    @abstractmethod
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
            **kwargs: Additional provider-specific parameters
            
        Returns:
            List of floats for single text, list of lists for multiple texts
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health status of the provider.
        
        Returns:
            Dict containing health status information:
            - healthy: bool
            - models_loaded: Dict[str, bool]
            - error: Optional[str]
            - metadata: Dict[str, Any]
        """
        pass
    
    async def cleanup(self) -> None:
        """
        Clean up resources (models, connections, etc).
        Override in subclasses if cleanup is needed.
        """
        self._models.clear()
        self._initialized = False
    
    def get_model_info(self, model_type: ModelType) -> Dict[str, Any]:
        """
        Get information about a specific model.
        
        Args:
            model_type: Type of model to get info for
            
        Returns:
            Dict containing model information
        """
        return {
            "type": model_type.value,
            "loaded": model_type.value in self._models,
            "provider": self.config.provider_type.value,
            "config": {
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature
            }
        }
    
    async def _handle_fallback(
        self,
        operation: str,
        error: Exception,
        *args,
        **kwargs
    ) -> Any:
        """
        Handle fallback to another provider if configured.
        
        Args:
            operation: Name of the operation that failed
            error: The exception that occurred
            *args: Positional arguments for the operation
            **kwargs: Keyword arguments for the operation
            
        Returns:
            Result from fallback provider or raises the original error
        """
        if not self.config.fallback_provider:
            raise error
        
        # Import here to avoid circular dependency
        from .factory import get_provider
        
        fallback = await get_provider(self.config.fallback_provider)
        if not fallback:
            raise error
        
        # Try the operation with the fallback provider
        operation_method = getattr(fallback, operation, None)
        if not operation_method:
            raise error
        
        try:
            return await operation_method(*args, **kwargs)
        except Exception as fallback_error:
            # If fallback also fails, raise the original error
            raise error from fallback_error
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.config.provider_type.value}, initialized={self._initialized})"
