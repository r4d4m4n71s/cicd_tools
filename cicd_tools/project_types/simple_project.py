"""
Simple project type for CICD Tools.

This module provides the SimpleProject class, which represents a basic project
with minimal functionality.
"""

from pathlib import Path
from typing import Dict, List, Any
from cicd_tools.project_types.base_project import BaseProject


class SimpleProject(BaseProject):
    """
    Simple project type with basic functionality.
    
    This class represents a basic project with minimal functionality,
    including installation and testing.
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize a simple project.
        
        Args:
            project_path: Path to the project directory
        """
        super().__init__(project_path)
        
    def get_menus(self) -> List[Dict[str, Any]]:
        """
        Get the menu actions available for this project type.
        
        Returns:
            A list of menu action dictionaries
        """
        return self.get_common_menu_items()
        
    # All methods are inherited from BaseProject
