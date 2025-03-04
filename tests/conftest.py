"""
Pytest configuration for CICD Tools tests.

This module contains fixtures and configuration for pytest.
"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def project_dir(temp_dir):
    """Create a temporary project directory for tests."""
    project_dir = temp_dir / "test_project"
    project_dir.mkdir()
    yield project_dir


@pytest.fixture
def simple_project_dir(project_dir):
    """Create a temporary simple project directory for tests."""
    # Add files specific to a simple project
    (project_dir / "setup.py").touch()
    (project_dir / "README.md").touch()
    yield project_dir


@pytest.fixture
def development_project_dir(project_dir):
    """Create a temporary development project directory for tests."""
    # Add files specific to a development project
    (project_dir / "pyproject.toml").touch()
    (project_dir / "README.md").touch()
    (project_dir / ".pre-commit-config.yaml").touch()
    yield project_dir


@pytest.fixture
def github_project_dir(project_dir):
    """Create a temporary GitHub project directory for tests."""
    # Add files specific to a GitHub project
    (project_dir / "pyproject.toml").touch()
    (project_dir / "README.md").touch()
    (project_dir / ".github").mkdir()
    (project_dir / ".github" / "workflows").mkdir()
    (project_dir / ".github" / "workflows" / "tests.yml").touch()
    yield project_dir