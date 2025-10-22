# OpenAPI MCP Server

[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Linting: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

A generic MCP (Model Context Protocol) server that provides access to any OpenAPI specifications as resources. This server fetches and caches OpenAPI specifications from configurable API endpoints, making them available to MCP clients like Claude Desktop or Cursor.

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/en-US/install-mcp?name=openapi&config=eyJ1cmwiOiJodHRwOi8vbG9jYWxob3N0OjgwMDAvc3NlIn0%3D)

## Features

- **Generic & Configurable**: Works with any OpenAPI specification URL - not tied to any specific API provider
- **Automated Spec Fetching**: Automatically downloads the latest OpenAPI specifications on startup
- **Local Caching**: Caches specifications locally for performance and offline access
- **MCP Resource Protocol**: Exposes OpenAPI specifications as MCP resources
- **Extensible Design**: Easy to add APIs through simple configuration
- **Customizable**: Configure server name, URI scheme, and cache directory via environment variables
- **Example Configuration**: Pre-configured with VA (Department of Veterans Affairs) APIs
  - Benefits Claims API V2
  - Benefits Documents API V1

## How It Works

1. On startup, the server fetches OpenAPI specifications from configured API endpoints
2. Specifications are cached locally (default: `.cache/openapi-specs/`)
3. The MCP server exposes these specs as resources via HTTP/SSE transport
4. MCP clients can discover and read the OpenAPI specifications

## Configuration

The server can be configured via environment variables:

- `MCP_SERVER_NAME`: Name of the MCP server (default: `openapi-mcp`)
- `MCP_URI_SCHEME`: URI scheme for resources (default: `openapi`)
- `CACHE_DIR`: Cache directory path (default: `.cache/openapi-specs`)
- `DEBUG`: Enable debug logging (default: `False`)

You can also modify the API configurations directly in `src/app/config.py` by editing the `API_CONFIGS` dictionary.

## Project Structure
```
.
├── api/                # Vercel serverless functions
│   └── index.py        # HTTP/SSE entry point for Vercel
├── end_to_end/          # End-to-end tests
│   ├── __init__.py
│   ├── conftest.py
│   └── test_end_to_end.py
├── integration/         # Integration tests
│   ├── __init__.py
│   ├── conftest.py
│   └── test_integration.py
├── src/                # Source code
│   └── app/
│       ├── __init__.py
│       ├── http_server.py  # HTTP/SSE server for Vercel
│       ├── mcp_server.py   # Core MCP server logic
│       ├── spec_fetcher.py # OpenAPI spec fetcher
│       └── config.py       # Configuration
├── test/               # Unit tests
│   ├── __init__.py
│   ├── conftest.py
│   └── test_app.py
├── docker-entrypoint.sh
├── DEPLOYMENT.md      # Deployment guide
├── getting_started.md
├── pyproject.toml
├── requirements.txt    # For Vercel deployment
├── vercel.json         # Vercel configuration
├── .vercelignore       # Files to exclude from deployment
└── README.md
```

### File Purposes
* `README.md` - Project overview, documentation, instructions, and usage examples
* `DEPLOYMENT.md` - Detailed deployment guide for running locally and deploying to Vercel
* `getting_started.md` - Detailed setup instructions for development
* `pyproject.toml` - Project metadata, dependencies, and build configuration using Poetry
* `requirements.txt` - Python dependencies for Vercel deployment
* `vercel.json` - Vercel deployment configuration
* `.vercelignore` - Files to exclude from Vercel deployment
* `docker-entrypoint.sh` - Simple docker entrypoint for use with docker-compose
* `**/__init__.py` - Marks directories as Python packages

### Folder Purposes
* `/api` - Vercel serverless function entry points for HTTP/SSE transport
* `/src` - Contains the application source code
* `/test` - Contains unit tests that don't require external resources
* `/integration` - Contains tests that interact with external resources (e.g., databases, message queues) with some mocking
* `/end_to_end` - Contains tests that validate the entire application without mocking

## Installation

### Prerequisites

