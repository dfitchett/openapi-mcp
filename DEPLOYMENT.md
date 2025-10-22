# Deployment Guide

This guide covers how to run and deploy the OpenAPI MCP Server.

## Running Locally (HTTP/SSE)

You can run the HTTP/SSE server locally for testing before deploying to Vercel:

```bash
# Install dependencies (uvicorn is included in dev dependencies)
poetry install

# Run the HTTP/SSE server locally
poetry run uvicorn app.http_server:app --reload --port 8000
```

The server will be available at `http://localhost:8000/sse`.

### Configure MCP Client for Local Testing

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

## Deploying to Vercel (HTTP/SSE)

Deploy the MCP server to Vercel for remote access via HTTP/SSE transport:

### Prerequisites
- [Vercel account](https://vercel.com/signup)
- [Vercel CLI](https://vercel.com/docs/cli) (optional but recommended)

### Quick Deploy

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

### Deployment Configuration

The project includes optimized Vercel configuration in `vercel.json`:
- **Bundle size optimization**: Automatically excludes test files, build artifacts, and development files to stay under Vercel's 250 MB bundle limit
- **Memory**: Configured for 1024 MB
- **Timeout**: Set to 60 seconds for long-running SSE connections
- **Python version**: Uses Python 3.12+ as specified in `pyproject.toml`

### Environment Variables (Optional)

You can configure the server via environment variables in your Vercel project settings or `.env` file:

- `MCP_SERVER_NAME`: Name of the MCP server (default: `openapi-mcp`)
- `MCP_URI_SCHEME`: URI scheme for resources (default: `openapi`)
- `DEBUG`: Enable debug logging (default: `False`)

## Using Your Deployed Server

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

**Claude Desktop (Windows)**: `%APPDATA%/Claude/claude_desktop_config.json`
```json
{
  "mcpServers": {
    "openapi-mcp": {
      "url": "https://your-project.vercel.app/sse"
    }
  }
}
```

After updating the configuration, restart Claude Desktop or Cursor to load the MCP server.

## Accessing API Specifications

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
