import os
import base64
from typing import Optional
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()  # noqa: E402

import structlog

logger = structlog.get_logger("config")


# LLM
MODEL_ID = os.getenv("MODEL_ID")
assert MODEL_ID, "MODEL_ID environment variable not set"
AWS_PROFILE_NAME = os.getenv("AWS_PROFILE_NAME")
MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", 0.3))
MODEL_MAX_TOKENS = int(os.getenv("MODEL_MAX_TOKENS", 1024 * 2))
logger.info(
    "LLM configuration",
    model_id=MODEL_ID,
    temperature=MODEL_TEMPERATURE,
    max_tokens=MODEL_MAX_TOKENS,
    aws_profile_name=AWS_PROFILE_NAME,
)

# Guardrail
GUARDRAIL_ID = os.getenv("GUARDRAIL_ID", None)
GUARDRAIL_VERSION = os.getenv("GUARDRAIL_VERSION", None)
logger.info(
    "Guardrail configuration",
    guardrail_id=GUARDRAIL_ID,
    guardrail_version=GUARDRAIL_VERSION,
)

# S3 Session
SESSION_BUCKET_NAME = os.getenv("SESSION_BUCKET_NAME", None)
SESSION_PREFIX = os.getenv("SESSION_PREFIX", None)
logger.info(
    "S3 Session configuration",
    session_bucket_name=SESSION_BUCKET_NAME,
    session_prefix=SESSION_PREFIX,
)

# Observability
LANGFUSE_SECRET_KEY = os.environ.get("LANGFUSE_SECRET_KEY", "")
LANGFUSE_PUBLIC_KEY = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_HOST = os.environ.get("LANGFUSE_HOST", "")
TRACING_ENABLED = False
if LANGFUSE_HOST:
    TRACING_ENABLED = True
    # Build Basic Auth header.
    LANGFUSE_AUTH = base64.b64encode(f"{LANGFUSE_PUBLIC_KEY}:{LANGFUSE_SECRET_KEY}".encode()).decode()
    # Configure OpenTelemetry endpoint & headers
    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = LANGFUSE_HOST + "/api/public/otel"
    os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"
logger.info(
    "Observability configuration",
    tracing_enabled=TRACING_ENABLED,
    langfuse_secret_key=LANGFUSE_SECRET_KEY[:10],
    langfuse_public_key=LANGFUSE_PUBLIC_KEY[:10],
    langfuse_host=LANGFUSE_HOST,
)

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
assert ENVIRONMENT, "ENVIRONMENT environment variable not set"
logger.info("Environment configuration", environment=ENVIRONMENT)


@dataclass
class AppConfig:
    model_id: str
    temperature: float
    max_tokens: int
    aws_profile_name: Optional[str]
    guardrail_id: Optional[str]
    guardrail_version: Optional[str]
    session_bucket_name: Optional[str]
    session_prefix: Optional[str]
    tracing_enabled: bool
    environment: str


app_config = AppConfig(
    model_id=MODEL_ID,
    temperature=MODEL_TEMPERATURE,
    max_tokens=MODEL_MAX_TOKENS,
    aws_profile_name=AWS_PROFILE_NAME,
    guardrail_id=GUARDRAIL_ID,
    guardrail_version=GUARDRAIL_VERSION,
    session_bucket_name=SESSION_BUCKET_NAME,
    session_prefix=SESSION_PREFIX,
    tracing_enabled=TRACING_ENABLED,
    environment=ENVIRONMENT,
)
