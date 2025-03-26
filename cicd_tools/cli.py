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
def main():
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
def create(directory):
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
def app(directory):
    """Work with an existing project."""
    app_menu = AppMenu()
    app_menu.show_menu(Path(directory).absolute())


if __name__ == "__main__":
    main()
