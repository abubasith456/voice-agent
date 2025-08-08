from __future__ import annotations

import os
from pydantic import BaseModel, Field
from functools import lru_cache


class Settings(BaseModel):
    livekit_url: str = Field(default_factory=lambda: os.getenv("LIVEKIT_URL", "wss://your-livekit-server"))
    livekit_api_key: str = Field(default_factory=lambda: os.getenv("LIVEKIT_API_KEY", ""))
    livekit_api_secret: str = Field(default_factory=lambda: os.getenv("LIVEKIT_API_SECRET", ""))

    openrouter_api_key: str = Field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY", ""))
    openrouter_base_url: str = Field(default_factory=lambda: os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"))
    openrouter_model: str = Field(default_factory=lambda: os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"))

    deepgram_api_key: str = Field(default_factory=lambda: os.getenv("DEEPGRAM_API_KEY", ""))

    environment: str = Field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()