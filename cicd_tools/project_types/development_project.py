"""
Development project type for CICD Tools.

This module provides the DevelopmentProject class, which represents an advanced project
with development capabilities.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import questionary

from cicd_tools.project_types.base_project import BaseProject
from cicd_tools.utils.env_manager import EnvManager


class DevelopmentProject(BaseProject):
    """
    Development project type with advanced capabilities.
    
    This class represents an advanced project with development capabilities,
    including installation, testing, pre-commit hooks, release management, and deployment.
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize a development project.
        
        Args:
            project_path: Path to the project directory
        """
        super().__init__(project_path)
        
    def get_menus(self) -> List[Dict[str, Any]]:
        """
        Get the menu actions available for this project type.
        
        Returns:
            A list of menu action dictionaries
        """
        return [
            {
                "name": "Install",
                "description": "Install the project with development dependencies",
                "callback": self.install
            },
            {
                "name": "Test",
                "description": "Run tests",
                "callback": self.test
            },
            {
                "name": "Prehook",
                "description": "Configure pre-commit hooks",
                "callback": self.prehook
            },
            {
                "name": "Release",
                "description": "Create a release",
                "callback": self.release
            },
            {
                "name": "Deploy",
                "description": "Deploy the project",
                "callback": self.deploy
            },
            {
                "name": "Clean",
                "description": "Clean build artifacts",
                "callback": self.clean
            }
        ]
        
    def install(self) -> bool:
        """
        Install the project with development dependencies.
        
        Returns:
            True if installation was successful, False otherwise
        """
        try:
            env_manager = self.get_env_manager()
            env_manager.run("pip", "install", "-e", ".[dev]")
            return True
        except Exception as e:
            print(f"Installation failed: {e}")
            return False
            
    def test(self) -> bool:
        """
        Run tests.
        
        Returns:
            True if tests passed, False otherwise
        """
        try:
            # Ask for test options
            test_option = questionary.select(
                "Select test option:",
                choices=[
                    "All tests",
                    "Failed tests only",
                    "With coverage"
                ]
            ).ask()
            
            env_manager = self.get_env_manager()
            
            if test_option == "All tests":
                env_manager.run("pytest", "--tb=short", "-v")
            elif test_option == "Failed tests only":
                env_manager.run("pytest", "--tb=short", "-v", "--last-failed")
            elif test_option == "With coverage":
                env_manager.run("pytest", "--tb=short", "-v", "--cov")
                
            return True
        except Exception as e:
            print(f"Tests failed: {e}")
            return False
            
    def prehook(self, action: Optional[str] = None) -> bool:
        """
        Configure pre-commit hooks.
        
        Args:
            action: Action to perform ('on' or 'off')
            
        Returns:
            True if configuration was successful, False otherwise
        """
        if action is None:
            action = questionary.select(
                "Select pre-commit hook action:",
                choices=["on", "off"]
            ).ask()
            
        try:
            env_manager = self.get_env_manager()
            
            # Install pre-commit if needed
            self._install_if_needed("pre-commit")
            
            if action == "on":
                env_manager.run("pre-commit", "install")
                print("Pre-commit hooks enabled")
            else:
                env_manager.run("pre-commit", "uninstall")
                print("Pre-commit hooks disabled")
                
            return True
        except Exception as e:
            print(f"Pre-commit hook configuration failed: {e}")
            return False
            
    def release(self, release_type: Optional[str] = None) -> bool:
        """
        Create a release.
        
        Args:
            release_type: Type of release ('beta' or 'prod')
            
        Returns:
            True if release creation was successful, False otherwise
        """
        if release_type is None:
            release_type = questionary.select(
                "Select release type:",
                choices=["beta", "prod"]
            ).ask()
            
        try:
            env_manager = self.get_env_manager()
            
            # Install required packages
            self._install_if_needed("build")
            self._install_if_needed("bump2version")
            
            # Configure git for release
            self._configure_git_for_release()
            
            # Bump version
            if release_type == "prod":
                env_manager.run("bump2version", "patch")
            else:
                # Get current version
                current_version = self._get_current_version()
                env_manager.run("bump2version", "patch", "--new-version", f"{current_version}.beta")
                
            # Build the project
            env_manager.run("python", "-m", "build")
            
            # Prepare release directory
            self._prepare_release_directory(release_type)
            
            print(f"Release created successfully ({release_type})")
            return True
        except Exception as e:
            print(f"Release creation failed: {e}")
            return False
            
    def deploy(self, target: Optional[str] = None) -> bool:
        """
        Deploy the project.
        
        Args:
            target: Deployment target ('test' or 'prod')
            
        Returns:
            True if deployment was successful, False otherwise
        """
        if target is None:
            target = questionary.select(
                "Select deployment target:",
                choices=["test", "prod"]
            ).ask()
            
        try:
            env_manager = self.get_env_manager()
            
            # Install twine if needed
            self._install_if_needed("twine")
            
            # Deploy to the selected target
            if target == "prod":
                # Check if production release exists
                release_dir = self.project_path / "dist" / "release"
                if not release_dir.exists() or not list(release_dir.glob("*")):
                    print("No production release found. Create a production release first.")
                    return False
                    
                env_manager.run("twine", "upload", "dist/release/*")
            else:
                # Check if beta release exists
                beta_dir = self.project_path / "dist" / "beta"
                if not beta_dir.exists() or not list(beta_dir.glob("*")):
                    print("No beta release found. Create a beta release first.")
                    return False
                    
                env_manager.run("twine", "upload", "--repository", "testpypi", "dist/beta/*")
                
            print(f"Deployment to {target} successful")
            return True
        except Exception as e:
            print(f"Deployment failed: {e}")
            return False
            
    def clean(self) -> bool:
        """
        Clean build artifacts.
        
        Returns:
            True if cleaning was successful, False otherwise
        """
        try:
            # Remove build directory
            build_dir = self.project_path / "build"
            if build_dir.exists():
                shutil.rmtree(build_dir)
                
            # Remove dist directory
            dist_dir = self.project_path / "dist"
            if dist_dir.exists():
                shutil.rmtree(dist_dir)
                
            # Remove egg-info directory
            for egg_info_dir in self.project_path.glob("*.egg-info"):
                shutil.rmtree(egg_info_dir)
                
            print("Build artifacts cleaned successfully")
            return True
        except Exception as e:
            print(f"Cleaning failed: {e}")
            return False
            
    def _install_if_needed(self, package: str) -> None:
        """
        Install a package if it's not already installed.
        
        Args:
            package: Package to install
        """
        env_manager = self.get_env_manager()
        
        try:
            # Check if the package is installed
            env_manager.run("pip", "show", package, capture_output=True)
        except Exception:
            # Package is not installed, install it
            env_manager.install_pkg(package)
            
    def _configure_git_for_release(self) -> None:
        """Configure git for release."""
        # Check if git is configured
        try:
            env_manager = self.get_env_manager()
            
            # Check if git user name is configured
            try:
                env_manager.run("git", "config", "user.name", capture_output=True)
            except Exception:
                # Configure git user name
                name = questionary.text("Enter git user name:").ask()
                env_manager.run("git", "config", "user.name", name)
                
            # Check if git user email is configured
            try:
                env_manager.run("git", "config", "user.email", capture_output=True)
            except Exception:
                # Configure git user email
                email = questionary.text("Enter git user email:").ask()
                env_manager.run("git", "config", "user.email", email)
                
        except Exception as e:
            print(f"Git configuration failed: {e}")
            
    def _get_current_version(self) -> str:
        """
        Get the current version of the project.
        
        Returns:
            Current version
        """
        # Try to get version from .bumpversion.cfg
        bumpversion_cfg = self.project_path / ".bumpversion.cfg"
        if bumpversion_cfg.exists():
            with open(bumpversion_cfg, "r", encoding="utf-8") as f:
                content = f.read()
                match = re.search(r'current_version\s*=\s*([^\s]+)', content)
                if match:
                    return match.group(1)
                    
        # Try to get version from pyproject.toml
        pyproject_toml = self.project_path / "pyproject.toml"
        if pyproject_toml.exists():
            with open(pyproject_toml, "r", encoding="utf-8") as f:
                content = f.read()
                match = re.search(r'version\s*=\s*"([^"]+)"', content)
                if match:
                    return match.group(1)
                    
        # Default version
        return "0.1.0"
        
    def _prepare_release_directory(self, release_type: str) -> None:
        """
        Prepare the release directory.
        
        Args:
            release_type: Type of release ('beta' or 'prod')
        """
        # Create release directory
        release_dir = self.project_path / "dist" / (
            "beta" if release_type == "beta" else "release"
        )
        release_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy build artifacts to release directory
        dist_dir = self.project_path / "dist"
        for artifact in dist_dir.glob("*"):
            if artifact.is_file():
                shutil.copy(artifact, release_dir)