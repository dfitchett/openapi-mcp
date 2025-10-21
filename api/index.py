"""Vercel serverless function entry point for the OpenAPI MCP server.

This module exposes an ASGI application that Vercel's Python runtime can handle.
According to Vercel docs, the entry point should define an 'app' variable that
exposes an ASGI Application.
"""

import sys
from pathlib import Path

# Add src directory to Python path for imports
# Vercel uses /var/task as the base directory
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from app.http_server import asgi_app as app  # noqa: E402

# Vercel's Python runtime looks for an 'app' variable that is an ASGI application
__all__ = ['app']
