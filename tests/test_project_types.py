"""
Tests for the project type classes.
"""

import os
import tempfile
from pathlib import Path

import pytest

from cicd_tools.project_types.base_project import BaseProject
from cicd_tools.project_types.simple_project import SimpleProject
from cicd_tools.project_types.development_project import DevelopmentProject
from cicd_tools.project_types.github_project import GitHubProject


class TestBaseProject(BaseProject):
    """Test implementation of BaseProject."""
    
    def get_menus(self):
        """Return menu actions."""
        return [
            {
                "name": "Test Action",
                "description": "Test action description",
                "callback": lambda: True
            }
        ]


def test_base_project_init():
    """Test BaseProject initialization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project = TestBaseProject(Path(temp_dir))
        
        assert project.project_path == Path(temp_dir)
        assert project.env_manager is None


def test_base_project_get_menus():
    """Test BaseProject get_menus method."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project = TestBaseProject(Path(temp_dir))
        
        menus = project.get_menus()
        
        assert len(menus) == 1
        assert menus[0]["name"] == "Test Action"
        assert menus[0]["description"] == "Test action description"
        assert menus[0]["callback"]() is True


def test_simple_project_init():
    """Test SimpleProject initialization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project = SimpleProject(Path(temp_dir))
        
        assert project.project_path == Path(temp_dir)
        assert project.env_manager is None


def test_simple_project_get_menus():
    """Test SimpleProject get_menus method."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project = SimpleProject(Path(temp_dir))
        
        menus = project.get_menus()
        
        assert len(menus) == 4
        assert menus[0]["name"] == "Install"
        assert menus[1]["name"] == "Test"
        assert menus[2]["name"] == "Build"
        assert menus[3]["name"] == "Clean"


def test_development_project_init():
    """Test DevelopmentProject initialization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project = DevelopmentProject(Path(temp_dir))
        
        assert project.project_path == Path(temp_dir)
        assert project.env_manager is None


def test_development_project_get_menus():
    """Test DevelopmentProject get_menus method."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project = DevelopmentProject(Path(temp_dir))
        
        menus = project.get_menus()
        
        assert len(menus) == 6
        assert menus[0]["name"] == "Install"
        assert menus[1]["name"] == "Test"
        assert menus[2]["name"] == "Prehook"
        assert menus[3]["name"] == "Release"
        assert menus[4]["name"] == "Deploy"
        assert menus[5]["name"] == "Clean"


def test_github_project_init():
    """Test GitHubProject initialization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project = GitHubProject(Path(temp_dir))
        
        assert project.project_path == Path(temp_dir)
        assert project.env_manager is None


def test_github_project_get_menus():
    """Test GitHubProject get_menus method."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project = GitHubProject(Path(temp_dir))
        
        menus = project.get_menus()
        
        assert len(menus) == 7
        assert menus[0]["name"] == "Install"
        assert menus[1]["name"] == "Test"
        assert menus[2]["name"] == "Prehook"
        assert menus[3]["name"] == "Clone Repository"
        assert menus[4]["name"] == "Pull Changes"
        assert menus[5]["name"] == "Push Changes"
        assert menus[6]["name"] == "Clean"


@pytest.mark.skipif(
    "GITHUB_ACTIONS" in os.environ,
    reason="Skip project operations in CI"
)
def test_simple_project_clean():
    """Test SimpleProject clean method."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = Path(temp_dir)
        project = SimpleProject(project_dir)
        
        # Create some build artifacts
        build_dir = project_dir / "build"
        build_dir.mkdir()
        
        dist_dir = project_dir / "dist"
        dist_dir.mkdir()
        
        egg_info_dir = project_dir / "project.egg-info"
        egg_info_dir.mkdir()
        
        # Clean the artifacts
        result = project.clean()
        
        # Check that the artifacts were removed
        assert result is True
        assert not build_dir.exists()
        assert not dist_dir.exists()
        assert not egg_info_dir.exists()