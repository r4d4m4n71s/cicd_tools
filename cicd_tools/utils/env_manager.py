"""
Environment management for CICD Tools.

This module provides functionality for managing Python environments,
adapted from the existing env_manager module.
"""

import os
import sys
import re
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Optional, Any, Dict, List, Union

class Environment:
    """
    Python environment information and paths.
    
    Represents a Python environment (virtual or local) with all its relevant paths
    and properties.
    
    Attributes:
        name: Environment name (derived from directory name)
        root: Root directory of the environment
        bin: Directory containing executables (Scripts on Windows, bin on Unix)
        lib: Directory containing libraries
        python: Path to the Python executable
        is_virtual: Whether the environment is a virtual environment
    """
    
    def __init__(self, path: Optional[Union[str, Path]] = None):
        """
        Initialize an Environment instance.
        
        Args:
            path: Path to the environment root directory
        """
        # Determine environment root path
        self.root = os.path.abspath(
            str(path) if path else os.environ.get("VIRTUAL_ENV") or sys.prefix
        )
        
        # Set platform-specific paths
        is_windows = os.name == "nt"
        self.bin = os.path.join(self.root, "Scripts" if is_windows else "bin")
        self.lib = os.path.join(self.root, "Lib" if is_windows else "lib")
        self.python = os.path.join(self.bin, "python.exe" if is_windows else "python")
        
        # Use system executable for non-virtual environments
        self.is_virtual = not self._is_local(self.root)
        if not self.is_virtual:
            self.python = sys.executable
                
        # Extract environment name from directory
        self.name = os.path.basename(self.root)

    @staticmethod
    def _is_local(path: str) -> bool:
        """
        Determine if a path points to a local Python installation.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path points to a local Python installation, False otherwise
        """
        patterns = {
            "nt": [  # Windows patterns
                r"Python\d+",
                r"AppData\\Local\\Programs\\Python\\Python\d+",
                r"(Ana|Mini)conda3"
            ],
            "posix": [  # Unix patterns
                r"/usr(/local)?$",
                r"/usr(/local)?/bin$",
                r"/opt/homebrew/bin$",
                r"/Library/Frameworks/Python\.framework",
                r"/(ana|mini)conda3?/bin$"
            ]
        }
        os_patterns = patterns.get(os.name, patterns["posix"])
        return any(re.search(pattern, path) for pattern in os_patterns)


class EnvManager:
    """
    Environment Manager for handling Python environments.
    
    Provides functionality to manage both local and virtual Python environments,
    including creation, activation, deactivation, and package management.
    """
    
    def __init__(
        self,
        path: Optional[Union[str, Path]] = None,
        clear: bool = False,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """
        Initialize an EnvManager instance.
        
        Args:
            path: Path to the environment root directory
            clear: Whether to clear the environment if it exists
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.env = Environment(path)
        
        # Create virtual environment if needed
        if self.env.is_virtual and clear:
            self.remove()
            self._create_venv()

    def _create_venv(self) -> None:
        """
        Create a virtual environment at the specified path.
        
        Raises:
            RuntimeError: If the virtual environment creation fails
        """
        try:
            # Create the directory for the environment if it doesn't exist
            os.makedirs(self.env.root, exist_ok=True)
            
            # Use the venv module to create the environment
            subprocess.run(
                [sys.executable, "-m", "venv", self.env.root],
                check=True,
                capture_output=True,
                text=True
            )
            self.logger.info(f"Created virtual environment at {self.env.root}")
        except Exception as e:
            error_msg = f"Failed to create virtual environment: {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def remove(self) -> None:
        """
        Remove the virtual environment if it exists.
        
        Raises:
            RuntimeError: If the virtual environment removal fails
        """
        if not self.env.is_virtual:
            return
            
        try:
            if os.path.exists(self.env.root):
                shutil.rmtree(self.env.root)
                self.logger.info(f"Removed virtual environment at {self.env.root}")
        except Exception as e:
            self.logger.error(f"Failed to remove virtual environment: {e}")
            raise RuntimeError(f"Failed to remove virtual environment: {e}") from e
    
    def run(self, *cmd_args: str, capture_output: bool = True, **kwargs: Any) -> subprocess.CompletedProcess:
        """
        Execute a command in the environment context.
        
        Args:
            *cmd_args: Command and arguments as separate strings
            capture_output: Whether to capture command output
            **kwargs: Additional arguments to pass to subprocess.run
            
        Returns:
            Result of the command execution
            
        Raises:
            ValueError: If no command is provided
            RuntimeError: If command execution fails
        """
        if not cmd_args:
            raise ValueError("No command provided")
            
        # Set default kwargs
        kwargs.setdefault('text', True)
        kwargs.setdefault('check', True)
        kwargs.setdefault('capture_output', capture_output)
        
        try:
            is_windows = os.name == "nt"
            cmd_list = [str(arg) for arg in cmd_args]
            
            # Determine command execution strategy
            if self.env.is_virtual:
                # Virtual environment
                if cmd_list and cmd_list[0].lower() == 'python':
                    # Use environment's Python executable
                    shell_cmd = [self.env.python] + cmd_list[1:]
                else:
                    # Look for command in environment's bin directory
                    cmd_path = os.path.join(
                        self.env.bin,
                        cmd_list[0] + (".exe" if is_windows else "")
                    )
                    if not os.path.exists(cmd_path):
                        cmd_path = cmd_list[0]
                    shell_cmd = [cmd_path] + cmd_list[1:]
                
                kwargs['shell'] = False
            else:
                # Local Python
                if cmd_list and cmd_list[0].lower() == 'python':
                    # Use environment's Python executable
                    shell_cmd = [self.env.python] + cmd_list[1:]
                else:
                    # Use command directly
                    shell_cmd = cmd_list
                
                kwargs['shell'] = False
            
            # Execute command
            result = subprocess.run(shell_cmd, **kwargs)
            self.logger.info(f"Successfully executed command: {' '.join(cmd_list)}")
            return result
            
        except subprocess.CalledProcessError as e:
            # Let CalledProcessError propagate for proper error handling
            self.logger.error(f"Command failed: {' '.join(cmd_list)}, return code: {e.returncode}")
            if hasattr(e, 'stdout') and e.stdout:
                self.logger.error(f"Command stdout: {e.stdout}")
            if hasattr(e, 'stderr') and e.stderr:
                self.logger.error(f"Command stderr: {e.stderr}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to execute command: {e}")
            raise RuntimeError(f"Failed to execute command: {e}") from e
    
    def install_pkg(self, package: str) -> None:
        """
        Install a package in the Python environment.
        
        Args:
            package: Package to install
            
        Raises:
            RuntimeError: If package installation fails
        """
        try:
            self.run("pip", "install", package)
            self.logger.info(f"Installed package: {package}")
        except Exception as e:
            self.logger.error(f"Failed to install package {package}: {e}")
            raise RuntimeError(f"Failed to install package {package}: {e}") from e