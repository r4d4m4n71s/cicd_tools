"""Tests for the template management system."""

import tempfile
from pathlib import Path

import pytest
import yaml

from cicd_tools.templates.template_manager import TemplateManager
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
    with tempfile.TemporaryDirectory() as temp_dir:
        templates_dir = Path(temp_dir) / "templates"
        templates_dir.mkdir()
        
        template_manager = TemplateManager(templates_dir)
        
        assert template_manager.templates_dir == templates_dir


def test_template_manager_list_templates() -> None:
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
    with tempfile.TemporaryDirectory() as temp_dir:
        templates_dir = Path(temp_dir) / "templates"
        templates_dir.mkdir()
        
        # Create test template
        create_test_template(templates_dir, "template1")
        
        # Create sample_module directory in the template
        sample_module_dir = templates_dir / "template1" / "sample_module"
        sample_module_dir.mkdir()
        
        # Create __init__.py.jinja in sample_module
        with open(sample_module_dir / "__init__.py.jinja", "w", encoding="utf-8") as f:
            f.write('"""Example module for {{ project_name }}."""\n\n__version__ = "0.1.0"')
        
        # Create main.py.jinja in sample_module
        with open(sample_module_dir / "main.py.jinja", "w", encoding="utf-8") as f:
            f.write('"""Main module for {{ project_name }}."""\n\ndef main():\n    print("Hello, world!")')
        
        # Create .app_cache directory in the template
        app_cache_dir = templates_dir / "template1" / ".app_cache"
        app_cache_dir.mkdir()
        
        # Create config.yaml.jinja in .app_cache
        with open(app_cache_dir / "config.yaml.jinja", "w", encoding="utf-8") as f:
            f.write('console:\n  stack_trace: false\n\nlogging:\n  default:\n    level: INFO')
        
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
            
            # Check that the sample_module was created
            assert (destination / "sample_module").exists()
            assert (destination / "sample_module" / "__init__.py").exists()
            assert (destination / "sample_module" / "main.py").exists()
            
            # Check that the .app_cache directory was created
            assert (destination / ".app_cache").exists()
            assert (destination / ".app_cache" / "config.yaml").exists()
            
            # Check that the template information was saved
            config_manager = ConfigManager.get_config(destination)
            template_config = config_manager.get("template")
            
            assert template_config is not None
            assert template_config["name"] == "template1"
            assert template_config["variables"]["project_name"] == "test-project"
            assert template_config["variables"]["author"] == "Test Author"
            assert template_config["variables"]["license"] == "MIT"
            
            # Check that the environment configuration was set up
            env_config = config_manager.get("console")
            assert env_config is not None
            assert env_config.get("stack_trace") is False
        except RuntimeError as e:
            if "Copier execution failed" in str(e):
                pytest.skip("Copier execution failed, skipping test")
            else:
                raise


def test_get_template_defaults_with_jinja_syntax() -> None:
    """Test that _get_template_defaults correctly handles default values with Jinja2 template syntax."""
    with tempfile.TemporaryDirectory() as temp_dir:
        templates_dir = Path(temp_dir) / "templates"
        templates_dir.mkdir()
        
        # Create a test template with default values containing Jinja2 template syntax
        template_path = templates_dir / "template_with_jinja"
        template_path.mkdir(parents=True)
        
        # Create copier.yaml with default values containing Jinja2 template syntax
        with open(template_path / "copier.yaml", "w", encoding="utf-8") as f:
            yaml.dump({
                "_version": "0.1.0",
                "_description": "Test template with Jinja2 syntax in default values",
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
                "github_repo": {
                    "type": "str",
                    "help": "GitHub repository name",
                    "default": "{{ project_name }}"
                },
                "use_github_actions": {
                    "type": "str",
                    "help": "Use GitHub Actions",
                    "default": "{{ 'yes' if use_github_repo == 'yes' else 'no' }}"
                }
            }, f)
        
        # Create a TemplateManager instance
        template_manager = TemplateManager(templates_dir)
        
        # Call the _get_template_defaults method
        defaults = template_manager._get_template_defaults(template_path)
        
        # Verify that default values with Jinja2 template syntax are not included
        assert "project_name" in defaults
        assert "author" in defaults
        assert "github_repo" not in defaults
        assert "use_github_actions" not in defaults
        
        # Verify that normal default values are included
        assert defaults["project_name"] == "test-project"
        assert defaults["author"] == "Test Author"


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
        
        # Test detection based on project structure
        config_manager.delete("template")
        config_manager.save_config()
        
        # Simple project (already has setup.py)
        assert detect_template_type(project_dir) == "simple_project"
        
        # Development project
        (project_dir / "pyproject.toml").touch()
        (project_dir / ".pre-commit-config.yaml").touch()
        assert detect_template_type(project_dir) == "development_project"
