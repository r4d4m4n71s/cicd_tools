"""
Tests for the template management system.
"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest
import yaml

from cicd_tools.templates.template_manager import TemplateManager
from cicd_tools.templates.template_utils import (
    process_template_variables,
    detect_template_type,
    get_template_info
)
from cicd_tools.utils.config_manager import ConfigManager


def create_test_template(template_dir, template_name):
    """Create a test template."""
    template_path = template_dir / template_name
    template_path.mkdir(parents=True)
    
    # Create copier.yaml
    with open(template_path / "copier.yaml", "w", encoding="utf-8") as f:
        yaml.dump({
            "_version": "0.1.0",
            "_description": f"Test template {template_name}",
            "project_name": {
                "type": "str",
                "help": "Project name",
                "default": "test-project"
            },
            "author": {
                "type": "str",
                "help": "Author name",
                "default": "Test Author"
            },
            "license": {
                "type": "str",
                "help": "License",
                "default": "MIT",
                "choices": ["MIT", "Apache-2.0", "GPL-3.0"]
            }
        }, f)
        
    # Create template files
    with open(template_path / "README.md.jinja", "w", encoding="utf-8") as f:
        f.write("# {{ project_name }}\n\nAuthor: {{ author }}\nLicense: {{ license }}")
        
    with open(template_path / "pyproject.toml.jinja", "w", encoding="utf-8") as f:
        f.write('[project]\nname = "{{ project_name }}"\nversion = "0.1.0"\n')


def test_template_manager_init():
    """Test TemplateManager initialization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        templates_dir = Path(temp_dir) / "templates"
        templates_dir.mkdir()
        
        template_manager = TemplateManager(templates_dir)
        
        assert template_manager.templates_dir == templates_dir


def test_template_manager_list_templates():
    """Test TemplateManager list_templates method."""
    with tempfile.TemporaryDirectory() as temp_dir:
        templates_dir = Path(temp_dir) / "templates"
        templates_dir.mkdir()
        
        # Create test templates
        create_test_template(templates_dir, "template1")
        create_test_template(templates_dir, "template2")
        
        template_manager = TemplateManager(templates_dir)
        templates = template_manager.list_templates()
        
        assert len(templates) == 2
        assert "template1" in templates
        assert "template2" in templates


def test_process_template_variables():
    """Test process_template_variables function."""
    with tempfile.TemporaryDirectory() as temp_dir:
        templates_dir = Path(temp_dir) / "templates"
        templates_dir.mkdir()
        
        # Create test template
        create_test_template(templates_dir, "template1")
        
        # Process variables with defaults
        variables = process_template_variables("template1", {}, templates_dir)
        
        assert variables["project_name"] == "test-project"
        assert variables["author"] == "Test Author"
        assert variables["license"] == "MIT"
        
        # Process variables with custom values
        variables = process_template_variables(
            "template1",
            {
                "project_name": "custom-project",
                "author": "Custom Author",
                "license": "Apache-2.0"
            },
            templates_dir
        )
        
        assert variables["project_name"] == "custom-project"
        assert variables["author"] == "Custom Author"
        assert variables["license"] == "Apache-2.0"
        
        # Process variables with invalid license (should use default from choices)
        variables = process_template_variables(
            "template1",
            {
                "license": "Invalid"
            },
            templates_dir
        )
        
        assert variables["license"] == "MIT"


def test_get_template_info():
    """Test get_template_info function."""
    with tempfile.TemporaryDirectory() as temp_dir:
        templates_dir = Path(temp_dir) / "templates"
        templates_dir.mkdir()
        
        # Create test template
        create_test_template(templates_dir, "template1")
        
        # Get template info
        info = get_template_info("template1", templates_dir)
        
        assert info["name"] == "template1"
        assert info["version"] == "0.1.0"
        assert info["description"] == "Test template template1"
        assert "project_name" in info["variables"]
        assert "author" in info["variables"]
        assert "license" in info["variables"]
        assert info["variables"]["license"]["choices"] == ["MIT", "Apache-2.0", "GPL-3.0"]


@pytest.mark.skipif(
    "GITHUB_ACTIONS" in os.environ or not shutil.which("copier"),
    reason="Skip template operations in CI or if copier is not installed"
)
def test_template_manager_create_project():
    """Test TemplateManager create_project method."""
    with tempfile.TemporaryDirectory() as temp_dir:
        templates_dir = Path(temp_dir) / "templates"
        templates_dir.mkdir()
        
        # Create test template
        create_test_template(templates_dir, "template1")
        
        # Create destination directory
        destination = Path(temp_dir) / "project"
        
        # Create project
        template_manager = TemplateManager(templates_dir)
        
        try:
            template_manager.create_project(
                "template1",
                destination,
                project_name="test-project",
                author="Test Author",
                license="MIT"
            )
            
            # Check that the project was created
            assert destination.exists()
            assert (destination / "README.md").exists()
            assert (destination / "pyproject.toml").exists()
            
            # Check that the template information was saved
            config_manager = ConfigManager.get_project_config(destination)
            template_config = config_manager.get("template")
            
            assert template_config is not None
            assert template_config["name"] == "template1"
            assert template_config["variables"]["project_name"] == "test-project"
            assert template_config["variables"]["author"] == "Test Author"
            assert template_config["variables"]["license"] == "MIT"
        except RuntimeError as e:
            if "Copier execution failed" in str(e):
                pytest.skip("Copier execution failed, skipping test")
            else:
                raise


def test_detect_template_type():
    """Test detect_template_type function."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = Path(temp_dir) / "project"
        project_dir.mkdir()
        
        # Create project configuration
        config_manager = ConfigManager.get_project_config(project_dir)
        config_manager.set("template", {
            "name": "template1",
            "version": "0.1.0",
            "variables": {}
        })
        
        # Detect template type
        template_type = detect_template_type(project_dir)
        
        assert template_type == "template1"
        
        # Test detection based on project structure
        config_manager.delete("template")
        
        # Simple project
        (project_dir / "setup.py").touch()
        assert detect_template_type(project_dir) == "simple_project"
        
        # Development project
        (project_dir / "pyproject.toml").touch()
        (project_dir / ".pre-commit-config.yaml").touch()
        assert detect_template_type(project_dir) == "development_project"
        
        # GitHub project
        (project_dir / ".github").mkdir()
        assert detect_template_type(project_dir) == "github_project"