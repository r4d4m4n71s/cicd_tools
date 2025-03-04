"""
Create menu for CICD Tools.

This module provides the CreateMenu class for project creation and updates.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List

import questionary
from questionary import Choice

from cicd_tools.menus.menu_utils import Menu, MenuAction, confirm_action, ask_for_input, ask_for_selection
from cicd_tools.templates.template_manager import TemplateManager
from cicd_tools.templates.template_utils import get_template_info, process_template_variables


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
        menu = Menu("Create Menu")
        
        menu.add_action(MenuAction(
            "Create Project",
            "Create a new project from a template",
            self._create_project,
            directory=directory
        ))
        
        menu.add_action(MenuAction(
            "Update Project",
            "Update an existing project using its template",
            self._update_project,
            directory=directory
        ))
        
        menu.add_action(MenuAction(
            "List Templates",
            "List available templates",
            self._list_templates
        ))
        
        menu.display()
        
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
            
        # Get template information
        template_info = get_template_info(template_name)
        
        # Get project name
        project_name = ask_for_input("Enter project name:")
        
        if not project_name:
            return
            
        # Get project directory
        project_dir = directory / project_name
        
        if project_dir.exists():
            if not confirm_action(f"Project directory {project_dir} already exists. Overwrite?"):
                return
                
        # Get template variables
        variables = {"project_name": project_name}
        
        for var_name, var_info in template_info["variables"].items():
            if var_name == "project_name":
                continue
                
            prompt = f"{var_info['description']} ({var_info['default']}):"
            
            if var_info["choices"]:
                value = ask_for_selection(prompt, var_info["choices"])
            else:
                value = ask_for_input(prompt, var_info["default"])
                
            variables[var_name] = value
            
        # Create the project
        try:
            self.template_manager.create_project(
                template_name,
                project_dir,
                **variables
            )
            
            print(f"Project created successfully at {project_dir}")
        except Exception as e:
            print(f"Failed to create project: {e}")
            
    def _update_project(self, directory: Path) -> None:
        """
        Update an existing project using its template.
        
        Args:
            directory: Project directory to update
        """
        # Check if the directory is a project created from a template
        try:
            # Update the project
            self.template_manager.update_project(directory)
            
            print(f"Project updated successfully at {directory}")
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Failed to update project: {e}")
            
    def _list_templates(self) -> None:
        """List available templates."""
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