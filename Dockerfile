# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
  UV_LINK_MODE=copy \
  UV_PYTHON_DOWNLOADS=never \
  UV_PYTHON=/usr/bin/python

WORKDIR /app

# Symlink the distroless interpreter path (/usr/bin/python) to this build
# image's path so the venv created below records import paths that also
# resolve correctly in the distroless runtime image.
RUN ln -s /usr/local/bin/python3 /usr/bin/python

# Install dependencies first (cached separately from app source).
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --locked --no-install-project --no-dev

COPY src ./src
COPY README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --locked --no-dev

FROM gcr.io/distroless/python3-debian13:nonroot AS runtime

WORKDIR /app

COPY --from=builder --chown=nonroot:nonroot /app/.venv /app/.venv
COPY --chown=nonroot:nonroot src ./src
COPY --chown=nonroot:nonroot config.toml ./

ENV PATH="/app/.venv/bin:${PATH}" \
  HOST=0.0.0.0 \
  PORT=8000

EXPOSE 8000

ENTRYPOINT ["python", "-m", "uvicorn", "fastapi_template.main:app", "--host", "0.0.0.0", "--port", "8000"]
