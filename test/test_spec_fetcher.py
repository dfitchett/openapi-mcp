"""Tests for the spec_fetcher module."""

import json
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.spec_fetcher import SpecFetcher


@pytest.fixture
def temp_cache_dir(tmp_path: Path) -> Path:
    """Create a temporary cache directory for tests."""
    cache_dir = tmp_path / 'cache'
    cache_dir.mkdir()
    return cache_dir


@pytest.fixture
def spec_fetcher(temp_cache_dir: Path) -> SpecFetcher:
    """Create a SpecFetcher instance with a temporary cache directory."""
    return SpecFetcher(cache_dir=temp_cache_dir)


@pytest.fixture
def sample_spec() -> dict[str, Any]:
    """Sample OpenAPI specification for testing."""
    return {
        'openapi': '3.0.1',
        'info': {'title': 'Test API', 'version': 'v1'},
        'paths': {},
    }


class TestSpecFetcher:
    """Tests for the SpecFetcher class."""

    def test_init(self, spec_fetcher: SpecFetcher, temp_cache_dir: Path) -> None:
        """Test that SpecFetcher initializes correctly."""
        assert spec_fetcher.cache_dir == temp_cache_dir
        assert temp_cache_dir.exists()

    def test_get_cache_path(self, spec_fetcher: SpecFetcher) -> None:
        """Test that cache path is generated correctly."""
        cache_path = spec_fetcher._get_cache_path('test-api')
        assert cache_path.name == 'test-api.json'
        assert cache_path.parent == spec_fetcher.cache_dir

    @pytest.mark.asyncio
    async def test_fetch_spec_success(self, spec_fetcher: SpecFetcher, sample_spec: dict[str, Any]) -> None:
        """Test successfully fetching an OpenAPI specification."""
        mock_response = MagicMock()
        mock_response.json.return_value = sample_spec
        mock_response.raise_for_status = MagicMock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await spec_fetcher.fetch_spec('test-api', 'https://example.com/openapi.json')

            assert result == sample_spec
            # Verify it was cached
            cache_path = spec_fetcher._get_cache_path('test-api')
            assert cache_path.exists()
            with open(cache_path) as f:
                cached_data = json.load(f)
            assert cached_data == sample_spec

    def test_load_cached_spec_exists(self, spec_fetcher: SpecFetcher, sample_spec: dict[str, Any]) -> None:
        """Test loading a cached specification that exists."""
        cache_path = spec_fetcher._get_cache_path('test-api')
        with open(cache_path, 'w') as f:
            json.dump(sample_spec, f)

        result = spec_fetcher.load_cached_spec('test-api')
        assert result == sample_spec

    def test_load_cached_spec_not_exists(self, spec_fetcher: SpecFetcher) -> None:
        """Test loading a cached specification that doesn't exist."""
        result = spec_fetcher.load_cached_spec('nonexistent-api')
        assert result is None

    def test_load_cached_spec_invalid_json(self, spec_fetcher: SpecFetcher) -> None:
        """Test loading a cached specification with invalid JSON."""
        cache_path = spec_fetcher._get_cache_path('test-api')
        with open(cache_path, 'w') as f:
            f.write('invalid json')

        result = spec_fetcher.load_cached_spec('test-api')
        assert result is None

    @pytest.mark.asyncio
    async def test_get_spec_with_cache(self, spec_fetcher: SpecFetcher, sample_spec: dict[str, Any]) -> None:
        """Test getting a spec when cached version exists."""
        # Pre-populate cache
        cache_path = spec_fetcher._get_cache_path('test-api')
        with open(cache_path, 'w') as f:
            json.dump(sample_spec, f)

        result = await spec_fetcher.get_spec('test-api', 'https://example.com/openapi.json', use_cache=True)
        assert result == sample_spec

    @pytest.mark.asyncio
    async def test_get_spec_without_cache(self, spec_fetcher: SpecFetcher, sample_spec: dict[str, Any]) -> None:
        """Test getting a spec when cache should not be used."""
        mock_response = MagicMock()
        mock_response.json.return_value = sample_spec
        mock_response.raise_for_status = MagicMock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await spec_fetcher.get_spec('test-api', 'https://example.com/openapi.json', use_cache=False)
            assert result == sample_spec

    @pytest.mark.asyncio
    async def test_fetch_all_specs_success(self, spec_fetcher: SpecFetcher, sample_spec: dict[str, Any]) -> None:
        """Test fetching all configured API specifications."""
        mock_response = MagicMock()
        mock_response.json.return_value = sample_spec
        mock_response.raise_for_status = MagicMock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await spec_fetcher.fetch_all_specs()

            assert 'benefits-claims-v2' in result
            assert 'benefits-documents-v1' in result
            assert result['benefits-claims-v2'] == sample_spec
            assert result['benefits-documents-v1'] == sample_spec

    @pytest.mark.asyncio
    async def test_fetch_all_specs_with_fallback(self, spec_fetcher: SpecFetcher, sample_spec: dict[str, Any]) -> None:
        """Test fetching all specs with fallback to cache on error."""
        # Pre-populate cache for one API
        cache_path = spec_fetcher._get_cache_path('benefits-claims-v2')
        with open(cache_path, 'w') as f:
            json.dump(sample_spec, f)

        # Mock httpx to fail for benefits-claims-v2 but succeed for others
        async def mock_get(url: str) -> MagicMock:
            if 'benefits-claims' in url:
                raise Exception('Network error')
            mock_response = MagicMock()
            mock_response.json.return_value = sample_spec
            mock_response.raise_for_status = MagicMock()
            return mock_response

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = mock_get

            result = await spec_fetcher.fetch_all_specs()

            # Should use cached version for benefits-claims-v2
            assert 'benefits-claims-v2' in result
            assert result['benefits-claims-v2'] == sample_spec
