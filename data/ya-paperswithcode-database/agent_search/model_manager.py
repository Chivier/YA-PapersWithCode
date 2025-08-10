"""
Model Manager - Ensures only one model is loaded at a time to prevent GPU OOM
"""
import threading
from typing import Optional, Dict, Any
from .models import Agent
import torch
import gc

class ModelManager:
    """Singleton manager to ensure only one model is loaded at a time"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.current_model = None
        self.current_model_name = None
        self.models = {}  # Cache of model instances (not loaded)
        
    def get_model(self, model_name: str, model_type: str = 'agent') -> Agent:
        """
        Get a model, loading it if necessary and unloading others
        
        Args:
            model_name: Path to the model
            model_type: Type of model ('agent', 'llm')
            
        Returns:
            Loaded model instance
        """
        with self._lock:
            # If we already have this model loaded, return it
            if self.current_model_name == model_name and self.current_model is not None:
                if self.current_model.is_loaded():
                    return self.current_model
            
            # Unload current model if different
            if self.current_model is not None and self.current_model_name != model_name:
                print(f"Swapping models: {self.current_model_name} -> {model_name}")
                self.current_model.unload()
                self.current_model = None
                self.current_model_name = None
                
                # Force cleanup
                torch.cuda.empty_cache()
                gc.collect()
            
            # Get or create model instance
            if model_name not in self.models:
                print(f"Creating new model instance: {model_name}")
                self.models[model_name] = Agent(model_name, auto_load=False)
            
            model = self.models[model_name]
            
            # Load the model
            if not model.is_loaded():
                model.load_model()
            
            self.current_model = model
            self.current_model_name = model_name
            
            return model
    
    def unload_all(self):
        """Unload all models from memory"""
        with self._lock:
            if self.current_model is not None:
                self.current_model.unload()
                self.current_model = None
                self.current_model_name = None
            
            # Also unload any cached models that might be loaded
            for model_name, model in self.models.items():
                if model.is_loaded():
                    model.unload()
            
            torch.cuda.empty_cache()
            gc.collect()
            print("✓ All models unloaded")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of model manager"""
        return {
            'current_model': self.current_model_name,
            'is_loaded': self.current_model is not None and self.current_model.is_loaded(),
            'cached_models': list(self.models.keys())
        }

# Global instance
model_manager = ModelManager()