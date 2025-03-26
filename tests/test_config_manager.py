"""
Tests for the ConfigManager class.
"""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from cicd_tools.utils.config_manager import ConfigManager


def test_config_manager_init():
    """Test ConfigManager initialization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.yaml"
        config_manager = ConfigManager(config_path)
        
        assert config_manager.config_path == config_path
        assert config_manager.config == {}


def test_config_manager_save_load():
    """Test ConfigManager save and load."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a valid project directory structure
        project_dir = Path(temp_dir) / "project"
        project_dir.mkdir()
        
        # Create files to make it a valid project directory
        (project_dir / "setup.py").touch()
        (project_dir / "README.md").touch()
        
        # Create .app_cache directory
        app_cache_dir = project_dir / ".app_cache"
        app_cache_dir.mkdir()
        
        # Create config file
        config_path = app_cache_dir / "config.yaml"
        config_manager = ConfigManager(config_path)
        
        # Set some values
        config_manager.set("key1", "value1")
        config_manager.set("key2", {"nested": "value2"})
        
        # Create a new instance to load from file
        config_manager2 = ConfigManager(config_path)
        
        assert config_manager2.get("key1") == "value1"
        assert config_manager2.get("key2") == {"nested": "value2"}


def test_config_manager_get_default():
    """Test ConfigManager get with default value."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.yaml"
        config_manager = ConfigManager(config_path)
        
        assert config_manager.get("nonexistent") is None
        assert config_manager.get("nonexistent", "default") == "default"


def test_config_manager_delete():
    """Test ConfigManager delete."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a valid project directory structure
        project_dir = Path(temp_dir) / "project"
        project_dir.mkdir()
        
        # Create files to make it a valid project directory
        (project_dir / "setup.py").touch()
        (project_dir / "README.md").touch()
        
        # Create .app_cache directory
        app_cache_dir = project_dir / ".app_cache"
        app_cache_dir.mkdir()
        
        # Create config file
        config_path = app_cache_dir / "config.yaml"
        config_manager = ConfigManager(config_path)
        
        # Set some values
        config_manager.set("key1", "value1")
        config_manager.set("key2", "value2")
        
        assert config_manager.get("key1") == "value1"
        assert config_manager.get("key2") == "value2"
        
        config_manager.delete("key1")
        
        assert config_manager.get("key1") is None
        assert config_manager.get("key2") == "value2"


def test_config_manager_get_all():
    """Test ConfigManager get_all."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a valid project directory structure
        project_dir = Path(temp_dir) / "project"
        project_dir.mkdir()
        
        # Create files to make it a valid project directory
        (project_dir / "setup.py").touch()
        (project_dir / "README.md").touch()
        
        # Create .app_cache directory
        app_cache_dir = project_dir / ".app_cache"
        app_cache_dir.mkdir()
        
        # Create config file
        config_path = app_cache_dir / "config.yaml"
        config_manager = ConfigManager(config_path)
        
        # Set some values
        config_manager.set("key1", "value1")
        config_manager.set("key2", "value2")
        
        assert config_manager.get_all() == {"key1": "value1", "key2": "value2"}


def test_config_manager_clear():
    """Test ConfigManager clear."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a valid project directory structure
        project_dir = Path(temp_dir) / "project"
        project_dir.mkdir()
        
        # Create files to make it a valid project directory
        (project_dir / "setup.py").touch()
        (project_dir / "README.md").touch()
        
        # Create .app_cache directory
        app_cache_dir = project_dir / ".app_cache"
        app_cache_dir.mkdir()
        
        # Create config file
        config_path = app_cache_dir / "config.yaml"
        config_manager = ConfigManager(config_path)
        
        # Set some values
        config_manager.set("key1", "value1")
        config_manager.set("key2", "value2")
        
        assert config_manager.get_all() == {"key1": "value1", "key2": "value2"}
        
        config_manager.clear()
        
        assert config_manager.get_all() == {}


def test_config_manager_get_config():
    """Test ConfigManager get_config."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a valid project directory structure
        project_dir = Path(temp_dir) / "project"
        project_dir.mkdir()
        
        # Create files to make it a valid project directory
        (project_dir / "setup.py").touch()
        (project_dir / "README.md").touch()
        
        config_manager = ConfigManager.get_config(project_dir)
        
        assert config_manager.config_path == project_dir / '.app_cache/config.yaml'


def test_config_manager_get_logger_config():
    """Test ConfigManager get_logger_config method."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a valid project directory structure
        project_dir = Path(temp_dir) / "project"
        project_dir.mkdir()
        
        # Create files to make it a valid project directory
        (project_dir / "setup.py").touch()
        (project_dir / "README.md").touch()
        
        # Create .app_cache directory
        app_cache_dir = project_dir / ".app_cache"
        app_cache_dir.mkdir()
        
        # Create config file
        config_path = app_cache_dir / "config.yaml"
        config_manager = ConfigManager(config_path)
        
        # Set logging configuration without saving (to avoid validation)
        config_manager.config["logging"] = {
            "default": {
                "level": "INFO",
                "handlers": [
                    {
                        "type": "console",
                        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                    }
                ]
            },
            "debug": {
                "level": "DEBUG",
                "handlers": [
                    {
                        "type": "file",
                        "filename": "debug.log"
                    }
                ]
            }
        }
        
        # Get default logger config
        default_config = config_manager.get_logger_config()
        assert default_config["level"] == "INFO"
        assert len(default_config["handlers"]) == 1
        assert default_config["handlers"][0]["type"] == "console"
        
        # Get specific logger config
        debug_config = config_manager.get_logger_config("debug")
        assert debug_config["level"] == "DEBUG"
        assert len(debug_config["handlers"]) == 1
        assert debug_config["handlers"][0]["type"] == "file"
        
        # Get non-existent logger config (should return default)
        nonexistent_config = config_manager.get_logger_config("nonexistent")
        assert nonexistent_config["level"] == "INFO"


def test_config_manager_setup_default_config():
    """Test ConfigManager setup_default_config method."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a valid project directory structure
        project_dir = Path(temp_dir) / "project"
        project_dir.mkdir()
        
        # Create files to make it a valid project directory
        (project_dir / "setup.py").touch()
        (project_dir / "README.md").touch()
        
        # Create .app_cache directory
        app_cache_dir = project_dir / ".app_cache"
        app_cache_dir.mkdir()
        
        # Create config file
        config_path = app_cache_dir / "config.yaml"
        config_manager = ConfigManager(config_path)
        
        # Set up default configuration
        config_manager.setup_default_config()
        
        # Check that default values were set
        assert config_manager.get("console", {}).get("stack_trace") is False
        assert "logging" in config_manager.get_all()
        assert "styling" in config_manager.get_all()
