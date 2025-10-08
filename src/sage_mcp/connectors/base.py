"""Base connector interface for plugin system."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol

from mcp import types

from ..models.connector import Connector
from ..models.oauth_credential import OAuthCredential


class ConnectorPlugin(Protocol):
    """Protocol for connector plugins."""

    @property
    def name(self) -> str:
        """Connector name."""
        ...

    @property
    def display_name(self) -> str:
        """Human-readable display name."""
        ...

    @property
    def description(self) -> str:
        """Connector description."""
        ...

    @property
    def requires_oauth(self) -> bool:
        """Whether this connector requires OAuth authentication."""
        ...

    async def get_tools(self, connector: Connector, oauth_cred: Optional[OAuthCredential] = None) -> List[types.Tool]:
        """Get available tools for this connector."""
        ...

    async def get_resources(self, connector: Connector, oauth_cred: Optional[OAuthCredential] = None) -> List[types.Resource]:
        """Get available resources for this connector."""
        ...

    async def execute_tool(
        self,
        connector: Connector,
        tool_name: str,
        arguments: Dict[str, Any],
        oauth_cred: Optional[OAuthCredential] = None
    ) -> str:
        """Execute a tool action."""
        ...

    async def read_resource(
        self,
        connector: Connector,
        resource_path: str,
        oauth_cred: Optional[OAuthCredential] = None
    ) -> str:
        """Read a resource."""
        ...


class BaseConnector(ABC):
    """Base class for all connectors."""

    def __init__(self):
        self._name = self.__class__.__name__.lower().replace("connector", "")

    @property
    def name(self) -> str:
        """Connector name."""
        return self._name

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable display name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Connector description."""
        pass

    @property
    @abstractmethod
    def requires_oauth(self) -> bool:
        """Whether this connector requires OAuth authentication."""
        pass

    @abstractmethod
    async def get_tools(self, connector: Connector, oauth_cred: Optional[OAuthCredential] = None) -> List[types.Tool]:
        """Get available tools for this connector."""
        pass

    @abstractmethod
    async def get_resources(self, connector: Connector, oauth_cred: Optional[OAuthCredential] = None) -> List[types.Resource]:
        """Get available resources for this connector."""
        pass

    @abstractmethod
    async def execute_tool(
        self,
        connector: Connector,
        tool_name: str,
        arguments: Dict[str, Any],
        oauth_cred: Optional[OAuthCredential] = None
    ) -> str:
        """Execute a tool action."""
        pass

    @abstractmethod
    async def read_resource(
        self,
        connector: Connector,
        resource_path: str,
        oauth_cred: Optional[OAuthCredential] = None
    ) -> str:
        """Read a resource."""
        pass

    def validate_oauth_credential(self, oauth_cred: OAuthCredential) -> bool:
        """Validate OAuth credentials for this connector."""
        if not self.requires_oauth:
            return True

        if not oauth_cred or not oauth_cred.is_active:
            return False

        # Check if token is expired
        if oauth_cred.is_expired:
            return False

        return True

    async def _make_authenticated_request(
        self,
        method: str,
        url: str,
        oauth_cred: OAuthCredential,
        **kwargs
    ) -> Any:
        """Make an authenticated HTTP request using OAuth credentials."""
        import httpx

        if not self.validate_oauth_credential(oauth_cred):
            raise ValueError("Invalid or expired OAuth credentials")

        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {oauth_cred.access_token}"
        kwargs["headers"] = headers

        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
