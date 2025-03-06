"""
Environment management for CICD Tools.

This module provides functionality for managing Python environments
using the env_manager library.
"""

import logging
from pathlib import Path
from typing import Optional, Any, Union, Dict, List
import subprocess

# Import from the external library
from env_manager import Environment, EnvManager as BaseEnvManager

# Re-export Environment class for backward compatibility
__all__ = ["Environment", "EnvManager"]

class EnvManager(BaseEnvManager):
    """
    Environment Manager for handling Python environments.
    
    This class extends the EnvManager from python-env-manager library
    to maintain interface compatibility with existing code.
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
        super().__init__(path, clear, logger)