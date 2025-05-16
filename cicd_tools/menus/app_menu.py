"""
App menu for CICD Tools.

This module provides the AppMenu class for project-specific operations with enhanced styling.
"""

from pathlib import Path
from typing import Optional, Type

from cicd_tools.menus.menu_utils import (
    Menu,
    MenuAction,
    ask_for_input,
    ask_for_selection,
    confirm_action,
)
from cicd_tools.project_types.base_project import BaseProject
from cicd_tools.project_types.development_project import DevelopmentProject
from cicd_tools.project_types.simple_project import SimpleProject
from cicd_tools.templates.template_utils import detect_template_type, detect_type
from cicd_tools.utils.config_manager import ConfigManager


class AppMenu:
    """
    Menu for project-specific operations.
    
    This class provides functionality to work with existing projects.
    """
    
    def __init__(self) -> None:
        """Initialize an app menu."""
        pass
        
    def show_menu(self, project_dir: Path) -> None:
        """
        Show the app menu.
        
        Args:
            project_dir: Project directory to work with

        """
        # Clear the screen before showing the menu
        from rich.console import Console
        Console().clear()
        # Detect project type
        project_type = self._detect_project_type(project_dir)
        
        if project_type is None:
            print(f"{project_dir} is not a valid project directory")
            return
            
        # Create project instance
        project = project_type(project_dir)                
        
        self._configure_new_environment_if_not_exist(project)
        
        # Get styling configuration
        config_manager = ConfigManager.get_config(project_dir)
        style_config = config_manager.get("styling", {})
        
        # Loop until user chooses to exit
        while True:
            # Create menu with styling
            menu = Menu(f"App Menu - {project_dir.name}", style_config)
            
            # If this is not a project from template, add the conversion option as the last menu item
            template_type = detect_template_type(project_dir)
            if not template_type:                
                menu.add_spacer()            
                # Add conversion option as the last menu item (as a highlighted option)
                menu.add_action(MenuAction(
                    f"Convert {project_dir.name} to CI-CD project",
                    "Enable features like testing, git workflows, code analysis and so on",
                    self._convert_to_cicd_project,
                    icon="⭐⭐",  # Use a star icon to highlight importance
                    project_dir=project_dir,
                    pause_after_execution=True,  # Pause needed as this shows output
                ))
                menu.add_spacer() 

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
                    icon=action.get("icon"),
                    pause_after_execution=action.get("pause_after_execution", False)
                ))                                       
                
            # Display the menu and get the result
            result = menu.display()
            
            # If the user selected "Back/Exit" or an action returned a redirect to exit, break the loop
            #if result.get_redirect() in ["back", "exit"]:
            break
        
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
        
        if template_type is None:
            template_type = detect_type(project_dir)
        
        if template_type == "development_project":
            return DevelopmentProject
        elif template_type == "simple_project":
            return SimpleProject
                   
        # Default to simple project
        return None
        
    def _configure_new_environment_if_not_exist(self, project: BaseProject) -> bool:
        """
        Configure a new environment if one doesn't already exist.
        
        Args:
            project: Project instance
            
        Returns:
            True if a new environment was created, False if the environment already existed

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
            
            print("Environment configured successfully")
            
            # Pause to show output
            input("\nPress Enter to continue...")
            
            # Return True to indicate a new environment was created
            return True

        # Return False to indicate the environment already existed
        return False
                
    def _manage_environment(self, project: BaseProject) -> bool:
        """
        Manage the project environment.
        
        Args:
            project: Project instance

        """
        # Get project configuration
        # Configure new environment if it doesn't exist
        # If a new environment was created, we'll exit and let the user restart
        if self._configure_new_environment_if_not_exist(project):
            return True
        
        config_manager = ConfigManager.get_config(project.project_path)
        env_config = config_manager.get("environment")
                   
        # Get styling configuration
        style_config = config_manager.get("styling", {})
        
        # Loop until user chooses to exit
        while True:
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
                    config_manager=config_manager,
                pause_after_execution=True,  # Pause needed as this shows output
                redirect="exit"  # Return to the main AppMenu after execution
                ))
                
                menu.add_action(MenuAction(
                    f"Delete Environment {Path(env_config["path"]).name}",
                    "Removing physical environment folders",
                    self._delete_environment,
                    icon="🗑️",
                    project=project,
                    config_manager=config_manager,
                    pause_after_execution=True,  # Pause needed as this shows output
                redirect="exit"  # Return to the main AppMenu after execution
                ))
                
            menu.add_action(MenuAction(
                "Create New Environment",
                "Used for install dependencies and project execution",
                self._create_environment,
                icon="➕",
                project=project,
                config_manager=config_manager,
                pause_after_execution=True,  # Pause needed as this shows output
                redirect="exit"  # Return to the main AppMenu after execution
            ))
            
            # Display the menu and get the result
            result = menu.display()
            
            # If the user selected "Back/Exit" or an action returned a redirect to exit, break the loop
            if result.get_redirect() in ["back", "exit"]:
                break
        
        # Return True to indicate the app menu should continue
        return True
        
    def _recreate_environment(self, project: BaseProject, config_manager: ConfigManager) -> None:
        """
        Recreate the virtual environment.
        
        Args:
            project: Project instance
            config_manager: Configuration manager

        """
        env_config = config_manager.get("environment")
        
        if env_config is None or env_config["type"] != "virtual":
            # Configure new environment if it doesn't exist
            # If a new environment was created, we'll exit
            if self._configure_new_environment_if_not_exist(project):
                return
            
            # Refresh env_config after configuration
            config_manager = ConfigManager.get_config(project.project_path)
            env_config = config_manager.get("environment")
            
            # If still not configured or not virtual, return
            if env_config is None or env_config["type"] != "virtual":
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
            
            # Refresh env_config after configuration
            config_manager = ConfigManager.get_config(project.project_path)
            env_config = config_manager.get("environment")
            
            # If still not configured or not virtual, return
            if env_config is None or env_config["type"] != "virtual":
                return
            
        if not confirm_action("Are you sure you want to delete the virtual environment?"):
            print("Exiting..")
            # Exit the application
            import sys
            sys.exit(0)
            
        try:
            # Get environment manager
            env_manager = project.create_env_manager(env_config["path"])
            
            # Remove environment
            env_manager.remove()
            
            # Update configuration
            config_manager.delete("environment")
            
            print("Environment deleted successfully")
            
            if not confirm_action("A new environment is required, do you want to create one?"):
                return
            
            # Ensure the user has a environment configured for use
            self._configure_new_environment_if_not_exist(project) 
        except Exception as e:
            print(f"Failed to delete environment: {e}")
            
    def _convert_to_cicd_project(self, project_dir: Path) -> None:
        """
        Convert the current directory to a CI-CD project.
        
        Args:
            project_dir: Directory to convert to CI-CD project

        """
        from cicd_tools.menus.create_menu import CreateMenu
        
        # Create create menu instance
        create_menu = CreateMenu()
        
        # Call the recreate_project method
        result = create_menu._recreate_project(project_dir)
        
        # If conversion was successful and resulted in a project
        if result:
            print(f"Successfully converted {project_dir.name} to a CI-CD project.")
            
            # Show the app menu for the newly converted project
            self.show_menu(project_dir)
            
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
