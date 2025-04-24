"""
Mixins for project types.

This module provides mixins that can be used by different project types
to share common functionality.
"""

from typing import Optional

import questionary
from env_manager import PackageManager


class GitMixin:
    """Mixin providing Git-related functionality."""
    
    def prehook(self, action: Optional[str] = None) -> bool:
        """
        Configure pre-commit hooks.
        
        Args:
            action: Action to perform ('enable', 'disable', or 'run')
            
        Returns:
            True if configuration was successful, False otherwise

        """
        if action is None:
            action = questionary.select(
                "Select pre-commit hook action:",
                choices=["enable", "disable", "run"]
            ).ask()
            
        try:
            # Install pre-commit if needed
            pck_manager = PackageManager(self.get_env_manager().get_runner())
            if not pck_manager.is_installed("pre-commit"):
                pck_manager.install("pre-commit")
            
            if action == "enable":
                self.run("pre-commit", "install")
                print("✅ Pre-commit hooks enabled, automatically executed when git commit.")
            elif action == "run":
                self.prehook_run_action()
                self.run("pre-commit", "run", "--all-files", capture_output=False)
                print("✅ Pre-commit hooks executed manually on all files.")
            else:
                self.run("pre-commit", "uninstall")
                print("✅ Pre-commit hooks disabled")
                
            return True
        except Exception as e:
            print(f"❌ Pre-commit hook configuration failed: {e}")
            return False
            
    def _configure_git_for_release(self) -> None:
        """Configure git for release."""
        # Check if git is configured
        try:
            # Check if git user name is configured
            try:
                self.run("git", "config", "user.name", capture_output=False)
            except Exception:
                # Configure git user name
                name = questionary.text("Enter git user name:").ask()
                self.run("git", "config", "user.name", name)
                
            # Check if git user email is configured
            try:
                self.run("git", "config", "user.email", capture_output=False)
            except Exception:
                # Configure git user email
                email = questionary.text("Enter git user email:").ask()
                self.run("git", "config", "user.email", email)
                
        except Exception as e:
            print(f"❌ Git configuration failed: {e}")


