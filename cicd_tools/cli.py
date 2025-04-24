"""
Command-line interface for CICD Tools.

This module provides the main entry point for the CICD Tools CLI.
"""

from pathlib import Path

import click

from cicd_tools.menus.app_menu import AppMenu
from cicd_tools.menus.create_menu import CreateMenu


@click.group()
@click.version_option()
def main() -> None:
    """CICD Tools - A flexible framework for development tasks."""
    pass


@main.command()
@click.option(
    "--directory",
    "-d",
    default=".",
    help="Directory where the project will be created",
    type=click.Path(file_okay=False),
)
def create(directory) -> None:
    """Create a new project from templates."""
    create_menu = CreateMenu()
    create_menu.show_menu(Path(directory).absolute())


@main.command()
@click.option(
    "--directory",
    "-d",
    default=".",
    help="Project directory to work with",
    type=click.Path(exists=True, file_okay=False),
)
def app(directory) -> None:
    """Work with an existing project."""
    app_menu = AppMenu()
    app_menu.show_menu(Path(directory).absolute())


@main.command()
@click.option(
    "--directory",
    "-d",
    default=".",
    help="Project directory to initialize",
    type=click.Path(file_okay=False),
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def init(directory, verbose) -> None:
    """
    Initialize or reset configuration.

    This command creates or resets the configuration in the specified directory.
    It's useful when starting a new project or when you want to restore
    default settings.
    """
    import datetime
    import json
    from pathlib import Path

    from cicd_tools.utils.config_manager import ConfigManager
    
    dir_path = Path(directory).absolute()
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
    
    if verbose:
        print("Configuration initialized with the following settings:")
        print(json.dumps(config_manager.get_all(), indent=2))
    else:
        print("✅ Configuration initialized successfully")
        print("Run with --verbose to see the full configuration")


if __name__ == "__main__":
    main()
