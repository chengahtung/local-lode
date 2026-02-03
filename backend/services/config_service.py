"""
Configuration Manager Service - Handles application configuration
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """
    Manages application configuration.
    Loads/saves configuration from rag_config.json.
    """
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to config file. If None, uses default location.
        """
        self.logger = logging.getLogger(__name__)
        
        if config_file is None:
            # Default to project root / rag_config.json
            project_root = Path(__file__).resolve().parent.parent.parent
            self.config_file = project_root / "rag_config.json"
        else:
            self.config_file = Path(config_file)
        
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                config_text = self.config_file.read_text(encoding="utf-8")
                config = json.loads(config_text)
                self.logger.info(f"Configuration loaded from {self.config_file}")
                return config
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}. Using defaults.")
                return self._get_default_config()
        else:
            self.logger.info("Config file not found. Using defaults.")
            return self._get_default_config()
    
    def save_config(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Save configuration to file.
        
        Args:
            config: Configuration dict to save. If None, saves current config.
        """
        if config is not None:
            self.config = config
        
        try:
            config_text = json.dumps(self.config, indent=2)
            self.config_file.write_text(config_text, encoding="utf-8")
            self.logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            self.logger.exception(f"Failed to save config: {e}")
            raise e
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value and save"""
        self.config[key] = value
        self.save_config()
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values and save"""
        self.config.update(updates)
        self.save_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values"""
        return {
            "kb_folder": "kb",
            "original_kb_folder": "kb",
            "chunk_size": 100000,
            "overlap": 200,
            "batch_size": 64,
            "ingest_docx": False,
            "reranker_keep_loaded": True
        }
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return self.config.copy()


    
    def reset_to_default(self) -> Dict[str, Any]:
        """Reset kb_folder to original_kb_folder."""
        config = self.get_all()
        original_kb = config.get("original_kb_folder", "kb")
        
        self.update({"kb_folder": original_kb})
        return self.get_all()


# Create singleton instance
config_manager = ConfigManager()
