"""
Base project class for CICD Tools.

This module provides the abstract base class for all project types.
"""

from abc import ABC, abstractmethod
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import EnvManager directly from env_manager
from env_manager import EnvManager, ProgressRunner, IRunner
from cicd_tools.utils.config_manager import ConfigManager


class BaseProject(ABC):
    """
    Abstract base class for all project types.
    
    This class defines the interface that all project types must implement.
    It provides common functionality for project operations.
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize a project.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = project_path
        self.env_manager:EnvManager = None
        
    def create_env_manager(self, env_path, clear = False):
         # Initialize environment manager with the project path
        env_manager = EnvManager(env_path, clear)
        # Replace it with our custom method
        env_manager.get_runner = lambda: self._custom_runner()
        return env_manager
    
    def _custom_runner(self) -> IRunner:
        """
        Customize runner according to configuration.
        
        Returns:
            A customized runner instance
        """
        config_manager = ConfigManager.get_config(self.project_path)
        capture_output = config_manager.get("console", {}).get("capture_output", True)
        
        if capture_output and self.env_manager is not None:
            # Set inline_output to 1 to show the last line of output during execution
            return ProgressRunner(inline_output=1).with_env(self.env_manager)            
        elif self.env_manager is not None:
            # Use the original get_runner method from the EnvManager instance
            original_get_runner = self.env_manager.__class__.get_runner
            return original_get_runner(self.env_manager)
        else:
            # Return a default runner if _env_manager is not initialized yet
            # This should not happen in normal operation
            return lambda *args, **kwargs: subprocess.run(args, **kwargs)
        
    @abstractmethod
    def get_menus(self) -> List[Dict[str, Any]]:
        """
        Get the menu actions available for this project type.
        
        Returns:
            A list of menu action dictionaries
        """
        pass
        
    def get_env_config(self) -> Dict[str, Any]:
        """
        Get environment configuration for this project.
        
        Returns:
            A dictionary with environment configuration
        """
        env_manager = self.env_manager
        return {
            "name": env_manager.env.name,
            "root": str(env_manager.env.root),
            "is_virtual": env_manager.env.is_virtual,
            "python": str(env_manager.env.python)
        }
        
    def configure_environment(self, env_type: str, env_name: Optional[str] = None) -> None:
        """
        Configure the environment for this project.
        
        Args:
            env_type: Type of environment ('current' or 'virtual')
            env_name: Name of the virtual environment (if env_type is 'virtual')
        """
        if env_type == 'current':
            # Use the current Python environment
            self.env_manager = self.create_env_manager(None)
        elif env_type == 'virtual':
            # Use a virtual environment
            if env_name:
                venv_path = self.project_path / env_name
            else:
                venv_path = self.project_path / '.venv'
            
            # Create the virtual environment if it doesn't exist
            self.env_manager = self.create_env_manager(venv_path)

        config_manager = ConfigManager.get_config(self.project_path)    
        config_manager.set("environment", {"type": env_type, "path": self.env_manager.env.root})    
