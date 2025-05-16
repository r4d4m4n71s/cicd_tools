"""
Command-line interface for CICD Tools.

This module provides the main entry point for the CICD Tools CLI.
"""

from pathlib import Path

import click

from cicd_tools import __version__
from cicd_tools.menus.app_menu import AppMenu
from cicd_tools.menus.create_menu import CreateMenu
from cicd_tools.utils.config_manager import ConfigManager


@click.command()
@click.option("--create", "-c", is_flag=True, help="Create a new project from templates.")
@click.option("--restore", "-r", is_flag=True, help="Restore project configuration.")
@click.option("-v", "--version", is_flag=True, help="Show the version.")
@click.option(
    "--directory",
    "-d",
    default=".",
    help="Set target directory",
    type=click.Path(file_okay=False),
)
@click.help_option("-h", "--help")
def main(version, create, restore, directory) -> None:
    """CICD Tools - A flexible framework for development tasks."""
    dir_path = Path(directory).absolute()
    
    # Show version if requested
    if version:
        click.echo(f"python -m cicd_tools.cli, version {__version__}")
        return
        
    # Count how many command flags are set
    command_count = sum([create, restore])
    
    if command_count > 1:
        click.echo("Error: Only one command can be specified at a time")
        return
        
    if command_count == 0:
        # No command specified, check if we're in a valid project directory
        if ConfigManager.is_project_directory(dir_path):
            # Show app menu        
            config_manager = ConfigManager.get_config(dir_path)
            app_menu = AppMenu()
            app_menu.show_menu(dir_path)            
        else:
            # Offers create a new project
            create_menu = CreateMenu()
            create_menu.show_menu(dir_path)
            return
    
    if create:
        # Create a new project
        create_menu = CreateMenu()
        create_menu.show_menu(dir_path)
            
    elif restore:

        if not ConfigManager.is_project_directory(dir_path):
            click.echo(f"❌ Error: The directory '{dir_path}' does not appear to be a valid CICD Tools project.")
            click.echo("Make sure you're in the correct project directory")
            return            

        # Initialize configuration
        print(f"Initializing configuration in {dir_path}")
        
        # Create .app_cache directory if it doesn't exist
        config_dir = dir_path / ".app_cache"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Get configuration and clear it
        config_manager = ConfigManager.get_config(dir_path)
        # Force setup_default_config to clear any existing configuration and set defaults
        config_manager.setup_default_config()
        print("Configuration reset to defaults")
                
if __name__ == "__main__":
    main()
