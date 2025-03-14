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

# Update path to use .app_cache instead of .cicd_tools_cache
CICD_TOOLS_CACHE_FILE = '.app_cache/config.yaml'
OLD_CACHE_FILE = '.cicd_tools_cache/config.yaml'

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
        
        # Check for migration from old path
        self._check_migration()
        self._load_config()
        
    def _check_migration(self) -> None:
        """
        Check if we need to migrate from old config path to new one.
        """
        # If new config doesn't exist but old one does, migrate
        old_path = self.config_path.parent.parent / OLD_CACHE_FILE
        if not self.config_path.exists() and old_path.exists():
            try:
                # Ensure parent directory exists
                self.config_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy old config to new location
                shutil.copy2(old_path, self.config_path)
                print(f"Migrated configuration from {old_path} to {self.config_path}")
            except Exception as e:
                print(f"Error migrating configuration: {e}")
        
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
        """
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
        """
        self.config[key] = value
        self.save_config()
        
    def delete(self, key: str) -> None:
        """
        Delete a configuration value and save the configuration.
        
        Args:
            key: The configuration key
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
        """
        default_config = {
            "environment": {"capture_output": True},  # Enabled by default
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
    def get_project_config(project_path: Path) -> 'ConfigManager':
        """
        Get a configuration manager for a project.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            A configuration manager for the project
        """
        config_path = project_path / CICD_TOOLS_CACHE_FILE
        config_manager = ConfigManager(config_path)
        
        # Set up default configuration if it doesn't exist
        if not config_path.exists():
            config_manager.setup_default_config()
            
        return config_manager