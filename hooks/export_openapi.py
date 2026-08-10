"""MkDocs build hook that regenerates the OpenAPI schema before each build."""

from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent


def on_pre_build(config: Any) -> None:  # noqa: ANN401, ARG001
    """Regenerate docs/openapi.json before mkdocs builds or serves the site."""
    runpy.run_path(str(REPO_ROOT / "scripts" / "export_openapi.py"), run_name="__main__")
