"""
Context management module
"""
# Use simple manager to avoid llama-index issues
try:
    from .manager import ContextManager, context_manager
except ImportError:
    # Fallback to simple implementation
    from .manager_simple import SimpleContextManager as ContextManager
    from .manager_simple import context_manager

__all__ = ["ContextManager", "context_manager"]