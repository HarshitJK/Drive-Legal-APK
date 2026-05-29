from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # ── LLM ──────────────────────────────────────────────────────────────────
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "mistralai/mixtral-8x7b-instruct"
    XAI_API_KEY: str = ""
    XAI_MODEL: str = "grok-2-1212"

    # Oracle A1 / local Ollama — set OLLAMA_BASE_URL to override cloud LLMs
    OLLAMA_BASE_URL: str = ""           # e.g. "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma2:9b"

    # ── Redis (Upstash) ───────────────────────────────────────────────────────
    UPSTASH_REDIS_REST_URL: str = ""
    UPSTASH_REDIS_REST_TOKEN: str = ""
    SESSION_TTL_SECONDS: int = 86400    # 24 hours

    # ── WhatsApp ──────────────────────────────────────────────────────────────
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    META_VERIFY_TOKEN: str = ""
    META_ACCESS_TOKEN: str = ""
    WHATSAPP_PROVIDER: str = "twilio"   # "twilio" | "meta"

    # ── App ───────────────────────────────────────────────────────────────────
    WIKI_DIR: str = "wiki"
    MAX_HISTORY_TURNS: int = 6          # keep last 6 turns in context
    MAX_WIKI_ARTICLES: int = 3          # top 3 articles injected per query
    PARIVAHAN_BASE_URL: str = "https://echallan.parivahan.gov.in"
    DEBUG: bool = False
    RATE_LIMIT_PER_MINUTE: int = 30

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
