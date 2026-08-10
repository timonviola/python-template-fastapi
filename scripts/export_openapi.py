"""Export the FastAPI OpenAPI schema for the docs site.

Run before building/serving the docs so ``docs/openapi.json`` reflects the
current routes:

    uv run python scripts/export_openapi.py
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi_template.main import app

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "docs" / "openapi.json"


def main() -> None:
    """Write the app's OpenAPI schema to the docs directory."""
    schema = app.openapi()
    OUTPUT_PATH.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote OpenAPI schema to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