- Python 3.12 or higher
- Poetry 2 for dependency management

### Setup

1. Clone this repository:
```bash
git clone <repository-url>
cd va-api-mcp
```

2. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies:
```bash
poetry install
```

4. (Optional) Set up pre-commit hooks for development:
```bash
pre-commit install
```

## Usage

This server uses HTTP/SSE transport and can be run locally for testing or deployed to Vercel for remote access.

**For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).**

### Quick Start

Run the server locally:
```bash
poetry install
poetry run uvicorn app.http_server:app --reload --port 8000
```

Configure your MCP client (Cursor or Claude Desktop) to connect to `http://localhost:8000/sse`.

For production deployment to Vercel and complete configuration instructions, refer to the [Deployment Guide](DEPLOYMENT.md).

## Development

### Development Setup

1. Activate the virtual environment:
```bash
# For Poetry 2.0.0+, you need to install the shell plugin first:
poetry self add poetry-plugin-shell

# Then you can activate the virtual environment:
poetry shell
```

## Available Commands

- Run tests:
```bash
poetry run pytest
```

- Run integration tests:
```bash
poetry run pytest integration
```

- Run end-to-end tests:
```bash
poetry run pytest end_to_end
```

- Run linting:
```bash
poetry run ruff check .
```

- Run type checking:
```bash
poetry run mypy src
```

- Format code:
```bash
poetry run ruff format .
```

- Run security checks:
```bash
poetry run bandit -r src
```

## Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. The following checks are performed automatically before each commit:

- Code formatting (ruff)
- Type checking (mypy)
- Security checks (bandit)
- YAML validation
- Poetry dependency validation
- And more...

To run pre-commit checks manually:
```bash
pre-commit run --all-files
```

## Code Quality Tools

This project uses several tools to maintain code quality:

- **Ruff**: Fast Python linter and formatter
- **Mypy**: Static type checker
- **Bandit**: Security linter
- **Pytest**: Testing framework
- **Pre-commit**: Git hook manager

Configuration for these tools can be found in `pyproject.toml` and `.pre-commit-config.yaml`.

## Architecture

```
openapi-mcp/
├── api/
│   └── index.py              # Vercel serverless function entry point (HTTP/SSE)
├── src/
│   └── app/
│       ├── config.py         # Configuration (API URLs, server settings, cache settings)
│       ├── spec_fetcher.py   # Generic OpenAPI spec fetcher and caching
│       ├── mcp_server.py     # Generic MCP server implementation
│       └── http_server.py    # HTTP/SSE server for remote deployment
├── test/                     # Unit tests
├── .cache/                   # Cached OpenAPI specifications (gitignored, local only)
├── pyproject.toml           # Project dependencies (Poetry)
├── requirements.txt         # Dependencies for Vercel
└── vercel.json              # Vercel deployment configuration
```

### Transport Mode

This server uses **HTTP/SSE (Server-Sent Events)** transport for communication. Implemented in `http_server.py`, it can be:
- Run locally with `uvicorn` for testing the HTTP/SSE transport before deployment
- Deployed to cloud platforms like Vercel for remote access by multiple clients

### Design Philosophy

This server is intentionally generic and not tied to any specific API provider. The core components (`spec_fetcher.py`, `mcp_server.py`) work with any valid OpenAPI specification. The only VA-specific elements are in the default configuration, which can be easily replaced with any other APIs.

## Resources

- [MCP (Model Context Protocol) Specification](https://modelcontextprotocol.io/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Vercel Python Runtime Documentation](https://vercel.com/docs/functions/runtimes/python)
- [VA Developer Portal](https://developer.va.gov/) (example API provider)
- [Benefits Claims API Documentation](https://developer.va.gov/explore/api/benefits-claims)
- [Benefits Documents API Documentation](https://developer.va.gov/explore/api/benefits-documents)

## License

This project provides generic tooling for accessing OpenAPI specifications via MCP. When using this server with specific APIs (like the VA APIs in the default configuration), please ensure you comply with the respective API's terms of service.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
