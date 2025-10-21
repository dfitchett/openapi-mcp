"""Tests for the mcp_server module."""

from typing import Any

import pytest

from app.mcp_server import OpenAPIMCPServer


@pytest.fixture
def sample_specs() -> dict[str, dict[str, Any]]:
    """Sample OpenAPI specifications for testing."""
    return {
        'benefits-claims-v2': {
            'openapi': '3.0.1',
            'info': {'title': 'Benefits Claims API', 'version': 'v2'},
            'paths': {},
        },
        'benefits-documents-v1': {
            'openapi': '3.0.1',
            'info': {'title': 'Benefits Documents API', 'version': 'v1'},
            'paths': {},
        },
    }


@pytest.fixture
def mcp_server(sample_specs: dict[str, dict[str, Any]]) -> OpenAPIMCPServer:
    """Create an OpenAPIMCPServer instance for testing."""
    return OpenAPIMCPServer(sample_specs)


class TestOpenAPIMCPServer:
    """Tests for the OpenAPIMCPServer class."""

    def test_init(self, mcp_server: OpenAPIMCPServer, sample_specs: dict[str, dict[str, Any]]) -> None:
        """Test that OpenAPIMCPServer initializes correctly."""
        assert mcp_server.specs == sample_specs
        assert mcp_server.server is not None
        assert mcp_server.server_name is not None
        assert mcp_server.uri_scheme is not None

    def test_get_server(self, mcp_server: OpenAPIMCPServer) -> None:
        """Test that get_server returns the server instance."""
        server = mcp_server.get_server()
        assert server is not None
        assert server == mcp_server.server

    def test_specs_loaded(self, mcp_server: OpenAPIMCPServer, sample_specs: dict[str, dict[str, Any]]) -> None:
        """Test that specs are properly loaded into the server."""
        assert mcp_server.specs == sample_specs
        assert len(mcp_server.specs) == 2
        assert 'benefits-claims-v2' in mcp_server.specs
        assert 'benefits-documents-v1' in mcp_server.specs
