"""
Simple project type for CICD Tools.

This module provides the SimpleProject class, which represents a basic project
with minimal functionality.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional

from cicd_tools.project_types.base_project import BaseProject
from cicd_tools.utils.env_manager import EnvManager


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
        return [
            {
                "name": "Install",
                "description": "Install the project",
                "callback": self.install
            },
            {
                "name": "Test",
                "description": "Run tests",
                "callback": self.test
            },
            {
                "name": "Build",
                "description": "Build the project",
                "callback": self.build
            },
            {
                "name": "Clean",
                "description": "Clean build artifacts",
                "callback": self.clean
            }
        ]
        
    def install(self) -> bool:
        """
        Install the project.
        
        Returns:
            True if installation was successful, False otherwise
        """
        try:
            env_manager = self.get_env_manager()
            env_manager.run("pip", "install", "-e", ".")
            return True
        except Exception as e:
            print(f"Installation failed: {e}")
            return False
            
    def test(self) -> bool:
        """
        Run tests.
        
        Returns:
            True if tests passed, False otherwise
        """
        try:
            env_manager = self.get_env_manager()
            env_manager.run("python", "-m", "unittest", "discover")
            return True
        except Exception as e:
            print(f"Tests failed: {e}")
            return False
            
    def build(self) -> bool:
        """
        Build the project.
        
        Returns:
            True if build was successful, False otherwise
        """
        try:
            env_manager = self.get_env_manager()
            env_manager.run("python", "setup.py", "build")
            return True
        except Exception as e:
            print(f"Build failed: {e}")
            return False
            
    def clean(self) -> bool:
        """
        Clean build artifacts.
        
        Returns:
            True if cleaning was successful, False otherwise
        """
        try:
            # Remove build directory
            build_dir = self.project_path / "build"
            if build_dir.exists():
                import shutil
                shutil.rmtree(build_dir)
                
            # Remove dist directory
            dist_dir = self.project_path / "dist"
            if dist_dir.exists():
                import shutil
                shutil.rmtree(dist_dir)
                
            # Remove egg-info directory
            for egg_info_dir in self.project_path.glob("*.egg-info"):
                import shutil
                shutil.rmtree(egg_info_dir)
                
            return True
        except Exception as e:
            print(f"Cleaning failed: {e}")
            return False