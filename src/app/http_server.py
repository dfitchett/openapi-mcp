"""HTTP/SSE server implementation for the OpenAPI MCP server."""

import asyncio
import logging
import sys
from collections.abc import Awaitable, Callable, MutableMapping
from typing import Any

from mcp.server.sse import SseServerTransport

from app.config import DEBUG, SERVER_NAME
from app.mcp_server import OpenAPIMCPServer
from app.spec_fetcher import SpecFetcher

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr,
)

logger = logging.getLogger(__name__)

# Global instances (initialized on first request)
_mcp_server: OpenAPIMCPServer | None = None
_sse_transport: SseServerTransport | None = None
_initialization_lock = asyncio.Lock()


async def initialize_server() -> tuple[OpenAPIMCPServer, SseServerTransport]:
    """Initialize the MCP server and SSE transport.

    Returns:
        Tuple of (mcp_server, sse_transport)
    """
    global _mcp_server, _sse_transport

    if _mcp_server is not None and _sse_transport is not None:
        return _mcp_server, _sse_transport

    async with _initialization_lock:
        # Double-check after acquiring lock
        if _mcp_server is not None and _sse_transport is not None:
            return _mcp_server, _sse_transport

        logger.info(f'Initializing {SERVER_NAME} MCP server...')

        # Initialize spec fetcher and fetch all API specifications
        spec_fetcher = SpecFetcher()
        logger.info('Fetching OpenAPI specifications...')
        specs = await spec_fetcher.fetch_all_specs()
        logger.info(f'Successfully fetched {len(specs)} API specifications')

        # Initialize MCP server
        _mcp_server = OpenAPIMCPServer(specs)

        # Create SSE transport (must be persistent across requests)
        _sse_transport = SseServerTransport('/messages')

        logger.info('MCP server and SSE transport initialized successfully')

        return _mcp_server, _sse_transport


async def handle_sse(
    scope: dict[str, Any],
    receive: Callable[[], Awaitable[dict[str, Any]]],
    send: Callable[[MutableMapping[str, Any]], Awaitable[None]],
) -> None:
    """Handle SSE connection for MCP.

    This is a raw ASGI endpoint that establishes an SSE connection.

    Args:
        scope: ASGI scope
        receive: ASGI receive callable
        send: ASGI send callable
    """
    logger.info('New SSE connection received')

    try:
        # Get or initialize the server and transport
        mcp_server, sse_transport = await initialize_server()
        server = mcp_server.get_server()

        # Handle the SSE connection
        async with sse_transport.connect_sse(scope, receive, send) as streams:
            await server.run(
                streams[0],
                streams[1],
                server.create_initialization_options(),
            )
    except Exception as e:
        logger.error(f'Error handling SSE connection: {e}', exc_info=True)
        raise


async def handle_messages(
    scope: dict[str, Any],
    receive: Callable[[], Awaitable[dict[str, Any]]],
    send: Callable[[MutableMapping[str, Any]], Awaitable[None]],
) -> None:
    """Handle messages endpoint for MCP SSE transport.

    This is a raw ASGI endpoint that delegates to the SSE transport.

    Args:
        scope: ASGI scope
        receive: ASGI receive callable
        send: ASGI send callable
    """
    logger.info('Message received on /messages endpoint')

    try:
        # Get or initialize the server and transport
        _, sse_transport = await initialize_server()

        # Handle the message through the SSE transport (this handles the response directly)
        await sse_transport.handle_post_message(scope, receive, send)
    except Exception as e:
        logger.error(f'Error handling message: {e}', exc_info=True)
        raise


# Create a custom ASGI app that routes to the correct handler
async def asgi_app(
    scope: dict[str, Any],
    receive: Callable[[], Awaitable[dict[str, Any]]],
    send: Callable[[MutableMapping[str, Any]], Awaitable[None]],
) -> None:
    """Main ASGI application that routes requests."""
    # Handle lifespan protocol
    if scope['type'] == 'lifespan':
        while True:
            message = await receive()
            if message['type'] == 'lifespan.startup':
                await send({'type': 'lifespan.startup.complete'})
            elif message['type'] == 'lifespan.shutdown':
                await send({'type': 'lifespan.shutdown.complete'})
                return
        return

    # Handle HTTP requests
    if scope['type'] != 'http':
        return

    path = scope['path']
    method = scope['method']

    logger.info(f'Received {method} request to {path}')

    if path == '/' and method == 'GET':
        # Health check endpoint
        await send(
            {
                'type': 'http.response.start',
                'status': 200,
                'headers': [[b'content-type', b'text/plain']],
            }
        )
        await send(
            {
                'type': 'http.response.body',
                'body': b'OpenAPI MCP Server - OK',
            }
        )
    elif path == '/sse' and method == 'GET':
        await handle_sse(scope, receive, send)
    elif path == '/messages' and method == 'POST':
        await handle_messages(scope, receive, send)
    else:
        # Return 404 for unknown paths
        logger.warning(f'404 - Unknown path: {method} {path}')
        await send(
            {
                'type': 'http.response.start',
                'status': 404,
                'headers': [[b'content-type', b'text/plain']],
            }
        )
        await send(
            {
                'type': 'http.response.body',
                'body': b'Not Found',
            }
        )


# Use the raw ASGI app (bypassing Starlette's routing for these endpoints)
app = asgi_app
