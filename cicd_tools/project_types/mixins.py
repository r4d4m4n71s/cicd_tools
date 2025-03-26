"""
Mixins for project types.

This module provides mixins that can be used by different project types
to share common functionality.
"""

from typing import Optional
import questionary
from env_manager import PackageManager

class PackageManagerMixin:
    """Mixin providing package management functionality."""
    
    def _install_if_needed(self, package: str) -> None:
        """
        Install a package if it's not already installed.
        
        Args:
            package: Package to install
        """
        pck_manager = PackageManager(self.get_env_manager().get_runner())

        if not pck_manager.is_installed(package):
            pck_manager.install(package)        

class GitMixin(PackageManagerMixin):
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
            self._install_if_needed("pre-commit")
            
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
