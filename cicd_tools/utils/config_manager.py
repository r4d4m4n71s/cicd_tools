"""
Configuration management for CICD Tools.

This module provides functionality for managing project configuration.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, Union

import yaml


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
        
    @staticmethod
    def get_project_config(project_path: Path) -> 'ConfigManager':
        """
        Get a configuration manager for a project.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            A configuration manager for the project
        """
        config_path = project_path / '.cicd_tools' / 'config.yaml'
        return ConfigManager(config_path)