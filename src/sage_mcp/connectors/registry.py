"""Connector registry for managing available connectors."""

import json
from typing import Dict, List, Optional, Type, TYPE_CHECKING

from ..models.connector import ConnectorType, ConnectorRuntimeType
from .base import BaseConnector

if TYPE_CHECKING:
    from ..models.connector import Connector


class ConnectorRegistry:
    """Registry for managing connector plugins."""

    def __init__(self):
        self._connectors: Dict[str, BaseConnector] = {}
        self._connector_types: Dict[ConnectorType, str] = {}

    def register(self, connector_type: ConnectorType, connector_class: Type[BaseConnector]):
        """Register a connector plugin."""
        connector_instance = connector_class()
        connector_name = connector_instance.name

        self._connectors[connector_name] = connector_instance
        self._connector_types[connector_type] = connector_name

        print(f"Registered connector: {connector_name} ({connector_type.value})")

    def get_connector(self, connector_type: ConnectorType) -> Optional[BaseConnector]:
        """Get a connector instance by type (for native connectors only)."""
        connector_name = self._connector_types.get(connector_type)
        if not connector_name:
            return None

        return self._connectors.get(connector_name)

    def get_connector_for_config(self, connector_config: "Connector") -> Optional[BaseConnector]:
        """Get connector instance based on connector configuration.

        This method checks the runtime_type and returns either:
        - A native Python connector (for runtime_type == NATIVE)
        - A GenericMCPConnector (for external runtime types)

        Args:
            connector_config: Connector model instance with runtime configuration

        Returns:
            BaseConnector instance (either native or GenericMCPConnector)
        """
        # Check if this is an external MCP server
        if connector_config.runtime_type != ConnectorRuntimeType.NATIVE:
            # Import here to avoid circular dependency
            from ..runtime import GenericMCPConnector

            # Parse runtime command
            try:
                command = (
                    json.loads(connector_config.runtime_command)
                    if connector_config.runtime_command
                    else []
                )
            except json.JSONDecodeError:
                raise Exception(
                    f"Invalid runtime_command JSON: {connector_config.runtime_command}"
                )

            if not command:
                raise Exception(
                    "runtime_command is required for external MCP connectors"
                )

            # Return generic wrapper (will be started lazily)
            return GenericMCPConnector(
                runtime_type=connector_config.runtime_type.value,
                command=command,
                env=connector_config.runtime_env or {},
                working_dir=connector_config.package_path,
            )

        # Fallback to native connector
        return self.get_connector(connector_config.connector_type)

    def get_connector_by_name(self, name: str) -> Optional[BaseConnector]:
        """Get a connector instance by name."""
        return self._connectors.get(name)

    def list_connectors(self) -> List[str]:
        """List all registered connector names."""
        return list(self._connectors.keys())

    def list_connector_types(self) -> List[ConnectorType]:
        """List all registered connector types."""
        return list(self._connector_types.keys())

    def get_connector_info(self, connector_type: ConnectorType) -> Optional[Dict[str, str]]:
        """Get connector information."""
        connector = self.get_connector(connector_type)
        if not connector:
            return None

        return {
            "name": connector.name,
            "display_name": connector.display_name,
            "description": connector.description,
            "requires_oauth": connector.requires_oauth,
            "type": connector_type.value
        }


# Global connector registry instance
connector_registry = ConnectorRegistry()


def register_connector(connector_type: ConnectorType):
    """Decorator to register a connector."""
    def decorator(connector_class: Type[BaseConnector]):
        connector_registry.register(connector_type, connector_class)
        return connector_class
    return decorator
