# FastAPI Template Docs

Developer documentation generated from source code and Google-style docstrings.

## Local docs workflow

```bash
uv sync --dev
uv run mkdocs serve
```

Open `http://127.0.0.1:8000`.

## What this docs site includes

- API reference pages generated with `mkdocstrings` from `src/fastapi_template`.
- An interactive [OpenAPI reference](openapi.md) rendered with Swagger UI, regenerated automatically on every docs build via `hooks/export_openapi.py`.
- Material for MkDocs theme with light and dark palettes.
