"""Tests for basic application configuration."""

from app import config


def test_config_values() -> None:
    """Test that configuration values are set correctly."""
    assert config.ENV == 'local'
    assert config.DEBUG  # from pyproject DEBUG env block
    assert config.CACHE_DIR is not None
    assert config.SERVER_NAME is not None
    assert config.URI_SCHEME is not None
    assert len(config.API_CONFIGS) == 2
    assert 'benefits-claims-v2' in config.API_CONFIGS
    assert 'benefits-documents-v1' in config.API_CONFIGS
