"""
App menu for CICD Tools.

This module provides the AppMenu class for project-specific operations with enhanced styling.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List, Type

from cicd_tools.menus.menu_utils import Menu, MenuAction, confirm_action, ask_for_input, ask_for_selection
from cicd_tools.project_types.base_project import BaseProject
from cicd_tools.project_types.simple_project import SimpleProject
from cicd_tools.project_types.development_project import DevelopmentProject
from cicd_tools.templates.template_utils import detect_template_type
from cicd_tools.utils.config_manager import ConfigManager


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
            print(f"{project_dir} is not a valid project directory")
            return
            
        # Create project instance
        project = project_type(project_dir)
        
        # Check environment configuration
        self._check_environment_config(project)
        
        # Get styling configuration
        config_manager = ConfigManager.get_config(project_dir)
        style_config = config_manager.get("styling", {})
        
        # Create menu with styling
        menu = Menu(f"App Menu - {project_dir.name}", style_config)
        
        # Add environment management action with icon
        menu.add_action(MenuAction(
            "Manage Environment",
            "Manage the project environment",
            self._manage_environment,
            icon="🔧",
            project=project
        ))
        
        # Add project-specific actions with icons
        for action in project.get_menus():
            menu.add_action(MenuAction(
                action["name"],
                action["description"],
                action["callback"],
                icon=action.get("icon")
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
        
        if template_type == "development_project":
            return DevelopmentProject
        elif template_type == "simple_project":
            return SimpleProject
                   
        # Default to simple project
        return None
        
    def _check_environment_config(self, project: BaseProject) -> None:
        """
        Check if the environment is configured for the project.
        
        Args:
            project: Project instance
        """
        # Get project configuration
        config_manager = ConfigManager.get_config(project.project_path)
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
            else:
                # Create new virtual environment
                env_name = ask_for_input("Enter environment name:", ".venv")
                
                print(f"Creating {env_name} ...")                                 
                project.configure_environment("virtual", env_name)                
                
            # Install project
            project.install()
            
    def _manage_environment(self, project: BaseProject) -> None:
        """
        Manage the project environment.
        
        Args:
            project: Project instance
        """
        # Get project configuration
        config_manager = ConfigManager.get_config(project.project_path)
        env_config = config_manager.get("environment")
        
        if env_config is None:
            print("No environment configured")
            return
            
        # Get styling configuration
        style_config = config_manager.get("styling", {})
        
        # Create menu with styling
        menu = Menu("Environment Management", style_config)
        
        if env_config["type"] == "virtual":
            # Add actions for virtual environment with icons
            menu.add_action(MenuAction(
                f"Recreate Environment {Path(env_config["path"]).name}",
                "Recomended in case of files curruption problems or starting from scratch",
                self._recreate_environment,
                icon="🔄",
                project=project,
                config_manager=config_manager
            ))
            
            menu.add_action(MenuAction(
                f"Delete Environment {Path(env_config["path"]).name}",
                "Removing physical environment folders",
                self._delete_environment,
                icon="🗑️",
                project=project,
                config_manager=config_manager
            ))
            
        menu.add_action(MenuAction(
            "Create New Environment",
            "Use for install dependencies and project execution",
            self._create_environment,
            icon="➕",
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

        env_name = Path(env_config["path"]).name
        print(f"Recreating {env_name} ...")            

        try:
            # Get environment manager
            env_manager = project.create_env_manager(env_config["path"])
            
            # Remove environment
            env_manager.remove()
            
            # Create new environment
            project.configure_environment("virtual", env_name)
            
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
            env_manager = project.create_env_manager(env_config["path"])
            
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
        env_name = ask_for_input("Enter environment name:", ".venv")
        
        if not env_name:
            return
        
        print(f"Creating {env_name} ...") 

        try:
                       
            # Configure environment
            project.configure_environment("virtual", env_name)
                        
            # Install project
            project.install()
            
            print("Environment created successfully")
        except Exception as e:
            print(f"Failed to create environment: {e}")
