"""
Command-line interface for CICD Tools.

This module provides the main entry point for the CICD Tools CLI.
"""

import datetime
import json
from pathlib import Path

import click

from cicd_tools import __version__
from cicd_tools.menus.app_menu import AppMenu
from cicd_tools.menus.create_menu import CreateMenu
from cicd_tools.utils.config_manager import ConfigManager


@click.command()
@click.option("-v", "--version", is_flag=True, help="Show the version and exit.")
@click.option("--create", "-c", is_flag=True, help="Create a new project from templates")
@click.option("--app", "-a", is_flag=True, help="Work with an existing project")
@click.option("--init", "-i", is_flag=True, help="Initialize or reset configuration")
@click.option("--enable", "-e", is_flag=True, help="Enable development tasks for a existing project")
@click.option(
    "--directory",
    "-d",
    default=".",
    help="Directory to work with if its diferent to the current",
    type=click.Path(file_okay=False),
)
@click.option("--log_verbose", "-l", is_flag=True, help="Enable verbose output")
@click.help_option("-h", "--help")
def main(version, create, app, init, enable, directory, log_verbose) -> None:
    """CICD Tools - A flexible framework for development tasks."""
    dir_path = Path(directory).absolute()
    
    # Show version if requested
    if version:
        click.echo(f"python -m cicd_tools.cli, version {__version__}")
        return
        
    # Count how many command flags are set
    command_count = sum([create, app, init, enable])
    
    if command_count > 1:
        click.echo("Error: Only one command can be specified at a time")
        return
    
    if command_count == 0:
        # No command specified, show help
        click.echo(main.get_help(click.Context(main)))
        return
    
    if create:
        # Create a new project
        create_menu = CreateMenu()
        create_menu.show_menu(dir_path)
    
    elif app:
        # Work with an existing project
        try:
            app_menu = AppMenu()
            app_menu.show_menu(dir_path)
        except Exception as e:
            click.echo(f"❌ Error: The directory '{dir_path}' does not appear to be a valid CICD Tools project.")
            click.echo("Make sure you're in the correct directory or initialize a new project with:")
            click.echo("  cicd_tools --init")
            click.echo("  cicd_tools --create")
            if log_verbose:
                click.echo("\nDetailed error information:")
                click.echo(str(e))
    
    elif init:
        # Initialize configuration
        print(f"Initializing configuration in {dir_path}")
        
        # Create .app_cache directory if it doesn't exist
        config_dir = dir_path / ".app_cache"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize configuration
        config_manager = ConfigManager.get_config(dir_path)
        config_manager.setup_default_config()
        
        # Get current timestamp
        current_time = datetime.datetime.now().isoformat()
        
        # Add project marker
        config_manager.set("project", {
            "initialized": True, 
            "init_date": current_time
        })
        
        if log_verbose:
            print("Configuration initialized with the following settings:")
            print(json.dumps(config_manager.get_all(), indent=2))
        else:
            print("✅ Configuration initialized successfully")
            print("Run with --log_verbose to see the full configuration")
    
    elif enable:
        # Enable development task for an existing project
        try:
            create_menu = CreateMenu()
            result = create_menu._recreate_project(dir_path)
            if result:
                print(f"Project successfully recreated at {result}")
        except Exception as e:
            click.echo(f"❌ Error: Failed to enable development tasks for '{dir_path}'")
            if log_verbose:
                click.echo("\nDetailed error information:")
                click.echo(str(e))


if __name__ == "__main__":
    main()
