"""
Sage MCP: Multi-tenant MCP (Model Context Protocol) server platform.

A scalable platform for hosting MCP servers with multi-tenant support,
OAuth integration, and connector plugins for various services.
"""

__version__ = "0.1.0"
__author__ = "Sage MCP Team"
__email__ = "contact@example.com"

from .config import Settings, get_settings

__all__ = ["Settings", "get_settings", "__version__"]
