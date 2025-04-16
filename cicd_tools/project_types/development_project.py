"""
Development project type for CICD Tools.

This module provides the DevelopmentProject class, which represents an advanced project
with development capabilities.
"""

import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional

import questionary
from env_manager import PackageManager
from cicd_tools.project_types.base_project import BaseProject
from cicd_tools.project_types.mixins import GitMixin, VersionManagerMixin
from cicd_tools.utils.config_manager import ConfigManager

class DevelopmentProject(GitMixin, VersionManagerMixin, BaseProject):
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
        common_menus = self.get_common_menu_items()
        
        # Get configuration
        config_manager = ConfigManager.get_config(self.project_path)
        
        # Add Development-specific menu items
        dev_menus = []
        
        # Add Prehook menu item if code analysis tools are enabled
        code_analysis_tools = config_manager.get("code_analysis_tools", "no")
        
        if code_analysis_tools == "yes":
            dev_menus.append({
                "name": "Prehook",
                "description": "Configure pre-commit hooks to automatically check code quality before commits, ensuring consistent standards and preventing issues from being committed",
                "callback": self.prehook,
                "icon": "🔄",
                "pause_after_execution": True,  # Pause after prehook to show output
                "redirect": "back"  # Return to main menu after pressing Enter
            })
        
        # Release and Deploy are core features of the development project
        dev_menus.extend([
            {
                "name": "Release",
                "description": "Create a versioned release package for distribution, including version bumping, building artifacts, and preparing release directories for beta or production",
                "callback": self.release,
                "icon": "🚀",
                "pause_after_execution": True,  # Pause after release to show output
                "redirect": "back"  # Return to main menu after pressing Enter
            },
            {
                "name": "Deploy",
                "description": "Deploy the project to test or production environments, uploading packages to PyPI or TestPyPI repositories for distribution to end users",
                "callback": self.deploy,
                "icon": "📦",
                "pause_after_execution": True,  # Pause after deploy to show output
                "redirect": "back"  # Return to main menu after pressing Enter
            }
        ])
        
        # Insert Development menus after Build
        build_index = next((i for i, item in enumerate(common_menus) if item["name"] == "Build"), -1)
        if build_index != -1:
            return common_menus[:build_index+1] + dev_menus + common_menus[build_index+1:]
        else:
            return common_menus + dev_menus
        
    # Common methods are inherited from BaseProject
    # Git-related methods are inherited from GitMixin
    # Version management methods are inherited from VersionManagerMixin

    # overrided methods
    def build(self) -> bool:
        """
        Build the project.
        
        Returns:
            True if build was successful, False otherwise
        """      
        try:
            # Build the project using pyproject.toml instead of setup.py
            self.run("python", "-m", "build", "--outdir", str(self.project_path / "build"))
            #self.run("python", "-m", "build")
            print("✅ Build finished.")
            return True
        except Exception as e:
            print(f"❌ Build failed: {e}")
            return False
    # end overrided methods

    def _clean_dist_root(self) -> None:
        """
        Clean up the root of the dist folder while preserving subdirectories.
        This prevents copying outdated files during the release process.
        """
        dist_dir = self.project_path / "dist"
        if dist_dir.exists():
            for file in dist_dir.glob("*"):
                if file.is_file():
                    file.unlink()
    
    def release(self, release_type: Optional[str] = None, bump_type: Optional[str] = None) -> bool:
        """
        Create a release.
        
        Args:
            release_type: Type of release ('beta' or 'prod')
            bump_type: Type of version increment ('patch', 'minor', or 'major').
                       Only used for production releases.
            
        Returns:
            True if release creation was successful, False otherwise
        """
        if release_type is None:
            release_type = questionary.select(
                "Select release type:",
                choices=["beta", "prod"]
            ).ask()
        
        # Get current version to display in prompts
        current_version = self._get_current_version()
        is_beta = self._is_beta_version(current_version)
        
        # For production releases, ask for bump type if not provided
        if release_type == "prod" and bump_type is None:
            # Calculate what the next versions would be for different bump types
            next_version_patch = self._calculate_next_version(current_version, "patch", "prod")
            next_version_minor = self._calculate_next_version(current_version, "minor", "prod")
            next_version_major = self._calculate_next_version(current_version, "major", "prod")
            
            bump_type = questionary.select(
                f"Current version: {current_version}\nSelect version increment type:",
                choices=[
                    {"name": f"patch - If it's for Bug fixes ({current_version} → {next_version_patch})", "value": "patch"},
                    {"name": f"minor - If it's for New features ({current_version} → {next_version_minor})", "value": "minor"},
                    {"name": f"major - If it's for Breaking changes ({current_version} → {next_version_major})", "value": "major"}
                ]
            ).ask()
        elif release_type == "beta" and bump_type is None:
            # For beta releases, show what the next beta version would be
            next_beta_version = self._calculate_next_version(current_version, "patch", "beta")
            print(f"Current version: {current_version}")
            print(f"Will create beta version: {next_beta_version}")
            # Default to patch for beta releases
            bump_type = "patch"
        else:
            # Use provided bump_type (or default to patch)
            bump_type = bump_type or "patch"
            
        try:
            # Install required packages
            pck_manager = PackageManager(self.get_env_manager().get_runner())
            if not pck_manager.is_installed("build"):
                pck_manager.install("build")
            if not pck_manager.is_installed("bump2version"):
                pck_manager.install("bump2version")
            
            # Configure git for release
            self._configure_git_for_release()
            
            # Bump version according to release type and bump type
            self.bump_version_for_release(release_type, bump_type)
            
            # Clean up the root of the dist folder before building
            self._clean_dist_root()
            
            # Build the project
            self.run("python", "-m", "build")
            
            # Prepare release directory
            self._prepare_release_directory(release_type)
            
            # Clean up the root of the dist folder again after copying files
            self._clean_dist_root()
            
            # Display success message with detailed information
            if release_type == "prod":
                print(f"✅ Production release created successfully ({bump_type} increment)")
            else:
                print(f"✅ Beta release created successfully")
            return True
        except Exception as e:
            print(f"❌ Release creation failed: {e}")
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
            
            # Install twine if needed
            pck_manager = PackageManager(self.get_env_manager().get_runner())
            if not pck_manager.is_installed("twine"):
                pck_manager.install("twine")
            
            # Deploy to the selected target
            if target == "prod":
                # Check if production release exists
                release_dir = self.project_path / "dist" / "release"
                if not release_dir.exists() or not list(release_dir.glob("*")):
                    print("⚠️ No production release found. Create a production release first.")
                    return False
                    
                self.run("twine", "upload", "dist/release/*")
            else:
                # Check if beta release exists
                beta_dir = self.project_path / "dist" / "beta"
                if not beta_dir.exists() or not list(beta_dir.glob("*")):
                    print("⚠️ No beta release found. Create a beta release first.")
                    return False
                    
                self.run("twine", "upload", "--repository", "testpypi", "dist/beta/*")
                
            print(f"✅ Deployment to {target} successful")
            return True
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            return False
                               
        
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
