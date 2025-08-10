"""
Provider Factory for Model Providers

This module provides factory functions to create and manage model providers.
"""

import os
import logging
from typing import Optional
from .base import BaseModelProvider, ModelProviderConfig, ProviderType
from .local import LocalModelProvider
from .api import APIModelProvider
from .service import ServiceModelProvider

logger = logging.getLogger(__name__)


def get_provider(
    provider_type: Optional[ProviderType] = None,
    config: Optional[ModelProviderConfig] = None
) -> BaseModelProvider:
    """
    Get a model provider instance based on type and configuration.
    
    Args:
        provider_type: Type of provider to create
        config: Configuration for the provider
        
    Returns:
        BaseModelProvider: Configured provider instance
    """
    # Auto-detect provider type from environment if not specified
    if provider_type is None:
        provider_type = detect_provider_type()
    
    # Create default config if not provided
    if config is None:
        config = create_default_config(provider_type)
    
    # Create and return the appropriate provider
    if provider_type == ProviderType.LOCAL:
        return LocalModelProvider(config)
    elif provider_type == ProviderType.API:
        return APIModelProvider(config)
    elif provider_type == ProviderType.SERVICE:
        return ServiceModelProvider(config)
    else:
        logger.warning(f"Unknown provider type: {provider_type}, falling back to LOCAL")
        return LocalModelProvider(config)


def detect_provider_type() -> ProviderType:
    """
    Detect the provider type from environment variables.
    
    Returns:
        ProviderType: Detected provider type
    """
    # Check environment variables
    deployment_mode = os.getenv("DEPLOYMENT_MODE", "").lower()
    
    if deployment_mode == "local":
        return ProviderType.LOCAL
    elif deployment_mode == "api":
        return ProviderType.API
    elif deployment_mode == "service":
        return ProviderType.SERVICE
    
    # Check for API keys
    if os.getenv("OPENAI_API_KEY"):
        logger.info("OpenAI API key detected, using API provider")
        return ProviderType.API
    
    if os.getenv("PASA_SERVICE_URL"):
        logger.info("PASA service URL detected, using service provider")
        return ProviderType.SERVICE
    
    # Default to local
    logger.info("No specific configuration detected, using local provider")
    return ProviderType.LOCAL


def create_default_config(provider_type: ProviderType) -> ModelProviderConfig:
    """
    Create default configuration based on provider type.
    
    Args:
        provider_type: Type of provider
        
    Returns:
        ModelProviderConfig: Default configuration
    """
    config = ModelProviderConfig(provider_type=provider_type)
    
    if provider_type == ProviderType.LOCAL:
        config.model_path = os.getenv("MODEL_PATH", "checkpoints")
        config.model_name = os.getenv("MODEL_NAME", "pasa-7b")
        config.extra_params = {
            "device": os.getenv("DEVICE", "cpu"),
            "torch_dtype": os.getenv("TORCH_DTYPE", "float32"),
            "embedding_model": os.getenv(
                "EMBEDDING_MODEL", 
                "sentence-transformers/all-MiniLM-L6-v2"
            )
        }
    
    elif provider_type == ProviderType.API:
        config.api_key = os.getenv("OPENAI_API_KEY", "")
        config.api_base = os.getenv("API_BASE", "https://api.openai.com/v1")
        config.model_name = os.getenv("MODEL_NAME", "gpt-4o-mini-2025-08-07")
    
    elif provider_type == ProviderType.SERVICE:
        config.api_base = os.getenv("PASA_SERVICE_URL", "http://localhost:8080")
        config.api_key = os.getenv("PASA_API_KEY", "")
    
    # Common settings
    config.max_tokens = int(os.getenv("MAX_TOKENS", "512"))
    config.temperature = float(os.getenv("TEMPERATURE", "0.7"))
    config.timeout = int(os.getenv("TIMEOUT", "30"))
    
    return config


def get_provider_from_env() -> BaseModelProvider:
    """
    Create a provider using environment variables for configuration.
    
    Returns:
        BaseModelProvider: Configured provider instance
    """
    provider_type = detect_provider_type()
    config = create_default_config(provider_type)
    return get_provider(provider_type, config)


# Singleton instance management
_current_provider: Optional[BaseModelProvider] = None


def get_current_provider() -> BaseModelProvider:
    """
    Get the current global provider instance.
    
    Returns:
        BaseModelProvider: Current provider instance
    """
    global _current_provider
    if _current_provider is None:
        _current_provider = get_provider_from_env()
    return _current_provider


def set_current_provider(provider: BaseModelProvider) -> None:
    """
    Set the current global provider instance.
    
    Args:
        provider: Provider instance to set as current
    """
    global _current_provider
    _current_provider = provider


async def cleanup_provider() -> None:
    """
    Clean up the current provider instance.
    """
    global _current_provider
    if _current_provider:
        await _current_provider.cleanup()
        _current_provider = None
