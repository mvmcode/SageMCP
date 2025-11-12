"""HTTP client for SageMCP API."""

import sys
from typing import Any, Dict, List, Optional

import httpx
from rich.console import Console

from sage_mcp.cli.config import ProfileConfig

console = Console()


class APIError(Exception):
    """API error exception."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class SageMCPClient:
    """HTTP client for SageMCP API."""

    def __init__(self, config: ProfileConfig):
        """Initialize API client.

        Args:
            config: Profile configuration
        """
        self.config = config
        self.base_url = config.base_url.rstrip("/")
        self.timeout = config.timeout
        self.api_key = config.api_key

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers.

        Returns:
            Dictionary of headers
        """
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle API response.

        Args:
            response: HTTP response

        Returns:
            Response data

        Raises:
            APIError: On API errors
        """
        try:
            response.raise_for_status()
            if response.status_code == 204:
                return None
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                message = error_data.get("detail", str(e))
            except Exception:
                message = str(e)
            raise APIError(message, e.response.status_code)
        except Exception as e:
            raise APIError(f"Request failed: {e}")

    # Tenant operations
    def list_tenants(self) -> List[Dict[str, Any]]:
        """List all tenants."""
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(
                f"{self.base_url}/api/v1/admin/tenants", headers=self._get_headers()
            )
            return self._handle_response(response)

    def get_tenant(self, tenant_slug: str) -> Dict[str, Any]:
        """Get tenant details."""
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(
                f"{self.base_url}/api/v1/admin/tenants/{tenant_slug}",
                headers=self._get_headers(),
            )
            return self._handle_response(response)

    def create_tenant(
        self,
        slug: str,
        name: str,
        description: Optional[str] = None,
        contact_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new tenant."""
        data = {"slug": slug, "name": name}
        if description:
            data["description"] = description
        if contact_email:
            data["contact_email"] = contact_email

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url}/api/v1/admin/tenants",
                json=data,
                headers=self._get_headers(),
            )
            return self._handle_response(response)

    def update_tenant(
        self,
        tenant_slug: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        contact_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update tenant."""
        # Get current tenant data
        current = self.get_tenant(tenant_slug)

        data = {
            "slug": current["slug"],
            "name": name or current["name"],
        }
        if description is not None:
            data["description"] = description
        if contact_email is not None:
            data["contact_email"] = contact_email

        with httpx.Client(timeout=self.timeout) as client:
            response = client.put(
                f"{self.base_url}/api/v1/admin/tenants/{tenant_slug}",
                json=data,
                headers=self._get_headers(),
            )
            return self._handle_response(response)

    def delete_tenant(self, tenant_slug: str) -> Dict[str, Any]:
        """Delete tenant."""
        with httpx.Client(timeout=self.timeout) as client:
            response = client.delete(
                f"{self.base_url}/api/v1/admin/tenants/{tenant_slug}",
                headers=self._get_headers(),
            )
            return self._handle_response(response)

    # Connector operations
    def list_connectors(self, tenant_slug: str) -> List[Dict[str, Any]]:
        """List connectors for a tenant."""
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(
                f"{self.base_url}/api/v1/admin/tenants/{tenant_slug}/connectors",
                headers=self._get_headers(),
            )
            return self._handle_response(response)

    def get_connector(self, tenant_slug: str, connector_id: str) -> Dict[str, Any]:
        """Get connector details."""
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(
                f"{self.base_url}/api/v1/admin/tenants/{tenant_slug}/connectors/{connector_id}",
                headers=self._get_headers(),
            )
            return self._handle_response(response)

    def create_connector(
        self,
        tenant_slug: str,
        connector_type: str,
        name: str,
        description: Optional[str] = None,
        configuration: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new connector."""
        data = {"connector_type": connector_type, "name": name}
        if description:
            data["description"] = description
        if configuration:
            data["configuration"] = configuration

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url}/api/v1/admin/tenants/{tenant_slug}/connectors",
                json=data,
                headers=self._get_headers(),
            )
            return self._handle_response(response)

    def update_connector(
        self,
        tenant_slug: str,
        connector_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        configuration: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update connector."""
        # Get current connector data
        current = self.get_connector(tenant_slug, connector_id)

        data = {
            "connector_type": current["connector_type"],
            "name": name or current["name"],
        }
        if description is not None:
            data["description"] = description
        if configuration is not None:
            data["configuration"] = configuration

        with httpx.Client(timeout=self.timeout) as client:
            response = client.put(
                f"{self.base_url}/api/v1/admin/tenants/{tenant_slug}/connectors/{connector_id}",
                json=data,
                headers=self._get_headers(),
            )
            return self._handle_response(response)

    def delete_connector(self, tenant_slug: str, connector_id: str) -> Dict[str, Any]:
        """Delete connector."""
        with httpx.Client(timeout=self.timeout) as client:
            response = client.delete(
                f"{self.base_url}/api/v1/admin/tenants/{tenant_slug}/connectors/{connector_id}",
                headers=self._get_headers(),
            )
            return self._handle_response(response)

    def toggle_connector(self, tenant_slug: str, connector_id: str) -> Dict[str, Any]:
        """Toggle connector enabled status."""
        with httpx.Client(timeout=self.timeout) as client:
            response = client.patch(
                f"{self.base_url}/api/v1/admin/tenants/{tenant_slug}/connectors/{connector_id}/toggle",
                headers=self._get_headers(),
            )
            return self._handle_response(response)

    # OAuth operations
    def list_oauth_providers(self) -> List[Dict[str, Any]]:
        """List available OAuth providers."""
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(
                f"{self.base_url}/api/v1/oauth/providers", headers=self._get_headers()
            )
            return self._handle_response(response)

    def list_oauth_credentials(self, tenant_slug: str) -> List[Dict[str, Any]]:
        """List OAuth credentials for a tenant."""
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(
                f"{self.base_url}/api/v1/oauth/{tenant_slug}/auth",
                headers=self._get_headers(),
            )
            return self._handle_response(response)

    def revoke_oauth_credential(self, tenant_slug: str, provider: str) -> Dict[str, Any]:
        """Revoke OAuth credentials."""
        with httpx.Client(timeout=self.timeout) as client:
            response = client.delete(
                f"{self.base_url}/api/v1/oauth/{tenant_slug}/auth/{provider}",
                headers=self._get_headers(),
            )
            return self._handle_response(response)

    def get_oauth_auth_url(self, tenant_slug: str, provider: str) -> str:
        """Get OAuth authorization URL."""
        return f"{self.base_url}/api/v1/oauth/{tenant_slug}/auth/{provider}"

    # MCP operations
    def get_mcp_info(self, tenant_slug: str, connector_id: str) -> Dict[str, Any]:
        """Get MCP server info."""
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(
                f"{self.base_url}/api/v1/{tenant_slug}/connectors/{connector_id}/mcp/info",
                headers=self._get_headers(),
            )
            return self._handle_response(response)

    def mcp_request(
        self,
        tenant_slug: str,
        connector_id: str,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        request_id: int = 1,
    ) -> Dict[str, Any]:
        """Send MCP JSON-RPC request."""
        data = {"jsonrpc": "2.0", "id": request_id, "method": method}
        if params:
            data["params"] = params

        headers = self._get_headers()
        headers["Accept"] = "application/json"

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url}/api/v1/{tenant_slug}/connectors/{connector_id}/mcp",
                json=data,
                headers=headers,
            )
            return self._handle_response(response)

    def list_mcp_tools(self, tenant_slug: str, connector_id: str) -> List[Dict[str, Any]]:
        """List MCP tools."""
        response = self.mcp_request(tenant_slug, connector_id, "tools/list")
        if "result" in response:
            return response["result"].get("tools", [])
        return []

    def list_mcp_resources(
        self, tenant_slug: str, connector_id: str
    ) -> List[Dict[str, Any]]:
        """List MCP resources."""
        response = self.mcp_request(tenant_slug, connector_id, "resources/list")
        if "result" in response:
            return response["result"].get("resources", [])
        return []

    def call_mcp_tool(
        self, tenant_slug: str, connector_id: str, tool_name: str, arguments: Dict[str, Any]
    ) -> Any:
        """Call MCP tool."""
        response = self.mcp_request(
            tenant_slug, connector_id, "tools/call", {"name": tool_name, "arguments": arguments}
        )
        if "result" in response:
            return response["result"]
        elif "error" in response:
            raise APIError(response["error"].get("message", "Tool call failed"))
        return response

    def read_mcp_resource(
        self, tenant_slug: str, connector_id: str, uri: str
    ) -> str:
        """Read MCP resource."""
        response = self.mcp_request(
            tenant_slug, connector_id, "resources/read", {"uri": uri}
        )
        if "result" in response:
            contents = response["result"].get("contents", [])
            if contents:
                return contents[0].get("text", "")
        elif "error" in response:
            raise APIError(response["error"].get("message", "Resource read failed"))
        return ""

    def ping(self) -> bool:
        """Ping the server to check connectivity."""
        try:
            with httpx.Client(timeout=5) as client:
                response = client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception:
            return False
