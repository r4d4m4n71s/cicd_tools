"""
Create menu for CICD Tools.

This module provides the CreateMenu class for project creation and updates.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List

from cicd_tools.menus.menu_utils import Menu, MenuAction, confirm_action, ask_for_input, ask_for_selection
from cicd_tools.templates.template_manager import TemplateManager
from cicd_tools.templates.template_utils import get_template_info
from cicd_tools.utils.config_manager import ConfigManager
from cicd_tools.utils.jinja_utils import evaluate_jinja_expression
class CreateMenu:
    """
    Menu for project creation and updates.
    
    This class provides functionality to create and update projects using templates.
    """
    
    def __init__(self):
        """Initialize a create menu."""
        self.template_manager = TemplateManager()
        
    def show_menu(self, directory: Path) -> None:
        """
        Show the create menu.
        
        Args:
            directory: Directory where the project will be created
        """
        # Loop until user chooses to exit
        while True:
            menu = Menu("Create Menu")
                    
            if self.template_manager.is_project_from_template(directory):
                menu.add_action(MenuAction(
                    "Update Project",
                    "Update the existing project using its proper template",
                    self._update_project,
                    directory=directory,
                    pause_after_execution=True,  # Pause after execution to show output
                    redirect="AppMenu"  # Redirect to the app menu after project creation
                ))
                menu.add_action(MenuAction(
                    "Create internal project",
                    "Create a new project from a template inside a separated folder",
                    self._create_project,
                    directory=directory,
                    pause_after_execution=True,
                    redirect="AppMenu"  # Redirect to the app menu after project creation
                ))
            else:
                menu.add_action(MenuAction(
                    "Create Project",
                    "Create a new project from a template",
                    self._create_project,
                    directory=directory,
                    pause_after_execution=True,
                    redirect="AppMenu"  # Redirect to the app menu after project creation
                ))

            menu.add_action(MenuAction(
                "List Templates",
                "List available templates",
                self._list_templates,
                pause_after_execution=True  # Pause needed as this shows output
            ))
            
            # Display the menu and get the result
            result = menu.display()
            
            # If the user selected "Back/Exit" or an action returned a redirect to exit, break the loop
            if result.get_redirect() == "back":
                break
            elif result.get_redirect() == "exit":
                break
            elif result.get_redirect() == "AppMenu":
                # If the result is a Path object, redirect to the AppMenu for that project
                if isinstance(result.get_result(), Path):
                    from cicd_tools.menus.app_menu import AppMenu                    
                    app_menu = AppMenu()
                    app_menu.show_menu(result.get_result())
                break
        
    def _create_project(self, directory: Path) -> None:
        """
        Create a new project from a template.
        
        Args:
            directory: Directory where the project will be created
        """
        # Get available templates
        templates = self.template_manager.list_templates()
        
        if not templates:
            print("No templates available")
            return
            
        # Select template
        template_name = ask_for_selection(
            "Select a template:",
            templates
        )
        
        if not template_name:
            return
            
        # Get project name
        project_name = ask_for_input("Enter project name:")
        
        if not project_name:
            return
            
        # Replace spaces with underscores in project name
        project_name_safe = project_name.replace(" ", "_")
            
        # Get project directory
        project_dir = directory / project_name_safe
        
        if project_dir.exists():
            if not confirm_action(f"Project directory {project_dir} already exists. Overwrite?"):
                return
                
        try:
            # Initialize project info with project name
            project_info = {"project_name": project_name_safe}
            
            # Create the project
            self.template_manager.create_project(
                template_name,
                project_dir,
                **project_info
            )
            
            print(f"Project created successfully at {project_dir}")
            
            # Return the project directory so it can be used for redirection
            return project_dir
            
        except Exception as e:
            print(f"Failed to create project: {e}")

    def _ask_questions(self, template_info: Dict[str, Any], project_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ask questions based on template variables with conditional logic.
        
        Args:
            template_info: Template information
            project_info: Project information with default values
            
        Returns:
            Dictionary of variable names and values
        """
        variables = {}
        
        for var_name, var_info in template_info["variables"].items():
            if var_name == "project_name":
                variables[var_name] = project_info[var_name]
                continue
            
            default_value = var_info.get("default")            
            # Evaluate the default value if it's a Jinja expression
            if isinstance(default_value, str) and "{{" in default_value and "}}" in default_value:
                default_value = evaluate_jinja_expression(default_value, variables, project_info)
            else:
                # Get default value from project_info or template default
                default_value = project_info.get(var_name, var_info["default"])

            # Check if the variable has a "when" condition
            if var_info.get("when"):
                # Evaluate the condition using the jinja_utils function
                condition_result = evaluate_jinja_expression(var_info["when"], variables, project_info)
                
                # If the condition is false, skip this question
                if not condition_result:
                    # Skip this question and use the default value
                    if var_name in project_info:
                        variables[var_name] = project_info[var_name]
                    else:
                        # Evaluate the default value if it's a Jinja expression
                        default_value = var_info["default"]
                        if isinstance(default_value, str) and "{{" in default_value and "}}" in default_value:
                            default_value = evaluate_jinja_expression(default_value, variables, project_info)
                        variables[var_name] = default_value
                    continue
            
            prompt = f"{var_info['description']}: "
            
            if var_info["choices"]:
                value = ask_for_selection(prompt, var_info["choices"], default_value)
            else:
                value = ask_for_input(prompt, default_value)
                
            variables[var_name] = value
            
        return variables
    
    def _update_project(self, directory: Path) -> None:
        """
        Update an existing project using its template.
        
        Args:
            directory: Project directory to update
        """
        try:
            # # Get template and project information
            # template_info = get_template_info(ConfigManager.get_config(directory).get("template", {}).get("name"))
            # project_info = TemplateManager.get_project_defaults(directory)
            
            # # Ask questions and get variable values
            # variables = self._ask_questions(template_info, project_info)
            
            # Update the project
            #self.template_manager.update_project(directory, **variables)

            # Get project name from config
            project_name = ConfigManager.get_config(directory).get("template", {}).get("variables", {}).get("project_name")
            
            # Initialize project info
            project_info = {}
            
            # Only include project_name if it's found in config
            if project_name is not None:
                project_info["project_name"] = project_name

            self.template_manager.update_project(directory, **project_info)

            print(f"Project updated successfully at {directory}")
            
            # Return the directory so it can be used for redirection
            return directory
            
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Failed to update project: {e}")
            
    def _list_templates(self) -> None:
        """
        List available templates.
        """
        templates = self.template_manager.list_templates()
        
        if not templates:
            print("No templates available")
            return
            
        print("Available templates:")
        
        for template in templates:
            try:
                template_info = get_template_info(template)
                print(f"- {template}: {template_info['description']}")
            except Exception:
                print(f"- {template}")
