"""Tests for the template management system."""

import tempfile
from pathlib import Path

import pytest
import yaml

from cicd_tools.templates.template_manager import Template, TemplateManager
from cicd_tools.templates.template_utils import (
    detect_template_type,
    get_template_info,
    process_template_variables,
)
from cicd_tools.utils.config_manager import ConfigManager


def create_test_template(template_dir, template_name) -> None:
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


def test_template_manager_init() -> None:
    """Test TemplateManager initialization."""
    # Create a template manager
    template_manager = TemplateManager()
    
    # Check that it was initialized
    assert template_manager.templates_package == "cicd_tools.project_templates"


def test_template_manager_list_templates() -> None:
    """Test TemplateManager list_templates method."""
    # This test now uses the actual importlib-based template manager
    # which loads templates from the package rather than a directory
    
    # Create a template manager
    template_manager = TemplateManager()
    
    # Get the templates (these will come from cicd_tools.project_templates)
    templates = template_manager.list_templates()
    
    # We should get at least one template
    assert len(templates) > 0
    
    # All items should be Template objects with name and description
    for template in templates:
        assert isinstance(template, Template)
        assert hasattr(template, 'name')
        assert hasattr(template, 'description')
        
        # Print template info for debugging
        print(f"Found template: {template.name} - '{template.description}'")
        
        # Check that descriptions were loaded from copier.yaml files
        if template.name == "development_project":
            assert "ci/cd" in template.description.lower(), \
                f"Expected CI/CD workflows in description, got: '{template.description}'"
        elif template.name == "simple_project":
            assert "basic" in template.description.lower(), \
                f"Expected basic project structure in description, got: '{template.description}'"


def test_process_template_variables() -> None:
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


def test_get_template_info() -> None:
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


def test_template_manager_create_project() -> None:
    """Test TemplateManager create_project method."""
    # Note: TemplateManager no longer supports custom template directories
    # Instead, it only loads templates from the package
    pytest.skip("TemplateManager no longer supports custom template directories")


def test_get_template_defaults_with_jinja_syntax() -> None:
    """Test that _get_template_defaults correctly handles default values with Jinja2 template syntax."""
    # This test needs to be updated to work with the new TemplateManager
    # that only loads templates from the package
    pytest.skip("TemplateManager no longer supports custom template directories")


def test_detect_template_type() -> None:
    """Test detect_template_type function."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = Path(temp_dir) / "project"
        project_dir.mkdir()
        
        # Create files to make it a valid project directory
        (project_dir / "setup.py").touch()
        (project_dir / "README.md").touch()
        
        # Create .app_cache directory for configuration
        app_cache_dir = project_dir / ".app_cache"
        app_cache_dir.mkdir()
        
        # Create project configuration
        config_manager = ConfigManager(app_cache_dir / "config.yaml")
        config_manager.set("template", {
            "name": "template1",
            "version": "0.1.0",
            "variables": {}
        })
        config_manager.save_config()
        
        # Detect template type
        template_type = detect_template_type(project_dir)
        
        assert template_type == "template1"
        
        # Test detection based on project structure using detect_type
        # (not detect_template_type which is meant for templates)
        config_manager.delete("template")
        config_manager.save_config()
        
        # Import detect_type (different from detect_template_type)
        from cicd_tools.templates.template_utils import detect_type
        
        # Simple project (already has setup.py)
        assert detect_type(project_dir) == "simple_project"
        
        # Development project
        (project_dir / "pyproject.toml").touch()
        (project_dir / ".pre-commit-config.yaml").touch()
        assert detect_type(project_dir) == "development_project"
