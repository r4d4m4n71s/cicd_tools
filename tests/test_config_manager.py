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
        config_path = Path(temp_dir) / "config.yaml"
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
        config_path = Path(temp_dir) / "config.yaml"
        config_manager = ConfigManager(config_path)
        
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
        config_path = Path(temp_dir) / "config.yaml"
        config_manager = ConfigManager(config_path)
        
        config_manager.set("key1", "value1")
        config_manager.set("key2", "value2")
        
        assert config_manager.get_all() == {"key1": "value1", "key2": "value2"}


def test_config_manager_clear():
    """Test ConfigManager clear."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.yaml"
        config_manager = ConfigManager(config_path)
        
        config_manager.set("key1", "value1")
        config_manager.set("key2", "value2")
        
        assert config_manager.get_all() == {"key1": "value1", "key2": "value2"}
        
        config_manager.clear()
        
        assert config_manager.get_all() == {}


def test_config_manager_get_project_config():
    """Test ConfigManager get_project_config."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        config_manager = ConfigManager.get_project_config(project_path)
        
        assert config_manager.config_path == project_path / ".cicd_tools" / "config.yaml"