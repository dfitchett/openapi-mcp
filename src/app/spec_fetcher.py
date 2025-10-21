"""Module for fetching and caching OpenAPI specifications."""

import json
import logging
from pathlib import Path
from typing import Any

import httpx

from app.config import API_CONFIGS, CACHE_DIR

logger = logging.getLogger(__name__)


class SpecFetcher:
    """Fetches and caches OpenAPI specifications from API endpoints."""

    def __init__(self, cache_dir: Path = CACHE_DIR) -> None:
        """Initialize the spec fetcher.

        Args:
            cache_dir: Directory to cache downloaded specifications
        """
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, api_id: str) -> Path:
        """Get the cache file path for an API specification.

        Args:
            api_id: API identifier (e.g., 'benefits-claims-v2')

        Returns:
            Path to the cached specification file
        """
        return self.cache_dir / f'{api_id}.json'

    async def fetch_spec(self, api_id: str, url: str) -> dict[str, Any]:
        """Fetch an OpenAPI specification from a URL.

        Args:
            api_id: API identifier for caching
            url: URL to fetch the OpenAPI specification from

        Returns:
            The OpenAPI specification as a dictionary

        Raises:
            httpx.HTTPError: If the request fails
        """
        logger.info(f'Fetching OpenAPI spec for {api_id} from {url}')

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            spec: dict[str, Any] = response.json()

        # Cache the specification
        cache_path = self._get_cache_path(api_id)
        with open(cache_path, 'w') as f:
            json.dump(spec, f, indent=2)

        logger.info(f'Cached OpenAPI spec for {api_id} at {cache_path}')
        return spec

    def load_cached_spec(self, api_id: str) -> dict[str, Any] | None:
        """Load a cached OpenAPI specification.

        Args:
            api_id: API identifier

        Returns:
            The cached specification or None if not found
        """
        cache_path = self._get_cache_path(api_id)
        if not cache_path.exists():
            return None

        try:
            with open(cache_path) as f:
                spec: dict[str, Any] = json.load(f)
                return spec
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f'Error loading cached spec for {api_id}: {e}')
            return None

    async def get_spec(self, api_id: str, url: str, use_cache: bool = True) -> dict[str, Any]:
        """Get an OpenAPI specification, using cache if available.

        Args:
            api_id: API identifier
            url: URL to fetch the specification from
            use_cache: Whether to use cached version if available

        Returns:
            The OpenAPI specification as a dictionary
        """
        if use_cache:
            cached = self.load_cached_spec(api_id)
            if cached is not None:
                logger.info(f'Using cached spec for {api_id}')
                return cached

        return await self.fetch_spec(api_id, url)

    async def fetch_all_specs(self, force_refresh: bool = False) -> dict[str, dict[str, Any]]:
        """Fetch all configured API specifications.

        Args:
            force_refresh: If True, fetch fresh specs even if cached versions exist

        Returns:
            Dictionary mapping API IDs to their specifications
        """
        specs = {}
        for api_id, api_config in API_CONFIGS.items():
            try:
                spec = await self.get_spec(api_id, api_config['url'], use_cache=not force_refresh)
                specs[api_id] = spec
            except Exception as e:
                logger.error(f'Failed to fetch spec for {api_id}: {e}')
                # Try to use cached version as fallback
                cached = self.load_cached_spec(api_id)
                if cached is not None:
                    logger.warning(f'Using cached spec for {api_id} after fetch failure')
                    specs[api_id] = cached
                else:
                    raise

        return specs
