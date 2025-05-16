"""
Template management for CICD Tools.

This module provides functionality for managing project templates using Copier.
"""

import contextlib
import shutil
import tempfile
from datetime import datetime
from importlib import resources
from importlib.abc import Traversable
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Union

import yaml
from copier import run_copy

from cicd_tools.templates.template_utils import detect_type
from cicd_tools.utils.config_manager import ConfigManager


class Template:
    """
    Represents a project template with name and description.
    
    This class encapsulates information about a template for easier access.
    """
    
    def __init__(self, name: str, description: str = "") -> None:
        """
        Initialize a template.
        
        Args:
            name: Name of the template
            description: Description of the template
            
        """
        self.name = name
        self.description = description
        
    def __repr__(self) -> str:
        """Return a string representation of the template."""
        return f"Template(name='{self.name}', description='{self.description}')"
        
    def __str__(self) -> str:
        """Return a user-friendly string representation of the template."""
        return self.name


@contextlib.contextmanager
def temp_template(template_path: Union[Path, Traversable], processed_answers: Dict[str, Any]) -> Generator[Path, None, None]:
    """
    Context manager for creating a temporary template with default values replaced by processed answers.
    
    Args:
        template_path: Path to the original template
        processed_answers: Processed template variables
        
    Yields:
        Path to the temporary template

    """
    # Create a temporary directory for the modified template
    temp_dir = tempfile.mkdtemp()
    temp_template_path = Path(temp_dir) / template_path.name
    
    try:
        # Copy the original template to the temporary directory
        shutil.copytree(template_path, temp_template_path)
        
        # Update the template configuration with the processed answers as defaults
        for config_name in ["copier.yaml", "copier.yml"]:
            config_path = temp_template_path / config_name
            if config_path.exists():
                with open(config_path, encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                
                # Update default values with processed answers
                for key, value in processed_answers.items():
                    if key in config and isinstance(config[key], dict) and "default" in config[key]:
                        default_value = config[key]["default"]
                        # Skip default values that contain Jinja2 template syntax
                        if not (isinstance(default_value, str) and "{{" in default_value and "}}" in default_value):
                            config[key]["default"] = value
                
                # Write the updated configuration back to the file
                with open(config_path, "w", encoding="utf-8") as f:
                    yaml.dump(config, f, sort_keys=False)
                
                break
        
        yield temp_template_path
    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)

