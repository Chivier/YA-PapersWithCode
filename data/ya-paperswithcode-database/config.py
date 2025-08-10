"""
Configuration management for YA-PapersWithCode backend

This module handles loading and validating configuration from environment variables.
"""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Configuration class for backend settings."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        # Deployment mode
        self.deployment_mode = os.getenv("DEPLOYMENT_MODE", "local").lower()
        
        # Local mode settings
        self.model_path = os.getenv("MODEL_PATH", "checkpoints")
        self.device = os.getenv("DEVICE", "cpu")
        self.torch_dtype = os.getenv("TORCH_DTYPE", "float32")
        self.embedding_model = os.getenv(
            "EMBEDDING_MODEL", 
            "sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # API mode settings
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.api_base = os.getenv("API_BASE", "https://api.openai.com/v1")
        self.model_name = os.getenv("MODEL_NAME", "gpt-4o-mini-2025-08-07")
        
        # Service mode settings
        self.pasa_service_url = os.getenv("PASA_SERVICE_URL", "http://localhost:8080")
        self.pasa_api_key = os.getenv("PASA_API_KEY", "")
        
        # Common settings
        self.max_tokens = int(os.getenv("MAX_TOKENS", "512"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        self.timeout = int(os.getenv("TIMEOUT", "30"))
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Database settings
        self.database_path = os.getenv("DATABASE_PATH", "paperswithcode.db")
        
        # API server settings
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        self.cors_origins = os.getenv(
            "CORS_ORIGINS", 
            "http://localhost:5173,http://localhost:3000"
        ).split(",")
        
        # Search settings
        self.enable_agent_search = os.getenv("ENABLE_AGENT_SEARCH", "true").lower() == "true"
        self.similarity_threshold = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
        self.max_search_results = int(os.getenv("MAX_SEARCH_RESULTS", "50"))
        
        # Cache settings
        self.enable_cache = os.getenv("ENABLE_CACHE", "true").lower() == "true"
        self.cache_ttl = int(os.getenv("CACHE_TTL", "3600"))
        
        # Feature flags
        self.enable_fallback = os.getenv("ENABLE_FALLBACK", "true").lower() == "true"
        self.enable_health_checks = os.getenv("ENABLE_HEALTH_CHECKS", "true").lower() == "true"
        self.enable_metrics = os.getenv("ENABLE_METRICS", "false").lower() == "true"
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def validate(self) -> bool:
        """
        Validate configuration based on deployment mode.
        
        Returns:
            bool: True if configuration is valid
        """
        if self.deployment_mode not in ["local", "api", "service"]:
            logger.error(f"Invalid deployment mode: {self.deployment_mode}")
            return False
        
        if self.deployment_mode == "api" and not self.openai_api_key:
            logger.warning("API mode selected but OPENAI_API_KEY not set")
            # Don't fail validation, allow mock mode
        
        if self.deployment_mode == "local":
            # Check if checkpoints directory exists
            checkpoints_path = Path(self.model_path)
            if not checkpoints_path.exists():
                logger.warning(f"Checkpoints directory not found: {checkpoints_path}")
                logger.info("Will use mock models for development")
        
        # Check database
        db_path = Path(self.database_path)
        if not db_path.exists():
            logger.warning(f"Database not found: {db_path}")
            logger.info("Database will be created on first run")
        
        return True
    
    def get_provider_config(self) -> Dict[str, Any]:
        """
        Get configuration for model provider.
        
        Returns:
            Dict: Provider configuration
        """
        from providers import ModelProviderConfig, ProviderType
        
        if self.deployment_mode == "local":
            provider_type = ProviderType.LOCAL
        elif self.deployment_mode == "api":
            provider_type = ProviderType.API
        elif self.deployment_mode == "service":
            provider_type = ProviderType.SERVICE
        else:
            provider_type = ProviderType.LOCAL  # Fallback
        
        config = ModelProviderConfig(provider_type=provider_type)
        
        # Set common parameters
        config.max_tokens = self.max_tokens
        config.temperature = self.temperature
        config.timeout = self.timeout
        
        # Set mode-specific parameters
        if provider_type == ProviderType.LOCAL:
            config.model_path = self.model_path
            config.model_name = "pasa-7b"
            config.extra_params = {
                "device": self.device,
                "torch_dtype": self.torch_dtype,
                "embedding_model": self.embedding_model
            }
        elif provider_type == ProviderType.API:
            config.api_key = self.openai_api_key
            config.api_base = self.api_base
            config.model_name = self.model_name
        elif provider_type == ProviderType.SERVICE:
            config.api_base = self.pasa_service_url
            config.api_key = self.pasa_api_key
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dict: Configuration as dictionary
        """
        return {
            "deployment_mode": self.deployment_mode,
            "database_path": self.database_path,
            "host": self.host,
            "port": self.port,
            "cors_origins": self.cors_origins,
            "enable_agent_search": self.enable_agent_search,
            "enable_fallback": self.enable_fallback,
            "enable_health_checks": self.enable_health_checks,
            "enable_metrics": self.enable_metrics,
            "log_level": self.log_level
        }
    
    def summary(self) -> str:
        """
        Get a summary of the configuration.
        
        Returns:
            str: Configuration summary
        """
        lines = [
            "YA-PapersWithCode Backend Configuration",
            "=" * 40,
            f"Deployment Mode: {self.deployment_mode}",
            f"Database: {self.database_path}",
            f"API Server: {self.host}:{self.port}",
            f"Agent Search: {'Enabled' if self.enable_agent_search else 'Disabled'}",
            f"Fallback Chain: {'Enabled' if self.enable_fallback else 'Disabled'}",
        ]
        
        if self.deployment_mode == "local":
            lines.extend([
                f"Model Path: {self.model_path}",
                f"Device: {self.device}",
                f"Embedding Model: {self.embedding_model}"
            ])
        elif self.deployment_mode == "api":
            lines.extend([
                f"API Base: {self.api_base}",
                f"Model: {self.model_name}",
                f"API Key: {'Configured' if self.openai_api_key else 'Not Set'}"
            ])
        elif self.deployment_mode == "service":
            lines.extend([
                f"Service URL: {self.pasa_service_url}",
                f"Auth: {'Configured' if self.pasa_api_key else 'None'}"
            ])
        
        return "\n".join(lines)


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration instance.
    
    Returns:
        Config: Configuration instance
    """
    global _config
    if _config is None:
        _config = Config()
        if not _config.validate():
            logger.warning("Configuration validation failed, using defaults")
    return _config


def reset_config() -> None:
    """Reset the global configuration instance."""
    global _config
    _config = None
