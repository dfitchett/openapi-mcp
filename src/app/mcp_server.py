"""MCP server implementation for OpenAPI specifications."""

import json
import logging
from collections.abc import Sequence
from typing import Any

from mcp.server import Server
from mcp.types import Resource

from app.config import API_CONFIGS, SERVER_NAME, URI_SCHEME

logger = logging.getLogger(__name__)


class OpenAPIMCPServer:
    """MCP server that exposes OpenAPI specifications as resources."""

    def __init__(
        self,
        specs: dict[str, dict[str, Any]],
        server_name: str = SERVER_NAME,
        uri_scheme: str = URI_SCHEME,
    ) -> None:
        """Initialize the MCP server.

        Args:
            specs: Dictionary mapping API IDs to their OpenAPI specifications
            server_name: Name of the MCP server
            uri_scheme: URI scheme to use for resources (e.g., 'openapi', 'va')
        """
        self.specs = specs
        self.server_name = server_name
        self.uri_scheme = uri_scheme
        self.server = Server(server_name)
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register MCP server handlers for resources."""

        @self.server.list_resources()  # type: ignore[no-untyped-call, misc]
        async def list_resources() -> Sequence[Resource]:
            """List all available OpenAPI specification resources."""
            resources = []
            for api_id, api_config in API_CONFIGS.items():
                if api_id in self.specs:
                    resources.append(
                        Resource(
                            uri=f'{self.uri_scheme}://api/{api_id}/openapi',
                            name=f'{api_config["name"]} - OpenAPI Specification',
                            mimeType='application/json',
                            description=api_config['description'],
                        )
                    )
            return resources

        @self.server.read_resource()  # type: ignore[no-untyped-call, misc]
        async def read_resource(uri: str) -> str:
            """Read a specific OpenAPI specification resource.

            Args:
                uri: Resource URI in format '{scheme}://api/{api_id}/openapi'

            Returns:
                The OpenAPI specification as a JSON string
            """
            # Convert URI to string (in case it's an AnyUrl object from Pydantic)
            uri_str = str(uri)

            # Parse URI to extract API ID
            expected_prefix = f'{self.uri_scheme}://api/'
            if not uri_str.startswith(expected_prefix):
                raise ValueError(f'Invalid URI format: {uri_str}. Expected prefix: {expected_prefix}')

            # Extract API ID from URI (e.g., 'openapi://api/benefits-claims-v2/openapi' -> 'benefits-claims-v2')
            parts = uri_str.replace(expected_prefix, '').split('/')
            if len(parts) < 2 or parts[1] != 'openapi':
                raise ValueError(f'Invalid URI format: {uri_str}')

            api_id = parts[0]

            if api_id not in self.specs:
                raise ValueError(f'Unknown API: {api_id}')

            spec = self.specs[api_id]
            return json.dumps(spec, indent=2)

    def get_server(self) -> Server:
        """Get the MCP server instance.

        Returns:
            The configured MCP Server instance
        """
        return self.server
