"""
Project type implementations for CICD Tools.

This package provides the project type implementations for CICD Tools, including:
- BaseProject: Abstract base class for all project types
- SimpleProject: Basic project with minimal functionality
- DevelopmentProject: Advanced project with development capabilities
- GitHubProject: Project with GitHub integration
"""

from cicd_tools.project_types.base_project import BaseProject
from cicd_tools.project_types.simple_project import SimpleProject
from cicd_tools.project_types.development_project import DevelopmentProject
from cicd_tools.project_types.github_project import GitHubProject

__all__ = ["BaseProject", "SimpleProject", "DevelopmentProject", "GitHubProject"]