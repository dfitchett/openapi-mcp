"""Main entry point for the OpenAPI MCP server."""

import asyncio
import logging
import sys

from mcp.server.stdio import stdio_server

from app.config import DEBUG, SERVER_NAME
from app.mcp_server import OpenAPIMCPServer
from app.spec_fetcher import SpecFetcher

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr,  # MCP uses stdout for communication, so log to stderr
)

logger = logging.getLogger(__name__)


async def main() -> None:
    """Main entry point for the OpenAPI MCP server."""
    try:
        logger.info(f'Starting {SERVER_NAME} MCP server...')

        # Initialize spec fetcher and fetch all API specifications
        spec_fetcher = SpecFetcher()
        logger.info('Fetching OpenAPI specifications...')
        specs = await spec_fetcher.fetch_all_specs()
        logger.info(f'Successfully fetched {len(specs)} API specifications')

        # Initialize and start MCP server
        mcp_server = OpenAPIMCPServer(specs)
        server = mcp_server.get_server()

        logger.info('Starting MCP server with stdio transport...')
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    except Exception as e:
        logger.error(f'Error running {SERVER_NAME} MCP server: {e}', exc_info=True)
        sys.exit(1)


def run() -> None:
    """Run the MCP server."""
    asyncio.run(main())


if __name__ == '__main__':
    run()
