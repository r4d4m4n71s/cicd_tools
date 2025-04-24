"""
Template management for CICD Tools.

This package provides template management functionality for CICD Tools, including:
- TemplateManager: For handling project creation and updates using Copier
- Template utilities: Helper functions for template operations
"""

from cicd_tools.templates.template_manager import TemplateManager
from cicd_tools.templates.template_utils import (
    detect_template_type,
    process_template_variables,
)

__all__ = ["TemplateManager", "process_template_variables", "detect_template_type"]