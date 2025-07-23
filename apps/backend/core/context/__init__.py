"""
Context management module
"""
# Force use of simple manager to avoid llama-index dependency issues
from .manager_simple import SimpleContextManager as ContextManager
from .manager_simple import context_manager

__all__ = ["ContextManager", "context_manager"]