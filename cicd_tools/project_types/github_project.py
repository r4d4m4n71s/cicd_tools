"""
GitHub project type for CICD Tools.

This module provides the GitHubProject class, which represents a project
with GitHub integration.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import questionary

from cicd_tools.project_types.base_project import BaseProject
from env_manager import PackageManager 
from cicd_tools.templates.template_manager import TemplateManager


class GitHubProject(BaseProject):
    """
    GitHub project type with GitHub integration.
    
    This class represents a project with GitHub integration,
    including installation, testing, pre-commit hooks, and repository cloning.
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize a GitHub project.
        
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
                "description": "Install the project with development dependencies",
                "callback": self.install
            },
            {
                "name": "Test",
                "description": "Run tests",
                "callback": self.test
            },
            {
                "name": "Prehook",
                "description": "Configure pre-commit hooks",
                "callback": self.prehook
            },
            {
                "name": "Clone Repository",
                "description": "Clone a GitHub repository",
                "callback": self.clone_repo
            },
            {
                "name": "Pull Changes",
                "description": "Pull changes from the remote repository",
                "callback": self.pull_changes
            },
            {
                "name": "Push Changes",
                "description": "Push changes to the remote repository",
                "callback": self.push_changes
            },
            {
                "name": "Clean",
                "description": "Clean build artifacts",
                "callback": self.clean
            }
        ]
        
    def install(self) -> bool:
        """
        Install the project with development dependencies.
        
        Returns:
            True if installation was successful, False otherwise
        """
        try:
            self.env_manager.get_runner().run("pip", "install", "-e", ".[dev]", capture_output = False)
            print("Successfully installed.")
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
            # Ask for test options
            test_option = questionary.select(
                "Select test option:",
                choices=[
                    "All tests",
                    "Failed tests only",
                    "With coverage"
                ]
            ).ask()
                        
            if test_option == "All tests":
                self.env_manager.get_runner().run("pytest", "--tb=short", "-v", capture_output = False)
            elif test_option == "Failed tests only":
                self.env_manager.get_runner().run("pytest", "--tb=short", "-v", "--last-failed", capture_output = False)
            elif test_option == "With coverage":
                self.env_manager.get_runner().run("pytest", "--tb=short", "-v", "--cov", capture_output = False)
            
            print("Test finished.")   
            return True
        except Exception as e:
            print(f"Tests failed: {e}")
            return False
            
    def prehook(self, action: Optional[str] = None) -> bool:
        """
        Configure pre-commit hooks.
        
        Args:
            action: Action to perform ('on' or 'off')
            
        Returns:
            True if configuration was successful, False otherwise
        """
        if action is None:
            action = questionary.select(
                "Select pre-commit hook action:",
                choices=["on", "off"]
            ).ask()
            
        try:
            
            # Install pre-commit if needed
            self._install_if_needed("pre-commit")
            
            if action == "on":
                self.env_manager.get_runner().run("pre-commit", "install")
                print("Pre-commit hooks enabled")
            else:
                self.env_manager.get_runner().run("pre-commit", "uninstall")
                print("Pre-commit hooks disabled")
                
            return True
        except Exception as e:
            print(f"Pre-commit hook configuration failed: {e}")
            return False
            
    def clone_repo(self, url: Optional[str] = None) -> bool:
        """
        Clone a GitHub repository.
        
        Args:
            url: URL of the repository to clone
            
        Returns:
            True if cloning was successful, False otherwise
        """
        if url is None:
            url = questionary.text("Enter repository URL:").ask()
            
        try:
            
            # Extract repository name from URL
            repo_name = url.split("/")[-1]
            if repo_name.endswith(".git"):
                repo_name = repo_name[:-4]
                
            # Determine clone destination
            destination = self.project_path / repo_name
            
            # Clone the repository
            self.env_manager.get_runner().run("git", "clone", url, str(destination))
            
            # Update the project with template if needed
            template_name = questionary.select(
                "Select template to apply (or 'None' to skip):",
                choices=["None", "github_project", "development_project", "simple_project"]
            ).ask()
            
            if template_name != "None":
                template_manager = TemplateManager()
                template_manager.update_project(destination, template_name=template_name)
                
            print(f"Repository cloned successfully to {destination}")
            return True
        except Exception as e:
            print(f"Repository cloning failed: {e}")
            return False
            
    def pull_changes(self) -> bool:
        """
        Pull changes from the remote repository.
        
        Returns:
            True if pulling was successful, False otherwise
        """
        try:
            
            # Check if the project is a git repository
            if not (self.project_path / ".git").exists():
                print("Not a git repository")
                return False
                
            # Pull changes
            self.env_manager.get_runner().run("git", "pull")
            
            print("Changes pulled successfully")
            return True
        except Exception as e:
            print(f"Pulling changes failed: {e}")
            return False
            
    def push_changes(self) -> bool:
        """
        Push changes to the remote repository.
        
        Returns:
            True if pushing was successful, False otherwise
        """
        try:\
                    
            # Check if the project is a git repository
            if not (self.project_path / ".git").exists():
                print("Not a git repository")
                return False
                
            # Check if there are changes to commit
            try:
                status = self.env_manager.run("git", "status", "--porcelain", capture_output=True)
                if not status.stdout.strip():
                    print("No changes to commit")
                    return True
            except Exception:
                pass
                
            # Ask for commit message
            commit_message = questionary.text("Enter commit message:").ask()
            
            # Add changes
            self.env_manager.get_runner().run("git", "add", ".")
            
            # Commit changes
            self.env_manager.get_runner().run("git", "commit", "-m", commit_message)
            
            # Push changes
            self.env_manager.get_runner().run("git", "push")
            
            print("Changes pushed successfully")
            return True
        except Exception as e:
            print(f"Pushing changes failed: {e}")
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
                if build_dir.exists():
                   print("Unable to delete build folder.") 
                
            # Remove dist directory
            dist_dir = self.project_path / "dist"
            if dist_dir.exists():
                import shutil
                shutil.rmtree(dist_dir)
                if dist_dir.exists():
                   print("Unable to delete dist folder.") 
                
            # Remove egg-info directory
            for egg_info_dir in self.project_path.glob("*.egg-info"):
                import shutil
                shutil.rmtree(egg_info_dir)
                if egg_info_dir.exists():
                   print("Unable to delete egg-info folder.") 
                
            print("Build artifacts cleaned successfully")
            return True
        except Exception as e:
            print(f"Cleaning failed: {e}")
            return False
            
    def _install_if_needed(self, package: str) -> None:
        """
        Install a package if it's not already installed.
        
        Args:
            package: Package to install
        """        
        try:
            # Check if the package is installed
            self.env_manager.get_runner().run("pip", "show", package, capture_output=True)
        except Exception:
            # Package is not installed, install it
            PackageManager(self.env_manager.get_runner()).install(package)