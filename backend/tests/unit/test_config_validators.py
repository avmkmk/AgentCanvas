"""
Unit tests for app/core/config.py — Settings field validators.

Coverage targets:
  - log_level_must_be_valid: valid values, invalid values, case normalisation
  - api_key_must_be_set: placeholder rejection, empty string rejection, valid key
  - get_allowed_origins_list: single origin, multi-origin comma list, extra whitespace

These are security-relevant validators: a misconfigured LOG_LEVEL silently
breaks observability; a placeholder API_KEY exposes the API to anyone.
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _make_settings(**overrides):
    """
    Build a Settings instance with a minimal valid env, applying overrides.

    Importing inside the function avoids the module-level singleton being
    re-evaluated — we want fresh instances for each parametrize case.
    """
    # Import here so the conftest env overrides are already active

    # We cannot easily re-instantiate the real Settings with arbitrary field
    # values because pydantic-settings reads from os.environ.  Instead we
    # patch os.environ for the duration of this call.
    import os
    base_env = {
        "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
        "MONGO_URI": "mongodb://localhost/test",
        "REDIS_URL": "redis://localhost:6379/1",
        "API_KEY": "a-valid-key-not-placeholder",
        "ANTHROPIC_API_KEY": "sk-ant-test",
        "LOG_LEVEL": "INFO",
    }
    base_env.update(overrides)

    old = {k: os.environ.get(k) for k in base_env}
    for k, v in base_env.items():
        os.environ[k] = v
    try:
        # Import fresh to pick up env changes
        import importlib
        import app.core.config as cfg_module
        importlib.reload(cfg_module)
        # Instantiate directly
        return cfg_module.Settings()
    finally:
        # Restore previous state
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        importlib.reload(cfg_module)


# ─── log_level validator ──────────────────────────────────────────────────────

class TestLogLevelValidator:
    """log_level_must_be_valid must normalise case and reject unknown levels."""

    @pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    def test_log_level_accepts_valid_values_uppercased(self, level: str) -> None:
        settings = _make_settings(LOG_LEVEL=level)
        assert settings.log_level == level.upper()

    @pytest.mark.parametrize("level", ["debug", "info", "warning", "error", "critical"])
    def test_log_level_normalises_lowercase_to_uppercase(self, level: str) -> None:
        settings = _make_settings(LOG_LEVEL=level)
        assert settings.log_level == level.upper()

    @pytest.mark.parametrize("bad_level", ["VERBOSE", "TRACE", "NOTICE", "", "info2"])
    def test_log_level_rejects_invalid_values(self, bad_level: str) -> None:
        with pytest.raises((ValidationError, ValueError)):
            _make_settings(LOG_LEVEL=bad_level)


# ─── api_key validator ────────────────────────────────────────────────────────

class TestApiKeyValidator:
    """api_key_must_be_set must reject placeholder strings that indicate an
    unconfigured .env file."""

    @pytest.mark.parametrize("placeholder", ["", "change-me", "your-api-key-here"])
    def test_api_key_rejects_placeholder_values(self, placeholder: str) -> None:
        with pytest.raises((ValidationError, ValueError)):
            _make_settings(API_KEY=placeholder)

    def test_api_key_accepts_real_key(self) -> None:
        settings = _make_settings(API_KEY="sk-real-secret-abc123")
        assert settings.api_key == "sk-real-secret-abc123"

    def test_api_key_accepts_short_non_placeholder_key(self) -> None:
        # Even a short key is fine as long as it is not a known placeholder
        settings = _make_settings(API_KEY="x")
        assert settings.api_key == "x"


# ─── get_allowed_origins_list ─────────────────────────────────────────────────

class TestGetAllowedOriginsList:
    """get_allowed_origins_list must split the env string correctly."""

    def test_single_origin_returns_list_of_one(self) -> None:
        settings = _make_settings(ALLOWED_ORIGINS="http://localhost:3000")
        result = settings.get_allowed_origins_list()
        assert result == ["http://localhost:3000"]

    def test_multiple_origins_comma_separated(self) -> None:
        settings = _make_settings(
            ALLOWED_ORIGINS="http://localhost:3000,https://app.example.com"
        )
        result = settings.get_allowed_origins_list()
        assert result == ["http://localhost:3000", "https://app.example.com"]

    def test_extra_whitespace_around_origins_is_stripped(self) -> None:
        settings = _make_settings(
            ALLOWED_ORIGINS="http://localhost:3000 , https://app.example.com "
        )
        result = settings.get_allowed_origins_list()
        assert result == ["http://localhost:3000", "https://app.example.com"]
