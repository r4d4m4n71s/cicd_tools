"""
Jinja utilities for CICD Tools.

This module provides utility functions for Jinja template expressions.
"""

from typing import Any, Dict


def evaluate_jinja_expression(expression: str, variables: Dict[str, Any], data: Dict[str, Any] = None) -> Any:
    """
    Evaluate a Jinja expression based on the current variables and data.
    
    Args:
        expression: Jinja expression to evaluate
        variables: Current variables
        data: Additional data for evaluation (optional)
        
    Returns:
        Evaluated value
        
    """
    if data is None:
        data = {}
        
    # Extract the expression from Jinja delimiters if present
    expr = expression.strip()
    if expr.startswith("{{") and expr.endswith("}}"):
        expr = expr[2:-2].strip()
    
    # Simple evaluation of common expressions
    # This is a basic implementation that handles common cases
    
    # Handle direct variable references (e.g., {{ use_github_repo }})
    if expr in variables:
        return variables[expr]
    elif expr in data:
        return data[expr]
    
    # Handle equality checks (var == 'value')
    if " == " in expr:
        parts = expr.split(" == ")
        var_to_check = parts[0].strip()
        expected_value = parts[1].strip().strip("'\"")
        
        if var_to_check in variables:
            return variables[var_to_check] == expected_value
        elif var_to_check in data:
            return data[var_to_check] == expected_value
        
        return False
    
    # Handle inequality checks (var != 'value')
    if " != " in expr:
        parts = expr.split(" != ")
        var_to_check = parts[0].strip()
        expected_value = parts[1].strip().strip("'\"")
        
        if var_to_check in variables:
            return variables[var_to_check] != expected_value
        elif var_to_check in data:
            return data[var_to_check] != expected_value
        
        return False
    
    # Handle ternary expressions (e.g., {{ 'yes' if use_github_repo == 'yes' else 'no' }})
    if " if " in expr and " else " in expr:
        # Split the expression into parts
        parts = expr.split(" if ")
        true_value = parts[0].strip().strip("'\"")
        
        condition_parts = parts[1].split(" else ")
        condition = condition_parts[0].strip()
        false_value = condition_parts[1].strip().strip("'\"")
        
        # Evaluate the condition recursively
        condition_result = evaluate_jinja_expression(condition, variables, data)
        
        return true_value if condition_result else false_value
    
    # If we can't evaluate the expression, return it as is
    return expression
