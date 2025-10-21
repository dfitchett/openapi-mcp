# OpenAPI MCP Server

[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Linting: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

A generic MCP (Model Context Protocol) server that provides access to any OpenAPI specifications as resources. This server fetches and caches OpenAPI specifications from configurable API endpoints, making them available to MCP clients like Claude Desktop or Cursor.

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
3. The MCP server exposes these specs as resources via the stdio transport
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
│       ├── main.py         # stdio entry point for local use
│       ├── http_server.py  # HTTP/SSE server for Vercel
│       ├── mcp_server.py   # Core MCP server logic
│       ├── spec_fetcher.py # OpenAPI spec fetcher
│       └── config.py       # Configuration
├── test/               # Unit tests
│   ├── __init__.py
│   ├── conftest.py
│   └── test_app.py
├── docker-entrypoint.sh
├── getting_started.md
├── pyproject.toml
├── requirements.txt    # For Vercel deployment
├── vercel.json         # Vercel configuration
├── .vercelignore       # Files to exclude from deployment
└── README.md
```

### File Purposes
* `README.md` - Project overview, documentation, instructions, and usage examples
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

### Deployment Options

This MCP server can be run in two ways:

1. **Local (stdio)**: For use with local MCP clients like Claude Desktop or Cursor
2. **Remote (HTTP/SSE)**: Deployed to Vercel or other hosting platforms for remote access

### Running Locally (stdio)

The MCP server runs via stdio transport, which is the standard way MCP servers communicate with local clients:

```bash
poetry run python -m app.main
```

### Running Locally (HTTP/SSE)

You can also run the HTTP/SSE server locally for testing before deploying to Vercel:

```bash
# Install dependencies (uvicorn is included in dev dependencies)
poetry install

# Run the HTTP/SSE server locally
poetry run uvicorn app.http_server:app --reload --port 8000
```

The server will be available at `http://localhost:8000/sse`.

**Configure MCP client for local HTTP/SSE testing:**

**Cursor**: `~/.cursor/mcp.json`
```json
{
  "mcpServers": {
    "openapi-mcp": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

**Claude Desktop (macOS)**: `~/Library/Application Support/Claude/claude_desktop_config.json`
```json
{
  "mcpServers": {
    "openapi-mcp": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

This is useful for testing the HTTP/SSE transport before deploying to Vercel.

### Deploying to Vercel (HTTP/SSE)

Deploy the MCP server to Vercel for remote access via HTTP/SSE transport:

#### Prerequisites
- [Vercel account](https://vercel.com/signup)
- [Vercel CLI](https://vercel.com/docs/cli) (optional but recommended)

#### Quick Deploy

1. **Install Vercel CLI** (if not already installed):
```bash
npm i -g vercel
```

2. **Deploy to Vercel**:
```bash
vercel
```

Follow the prompts to link your project and deploy. On subsequent deploys, use:
```bash
vercel --prod
```

#### Deployment Configuration

The project includes optimized Vercel configuration in `vercel.json`:
- **Bundle size optimization**: Automatically excludes test files, build artifacts, and development files to stay under Vercel's 250 MB bundle limit
- **Memory**: Configured for 1024 MB
- **Timeout**: Set to 60 seconds for long-running SSE connections
- **Python version**: Uses Python 3.12+ as specified in `pyproject.toml`

#### Environment Variables (Optional)

You can configure the server via environment variables in your Vercel project settings or `.env` file:

- `MCP_SERVER_NAME`: Name of the MCP server (default: `openapi-mcp`)
- `MCP_URI_SCHEME`: URI scheme for resources (default: `openapi`)
- `DEBUG`: Enable debug logging (default: `False`)

#### Using Your Deployed Server

Once deployed, you'll get a URL like `https://your-project.vercel.app`. Use this URL in your MCP client configuration:

**Cursor**: `~/.cursor/mcp.json`
```json
{
  "mcpServers": {
    "openapi-mcp": {
      "url": "https://your-project.vercel.app/sse"
    }
  }
}
```

**Claude Desktop (macOS)**: `~/Library/Application Support/Claude/claude_desktop_config.json`
```json
{
  "mcpServers": {
    "openapi-mcp": {
      "url": "https://your-project.vercel.app/sse"
    }
  }
}
```

### Configuring with Claude Desktop or Cursor (Local stdio)

To use this MCP server locally via stdio transport with Claude Desktop or Cursor, add the following to your MCP configuration file:

**Claude Desktop (macOS)**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Claude Desktop (Windows)**: `%APPDATA%/Claude/claude_desktop_config.json`
**Cursor**: `~/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "openapi-mcp": {
      "command": "/bin/sh",
      "args": ["-c", "cd /absolute/path/to/openapi-mcp && poetry run python -m app.main"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/openapi-mcp/src"
      }
    }
  }
}
```

Replace `/absolute/path/to/openapi-mcp` with the actual path to your cloned repository (e.g., `/Users/yourusername/Documents/dev/openapi-mcp`).

**Note:** This stdio configuration is ideal for local development. After updating the configuration, restart Claude Desktop or Cursor to load the MCP server.

### Accessing API Specifications

Once configured, the MCP server exposes resources based on your configuration. With the default VA API configuration, the following resources are available:

- `openapi://api/benefits-claims-v2/openapi` - Benefits Claims API V2 OpenAPI Specification
- `openapi://api/benefits-documents-v1/openapi` - Benefits Documents API V1 OpenAPI Specification

In Claude Desktop or Cursor, you can reference these resources in your conversations, and the AI will be able to read the complete OpenAPI specifications to help you understand and work with the APIs.

**Custom URI Scheme**: You can change the URI scheme by setting the `MCP_URI_SCHEME` environment variable (e.g., to `va` for `va://api/...` URIs).

## Adding Additional APIs

To add more APIs to the server:

1. Find the OpenAPI specification URL for your API. This could be:
   - A VA API: `https://api.va.gov/internal/docs/{api-name}/{version}/openapi.json`
   - Any other OpenAPI spec URL: `https://your-api.com/openapi.json`, `https://petstore.swagger.io/v2/swagger.json`, etc.

2. Add an entry to the `API_CONFIGS` dictionary in `src/app/config.py`:

```python
API_CONFIGS = {
    # ... existing APIs ...
    'my-api-v1': {
        'name': 'My Custom API V1',
        'url': 'https://api.example.com/openapi.json',
        'description': 'Description of what this API does',
    },
}
```

3. Restart the MCP server. The new API will automatically be fetched and exposed as a resource at `openapi://api/my-api-v1/openapi` (or your custom URI scheme).

No code changes are required—just configuration!

### Using with Any OpenAPI Specification

This server works with **any valid OpenAPI specification**, including:
- Public APIs (GitHub, Stripe, Twilio, etc.)
- Your own private APIs
- Government APIs (VA, IRS, etc.)
- Third-party service APIs

Just add the OpenAPI spec URL to the configuration!

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
│       ├── http_server.py    # HTTP/SSE server for remote deployment
│       └── main.py           # stdio entry point for local use
├── test/                     # Unit tests
├── .cache/                   # Cached OpenAPI specifications (gitignored, local only)
├── pyproject.toml           # Project dependencies (Poetry)
├── requirements.txt         # Dependencies for Vercel
└── vercel.json              # Vercel deployment configuration
```

### Transport Modes

This server supports two transport modes:

1. **stdio (local)**: Uses standard input/output for communication with local MCP clients. Implemented in `main.py`. Ideal for local development with Claude Desktop and Cursor. Most efficient for single-user local scenarios.

2. **HTTP/SSE (remote/local testing)**: Uses Server-Sent Events over HTTP for communication. Implemented in `http_server.py`. Can be:
   - Run locally with `uvicorn` for testing the HTTP/SSE transport before deployment
   - Deployed to cloud platforms like Vercel for remote access by multiple clients

Both modes use the same core MCP server logic, differing only in how they communicate with clients.

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
