"""
Base project class for CICD Tools.

This module provides the abstract base class for all project types.
"""

import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

import questionary

from cicd_tools.utils.config_manager import ConfigManager

# Import EnvManager with proper error handling
try:
    from env_manager import EnvManager, IRunner, PackageManager, ProgressRunner
except ImportError:
    print("Error: python-env-manager package not found.")
    print("Please install it with: pip install python-env-manager")
    sys.exit(1)

class BaseProject(ABC):
    """
    Abstract base class for all project types.
    
    This class defines the interface that all project types must implement.
    It provides common functionality for project operations.
    """
    
    def __init__(self, project_path: Path) -> None:
        """
        Initialize a project.
        
        Args:
            project_path: Path to the project directory
        
        """
        self.project_path = project_path
        self._env_manager:EnvManager = None
        
    def create_env_manager(self, env_path: Optional[Path], clear: bool = False) -> EnvManager:
        """
        Create and configure an environment manager.
        
        Args:
            env_path: Path to the virtual environment, None for current environment
            clear: Whether to clear any existing environment
        
        Returns:
            Configured environment manager

        """
        # Initialize environment manager with the project path
        env_manager = EnvManager(env_path, clear)
        # Replace it with our custom method
        env_manager.get_runner = lambda: self._custom_runner()
        return env_manager
    
    def _custom_runner(self) -> IRunner:
        """
        Customize runner according to configuration.
        
        Returns:
            A customized runner instance

        """
        config_manager = ConfigManager.get_config(self.project_path)
        stack_trace = config_manager.get("console", {}).get("stack_trace", False)
        
        if stack_trace and self._env_manager is not None:
            # Use the original get_runner method from the EnvManager instance
            original_get_runner = self._env_manager.__class__.get_runner
            return original_get_runner(self._env_manager)
        elif self._env_manager is not None:
            return ProgressRunner(inline_output=0).with_env(self._env_manager)            
        else:
            # Return a default runner if _env_manager is not initialized yet
            # This should not happen in normal operation
            return lambda *args, **kwargs: subprocess.run(args, **kwargs)
    
    def configure_environment(self, env_type: str, env_name: Optional[str] = None, delete_previus: bool = True) -> None:
        """
        Configure the environment for this project.
        
        Args:
            env_type: Type of environment ('current' or 'virtual')
            env_name: Name of the virtual environment (if env_type is 'virtual')
            delete_previus: Whether to delete previous environment if it exists
            
        """
        config_manager = ConfigManager.get_config(self.project_path)    

        if env_type == 'current':
            # Use the current Python environment
            self._env_manager = self.create_env_manager(None)
        elif env_type == 'virtual':
            # Use a virtual environment
            if env_name:
                venv_path = self.project_path / env_name
            else:
                venv_path = self.project_path / '.venv'
            
            env_config = config_manager.get("environment", {})
            if (delete_previus and env_config and 
                Path(env_config.get("path")).exists() and 
                env_config.get("type") == 'virtual'):
                import shutil
                shutil.rmtree(env_config.get("path"))
                
            # Create the virtual environment if it doesn't exist
            self._env_manager = self.create_env_manager(venv_path)
        
        config_manager.set("environment", {"type": env_type, "path": self._env_manager.env.root})    
    
    def get_env_manager(self) -> EnvManager:
        """
        Get the environment manager for this project.
        
        If no environment manager exists yet, create one based on the configuration.
        
        Returns:
            The environment manager
            
        Raises:
            OSError: If no environment is configured
            
        """
        if self._env_manager is None:            
            environment = ConfigManager.get_config(self.project_path).get("environment")        
            if not environment:
                raise OSError("No environment configured")
            
            if environment.get("type") == 'current':
                self._env_manager = self.create_env_manager(None)
            else:
                self._env_manager = self.create_env_manager(Path(environment.get("path")))
        
        return self._env_manager
    
    def run(self, *args: str, capture_output: bool = False, **kwargs) -> None:  # noqa: ANN003
        """
        Run a command in the project environment.
        
        Args:
            *args: Positional arguments for the command
            capture_output: Whether to capture command output (default: False)
            **kwargs: Keyword arguments for the command
            
        """
        # Set the current working directory to the project path if not specified
        if 'cwd' not in kwargs:
            kwargs['cwd'] = str(self.project_path)
        self.get_env_manager().get_runner().run(*args, capture_output=capture_output, **kwargs)
        
    ### Common methods between projects
    def install(self) -> bool:
        """
        Install the project.
        
        Returns:
            True if installation was successful, False otherwise

        """
        try:
            # Install the project in development mode
            self.run("pip", "install", "-e", ".[dev]")
            print("✅ Project successfully installed.")
            return True
        except Exception as e:
            print(f"❌ Project installation failed: {e}")
            return False
    
    def build(self) -> bool:
        """
        Build the project.
        
        Returns:
            True if build was successful, False otherwise

        """      
        try:
            # Ensure setuptools is installed
            pck_manager = PackageManager(self.get_env_manager().get_runner())
            
            if not pck_manager.is_installed("setuptools"):
                pck_manager.install("setuptools")
                
            if not pck_manager.is_installed("wheel"):
                pck_manager.install("wheel")
            
            # Build the project using setup.py and set the build output folder to the project path
            self.run("python", "setup.py", "build", "--build-base", str(self.project_path / "build"))
            print("✅ Build finished.")
            return True
        except Exception as e:
            print(f"❌ Build failed: {e}")
            return False
        
    def test(self) -> bool:
        """
        Run tests.
        
        Returns:
            True if tests passed, False otherwise

        """
        # Check if the runner has inline_output attribute and save its original value
        runner = self.get_env_manager().get_runner()
        if hasattr(runner, 'inline_output'):
            runner.inline_output = 0
            
        try:
            # Ask for test options
            test_option = questionary.select(
                "Select test option:",
                choices=[
                    "All tests",
                    "Failed tests only",
                    "With coverage",
                    "With parameters"
                ]
            ).ask()
                        
            if test_option == "All tests":
                runner.run("pytest", ".", "--tb=line", "-v", "--disable-warnings", 
                           capture_output=False, cwd=str(self.project_path))
            elif test_option == "Failed tests only":
                runner.run("pytest", ".", "--tb=line", "-v", "--last-failed", "--disable-warnings", 
                           capture_output=False, cwd=str(self.project_path))
            elif test_option == "With coverage":
                runner.run("pytest", ".", "--tb=line", "-v", "--cov", "--disable-warnings", 
                           capture_output=False, cwd=str(self.project_path))
            elif test_option == "With parameters":
                parameters = questionary.text("Enter the parameters you want to use for testing:").ask()
                runner.run("pytest", ".", *parameters.split(), capture_output=False, cwd=str(self.project_path))
            
            print("✅ Test finished.")
            return True
        except Exception as e:
            print(f"⚠️ Tests failed: {e}")
            print("⚠️ Tip. Ensure all dependencies are well configured and run install.")
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
                import shutil
                shutil.rmtree(build_dir)
                if build_dir.exists():
                   print("⚠️ Unable to delete build folder.") 
                
            # Remove dist directory
            dist_dir = self.project_path / "dist"
            if dist_dir.exists():
                import shutil
                shutil.rmtree(dist_dir)
                if dist_dir.exists():
                   print("⚠️ Unable to delete dist folder.") 
                
            # Remove egg-info directory
            for egg_info_dir in self.project_path.glob("*.egg-info"):
                import shutil
                shutil.rmtree(egg_info_dir)
                if egg_info_dir.exists():
                   print("⚠️ Unable to delete egg-info folder.") 
                
            print("✅ Build artifacts cleaned successfully")
            return True
        except Exception as e:
            print(f"❌ Cleaning failed: {e}")
            return False

    def get_common_menu_items(self) -> List[Dict[str, Any]]:
        """
        Get common menu items available for all project types.
        
        Returns:
            A list of common menu item dictionaries

        """
        # Get configuration
        config_manager = ConfigManager.get_config(self.project_path)
        template_vars = config_manager.get("template", {}).get("variables", {})
        
        # Common menu items
        common_menus = [
            {
                "name": "Install",
                "description": "Install the project in development mode with all dependencies, "
                "making it ready for testing and development work",
                "callback": self.install,
                "icon": "📥",
                "pause_after_execution": True,  # Pause after installation to show output
                "redirect": "back"  # Return to main menu after pressing Enter
            },
            {
                "name": "Build",
                "description": "Build the project into distributable packages, "
                "creating artifacts ready for release and distribution",
                "callback": self.build,
                "icon": "🏗️",
                "pause_after_execution": True,  # Pause after build to show output
                "redirect": "back"  # Return to main menu after pressing Enter
            },
            {
                "name": "Clean",
                "description": "Clean all build artifacts, removing build directories, distribution files, "
                "and egg-info to ensure a fresh build environment",
                "callback": self.clean,
                "icon": "🧹",
                "pause_after_execution": True,  # Pause after cleaning to show output
                "redirect": "back"  # Return to main menu after pressing Enter
            }
        ]
        
        # Add Test menu item if testing is enabled
        if template_vars.get("enable_testing", "no") == "yes":
            common_menus.insert(1, {
                "name": "Test",
                "description": "Run project tests with various options including all tests, failed tests only, "
                "with coverage reports, or with custom parameters",
                "callback": self.test,
                "icon": "🧪",
                "pause_after_execution": True,  # Pause after tests to show output
                "redirect": "back"  # Return to main menu after pressing Enter
            })
        
        return common_menus
        
    ## End common methods

    @abstractmethod
    def get_menus(self) -> List[Dict[str, Any]]:
        """
        Get the menu actions available for this project type.
        
        Returns:
            A list of menu action dictionaries

        """
        pass
        
    def get_env_config(self) -> Dict[str, Any]:
        """
        Get environment configuration for this project.
        
        Returns:
            A dictionary with environment configuration

        """
        env_manager = self.get_env_manager()
        return {
            "name": env_manager.env.name,
            "root": str(env_manager.env.root),
            "is_virtual": env_manager.env.is_virtual,
            "python": str(env_manager.env.python)
        }
