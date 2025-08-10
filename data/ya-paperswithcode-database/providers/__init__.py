"""
Model Provider System for YA-PapersWithCode

This module provides an abstraction layer for different AI model providers,
allowing flexible deployment options:
- Local PASA models
- API-based models (OpenAI, Claude)
- Remote PASA service
"""

from .base import BaseModelProvider, ModelProviderConfig, ModelType, ProviderType
from .local import LocalModelProvider
from .api import APIModelProvider
from .service import ServiceModelProvider
from .factory import (
    get_provider, 
    get_provider_from_env,
    get_current_provider,
    set_current_provider,
    cleanup_provider
)

__all__ = [
    'BaseModelProvider',
    'ModelProviderConfig',
    'ModelType',
    'ProviderType',
    'LocalModelProvider',
    'APIModelProvider',
    'ServiceModelProvider',
    'get_provider',
    'get_provider_from_env',
    'get_current_provider',
    'set_current_provider',
    'cleanup_provider'
]
