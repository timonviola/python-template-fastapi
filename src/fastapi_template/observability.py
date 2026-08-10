"""OpenTelemetry tracing and structured logging setup.

Tracing is opt-in: it activates only when ``OTEL_EXPORTER_OTLP_ENDPOINT`` is set,
so local development and tests run without a collector dependency. See the
``docker-compose.yml`` observability stack for a ready-to-run OTel collector,
Grafana Tempo, and Prometheus setup.
"""

from __future__ import annotations

import logging
import os

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

OTEL_ENDPOINT_ENV_VAR = "OTEL_EXPORTER_OTLP_ENDPOINT"
OTEL_SERVICE_NAME_ENV_VAR = "OTEL_SERVICE_NAME"
DEFAULT_SERVICE_NAME = "fastapi-template"

LOG_FORMAT = (
    "%(asctime)s %(levelname)s [%(name)s] "
    "[trace_id=%(otelTraceID)s span_id=%(otelSpanID)s] %(message)s"
)


def configure_logging() -> None:
    """Configure structured logging with OpenTelemetry trace correlation."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=log_level, format=LOG_FORMAT)
    LoggingInstrumentor().instrument(set_logging_format=False)


def configure_tracing(app: FastAPI) -> None:
    """Configure OpenTelemetry tracing and instrument the FastAPI app.

    Tracing stays disabled unless `OTEL_EXPORTER_OTLP_ENDPOINT` is set, keeping
    local runs and tests free of collector dependencies.
    """
    endpoint = os.getenv(OTEL_ENDPOINT_ENV_VAR)
    if not endpoint:
        return

    service_name = os.getenv(OTEL_SERVICE_NAME_ENV_VAR, DEFAULT_SERVICE_NAME)
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app)
