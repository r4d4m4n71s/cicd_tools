"""
Template management for CICD Tools.

This module provides functionality for managing project templates using Copier.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

import yaml

from cicd_tools.utils.config_manager import ConfigManager


class TemplateManager:
    """
    Manages project templates using Copier.
    
    This class provides functionality to create and update projects using templates.
    """
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Initialize a template manager.
        
        Args:
            templates_dir: Directory containing templates
        """
        if templates_dir is None:
            # Default to the project_templates directory in the package
            package_dir = Path(__file__).parent.parent.parent
            self.templates_dir = package_dir / "project_templates"
        else:
            self.templates_dir = templates_dir
            
    def list_templates(self) -> List[str]:
        """
        List available templates.
        
        Returns:
            List of template names
        """
        if not self.templates_dir.exists():
            return []
            
        return [
            d.name for d in self.templates_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]
        
    def create_project(
        self,
        template_name: str,
        destination: Path,
        **variables: Any
    ) -> None:
        """
        Create a new project from a template.
        
        Args:
            template_name: Name of the template to use
            destination: Destination directory for the project
            **variables: Template variables
            
        Raises:
            ValueError: If the template doesn't exist
            RuntimeError: If project creation fails
        """
        template_path = self.templates_dir / template_name
        
        if not template_path.exists():
            raise ValueError(f"Template '{template_name}' not found")
            
        # Process template variables
        processed_vars = self._process_template_variables(template_name, variables)
        
        # Create the project using Copier
        try:
            # Ensure the destination directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Run Copier to create the project
            self._run_copier("copy", template_path, destination, processed_vars)
            
            # Save template information in project configuration
            config_manager = ConfigManager.get_project_config(destination)
            config_manager.set("template", {
                "name": template_name,
                "version": self._get_template_version(template_path),
                "variables": processed_vars
            })
            
        except Exception as e:
            raise RuntimeError(f"Failed to create project: {e}") from e
            
    def update_project(
        self,
        project_dir: Path,
        **variables: Any
    ) -> None:
        """
        Update an existing project using its template.
        
        Args:
            project_dir: Project directory
            **variables: Template variables to update
            
        Raises:
            ValueError: If the project wasn't created from a template
            RuntimeError: If project update fails
        """
        # Get project configuration
        config_manager = ConfigManager.get_project_config(project_dir)
        template_config = config_manager.get("template")
        
        if not template_config or "name" not in template_config:
            raise ValueError("Project wasn't created from a template")
            
        template_name = template_config["name"]
        template_path = self.templates_dir / template_name
        
        if not template_path.exists():
            raise ValueError(f"Template '{template_name}' not found")
            
        # Merge existing variables with new ones
        existing_vars = template_config.get("variables", {})
        merged_vars = {**existing_vars, **variables}
        
        # Process template variables
        processed_vars = self._process_template_variables(template_name, merged_vars)
        
        # Update the project using Copier
        try:
            # Run Copier to update the project
            self._run_copier("update", project_dir, processed_vars=processed_vars)
            
            # Update template information in project configuration
            config_manager.set("template", {
                "name": template_name,
                "version": self._get_template_version(template_path),
                "variables": processed_vars
            })
            
        except Exception as e:
            raise RuntimeError(f"Failed to update project: {e}") from e
            
    def _process_template_variables(
        self,
        template_name: str,
        variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process template variables.
        
        Args:
            template_name: Name of the template
            variables: Template variables
            
        Returns:
            Processed template variables
        """
        # Get default variables from template
        template_path = self.templates_dir / template_name
        defaults = self._get_template_defaults(template_path)
        
        # Add current year for templates
        current_year = datetime.now().year
        
        # Merge defaults with provided variables and add current_year
        return {**defaults, **variables, "current_year": current_year}
        
    def _get_template_defaults(self, template_path: Path) -> Dict[str, Any]:
        """
        Get default variables from a template.
        
        Args:
            template_path: Path to the template
            
        Returns:
            Default template variables
        """
        copier_yaml_path = template_path / "copier.yml"
        copier_yaml_alt_path = template_path / "copier.yaml"
        
        if copier_yaml_path.exists():
            with open(copier_yaml_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        elif copier_yaml_alt_path.exists():
            with open(copier_yaml_alt_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        else:
            return {}
            
        # Extract default values from questions
        defaults = {}
        for key, value in config.items():
            if isinstance(value, dict) and "default" in value:
                defaults[key] = value["default"]
                
        return defaults
        
    def _get_template_version(self, template_path: Path) -> str:
        """
        Get the version of a template.
        
        Args:
            template_path: Path to the template
            
        Returns:
            Template version
        """
        copier_yaml_path = template_path / "copier.yml"
        copier_yaml_alt_path = template_path / "copier.yaml"
        
        if copier_yaml_path.exists():
            with open(copier_yaml_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        elif copier_yaml_alt_path.exists():
            with open(copier_yaml_alt_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        else:
            return "0.1.0"  # Default version
            
        return config.get("_version", "0.1.0")
        
    def _run_copier(
        self,
        command: str,
        source_or_destination: Path,
        destination: Optional[Path] = None,
        processed_vars: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Run Copier with the specified command.
        
        Args:
            command: Copier command ('copy' or 'update')
            source_or_destination: Source template path (for 'copy') or destination project path (for 'update')
            destination: Destination project path (for 'copy')
            processed_vars: Processed template variables
            
        Raises:
            RuntimeError: If Copier execution fails
        """
        # Build command arguments
        cmd = ["copier", command]
        
        if command == "copy":
            if destination is None:
                raise ValueError("Destination is required for 'copy' command")
            cmd.extend([str(source_or_destination), str(destination)])
        elif command == "update":
            cmd.append(str(source_or_destination))
        else:
            raise ValueError(f"Invalid Copier command: {command}")
            
        # Add variables
        if processed_vars:
            for key, value in processed_vars.items():
                cmd.extend(["--data", f"{key}={value}"])
                
        # Add common options
        cmd.extend(["--force", "--quiet"])
        
        # Run Copier
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Copier execution failed: {e.stderr}") from e