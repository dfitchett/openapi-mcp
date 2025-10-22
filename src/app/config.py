from os import getenv
from pathlib import Path

ENV = getenv('ENV', 'local')
DEBUG = getenv('DEBUG', 'False').lower() in ('true', '1', 'yes', 'on')

# Server configuration
SERVER_NAME = getenv('MCP_SERVER_NAME', 'openapi-mcp')
URI_SCHEME = getenv('MCP_URI_SCHEME', 'openapi')

# Cache directory for OpenAPI specifications
CACHE_DIR = Path(getenv('CACHE_DIR', f'{Path.home()}/.cache/openapi-specs'))

# API configurations with OpenAPI specification URLs
# This can be overridden by setting the API_CONFIGS environment variable
# with a JSON string in the same format
API_CONFIGS = {
    'benefits-claims-v2': {
        'name': 'Benefits Claims API V2',
        'url': 'https://api.va.gov/internal/docs/benefits-claims/v2/openapi.json',
        'description': 'Retrieve and submit disability compensation claims',
    },
    'benefits-documents-v1': {
        'name': 'Benefits Documents API V1',
        'url': 'https://api.va.gov/internal/docs/benefits-documents/v1/openapi.json',
        'description': 'Submit supporting documents for benefits claims',
    },
    'vets-api': {
        'name': 'Vets API',
        'url': 'https://dev-api.va.gov/v0/apidocs',
        'description': 'Retrieve and submit disability compensation claims',
    },
}
