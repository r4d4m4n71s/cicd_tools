"""
Template utilities for CICD Tools.

This module provides utility functions for template operations.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

import yaml

from cicd_tools.utils.config_manager import ConfigManager


def process_template_variables(
    template_name: str,
    variables: Dict[str, Any],
    templates_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Process template variables with validation and defaults.
    
    Args:
        template_name: Name of the template
        variables: Template variables
        templates_dir: Directory containing templates
        
    Returns:
        Processed template variables
        
    Raises:
        ValueError: If the template doesn't exist
    """
    # Determine templates directory
    if templates_dir is None:
        package_dir = Path(__file__).parent.parent.parent
        templates_dir = package_dir / "project_templates"
        
    template_path = templates_dir / template_name
    
    if not template_path.exists():
        raise ValueError(f"Template '{template_name}' not found")
        
    # Get template configuration
    template_config = _get_template_config(template_path)
    
    # Process variables
    processed_vars = {}
    
    # Add default values for missing variables
    for key, value in template_config.items():
        if isinstance(value, dict) and "default" in value:
            if key not in variables:
                processed_vars[key] = value["default"]
                
    # Add provided variables
    for key, value in variables.items():
        # Validate variable
        if key in template_config and isinstance(template_config[key], dict):
            config = template_config[key]
            
            # Check type
            if "type" in config:
                expected_type = config["type"]
                if expected_type == "str" and not isinstance(value, str):
                    value = str(value)
                elif expected_type == "int" and not isinstance(value, int):
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        value = config.get("default", 0)
                elif expected_type == "bool" and not isinstance(value, bool):
                    if isinstance(value, str):
                        value = value.lower() in ("yes", "true", "t", "1")
                    else:
                        value = bool(value)
                        
            # Check choices
            if "choices" in config and value not in config["choices"]:
                value = config.get("default", config["choices"][0] if config["choices"] else None)
                
        processed_vars[key] = value
        
    return processed_vars


def detect_template_type(project_dir: Path) -> Optional[str]:
    """
    Detect the template type of a project.
    
    Args:
        project_dir: Project directory
        
    Returns:
        Template type or None if not detected
    """
    # Check if the project was created from a template
    config_manager = ConfigManager.get_project_config(project_dir)
    template_config = config_manager.get("template")
    
    if template_config and "name" in template_config:
        return template_config["name"]
        
    # Try to detect based on project structure
    if _is_github_project(project_dir):
        return "github_project"
    elif _is_development_project(project_dir):
        return "development_project"
    elif _is_simple_project(project_dir):
        return "simple_project"
        
    return None


def get_template_info(
    template_name: str,
    templates_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Get information about a template.
    
    Args:
        template_name: Name of the template
        templates_dir: Directory containing templates
        
    Returns:
        Template information
        
    Raises:
        ValueError: If the template doesn't exist
    """
    # Determine templates directory
    if templates_dir is None:
        package_dir = Path(__file__).parent.parent.parent
        templates_dir = package_dir / "project_templates"
        
    template_path = templates_dir / template_name
    
    if not template_path.exists():
        raise ValueError(f"Template '{template_name}' not found")
        
    # Get template configuration
    template_config = _get_template_config(template_path)
    
    # Extract template information
    info = {
        "name": template_name,
        "version": template_config.get("_version", "0.1.0"),
        "description": template_config.get("_description", ""),
        "variables": {}
    }
    
    # Extract variable information
    for key, value in template_config.items():
        if not key.startswith("_") and isinstance(value, dict):
            info["variables"][key] = {
                "description": value.get("help", ""),
                "default": value.get("default", ""),
                "type": value.get("type", "str"),
                "choices": value.get("choices", [])
            }
            
    return info


def _get_template_config(template_path: Path) -> Dict[str, Any]:
    """
    Get the configuration of a template.
    
    Args:
        template_path: Path to the template
        
    Returns:
        Template configuration
    """
    copier_yaml_path = template_path / "copier.yml"
    copier_yaml_alt_path = template_path / "copier.yaml"
    
    if copier_yaml_path.exists():
        with open(copier_yaml_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    elif copier_yaml_alt_path.exists():
        with open(copier_yaml_alt_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
            
    return {}


def _is_simple_project(project_dir: Path) -> bool:
    """
    Check if a project is a simple project.
    
    Args:
        project_dir: Project directory
        
    Returns:
        True if the project is a simple project, False otherwise
    """
    # Simple projects typically have a setup.py file
    return (project_dir / "setup.py").exists()


def _is_development_project(project_dir: Path) -> bool:
    """
    Check if a project is a development project.
    
    Args:
        project_dir: Project directory
        
    Returns:
        True if the project is a development project, False otherwise
    """
    # Development projects typically have a pyproject.toml file and a .pre-commit-config.yaml file
    return (
        (project_dir / "pyproject.toml").exists() and
        (project_dir / ".pre-commit-config.yaml").exists()
    )


def _is_github_project(project_dir: Path) -> bool:
    """
    Check if a project is a GitHub project.
    
    Args:
        project_dir: Project directory
        
    Returns:
        True if the project is a GitHub project, False otherwise
    """
    # GitHub projects typically have a .github directory
    return (project_dir / ".github").is_dir()