"""
Tests for the menu system.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import questionary

from cicd_tools.menus.menu_utils import Menu, MenuAction, confirm_action, ask_for_input, ask_for_selection


def test_menu_action_init():
    """Test MenuAction initialization."""
    callback = MagicMock(return_value=True)
    action = MenuAction("Test Action", "Test description", callback, icon="🔧", arg1="value1")
    
    assert action.name == "Test Action"
    assert action.description == "Test description"
    assert action.callback == callback
    assert action.icon == "🔧"
    assert action.kwargs == {"arg1": "value1"}


def test_menu_action_execute():
    """Test MenuAction execute method."""
    callback = MagicMock(return_value=True)
    action = MenuAction("Test Action", "Test description", callback, arg1="value1")
    
    # Execute without additional arguments
    result = action.execute()
    
    assert result is True
    callback.assert_called_once_with(arg1="value1")
    
    # Reset mock
    callback.reset_mock()
    
    # Execute with additional arguments
    result = action.execute("pos_arg", arg2="value2")
    
    assert result is True
    callback.assert_called_once_with("pos_arg", arg1="value1", arg2="value2")


def test_menu_init():
    """Test Menu initialization."""
    menu = Menu("Test Menu")
    
    assert menu.title == "Test Menu"
    assert menu.actions == []
    assert menu.style_config == {}
    
    # Test with style_config
    style_config = {
        "colors": {
            "primary": "#007BFF"
        }
    }
    menu_with_style = Menu("Test Menu", style_config)
    
    assert menu_with_style.title == "Test Menu"
    assert menu_with_style.style_config == style_config


def test_menu_add_action():
    """Test Menu add_action method."""
    menu = Menu("Test Menu")
    action = MenuAction("Test Action", "Test description", lambda: True)
    
    menu.add_action(action)
    
    assert len(menu.actions) == 1
    assert menu.actions[0] == action


@patch("questionary.select")
def test_menu_display(mock_select):
    """Test Menu display method."""
    # Mock questionary.select
    mock_select.return_value.ask.return_value = 0
    
    # Create menu with actions
    menu = Menu("Test Menu")
    action1 = MenuAction("Action 1", "Description 1", MagicMock(return_value="Result 1"))
    action2 = MenuAction("Action 2", "Description 2", MagicMock(return_value="Result 2"))
    
    menu.add_action(action1)
    menu.add_action(action2)
    
    # Display menu and select first action
    result = menu.display()
    
    assert result == "Result 1"
    action1.callback.assert_called_once()
    action2.callback.assert_not_called()
    
    # Mock selecting second action
    mock_select.return_value.ask.return_value = 1
    
    # Reset mocks
    action1.callback.reset_mock()
    action2.callback.reset_mock()
    
    # Display menu and select second action
    result = menu.display()
    
    assert result == "Result 2"
    action1.callback.assert_not_called()
    action2.callback.assert_called_once()
    
    # Mock selecting back/exit option
    mock_select.return_value.ask.return_value = None
    
    # Reset mocks
    action1.callback.reset_mock()
    action2.callback.reset_mock()
    
    # Display menu and select back/exit
    result = menu.display()
    
    assert result is None
    action1.callback.assert_not_called()
    action2.callback.assert_not_called()


@patch("questionary.confirm")
def test_confirm_action(mock_confirm):
    """Test confirm_action function."""
    # Mock questionary.confirm
    mock_confirm.return_value.ask.return_value = True
    
    # Confirm action
    result = confirm_action("Confirm?")
    
    assert result is True
    mock_confirm.assert_called_once_with("Confirm?")
    
    # Mock declining
    mock_confirm.return_value.ask.return_value = False
    
    # Reset mock
    mock_confirm.reset_mock()
    
    # Decline action
    result = confirm_action("Confirm?")
    
    assert result is False
    mock_confirm.assert_called_once_with("Confirm?")


@patch("questionary.text")
def test_ask_for_input(mock_text):
    """Test ask_for_input function."""
    # Mock questionary.text
    mock_text.return_value.ask.return_value = "Input"
    
    # Ask for input
    result = ask_for_input("Enter input:")
    
    assert result == "Input"
    mock_text.assert_called_once_with("Enter input:", default="")
    
    # Mock with default value
    mock_text.reset_mock()
    
    # Ask for input with default
    result = ask_for_input("Enter input:", "Default")
    
    assert result == "Input"
    mock_text.assert_called_once_with("Enter input:", default="Default")


@patch("questionary.select")
def test_ask_for_selection(mock_select):
    """Test ask_for_selection function."""
    # Mock questionary.select
    mock_select.return_value.ask.return_value = "Option 2"
    
    # Ask for selection
    result = ask_for_selection("Select option:", ["Option 1", "Option 2", "Option 3"])
    
    assert result == "Option 2"
    mock_select.assert_called_once_with("Select option:", choices=["Option 1", "Option 2", "Option 3"], default=None)
    
    # Reset mock
    mock_select.reset_mock()
    
    # Test with default value
    mock_select.return_value.ask.return_value = "Option 1"
    result = ask_for_selection("Select option:", ["Option 1", "Option 2", "Option 3"], default="Option 1")
    
    assert result == "Option 1"
    mock_select.assert_called_once_with("Select option:", choices=["Option 1", "Option 2", "Option 3"], default="Option 1")
