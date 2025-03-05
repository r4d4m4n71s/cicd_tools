"""
Menu utilities for CICD Tools.

This module provides common menu functionality for CICD Tools.
"""

from typing import List, Callable, Dict, Any, Optional, Union

import questionary
from questionary import Choice


class MenuAction:
    """
    Represents a single menu action/option.
    
    This class encapsulates a menu action with a name, description, and callback function.
    """
    
    def __init__(self, name: str, description: str, callback: Callable, **kwargs):
        """
        Initialize a menu action.
        
        Args:
            name: Name of the action (displayed in the menu)
            description: Description of the action
            callback: Function to call when the action is selected
            **kwargs: Additional arguments to pass to the callback
        """
        self.name = name
        self.description = description
        self.callback = callback
        self.kwargs = kwargs
        
    def execute(self, *args, **kwargs) -> Any:
        """
        Execute the menu action.
        
        Args:
            *args: Positional arguments to pass to the callback
            **kwargs: Keyword arguments to pass to the callback
            
        Returns:
            The result of the callback function
        """
        # Merge the kwargs from initialization with the ones passed to execute
        merged_kwargs = {**self.kwargs, **kwargs}
        return self.callback(*args, **merged_kwargs)


class Menu:
    """
    Base menu class to display options and handle selection.
    
    This class provides functionality to display a menu and handle user selection.
    """
    
    def __init__(self, title: str):
        """
        Initialize a menu.
        
        Args:
            title: Title of the menu
        """
        self.title = title
        self.actions: List[MenuAction] = []
        
    def add_action(self, action: MenuAction) -> None:
        """
        Add a menu action to the menu.
        
        Args:
            action: The menu action to add
        """
        self.actions.append(action)
        
    def display(self) -> Optional[Any]:
        """
        Display the menu and handle user selection.
        
        Returns:
            The result of the selected action, or None if no action was selected
        """
        if not self.actions:
            print(f"No actions available for {self.title}")
            return None
            
        choices = [
            Choice(
                title=f"{action.name} - {action.description}",
                value=i
            )
            for i, action in enumerate(self.actions)
        ]
        
        # Add a back/exit option
        choices.append(Choice(title="Back/Exit", value=None))
        
        result = questionary.select(
            f"{self.title} - Select an action:",
            choices=choices
        ).ask()
        
        if result is None:
            return None
            
        selected_action = self.actions[result]
        return selected_action.execute()


def confirm_action(message: str) -> bool:
    """
    Ask for confirmation before performing an action.
    
    Args:
        message: The confirmation message to display
        
    Returns:
        True if the user confirmed, False otherwise
    """
    return questionary.confirm(message).ask()


def ask_for_input(message: str, default: Optional[Any] = None) -> str:
    """
    Ask the user for input.
    
    Args:
        message: The message to display
        default: The default value
        
    Returns:
        The user input
    """
    # Ensure default is a string (never None)
    if default is None:
        default = ""
    elif not isinstance(default, str):
        default = str(default)
    
    return questionary.text(message, default=default).ask()


def ask_for_selection(message: str, choices: List[Union[str, Dict[str, Any]]]) -> Any:
    """
    Ask the user to select from a list of choices.
    
    Args:
        message: The message to display
        choices: The list of choices
        
    Returns:
        The selected choice
    """
    # # Ensure all choices are properly formatted
    # formatted_choices = []
    # for choice in choices:
    #     if isinstance(choice, str):
    #         formatted_choices.append(choice)
    #     elif isinstance(choice, dict) and "value" in choice and "title" in choice:
    #         formatted_choices.append(choice)
    #     elif isinstance(choice, dict) and "name" in choice:
    #         # Convert to string if it's a dict with a name but not in the expected format
    #         formatted_choices.append(str(choice["name"]))
    #     else:
    #         # Convert to string for any other type
    #         formatted_choices.append(str(choice))
    
    return questionary.select(message, choices=choices).ask()