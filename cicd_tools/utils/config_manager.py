"""
Configuration management for CICD Tools.

This module provides functionality for managing project configuration.
"""

import os
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import yaml


class NotAProjectDirectoryError(Exception):
    """Raised when an operation requires a project directory but the path is not a valid project."""
    pass

CICD_TOOLS_CACHE_FILE = '.app_cache/config.yaml'

class ConfigManager:
    
    """
    Manages project configuration using YAML storage.
    
    This class provides functionality to load, save, and access configuration values.
    """
    
    def __init__(self, config_path: Path):
        """
        Initialize a configuration manager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}                
        self._load_config()
                
    def _load_config(self) -> None:
        """
        Load configuration from YAML file.
        
        If the file doesn't exist, an empty configuration is used.
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f)
                    self.config = loaded_config if loaded_config else {}
            except Exception as e:
                print(f"Error loading configuration: {e}")
                self.config = {}
        
    def save_config(self) -> None:
        """
        Save configuration to YAML file.
        
        Creates parent directories if they don't exist.
        Only saves if the config_path is in a project directory.
        
        Raises:
            NotAProjectDirectoryError: If the directory is not a valid project directory
        """                
        # Check if the directory is a project directory                    
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False)
        except Exception as e:
            print(f"Error saving configuration: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: The configuration key
            default: The default value to return if the key doesn't exist
            
        Returns:
            The configuration value, or the default if the key doesn't exist
        """
        return self.config.get(key, default)
        
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value and save the configuration.
        
        Args:
            key: The configuration key
            value: The configuration value
            
        Raises:
            NotAProjectDirectoryError: If the directory is not a valid project directory
        """
        self.config[key] = value
        self.save_config()
        
    def delete(self, key: str) -> None:
        """
        Delete a configuration value and save the configuration.
        
        Args:
            key: The configuration key
            
        Raises:
            NotAProjectDirectoryError: If the directory is not a valid project directory
        """
        if key in self.config:
            del self.config[key]
            self.save_config()
            
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            A dictionary with all configuration values
        """
        return self.config.copy()
        
    def clear(self) -> None:
        """
        Clear all configuration values and save the configuration.
        
        Raises:
            NotAProjectDirectoryError: If the directory is not a valid project directory
        """
        self.config = {}
        self.save_config()
    
    def get_logger_config(self, name: str = "default") -> Dict[str, Any]:
        """
        Get logger configuration by name.
        
        Args:
            name: Name of the logger configuration to retrieve
            
        Returns:
            Logger configuration dictionary
        """
        logger_configs = self.get("logging", {})
        return logger_configs.get(name, logger_configs.get("default", {}))
    
    def setup_default_config(self) -> None:
        """
        Set up default configuration if not present.
        
        This method adds default values for missing configuration entries.
        
        Raises:
            NotAProjectDirectoryError: If the directory is not a valid project directory
        """
        default_config = {
            "console": {"stack_trace": False},  # Disabled by default
            "logging": {
                "default": {
                    "level": "INFO",
                    "handlers": [
                        {
                            "type": "console",
                            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                        },
                        {
                            "type": "file",
                            "filename": "logs/app.log",
                            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                            "max_bytes": 10485760,  # 10MB
                            "backup_count": 3
                        }
                    ]
                }
            },
            "styling": {
                "colors": {
                    "primary": "#007BFF",
                    "secondary": "#6C757D",
                    "success": "#28A745",
                    "warning": "#FFC107",
                    "error": "#DC3545"
                },
                "formatting": {
                    "title_style": "bold underline",
                    "menu_item_style": "italic"
                }
            }
        }
        
        # Only set defaults for keys that don't exist
        for key, value in default_config.items():
            if key not in self.config:
                self.config[key] = value
            elif isinstance(self.config[key], dict) and isinstance(value, dict):
                # Merge nested dictionaries
                for subkey, subvalue in value.items():
                    if subkey not in self.config[key]:
                        self.config[key][subkey] = subvalue
        
        self.save_config()
        
    @staticmethod
    def get_config(config_path: Optional[Path] = None) -> 'ConfigManager':
        """
        Get a configuration manager.
        
        Args:
            config_path: Path to the config directory. If not provided, uses the current directory.
            
        Returns:
            A configuration manager
        """
        if config_path is None:
            config_path = Path(".")
            
        # Always use CICD_TOOLS_CACHE_FILE as the config file path
        config_file_path = config_path / CICD_TOOLS_CACHE_FILE
        config_manager = ConfigManager(config_file_path)
        
        # Set up default configuration if it doesn't exist
        if not config_file_path.exists():
            config_manager.setup_default_config()
            
        return config_manager
