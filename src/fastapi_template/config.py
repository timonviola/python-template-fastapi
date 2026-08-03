"""Application configuration loading utilities."""

from __future__ import annotations

import os
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

CONFIG_FILE_ENV_VAR = "FASTAPI_TEMPLATE_CONFIG"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_API_PREFIX = "/v1"


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Represent runtime configuration for the application."""

    host: str
    port: int
    api_prefix: str


def load_config(config_path: str | Path | None = None) -> AppConfig:
    """Load application configuration from TOML and environment variables.

    Environment variables override TOML values, following 12-factor style.
    """
    values = _load_toml_values(config_path)

    host = os.getenv("HOST", _read_host(values))
    host = host.strip()
    if not host:
        msg = "HOST cannot be blank."
        raise ValueError(msg)

    port = _read_port(os.getenv("PORT"), values)
    api_prefix = _normalize_api_prefix(os.getenv("API_PREFIX", _read_api_prefix(values)))

    return AppConfig(host=host, port=port, api_prefix=api_prefix)


def _load_toml_values(config_path: str | Path | None) -> Mapping[str, Any]:
    """Return parsed TOML values from a configuration file."""
    resolved_config_path, is_explicit = _resolve_config_path(config_path)

    if not resolved_config_path.exists():
        if is_explicit:
            msg = f"Config file not found: {resolved_config_path}"
            raise FileNotFoundError(msg)
        return {}

    if not resolved_config_path.is_file():
        msg = f"Config path is not a file: {resolved_config_path}"
        raise ValueError(msg)

    with resolved_config_path.open("rb") as file:
        parsed = _ensure_string_key_mapping(
            cast(Mapping[object, object], tomllib.load(file)),
            "config TOML root",
        )

    app_section = parsed.get("app")
    if app_section is None:
        return parsed
    if not isinstance(app_section, Mapping):
        msg = "The [app] section in config TOML must be a table."
        raise ValueError(msg)
    return _ensure_string_key_mapping(
        cast(Mapping[object, object], app_section),
        "config TOML [app] section",
    )


def _resolve_config_path(config_path: str | Path | None) -> tuple[Path, bool]:
    """Resolve the path to configuration file and whether it was explicit."""
    if config_path is not None:
        return Path(config_path), True

    config_path_env = os.getenv(CONFIG_FILE_ENV_VAR)
    if config_path_env:
        return Path(config_path_env), True

    return Path("config.toml"), False


def _ensure_string_key_mapping(values: Mapping[object, object], context: str) -> dict[str, Any]:
    """Ensure a mapping has string keys and return it as typed dict."""
    typed_values: dict[str, Any] = {}
    for key, value in values.items():
        if not isinstance(key, str):
            msg = f"{context} must only contain string keys."
            raise ValueError(msg)
        typed_values[key] = value

    return typed_values


def _read_host(values: Mapping[str, Any]) -> str:
    """Read HOST from parsed config values."""
    host = values.get("HOST", DEFAULT_HOST)
    if not isinstance(host, str):
        msg = "HOST in config TOML must be a string."
        raise ValueError(msg)
    return host


def _read_port(port_from_env: str | None, values: Mapping[str, Any]) -> int:
    """Read and validate PORT from environment or parsed config values."""
    if port_from_env is not None:
        return _parse_port(port_from_env, source="environment variable PORT")

    port_value = values.get("PORT", DEFAULT_PORT)
    if isinstance(port_value, int):
        port = port_value
    elif isinstance(port_value, str):
        port = _parse_port(port_value, source="config TOML PORT")
    else:
        msg = "PORT in config TOML must be an integer or numeric string."
        raise ValueError(msg)

    if not (1 <= port <= 65535):
        msg = "PORT must be between 1 and 65535."
        raise ValueError(msg)
    return port


def _parse_port(value: str, source: str) -> int:
    """Parse a string port value into an integer."""
    trimmed = value.strip()
    if not trimmed:
        msg = f"{source} cannot be blank."
        raise ValueError(msg)
    if not trimmed.isdigit():
        msg = f"{source} must be numeric."
        raise ValueError(msg)

    port = int(trimmed)
    if not (1 <= port <= 65535):
        msg = f"{source} must be between 1 and 65535."
        raise ValueError(msg)
    return port


def _read_api_prefix(values: Mapping[str, Any]) -> str:
    """Read API_PREFIX from parsed config values."""
    api_prefix = values.get("API_PREFIX", DEFAULT_API_PREFIX)
    if not isinstance(api_prefix, str):
        msg = "API_PREFIX in config TOML must be a string."
        raise ValueError(msg)
    return api_prefix


def _normalize_api_prefix(raw_prefix: str) -> str:
    """Normalize API prefix to a slash-prefixed path without trailing slash."""
    prefix = raw_prefix.strip()
    if not prefix:
        msg = "API_PREFIX cannot be blank."
        raise ValueError(msg)

    if not prefix.startswith("/"):
        prefix = f"/{prefix}"

    if len(prefix) > 1:
        prefix = prefix.rstrip("/")

    return prefix
