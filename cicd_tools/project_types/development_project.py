"""
Development project type for CICD Tools.

This module provides the DevelopmentProject class, which represents an advanced project
with development capabilities.
"""

import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

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
    
    def __init__(self, project_path: Path) -> None:
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
                "description": "Configure pre-commit hooks to automatically check code quality before commits, "
                "ensuring consistent standards and preventing issues from being committed",
                "callback": self.prehook,
                "icon": "🔄",
                "pause_after_execution": True,  # Pause after prehook to show output
                "redirect": "back"  # Return to main menu after pressing Enter
            })
        
        # Release and Deploy are core features of the development project
        dev_menus.extend([
            {
                "name": "Release",
                "description": "Create a versioned release package for distribution, including version bumping, "
                "building artifacts, and preparing release directories for beta or production",
                "callback": self.release,
                "icon": "🚀",
                "pause_after_execution": True,  # Pause after release to show output
                "redirect": "back"  # Return to main menu after pressing Enter
            },
            {
                "name": "Deploy",
                "description": "Deploy the project to test or production environments, "
                "uploading packages to PyPI or TestPyPI repositories for distribution to end users",
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
                print("✅ Beta release created successfully")
            return True
        except Exception as e:
            print(f"❌ Release creation failed: {e}")
            return False
            
    def _clean_old_package_versions(self, directory: Path) -> str:
        """
        Clean old package versions in the given directory, keeping only the latest version of each package.
        
        For the latest version, both wheel (.whl) and source distribution files are preserved.
        This prevents uploading multiple versions of the same package, which PyPI would reject anyway.
        
        Args:
            directory: Path to the directory containing package files
            
        Returns:
            The latest version string found (or empty if no packages found)

        """
        import re

        from packaging import version
        
        if not directory.exists():
            return ""
            
        # Group files by package name
        packages = {}
        latest_version_found = ""
        
        # Regular expressions for matching wheel and source distribution filenames
        # For wheel: package_name-1.0.0-py3-none-any.whl
        wheel_pattern = re.compile(r'([^-]+(?:-[^-]+)*)-(\d+\.\d+.*?)(?:-py|\.py)')
        # For sdist: package_name-1.0.0.tar.gz
        sdist_pattern = re.compile(r'([^-]+(?:-[^-]+)*)-(\d+\.\d+.*?)\.(?:tar\.gz|zip)')
        
        # Categorize files by package name, version and file type
        for file_path in directory.glob("*"):
            if not file_path.is_file():
                continue
                
            filename = file_path.name
            match = wheel_pattern.match(filename) or sdist_pattern.match(filename)
            
            if match:
                package_name, pkg_version = match.groups()
                # Determine file type (wheel or sdist)
                file_type = "wheel" if filename.endswith(".whl") else "sdist"
                
                if package_name not in packages:
                    packages[package_name] = []
                    
                packages[package_name].append((pkg_version, file_path, file_type))
        
        cleaned_files = 0
        # For each package, keep all distribution types of the latest version
        for _package_name, pkg_files in packages.items():
            if len(pkg_files) <= 1:
                # If only one file, it's the latest
                if pkg_files:
                    latest_version_found = pkg_files[0][0]  # Get version
                continue
                
            # Get unique versions
            unique_versions = {item[0] for item in pkg_files}
            
            if len(unique_versions) <= 1:
                # Only one version exists, keep all files
                latest_version_found = list(unique_versions)[0]
                continue
                
            # Find the latest version using semantic versioning
            latest_version = max(unique_versions, key=version.parse)
            latest_version_found = latest_version
            
            # Identify files to keep (latest version) and remove (older versions)
            for pkg_version, file_path, _file_type in pkg_files:
                if pkg_version != latest_version:
                    print(f"🧹 Removing old version: {file_path.name}")
                    file_path.unlink()
                    cleaned_files += 1
        
        if cleaned_files > 0:
            print(f"✅ Cleaned up {cleaned_files} old package versions in {directory}")
        else:
            print(f"✓ No old package versions to clean in {directory}")
            
        return latest_version_found
    
    def _check_pypirc_exists(self) -> bool:
        """
        Check if .pypirc file exists in the user's home directory.
        
        Returns:
            True if file exists, False otherwise

        """
        import os
        from pathlib import Path
        
        home = Path(os.path.expanduser("~"))
        pypirc_path = home / ".pypirc"
        
        return pypirc_path.exists()
    
    def _create_pypirc_template(self) -> bool:
        """
        Create a template .pypirc file in the user's home directory.
        
        Returns:
            True if file was created successfully, False otherwise

        """
        import os
        from pathlib import Path
        
        print("\n⚠️ No .pypirc file found in your home directory.")
        print("\n📝 A .pypirc file is recommended to configure PyPI and TestPyPI repositories.")
        print("\n💡 For more information about PyPI configuration, visit: https://packaging.python.org/en/latest/specifications/pypirc/")
        
        # Ask if user wants to create the template file
        create_file = questionary.confirm("Would you like to create a template .pypirc file now?").ask()
        
        if not create_file:
            print("\n⚠️ Continuing without .pypirc file. You may be prompted for credentials by twine.")
            return False
            
        # Template content with placeholders
        content = """[distutils]
index-servers =
    pypi
    testpypi

[pypi]
# For PyPI.org
username = your_username
password = your_password_or_token

[testpypi]
# For test.pypi.org
repository = https://test.pypi.org/legacy/
username = your_username
password = your_password_or_token

# For more secure authentication, consider using API tokens instead of passwords
# See: https://pypi.org/help/#apitoken
"""
        
        try:
            # Write the file
            home = Path(os.path.expanduser("~"))
            pypirc_path = home / ".pypirc"
            
            with open(pypirc_path, 'w') as f:
                f.write(content)
                
            # Set file permissions to be readable only by the owner
            import stat
            os.chmod(pypirc_path, stat.S_IRUSR | stat.S_IWUSR)
            
            print(f"\n✅ Created .pypirc template at: {pypirc_path}")
            print("🔐 File permissions set to read/write for owner only.")
            print("\n⚠️ IMPORTANT: You need to edit this file and replace " \
            "the placeholders with your actual credentials before deploying.")
            print("📝 You can use any text editor to update the file.")
            
            # Ask if user wants to edit the file now
            edit_now = questionary.confirm("Would you like to pause the deployment to edit the .pypirc file now?").ask()
            
            if edit_now:
                print("\n✏️ Please edit your .pypirc file now, then press Enter to continue...")
                input()
                print("✅ Continuing with deployment...")
            else:
                print("\n⚠️ Continuing without editing .pypirc. Authentication may fail.")
                
            return True
            
        except Exception as e:
            print(f"\n❌ Failed to create .pypirc template: {e}")
            print("⚠️ Continuing without .pypirc file. You may be prompted for credentials by twine.")
            return False
            
    def deploy(self, target: Optional[str] = None) -> bool:
        """
        Deploy the project.
        
        Args:
            target: Deployment target ('test' or 'prod')
            
        Returns:
            True if deployment was successful, False otherwise

        """
        import subprocess
        
        if target is None:
            target = questionary.select(
                "Select deployment target:",
                choices=["test.pypi.org", "pypi.org"]
            ).ask()
            
        try:
            # Install twine if needed
            pck_manager = PackageManager(self.get_env_manager().get_runner())
            if not pck_manager.is_installed("twine"):
                pck_manager.install("twine")
                
            # Install packaging if needed (used for version comparison)
            if not pck_manager.is_installed("packaging"):
                pck_manager.install("packaging")
            
            # Check if .pypirc exists and offer to create a template if not
            if not self._check_pypirc_exists():
                self._create_pypirc_template()
            
            # Deploy to the selected target
            if target == "pypi.org":
                # Check if production release exists
                release_dir = self.project_path / "dist" / "release"
                if not release_dir.exists() or not list(release_dir.glob("*")):
                    print("⚠️ No production release found. Create a production release first.")
                    return False
                
                # Clean old package versions, keeping only the latest
                version = self._clean_old_package_versions(release_dir)
                
                # Display deployment information
                if version:
                    print(f"📦 Deploying version {version} to PyPI (production)...")
                
                # Use glob to expand file paths instead of relying on shell=True
                import glob
                release_files = glob.glob(str(release_dir / "*"))
                if not release_files:
                    print("⚠️ No files found to upload in release directory.")
                    return False
                
                # Use subprocess without shell=True for security
                subprocess.run(["twine", "upload"] + release_files,
                               shell=False,
                               check=True,
                               cwd=str(self.project_path))
            else:
                # Check if beta release exists
                beta_dir = self.project_path / "dist" / "beta"
                if not beta_dir.exists() or not list(beta_dir.glob("*")):
                    print("⚠️ No beta release found. Create a beta release first.")
                    return False
                
                # Clean old package versions, keeping only the latest
                version = self._clean_old_package_versions(beta_dir)
                
                # Display deployment information
                if version:
                    print(f"📦 Deploying version {version} to TestPyPI (test)...")
                
                # Use glob to expand file paths instead of relying on shell=True
                import glob
                beta_files = glob.glob(str(beta_dir / "*"))
                if not beta_files:
                    print("⚠️ No files found to upload in beta directory.")
                    return False
                
                # Use subprocess without shell=True for security
                subprocess.run(["twine", "upload", "--repository", "testpypi"] + beta_files,
                               shell=False,
                               check=True,
                               cwd=str(self.project_path))
                
            print(f"✅ Deployment to {target} successful")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Deployment command failed: {e}")
            print("\n⚠️ Please verify your .pypirc file configuration at ~/.pypirc")
            print("   This file contains your PyPI credentials and repository settings.")
            return False
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            print("\n⚠️ Please verify your .pypirc file configuration at ~/.pypirc")
            print("   This file contains your PyPI credentials and repository settings.")
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
