"""
Base project class for CICD Tools.

This module provides the abstract base class for all project types.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import EnvManager directly from env_manager
from env_manager import EnvManager, ProgressRunner
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
        self._env_manager = None
        
    def get_env_manager(self) -> EnvManager:
        """
        Get or create an environment manager for this project.
        
        Returns:
            An environment manager instance
        """
        if self._env_manager is None:
            # Initialize environment manager with the project path
            self._env_manager = EnvManager(self.project_path)
        return self._env_manager
        
    def run(self, *cmd_args) -> str:
        """
        Run a command with progress tracking.
        
        Args:
            *cmd_args: Command arguments
            
        Returns:
            Command output
        """
        env_manager = self.get_env_manager()
        config_manager = ConfigManager.get_config(self.project_path)
        capture_output = config_manager.get("environment", {}).get("capture_output", True)
        
        if capture_output:
            try:
                # Set inline_output to 10 to show the last 10 lines of output during execution
                return ProgressRunner(inline_output=1).with_env(env_manager).run(*cmd_args)
            except ImportError:
                # Fall back to regular run if progress_runner is not available
                return env_manager.get_runner().run(*cmd_args)
        else:
            # Run directly without progress tracking
            return env_manager.get_runner().run(*cmd_args)
        
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
        env_manager = self.get_env_manager()
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
            self._env_manager = EnvManager()
        elif env_type == 'virtual':
            # Use a virtual environment
            if env_name:
                venv_path = self.project_path / env_name
            else:
                venv_path = self.project_path / '.venv'
            
            # Create the virtual environment if it doesn't exist
            self._env_manager = EnvManager(venv_path, clear=False)