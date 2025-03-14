"""
Tests for the Environment and BaseEnvManager classes.

These tests verify the functionality of the Environment and BaseEnvManager classes
from the python-env-manager library.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

from env_manager import Environment, EnvManager, PackageManager


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
    """Test BaseEnvManager initialization."""
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
    """Test BaseEnvManager create and remove methods."""
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
    """Test BaseEnvManager run method."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a virtual environment
        env_manager = EnvManager(temp_dir, clear=True)
        
        # Run a command
        result = env_manager.get_runner().run("python", "--version", capture_output=True)
        
        # Check that the command was executed successfully
        assert result.returncode == 0
        assert "Python" in result.stdout


@pytest.mark.skipif(
    "GITHUB_ACTIONS" in os.environ,
    reason="Skip virtual environment creation in CI"
)
def test_env_manager_install_pkg():
    """Test BaseEnvManager install_pkg method."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a virtual environment
        env_manager = EnvManager(temp_dir, clear=True)
        
        # Install a package
        packageManager = PackageManager(env_manager.get_runner())
        packageManager.install("pytest")

        # Check that the package was installed
        assert "pytest" in packageManager.list_packages()


@pytest.mark.skipif(
    "GITHUB_ACTIONS" in os.environ,
    reason="Skip virtual environment creation in CI"
)
def test_run_with_progress():
    """Test run method with progress tracking in BaseProject."""
    from cicd_tools.project_types.base_project import BaseProject
    
    class TestProject(BaseProject):
        def get_menus(self):
            return []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test project
        project = TestProject(Path(temp_dir))
        
        # Create .app_cache directory and config.yaml
        app_cache_dir = Path(temp_dir) / ".app_cache"
        app_cache_dir.mkdir()
        
        with open(app_cache_dir / "config.yaml", "w") as f:
            f.write("environment:\n  capture_output: true\n")
        
        # Test run method with progress tracking
        result = project.run("python", "--version")
        
        # Check that the command was executed successfully
        assert result.returncode == 0
        assert "Python" in result.stdout