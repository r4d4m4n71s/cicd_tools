"""
App menu for CICD Tools.

This module provides the AppMenu class for project-specific operations.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Type

import questionary
from questionary import Choice

from cicd_tools.menus.menu_utils import Menu, MenuAction, confirm_action, ask_for_input, ask_for_selection
from cicd_tools.project_types.base_project import BaseProject
from cicd_tools.project_types.simple_project import SimpleProject
from cicd_tools.project_types.development_project import DevelopmentProject
from cicd_tools.project_types.github_project import GitHubProject
from cicd_tools.templates.template_utils import detect_template_type
from cicd_tools.utils.config_manager import ConfigManager
from cicd_tools.utils.env_manager import EnvManager


class AppMenu:
    """
    Menu for project-specific operations.
    
    This class provides functionality to work with existing projects.
    """
    
    def __init__(self):
        """Initialize an app menu."""
        pass
        
    def show_menu(self, project_dir: Path) -> None:
        """
        Show the app menu.
        
        Args:
            project_dir: Project directory to work with
        """
        # Detect project type
        project_type = self._detect_project_type(project_dir)
        
        if project_type is None:
            print(f"Could not detect project type for {project_dir}")
            return
            
        # Create project instance
        project = project_type(project_dir)
        
        # Check environment configuration
        self._check_environment_config(project)
        
        # Create menu
        menu = Menu(f"App Menu - {project_dir.name}")
        
        # Add environment management action
        menu.add_action(MenuAction(
            "Manage Environment",
            "Manage the project environment",
            self._manage_environment,
            project=project
        ))
        
        # Add project-specific actions
        for action in project.get_menus():
            menu.add_action(MenuAction(
                action["name"],
                action["description"],
                action["callback"]
            ))
            
        # Add help action
        menu.add_action(MenuAction(
            "Help",
            "Show help for project operations",
            self._show_help,
            project=project
        ))
        
        menu.display()
        
    def _detect_project_type(self, project_dir: Path) -> Optional[Type[BaseProject]]:
        """
        Detect the project type.
        
        Args:
            project_dir: Project directory
            
        Returns:
            Project type class or None if not detected
        """
        # Check if the project was created from a template
        template_type = detect_template_type(project_dir)
        
        if template_type == "github_project":
            return GitHubProject
        elif template_type == "development_project":
            return DevelopmentProject
        elif template_type == "simple_project":
            return SimpleProject
            
        # Try to detect based on project structure
        if (project_dir / ".github").is_dir():
            return GitHubProject
        elif (project_dir / ".pre-commit-config.yaml").exists():
            return DevelopmentProject
        elif (project_dir / "setup.py").exists():
            return SimpleProject
            
        # Default to simple project
        return SimpleProject
        
    def _check_environment_config(self, project: BaseProject) -> None:
        """
        Check if the environment is configured for the project.
        
        Args:
            project: Project instance
        """
        # Get project configuration
        config_manager = ConfigManager.get_project_config(project.project_path)
        env_config = config_manager.get("environment")
        
        if env_config is None:
            # No environment configured, ask user
            env_type = ask_for_selection(
                "Select environment type:",
                ["Current", "New virtual environment"]
            )
            
            if env_type == "Current":
                # Use current environment
                project.configure_environment("current")
                config_manager.set("environment", {"type": "current"})
            else:
                # Create new virtual environment
                env_name = ask_for_input("Enter environment name:", ".venv")
                project.configure_environment("virtual", env_name)
                config_manager.set("environment", {"type": "virtual", "name": env_name})
                
            # Install project
            project.install()
            
    def _manage_environment(self, project: BaseProject) -> None:
        """
        Manage the project environment.
        
        Args:
            project: Project instance
        """
        # Get project configuration
        config_manager = ConfigManager.get_project_config(project.project_path)
        env_config = config_manager.get("environment")
        
        if env_config is None:
            print("No environment configured")
            return
            
        # Create menu
        menu = Menu("Environment Management")
        
        if env_config["type"] == "virtual":
            # Add actions for virtual environment
            menu.add_action(MenuAction(
                "Recreate Environment",
                "Recreate the virtual environment",
                self._recreate_environment,
                project=project,
                config_manager=config_manager
            ))
            
            menu.add_action(MenuAction(
                "Delete Environment",
                "Delete the virtual environment",
                self._delete_environment,
                project=project,
                config_manager=config_manager
            ))
            
        menu.add_action(MenuAction(
            "Create New Environment",
            "Create a new virtual environment",
            self._create_environment,
            project=project,
            config_manager=config_manager
        ))
        
        menu.display()
        
    def _recreate_environment(self, project: BaseProject, config_manager: ConfigManager) -> None:
        """
        Recreate the virtual environment.
        
        Args:
            project: Project instance
            config_manager: Configuration manager
        """
        env_config = config_manager.get("environment")
        
        if env_config is None or env_config["type"] != "virtual":
            print("No virtual environment configured")
            return
            
        if not confirm_action("Are you sure you want to recreate the virtual environment?"):
            return
            
        try:
            # Get environment manager
            env_manager = project.get_env_manager()
            
            # Remove environment
            env_manager.remove()
            
            # Create new environment
            project.configure_environment("virtual", env_config["name"])
            
            # Install project
            project.install()
            
            print("Environment recreated successfully")
        except Exception as e:
            print(f"Failed to recreate environment: {e}")
            
    def _delete_environment(self, project: BaseProject, config_manager: ConfigManager) -> None:
        """
        Delete the virtual environment.
        
        Args:
            project: Project instance
            config_manager: Configuration manager
        """
        env_config = config_manager.get("environment")
        
        if env_config is None or env_config["type"] != "virtual":
            print("No virtual environment configured")
            return
            
        if not confirm_action("Are you sure you want to delete the virtual environment?"):
            return
            
        try:
            # Get environment manager
            env_manager = project.get_env_manager()
            
            # Remove environment
            env_manager.remove()
            
            # Update configuration
            config_manager.delete("environment")
            
            print("Environment deleted successfully")
        except Exception as e:
            print(f"Failed to delete environment: {e}")
            
    def _create_environment(self, project: BaseProject, config_manager: ConfigManager) -> None:
        """
        Create a new virtual environment.
        
        Args:
            project: Project instance
            config_manager: Configuration manager
        """
        env_name = ask_for_input("Enter environment name:", project.project_path.name)
        
        if not env_name:
            return
            
        try:
            # Configure environment
            project.configure_environment("virtual", env_name)
            
            # Update configuration
            config_manager.set("environment", {"type": "virtual", "name": env_name})
            
            # Install project
            project.install()
            
            print("Environment created successfully")
        except Exception as e:
            print(f"Failed to create environment: {e}")
            
    def _show_help(self, project: BaseProject) -> None:
        """
        Show help for project operations.
        
        Args:
            project: Project instance
        """
        project_type = project.__class__.__name__
        
        print(f"Help for {project_type}:")
        print()
        
        if project_type == "SimpleProject":
            print("Simple Project Operations:")
            print("- Install: Install the project")
            print("- Test: Run tests")
            print("- Build: Build the project")
            print("- Clean: Clean build artifacts")
        elif project_type == "DevelopmentProject":
            print("Development Project Operations:")
            print("- Install: Install the project with development dependencies")
            print("- Test: Run tests")
            print("- Prehook: Configure pre-commit hooks")
            print("- Release: Create a release")
            print("- Deploy: Deploy the project")
            print("- Clean: Clean build artifacts")
        elif project_type == "GitHubProject":
            print("GitHub Project Operations:")
            print("- Install: Install the project with development dependencies")
            print("- Test: Run tests")
            print("- Prehook: Configure pre-commit hooks")
            print("- Clone Repository: Clone a GitHub repository")
            print("- Pull Changes: Pull changes from the remote repository")
            print("- Push Changes: Push changes to the remote repository")
            print("- Clean: Clean build artifacts")
        else:
            print("No help available for this project type")