class VersionManagerMixin:
    """Mixin providing version management functionality."""
    
    def _get_current_version(self) -> str:
        """
        Get the current version of the project.
        
        Returns:
            Current version

        """
        import re
        
        # Try to get version from .bumpversion.cfg
        bumpversion_cfg = self.project_path / ".bumpversion.cfg"
        if bumpversion_cfg.exists():
            with open(bumpversion_cfg, encoding="utf-8") as f:
                content = f.read()
                match = re.search(r'current_version\s*=\s*([^\s]+)', content)
                if match:
                    return match.group(1)
                    
        # Try to get version from pyproject.toml
        pyproject_toml = self.project_path / "pyproject.toml"
        if pyproject_toml.exists():
            with open(pyproject_toml, encoding="utf-8") as f:
                content = f.read()
                # Try to find version in the format version = "0.1.0"
                match = re.search(r'version\s*=\s*"([^"]+)"', content)
                if match:
                    return match.group(1)
                
                # Also try to find version in the format current_version = 0.1.0
                match = re.search(r'current_version\s*=\s*([^\s]+)', content)
                if match:
                    return match.group(1)
                    
        # Default version
        return "0.1.0"
        
    def bump_version_for_release(self, release_type: str, bump_type: str = "patch") -> None:
        """
        Bump the version number according to the release type.
        
        Args:
            release_type: Type of release ('beta' or 'prod')
            bump_type: Type of version increment ('patch', 'minor', or 'major')
                       - patch: Increment the patch version (e.g., 0.1.8 -> 0.1.9) for bug fixes
                       - minor: Increment the minor version (e.g., 0.1.9 -> 0.2.0) for new features
                       - major: Increment the major version (e.g., 0.9.9 -> 1.0.0) for breaking changes

        """
        # Get current version
        current_version = self._get_current_version()
        
        # Check if current version is a beta version
        is_beta = self._is_beta_version(current_version)
        
        if release_type == "prod":
            if is_beta:
                # Transition from beta to production
                self._transition_beta_to_prod(current_version, bump_type)
            else:
                # Standard production version bump
                self._bump_production_version(bump_type)
        else:  # beta release
            if is_beta:
                # Increment beta version
                self._bump_beta_version()
            else:
                # Transition from production to beta
                self._transition_prod_to_beta(current_version)
    
    def _is_beta_version(self, version: str) -> bool:
        """
        Check if the version is a beta version.
        
        Args:
            version: Version string to check
            
        Returns:
            True if it's a beta version, False otherwise

        """
        return 'b' in version or '.beta' in version
        
    def _calculate_next_version(self, current_version: str, bump_type: str, release_type: str) -> str:
        """
        Calculate what the next version would be based on the current version.
        
        bump type, and release type, without actually changing the version.

        Args:
            current_version: Current version string
            bump_type: Type of version increment ('patch', 'minor', or 'major')
            release_type: Type of release ('beta' or 'prod')

        Returns:
            The predicted next version string
            
        """
        # Check if current version is beta
        is_beta = self._is_beta_version(current_version)
        
        # Calculate based on release type
        if release_type == "prod":
            # Extract the base version without beta suffix if needed
            if is_beta:
                if '.beta' in current_version:
                    base_version = current_version.replace('.beta', '')
                else:
                    base_version = current_version.split('b')[0]
                    # Remove trailing dot if present
                    if base_version.endswith('.'):
                        base_version = base_version[:-1]
            else:
                base_version = current_version
                
            # Parse version components
            parts = base_version.split('.')
            
            # Calculate new version based on bump type
            if bump_type == "major":
                # Increment major version, reset minor and patch to 0
                parts[0] = str(int(parts[0]) + 1)
                parts[1] = "0"
                parts[2] = "0"
            elif bump_type == "minor":
                # Increment minor version, reset patch to 0
                parts[1] = str(int(parts[1]) + 1)
                parts[2] = "0"
            else:  # Default to patch
                # Increment patch version only
                parts[2] = str(int(parts[2]) + 1)
                
            # Return the new version
            return '.'.join(parts)
        else:  # beta release
            if is_beta:
                # For existing beta versions, increment the beta number
                if '.beta' in current_version:
                    # Not commonly used format, just increment major beta number
                    return current_version.replace('.beta', '.beta1')
                else:
                    # Standard beta format with 'b' prefix for beta number
                    base = current_version.split('b')[0]
                    beta_num = current_version.split('b')[1]
                    return f"{base}b{int(beta_num) + 1}"
            else:
                # For production versions, add beta suffix
                return f"{current_version}b0"
    
    def _transition_beta_to_prod(self, current_version: str, bump_type: str = "patch") -> None:
        """
        Transition from a beta version to a production version.
        
        Args:
            current_version: Current beta version
            bump_type: Type of version increment ('patch', 'minor', or 'major')

        """
        # Extract the base version without the beta suffix
        if '.beta' in current_version:
            base_version = current_version.replace('.beta', '')
        else:
            base_version = current_version.split('b')[0]
            # Remove trailing dot if present
            if base_version.endswith('.'):
                base_version = base_version[:-1]
        
        # Parse the version parts
        parts = base_version.split('.')
        
        if bump_type == "major":
            # Increment major version, reset minor and patch to 0
            parts[0] = str(int(parts[0]) + 1)
            parts[1] = "0"
            parts[2] = "0"
        elif bump_type == "minor":
            # Increment minor version, reset patch to 0
            parts[1] = str(int(parts[1]) + 1)
            parts[2] = "0"
        else:  # Default to patch
            # Increment patch version only
            parts[2] = str(int(parts[2]) + 1)
            
        # Create the new version
        new_version = '.'.join(parts)
        
        # Set the new version directly
        self.run("bump2version", "--allow-dirty", "--new-version", new_version, "patch", capture_output=False)
    
    def _transition_prod_to_beta(self, current_version: str) -> None:
        """
        Transition from a production version to a beta version.
        
        Args:
            current_version: Current production version

        """
        # Extract the base version parts
        parts = current_version.split('.')
        # Create the new version with beta suffix
        new_version = f"{parts[0]}.{parts[1]}.{parts[2]}b0"
        # Set the new version (need to specify a part even when using --new-version)
        self.run("bump2version", "patch", "--allow-dirty", "--new-version", new_version, capture_output=False)
    
    def _bump_beta_version(self) -> None:
        """Increment the beta version number."""
        self.run("bump2version", "beta", capture_output=False)
    
    def _bump_production_version(self, bump_type: str = "patch") -> None:
        """
        Increment the production version number.
        
        This ensures we get a proper production version without any beta suffix.
        
        Args:
            bump_type: Type of version increment ('patch', 'minor', or 'major')
                       - patch: Increment the patch version (e.g., 0.1.8 -> 0.1.9) for bug fixes
                       - minor: Increment the minor version (e.g., 0.1.9 -> 0.2.0) for new features
                       - major: Increment the major version (e.g., 0.9.9 -> 1.0.0) for breaking changes

        """
        # Get current version
        current_version = self._get_current_version()
        
        # Check if current version is a beta version
        is_beta = self._is_beta_version(current_version)
        
        if is_beta:
            # If we're on a beta version, use our existing method to transition to production
            self._transition_beta_to_prod(current_version, bump_type)
        else:
            # If already on a production version, directly calculate the next version
            # Parse version components
            parts = current_version.split('.')
            
            if bump_type == "major":
                # Increment major version, reset minor and patch to 0
                parts[0] = str(int(parts[0]) + 1)
                parts[1] = "0"
                parts[2] = "0"
            elif bump_type == "minor":
                # Increment minor version, reset patch to 0
                parts[1] = str(int(parts[1]) + 1)
                parts[2] = "0"
            else:  # Default to patch
                # Increment patch version only
                parts[2] = str(int(parts[2]) + 1)
                
            # Create the new version
            new_version = '.'.join(parts)
            
            # Set the new version directly
            self.run("bump2version", "--allow-dirty", "--new-version", new_version, "patch", capture_output=False)