class TemplateManager:
    """
    Manages project templates using Copier.
    
    This class provides functionality to create and update projects using templates.
    """
    
    def __init__(self) -> None:
        """Initialize a template manager using package resources."""
        # Use importlib.resources to access templates
        self.templates_package = "cicd_tools.project_templates"
            
    def list_templates(self) -> List[Template]:
        """
        List available templates.
        
        Returns:
            List of Template objects with name and description

        """
        templates = []
        
        # List templates using importlib.resources, excluding __pycache__ and dot directories
        template_names = [
            d.name for d in resources.files(self.templates_package).iterdir()
            if d.is_dir() and not d.name.startswith(".") and d.name != "__pycache__"
        ]
        
        # Create Template objects with name and description
        for name in template_names:
            try:
                # Use _get_template_path_context to access the template's copier.yaml
                with self._get_template_path_context(name) as template_path:
                    description = ""
                    
                    # Check for both copier.yaml and copier.yml
                    for config_name in ["copier.yaml", "copier.yml"]:
                        config_path = template_path / config_name
                        if config_path.exists():
                            with open(config_path, encoding="utf-8") as f:
                                config = yaml.safe_load(f) or {}
                                # Extract description from _description field
                                description = config.get("_description", "")
                                break
                
                # Create Template object
                template = Template(name, description)
                templates.append(template)
            except Exception as e:
                # If there's an error, just use the name without description
                print(f"Warning: Failed to read description for template '{name}': {e}")
                templates.append(Template(name))
        
        return templates
        
    @contextlib.contextmanager
    def _get_template_path_context(self, template_name: str) -> Generator[Path, None, None]:
        """
        Context manager that provides a filesystem path for a template.

        For package resources, creates a temporary copy that's cleaned up after use.
        
        Args:
            template_name: Name of the template
            
        Yields:
            Path to the template

        """
        # Get the template resource
        template_resource = resources.files(self.templates_package) / template_name
        
        if not template_resource.exists():
            raise ValueError(f"Template '{template_name}' not found")
            
        # Create a temporary copy that tools like Copier can work with
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir) / template_name
        
        try:
            # Copy the template resources to a temporary path
            shutil.copytree(template_resource, temp_path)
            yield temp_path
        finally:
            # Clean up temp dir
            shutil.rmtree(temp_dir)
        
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
        # Check if template exists
        template_resource = resources.files(self.templates_package) / template_name
        
        if not template_resource.exists():
            raise ValueError(f"Template '{template_name}' not found")
            
        # Ensure the destination directory exists
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Use the common method for project creation/update
            self._process_project(
                template_name=template_name,
                project_dir=destination,
                variables=variables,
                is_update=False
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create project: {e}") from e
            
    def is_project_from_template(self, dir: Path) -> Dict[str, Any]:
        """
        Check if a directory is a project created from a template.
        
        Args:
            dir: Directory to check
            
        Returns:
            Template configuration dictionary if the directory is a project from a template,
            otherwise False

        """
        # Check if the directory is a project directory
        if not detect_type(dir):
            return False        

        config_manager = ConfigManager.get_config(dir)     
        template_config = config_manager.get("template")        
        return template_config and "name" in template_config        
    
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
        # Get template configuration
        config_manager = ConfigManager.get_config(project_dir)
        template_config = config_manager.get("template")
        
        if not template_config or "name" not in template_config:
            raise ValueError("Project wasn't created from a template")
        
        template_name = template_config["name"]
        template_resource = resources.files(self.templates_package) / template_name
        
        if not template_resource.exists():
            raise ValueError(f"Template '{template_name}' not found")
        
        try:
            # Use the common method for project creation/update
            self._process_project(
                template_name=template_name,
                project_dir=project_dir,
                variables=variables,
                is_update=True
            )
        except Exception as e:
            raise RuntimeError(f"Failed to update project: {e}") from e
            
    def _process_project(
        self,
        template_name: str,
        project_dir: Path,
        variables: Dict[str, Any],
        is_update: bool
    ) -> None:
        """
        Process project creation and updates.
        
        Args:
            template_name: Name of the template
            project_dir: Destination directory for the project
            variables: Template variables
            is_update: Whether this is an update operation
            
        Raises:
            RuntimeError: If project processing fails

        """
        # Process template variables
        processed_answers = self._process_template_variables(template_name, project_dir, variables)
        
        # Add current year to data
        data = {'current_year': datetime.now().year}
        data = {**variables, **data}
        
        # Use the context manager to get a usable filesystem path
        with self._get_template_path_context(template_name) as template_path:
            # If processed_answers are not empty, create a temporary template with default values replaced
            if processed_answers:
                with temp_template(template_path, processed_answers) as temp_template_path:
                    # Run Copier to create/update the project using the temporary template
                    answers = self._run_copier(temp_template_path, project_dir, data=data)
            else:
                # Run Copier to create/update the project using the original template
                answers = self._run_copier(template_path, project_dir, data=data)
        
        # Merge the user's answers with the processed variables
        merged_vars = {**processed_answers, **answers}
        
        # Save/update template information in project configuration
        config_manager = ConfigManager.get_config(project_dir)
        config_manager.set("template", {
            "name": template_name,
            "version": self._get_template_version(template_name),
            "variables": merged_vars
        })
        
    def _process_template_variables(
        self,
        template_name: str,
        config_path: Optional[Path],
        variables: Dict[str, Any]        
    ) -> Dict[str, Any]:
        """
        Process template variables.
        
        Args:
            template_name: Name of the template
            variables: Template variables
            config_path: Config path to check for existing template variables
            
        Returns:
            Processed template variables

        """
        # Get default variables from template
        defaults = self.get_project_defaults(config_path)
        
        # If no stored template variables in app config then
        # extract defaults from the template configuration
        if not defaults:
            defaults = self._get_template_defaults(template_name)

        # Add current year for templates
        current_year = datetime.now().year
        
        # Merge defaults with provided variables and add current_year
        return {**defaults, **variables, "current_year": current_year}

    @staticmethod    
    def get_project_defaults(config_path: Path) -> Dict[str, Any]:
        """
        Get default variables from a template.
        
        Args:
            template_path: Path to the template
            config_path: config path to check for existing template variables
            
        Returns:
            Default template variables

        """
        defaults = {}
        
        # First, check if there are any stored template variables in the config_manager
        if config_path is not None and config_path.exists():
            try:
                config_manager = ConfigManager.get_config(config_path)
                template_config = config_manager.get("template")
                if template_config and "variables" in template_config:
                    # Use stored template variables as defaults
                    defaults = template_config["variables"]                    
            except Exception as e:
                print(f"Warning: Failed to get stored template variables: {e}")
                    
        return defaults
        
    def _get_template_defaults(self, template_name: str) -> Dict[str, Any]:
        """
        Get default values from a template configuration.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Default template variables

        """
        answers = {}
        
        with self._get_template_path_context(template_name) as template_path:
            # Read the template configuration
            for config_name in ["copier.yaml", "copier.yml"]:
                config_path = template_path / config_name
                if config_path.exists():
                    with open(config_path, encoding="utf-8") as f:
                        config = yaml.safe_load(f)                        
                    # Extract questions from the config
                    for key, value in config.items():
                        if isinstance(value, dict) and "type" in value and not key.startswith("_"):
                            # This is a question, add it to the answers with its default value
                            if "default" in value:
                                default_value = value["default"]
                                # Skip default values that contain Jinja2 template syntax
                                if not (isinstance(default_value, str) and "{{" in default_value and "}}" in default_value):
                                    answers[key] = default_value
                    break
        
        return answers
        
    def _get_template_version(self, template_name: str) -> str:
        """
        Get the version of a template.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template version

        """
        with self._get_template_path_context(template_name) as template_path:
            copier_yaml_path = template_path / "copier.yml"
            copier_yaml_alt_path = template_path / "copier.yaml"
            
            if copier_yaml_path.exists():
                with open(copier_yaml_path, encoding="utf-8") as f:
                    config = yaml.safe_load(f)
            elif copier_yaml_alt_path.exists():
                with open(copier_yaml_alt_path, encoding="utf-8") as f:
                    config = yaml.safe_load(f)
            else:
                return "0.1.0"  # Default version
                
            return config.get("_version", "0.1.0")        
    
    def _run_copier(
        self,
        template_path: Path,
        destination: Optional[Path] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run Copier with the specified command.
        
        This method handles both project creation and updates using Copier.
        For creation, it runs in non-interactive mode with quiet output.
        For updates, it runs in fully interactive mode to allow user input.
        
        Args:
            command: Copier command ('copy' or 'update')
            template_path: Source template path (for 'copy')
            destination: Destination project path (for 'copy') by defaul '.'
            data: data replacement for questions
            
        Raises:
            ValueError: If required parameters are missing or the command is invalid
            RuntimeError: If Copier execution fails
            
        Returns:
            Dict containing the user's answers
            
        """                
        # Prepare data dictionary from processed variables
        data = data or {}
        
        # Define the answers file path
        #answers_file_path = dst_path / "copier-answers.yml"
        
        try:
            # Run Copier using the Python API
            worker = run_copy(
                src_path=str(template_path),
                dst_path=str(destination),
                data=data,
                unsafe=True  # Equivalent to --trust
            )
            
            # Extract answers from the Worker object
            if hasattr(worker, 'answers') and hasattr(worker.answers, 'user'):
                return worker.answers.user            
            else:
                # Fall back to extracting defaults from the template configuration
                if isinstance(template_path, Path) and template_path.name:
                    return self._get_template_defaults(template_path.name)
                return {}
                
        except Exception as e:
            raise RuntimeError(f"Copier execution failed: {str(e)}") from e
