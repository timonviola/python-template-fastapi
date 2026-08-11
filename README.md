# FastAPI Template (uv + strict typing)

Template repository for FastAPI projects with:

- **Repository pattern** (protocol + implementation + service layer).
- **Strict typing** via `basedpyright`.
- **Google-style docstrings** enforced by `ruff` (`pydocstyle` convention).
- **Prek hooks** for always-on formatting/linting and commit message validation.
- **Rust-first tooling in CI** (`uv`, `ruff`, `typos`, `dprint`, `cocogitto` for releases).
- **Automated dependency updates** via Dependabot with automerge rules.
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

Dependabot is configured via `.github/dependabot.yml`, with automerge handled by `.github/workflows/dependabot-auto-merge.yml`.

- Python (`uv`) and GitHub Actions updates are checked **weekly** and grouped into a single PR per ecosystem.
- Updates use a **6-day cooldown** (14 days for major bumps).
- Transitive dependencies in `uv.lock` are refreshed too (`dependency-type: all`), the Dependabot equivalent of lock file maintenance.
- Automerge (`gh pr merge --auto --squash`) applies to all GitHub Actions updates and to non-major Python updates; major Python bumps stay manual.
- No approval step: `GITHUB_TOKEN` is not permitted to approve pull requests. If `trunk` ever requires approving reviews, swap in a PAT or GitHub App token.
- Requires **Allow auto-merge** in the repository settings; merges still wait for the required CI checks.

## Documentation site (MkDocs + Material)

Developer docs are configured with `mkdocs.yml` and published by `.github/workflows/docs.yml`.

The site is deployed to **GitHub Pages using GitHub Actions** (not a `gh-pages` branch): every push to
`trunk` builds the site with `mkdocs build --strict` and deploys it via `actions/deploy-pages`.
Set **Settings → Pages → Build and deployment → Source** to **GitHub Actions** for this to work.

The site is served from the custom domain <https://python-template.tmon.xyz/>, configured via
`docs/CNAME` and `site_url` in `mkdocs.yml`. This requires a DNS record at the `tmon.xyz` provider:

| Type    | Name              | Value                  |
| ------- | ----------------- | ---------------------- |
| `CNAME` | `python-template` | `timonviola.github.io` |

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

