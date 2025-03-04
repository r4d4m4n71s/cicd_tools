"""
Base project class for CICD Tools.

This module provides the abstract base class for all project types.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional

from cicd_tools.utils.env_manager import EnvManager


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
            # Initialize environment manager
            # This will be implemented when we adapt the env_manager module
            pass
        return self._env_manager
        
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
        # This will be implemented when we adapt the env_manager module
        return {}
        
    def configure_environment(self, env_type: str, env_name: Optional[str] = None) -> None:
        """
        Configure the environment for this project.
        
        Args:
            env_type: Type of environment ('current' or 'virtual')
            env_name: Name of the virtual environment (if env_type is 'virtual')
        """
        # This will be implemented when we adapt the env_manager module
        pass