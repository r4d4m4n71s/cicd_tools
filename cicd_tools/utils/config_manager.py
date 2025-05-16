"""
Configuration management for CICD Tools.

This module provides functionality for managing project configuration.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class NotAProjectDirectoryError(Exception):
    """Raised when an operation requires a project directory but the path is not a valid project."""

CICD_TOOLS_CACHE_FILE = '.app_cache/config.yaml'

class ConfigManager:
    """
    Manages project configuration using YAML storage.
    
    This class provides functionality to load, save, and access configuration values.
    """
    
    def __init__(self, config_path: Path) -> None:
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
                with open(self.config_path, encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f)
                    self.config = loaded_config if loaded_config else {}
            except Exception as e:
                print(f"Error loading configuration: {e}")
                self.config = {}

    @staticmethod    
    def is_project_directory(dir_path: Path) -> bool:
        """
        Check if the current directory is a valid project directory.
        
        Returns:
            True if the directory is a valid project directory, False otherwise

        """
        # A project directory is valid if it contains a pyproject.toml, setup.py, 
        # or is explicitly created as a project directory
        has_pyproject = (dir_path / "pyproject.toml").exists()
        has_setup = (dir_path / "setup.py").exists()
                
        return has_pyproject or has_setup
    
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
    
    def validate_config(self) -> List[str]:
        """
        Validate the current configuration.
        
        Returns:
            List of validation error messages, empty if valid

        """
        errors = []
        
        # Validate console section
        if "console" in self.config:
            if not isinstance(self.config["console"], dict):
                errors.append("console section must be a dictionary")
            elif "stack_trace" in self.config["console"]:
                if not isinstance(self.config["console"]["stack_trace"], bool):
                    errors.append("console.stack_trace must be a boolean")
        
        # Validate logging section
        if "logging" in self.config:
            if not isinstance(self.config["logging"], dict):
                errors.append("logging section must be a dictionary")
            if "default" in self.config["logging"]:
                logging_config = self.config["logging"]["default"]
                
                # Check level
                if "level" in logging_config:
                    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                    if logging_config["level"] not in valid_levels:
                        errors.append(
                            f"logging.default.level must be one of {', '.join(valid_levels)}, "
                            f"got {logging_config['level']}"
                        )
                
                # Check handlers
                if "handlers" in logging_config:
                    if not isinstance(logging_config["handlers"], list):
                        errors.append("logging.default.handlers must be a list")
                    else:
                        for i, handler in enumerate(logging_config["handlers"]):
                            if not isinstance(handler, dict):
                                errors.append(f"logging.default.handlers[{i}] must be a dictionary")
                            elif "type" not in handler:
                                errors.append(f"logging.default.handlers[{i}] missing required key 'type'")
                            elif handler["type"] not in ["console", "file"]:
                                errors.append(f"logging.default.handlers[{i}].type must be 'console' or 'file'")
        
        # Validate styling section
        if "styling" in self.config:
            if not isinstance(self.config["styling"], dict):
                errors.append("styling section must be a dictionary")
            
            # Check colors
            if "colors" in self.config["styling"]:
                colors = self.config["styling"]["colors"]
                if not isinstance(colors, dict):
                    errors.append("styling.colors must be a dictionary")
                else:
                    for color_name, color_value in colors.items():
                        # Simple check for hex color format
                        if not isinstance(color_value, str) or not color_value.startswith("#"):
                            errors.append(f"styling.colors.{color_name} must be a hex color code (e.g. #007BFF)")
        
        return errors
        
    def from_environment(self) -> None:
        """
        Update configuration from environment variables.
        
        Environment variables should be prefixed with CICD_TOOLS_.
        For example, CICD_TOOLS_CONSOLE_STACK_TRACE=true.
        """
        import os
        
        for key, value in os.environ.items():
            if key.startswith("CICD_TOOLS_"):
                # Convert CICD_TOOLS_CONSOLE_STACK_TRACE to console.stack_trace
                config_key = key[11:].lower().replace("_", ".")
                
                # Convert string value to appropriate type
                if value.lower() in ("true", "yes", "1"):
                    config_value = True
                elif value.lower() in ("false", "no", "0"):
                    config_value = False
                elif value.isdigit():
                    config_value = int(value)
                else:
                    config_value = value
                
                # Set the configuration value
                self.set(config_key, config_value)
        
    def setup_default_config(self) -> None:
        """
        Set up default configuration if not present.
        
        This method adds default values for missing configuration entries.
        First, it clears any existing configuration to ensure a clean state.
        
        Raises:
            NotAProjectDirectoryError: If the directory is not a valid project directory

        """
        # Clear any existing configuration
        self.config = {}
        
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
        
        # Set all the default configuration values
        self.config = default_config.copy()
        
        # Check for environment variables
        self.from_environment()
        
        # Validate configuration
        errors = self.validate_config()
        if errors:
            print("⚠️ Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
        
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
