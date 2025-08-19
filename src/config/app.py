import os
from typing import Optional
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()  # noqa: E402

# LLM
MODEL_ID = os.getenv("MODEL_ID")
assert MODEL_ID, "MODEL_ID environment variable not set"
AWS_PROFILE_NAME = os.getenv("AWS_PROFILE_NAME")
MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", 0.3))
MODEL_MAX_TOKENS = int(os.getenv("MODEL_MAX_TOKENS", 1024 * 2))

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
assert ENVIRONMENT, "ENVIRONMENT environment variable not set"


@dataclass
class AppConfig:
    model_id: str
    aws_profile_name: Optional[str]
    temperature: float
    max_tokens: int
    environment: str


app_config = AppConfig(
    model_id=MODEL_ID,
    temperature=MODEL_TEMPERATURE,
    max_tokens=MODEL_MAX_TOKENS,
    aws_profile_name=AWS_PROFILE_NAME,
    environment=ENVIRONMENT,
)
