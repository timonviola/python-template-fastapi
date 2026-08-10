# FastAPI Template (uv + strict typing)

Template repository for FastAPI projects with:

- **Repository pattern** (protocol + implementation + service layer).
- **Strict typing** via `basedpyright`.
- **Google-style docstrings** enforced by `ruff` (`pydocstyle` convention).
- **Prek hooks** for always-on formatting/linting and commit message validation.
- **Rust-first tooling in CI** (`uv`, `ruff`, `typos`, `dprint`, `cocogitto` for releases).
- **Automated dependency updates** via Renovate with automerge rules.
- **Material for MkDocs** docs site with API docs generated from docstrings.
- **Containerfile** uses distroless base image
- **Container-compose** ships with full observability stack

## Quick start

```bash
uv sync --dev
cargo install --locked cocogitto
uv run prek install
uv run prek run --all-files
uv run basedpyright --project basedpyrightconfig.json
uv run dev
```

Then open `http://127.0.0.1:8000/docs`.

API routes are versioned by default and exposed under the `/v1` prefix.

## Runtime configuration (12-factor style)

Runtime settings are loaded from `config.toml` and can be overridden with environment variables.

```toml
HOST = "127.0.0.1"
PORT = 8000
API_PREFIX = "/v1"
```

Supported environment variables:

- `HOST`
- `PORT`
- `API_PREFIX`
- `FASTAPI_TEMPLATE_CONFIG` (optional custom TOML path)
- `OTEL_EXPORTER_OTLP_ENDPOINT` (optional; enables OpenTelemetry tracing when set)
- `OTEL_SERVICE_NAME` (optional; defaults to `fastapi-template`)
- `LOG_LEVEL` (optional; defaults to `INFO`)

Tests are intentionally run in CI only by default.

## Observability (OpenTelemetry + Prometheus + Grafana Tempo)

The app ships with OpenTelemetry instrumentation for tracing (`opentelemetry-instrumentation-fastapi`)
and trace-correlated structured logging. Tracing is **opt-in**: it only activates when
`OTEL_EXPORTER_OTLP_ENDPOINT` is set, so local dev and tests run without a collector.

Spin up a full observability stack (OTel Collector → Grafana Tempo for traces, Prometheus for
span/service-graph metrics, Grafana for visualization) with:

```bash
docker compose up --build
```

- App: `http://localhost:8000` (see `/v1/docs` for interactive Swagger UI)
- Grafana: `http://localhost:3000` (anonymous admin access, Tempo + Prometheus pre-provisioned)
- Prometheus: `http://localhost:9090`
- Tempo query API: `http://localhost:3200`

Generate some traffic (e.g. `curl http://localhost:8000/v1/healthz`), then open Grafana → Explore →
Tempo to search and view traces, or the "FastAPI Template - Requests" dashboard for span-derived
metrics.

## Container image

A production Dockerfile (multi-stage, `uv`-based) is included:

```bash
docker build -t fastapi-template .
docker run -p 8000:8000 fastapi-template
```

## Project layout

```text
src/fastapi_template/
  domain/         # domain models
  repositories/   # repository contract + implementations
  services/       # business logic
  schemas/        # API DTOs
  api/routes/     # route factories
  main.py         # app factory + runtime entrypoint
```

## Conventional commits and releases

Releases and changelog generation use **cocogitto**:

- Follow conventional commits (`feat:`, `fix:`, `chore:`, ...).
- `prek` commit-msg hook validates each commit message via `cog verify --file`.
- Run a release locally with `cog bump --auto --changelog` (or patch/minor/major).
- GitHub Action `release.yml` automates bumping tags/changelog and publishing GitHub releases.

## Dependency updates

Renovate is configured via `.github/renovate.json` and scheduled in `.github/workflows/renovate.yml`.

- GitHub Actions and Python (`uv`/PyPI) updates use a **6-day cooldown**.
- Safe updates are **automerge-enabled**.
- Add a repository secret named `RENOVATE_TOKEN` (PAT or GitHub App token) for the workflow.

## Documentation site (MkDocs + Material)

Developer docs are configured with `mkdocs.yml` and published by `.github/workflows/docs.yml`.

```bash
uv sync --dev
uv run mkdocs serve
uv run mkdocs build
```

- API reference is generated from source docstrings via `mkdocstrings`.
- An interactive **OpenAPI reference** page renders the live schema with Swagger UI; it's
  regenerated automatically on every `mkdocs build`/`serve` via `hooks/export_openapi.py`
  (backed by `scripts/export_openapi.py`).
- Theme supports light mode (**white + teal**) and dark mode (**dark-gray + orange**).
