"""All settings come from environment variables / the .env file."""
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


@dataclass
class Settings:
    # LLM (any OpenAI-compatible API: OpenAI, Google Gemini, Groq, OpenRouter...)
    llm_api_key: str = field(default_factory=lambda: os.getenv("LLM_API_KEY", ""))
    llm_base_url: str | None = field(default_factory=lambda: os.getenv("LLM_BASE_URL") or None)
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4o-mini"))

    # Data sources: "json" now; "api" in Phase 2
    flight_source: str = field(default_factory=lambda: os.getenv("FLIGHT_SOURCE", "json"))
    product_source: str = field(default_factory=lambda: os.getenv("PRODUCT_SOURCE", "json"))
    cinema_source: str = field(default_factory=lambda: os.getenv("CINEMA_SOURCE", "json"))
    data_dir: Path = field(default_factory=lambda: Path(os.getenv("DATA_DIR", ROOT / "data")))

    # Reference "today" of the mock dataset (brief section 7)
    reference_date: str = field(default_factory=lambda: os.getenv("REFERENCE_DATE", "2026-11-02"))

    port: int = field(default_factory=lambda: int(os.getenv("PORT", "8000")))


settings = Settings()
