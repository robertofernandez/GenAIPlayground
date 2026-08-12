import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


@dataclass(frozen=True)
class Settings:
    app_name: str = "skill-extraction-service"
    app_version: str = "1.0.0"
    anthropic_api_key: str | None = None
    anthropic_api_url: str | None = None
    model: str = "claude-sonnet-5"
    ENVIRONMENT: str = "development"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            anthropic_api_url=os.getenv("ANTHROPIC_API_URL", "https://api.anthropic.com"),
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"),
            ENVIRONMENT=os.getenv("ENVIRONMENT", "development")
        )


settings = Settings.from_env()
