"""
Tests for the Environment and EnvManager classes.

These tests verify the functionality of the Environment and EnvManager classes
which are now using the python-env-manager library.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

from cicd_tools.utils.env_manager import Environment, EnvManager


def test_environment_init():
    """Test Environment initialization."""
    # Test with current environment
    env = Environment()
    
    # Use case-insensitive comparison for Windows paths
    assert env.root.lower() == os.path.abspath(sys.prefix).lower()
    assert env.name == os.path.basename(env.root)
    assert os.path.exists(env.python)
    
    # Test with custom path
    with tempfile.TemporaryDirectory() as temp_dir:
        env = Environment(temp_dir)
        
        # Use case-insensitive comparison for Windows paths
        assert env.root.lower() == os.path.abspath(temp_dir).lower()
        assert env.name == os.path.basename(temp_dir)


def test_env_manager_init():
    """Test EnvManager initialization."""
    # Test with current environment
    env_manager = EnvManager()
    
    # Use case-insensitive comparison for Windows paths
    assert env_manager.env.root.lower() == os.path.abspath(sys.prefix).lower()
    assert env_manager.env.name == os.path.basename(env_manager.env.root)
    
    # Test with custom path
    with tempfile.TemporaryDirectory() as temp_dir:
        env_manager = EnvManager(temp_dir)
        
        # Use case-insensitive comparison for Windows paths
        assert env_manager.env.root.lower() == os.path.abspath(temp_dir).lower()
        assert env_manager.env.name == os.path.basename(temp_dir)


@pytest.mark.skipif(
    "GITHUB_ACTIONS" in os.environ,
    reason="Skip virtual environment creation in CI"
)
def test_env_manager_create_remove():
    """Test EnvManager create and remove methods."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a virtual environment
        env_manager = EnvManager(temp_dir, clear=True)
        
        # Check that the environment was created
        assert os.path.exists(env_manager.env.root)
        assert os.path.exists(env_manager.env.bin)
        assert os.path.exists(env_manager.env.python)
        
        # Remove the environment
        env_manager.remove()
        
        # Check that the environment was removed
        assert not os.path.exists(env_manager.env.bin)


@pytest.mark.skipif(
    "GITHUB_ACTIONS" in os.environ,
    reason="Skip virtual environment creation in CI"
)
def test_env_manager_run():
    """Test EnvManager run method."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a virtual environment
        env_manager = EnvManager(temp_dir, clear=True)
        
        # Run a command
        result = env_manager.run("python", "--version", capture_output=True)
        
        # Check that the command was executed successfully
        assert result.returncode == 0
        assert "Python" in result.stdout


@pytest.mark.skipif(
    "GITHUB_ACTIONS" in os.environ,
    reason="Skip virtual environment creation in CI"
)
def test_env_manager_install_pkg():
    """Test EnvManager install_pkg method."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a virtual environment
        env_manager = EnvManager(temp_dir, clear=True)
        
        # Install a package
        env_manager.install_pkg("pytest")
        
        # Check that the package was installed
        result = env_manager.run("pip", "show", "pytest", capture_output=True)
        
        assert result.returncode == 0
        assert "pytest" in result.stdout