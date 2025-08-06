"""Backward compatibility layer for plugin access.

The project previously exposed plugin-related utilities from a
``plugin_system`` module.  Downstream code may still import from this
location, so we re-export :class:`PluginRegistry` here.
"""

from plugin_registry import PluginRegistry

__all__ = ["PluginRegistry"]
