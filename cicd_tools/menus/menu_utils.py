"""
Menu utilities for CICD Tools.

This module provides common menu functionality for CICD Tools with enhanced styling.
"""

from typing import List, Callable, Dict, Any, Optional, Union, TypeVar, Generic

T = TypeVar('T')

import questionary
from questionary import Choice
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.style import Style

# Initialize Rich console
console = Console()

def style_text(text: str, style_str: str) -> Text:
    """
    Apply style to text using Rich.
    
    Args:
        text: Text to style
        style_str: Style string (e.g., 'bold blue')
        
    Returns:
        Styled Text object
    """
    return Text(text, style=style_str)

def display_header(title: str, subtitle: Optional[str] = None) -> None:
    """
    Display a styled header.
    
    Args:
        title: Title text
        subtitle: Optional subtitle text
    """
    console.clear()
    console.print(Panel(
        Text(title, style="bold blue"),
        subtitle=subtitle,
        border_style="blue"
    ))

class ActionResult(Generic[T]):
    """
    Represents the result of a menu action.
    
    This class encapsulates the result of a menu action, including the redirect value and the result of the callback.
    """
    
    def __init__(self, result: T, redirect: Optional[str] = None):
        """
        Initialize an action result.
        
        Args:
            result: The result of the callback function
            redirect: The redirect value (e.g., 'back', 'exit')
        """
        self.result = result
        self.redirect = redirect
        
    def get_redirect(self) -> Optional[str]:
        """
        Get the redirect value.
        
        Returns:
            The redirect value, or None if no redirect was specified
        """
        return self.redirect
        
    def get_result(self) -> T:
        """
        Get the result of the callback function.
        
        Returns:
            The result of the callback function
        """
        return self.result

class MenuAction:
    """
    Represents a single menu action/option.
    
    This class encapsulates a menu action with a name, description, icon, and callback function.
    """
    
    def __init__(self, name: str, description: str, callback: Callable, icon: Optional[str] = None, **kwargs):
        """
        Initialize a menu action.
        
        Args:
            name: Name of the action (displayed in the menu)
            description: Description of the action
            callback: Function to call when the action is selected
            icon: Optional icon to display next to the action (emoji or symbol)
            **kwargs: Additional arguments to pass to the callback
                - pause_after_execution: Whether to pause after executing the action (default: False)
                - redirect: Where to redirect after execution ('back', 'exit', or None to stay in current menu)
        """
        self.name = name
        self.description = description
        self.callback = callback
        self.icon = icon
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
        
        # Extract special parameters before passing to callback
        pause_after_execution = merged_kwargs.pop('pause_after_execution', False)
        redirect = merged_kwargs.pop('redirect', None)
        
        # Call the callback with the remaining kwargs
        result = self.callback(*args, **merged_kwargs)
        
        # Add a pause after executing the action if requested
        if pause_after_execution:
            input("\nPress Enter to continue...")
        
        # Return an ActionResult object with both the redirect value and the result
        action_result = ActionResult(result, redirect)
        return action_result

class Menu:
    """
    Base menu class to display options and handle selection.
    
    This class provides functionality to display a menu and handle user selection
    with enhanced styling.
    """
    
    def __init__(self, title: str, style_config: Optional[Dict[str, Any]] = None):
        """
        Initialize a menu.
        
        Args:
            title: Title of the menu
            style_config: Optional styling configuration
        """
        self.title = title
        self.actions: List[MenuAction] = []
        self.style_config = style_config or {}
        
    def add_action(self, action: MenuAction) -> None:
        """
        Add a menu action to the menu.
        
        Args:
            action: The menu action to add
        """
        self.actions.append(action)
        
    def display(self) -> ActionResult:
        """
        Display the menu and handle user selection.
        
        Returns:
            The result of the selected action, or None if no action was selected
        """
        if not self.actions:
            console.print(f"[bold red]No actions available for {self.title}[/bold red]")
            return ActionResult(None, "back")
            
        # Display styled header
        display_header(self.title, "Select an action:")
        
        # Create choices with icons
        choices = []
        for i, action in enumerate(self.actions):
            icon_text = f"{action.icon} " if action.icon else ""
            choices.append(Choice(
                title=f"{icon_text} {action.name} - {action.description}",
                value=i
            ))
        
        # Add a back/exit option
        choices.append(Choice(title="↩️  Back/Exit", value=None))
        
        # Show menu and get selection
        result = questionary.select(
            "Select an action:",
            choices=choices
        ).ask()
        
        # Handle Back/Exit option
        if result is None:
            return ActionResult(None, "back")
        
        # Convert result to integer if it's a string that represents an integer
        if isinstance(result, str) and result.isdigit():
            result = int(result)
        
        # If result is still a string, try to find the corresponding action
        if isinstance(result, str):
            # Try to find the action by name
            for i, action in enumerate(self.actions):
                action_title = f"{action.name} - {action.description}"
                if result == action_title or result == action.name:
                    result = i
                    break
            else:
                # If we get here, we couldn't find a matching action
                # This is a fallback to prevent errors
                return ActionResult(None, "back")
            
        # Ensure result is a valid integer index
        if isinstance(result, int) and 0 <= result < len(self.actions):
            selected_action = self.actions[result]
        else:
            return ActionResult(None, "back")
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
    # Convert non-string defaults to string, or empty string if None
    if default is None:
        default = ""
    elif not isinstance(default, str):
        default = str(default)
    
    return questionary.text(message, default=default).ask()


def ask_for_selection(message: str, choices: List[Union[str, Dict[str, Any]]], default:Optional[Union[str, Choice, Dict[str, Any]]] = None) -> Any:
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
    
    return questionary.select(message, choices=choices, default=default).ask()
