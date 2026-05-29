import asyncio
import logging
import httpx
from config import settings

logger = logging.getLogger(__name__)

GROQ_URL        = "https://api.groq.com/openai/v1/chat/completions"
OPENROUTER_URL  = "https://openrouter.ai/api/v1/chat/completions"
XAI_URL         = "https://api.x.ai/v1/chat/completions"


# ── Individual provider calls ─────────────────────────────────────────────────

async def _xai_call(messages: list, system: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            XAI_URL,
            headers={"Authorization": f"Bearer {settings.XAI_API_KEY}"},
            json={
                "model": settings.XAI_MODEL,
                "messages": [{"role": "system", "content": system}] + messages,
                "temperature": 0.2,
                "max_tokens": 512,
            },
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


async def _openrouter_call(messages: list, system: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://drivelegal.in",
                "X-Title": "DriveLegal",
            },
            json={
                "model": settings.OPENROUTER_MODEL,
                "messages": [{"role": "system", "content": system}] + messages,
                "temperature": 0.2,
                "max_tokens": 512,
            },
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


async def _groq_call(messages: list, system: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
            json={
                "model": settings.GROQ_MODEL,
                "messages": [{"role": "system", "content": system}] + messages,
                "temperature": 0.2,
                "max_tokens": 512,
            },
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


async def _ollama_call(messages: list, system: str) -> str:
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            f"{settings.OLLAMA_BASE_URL}/api/chat",
            json={
                "model": settings.OLLAMA_MODEL,
                "messages": [{"role": "system", "content": system}] + messages,
                "stream": False,
                "options": {"temperature": 0.2},
            },
        )
        r.raise_for_status()
        return r.json()["message"]["content"]


# ── Provider registry ─────────────────────────────────────────────────────────

def _get_providers() -> list:
    """
    Return a list of (name, coroutine_factory) for each provider that has
    an API key configured, in priority order:
      1. xAI / Grok  (XAI_API_KEY)
      2. OpenRouter   (OPENROUTER_API_KEY)
      3. Groq         (GROQ_API_KEY)
    """
    providers = []
    if settings.XAI_API_KEY:
        providers.append(("xAI", _xai_call))
    if settings.OPENROUTER_API_KEY:
        providers.append(("OpenRouter", _openrouter_call))
    if settings.GROQ_API_KEY:
        providers.append(("Groq", _groq_call))
    return providers


# ── Public entry point ────────────────────────────────────────────────────────

async def call_llm(messages: list, system: str) -> str:
    """
    Call the best available LLM, with automatic fallback.

    Priority order:
      1. Ollama        — if OLLAMA_BASE_URL is set (local / Oracle A1 mode)
      2. xAI / Grok    — if XAI_API_KEY is set
      3. OpenRouter    — if OPENROUTER_API_KEY is set
      4. Groq          — if GROQ_API_KEY is set

    Each cloud provider is tried sequentially; if one fails its error is
    logged and the next one is attempted.  If none succeed a RuntimeError
    is raised.
    """
    # ── Local / Oracle mode ───────────────────────────────────────────────────
    if settings.OLLAMA_BASE_URL:
        logger.info("Using Ollama (local mode).")
        return await _ollama_call(messages, system)

    # ── Resolve which cloud providers are available ───────────────────────────
    providers = _get_providers()

    if not providers:
        logger.warning("No LLM API keys configured — returning stub response.")
        return (
            "DriveLegal is running in demo mode. "
            "Please configure XAI_API_KEY, OPENROUTER_API_KEY, or GROQ_API_KEY."
        )

    logger.debug(f"Available LLM providers: {[p[0] for p in providers]}")

    # ── Sequential fallback ───────────────────────────────────────────────────
    last_exc: Exception | None = None
    for name, fn in providers:
        try:
            logger.info(f"Calling LLM provider: {name}")
            result = await fn(messages, system)
            logger.debug(f"LLM provider {name} succeeded.")
            return result
        except Exception as exc:
            logger.warning(f"LLM provider {name} failed: {exc}")
            last_exc = exc

    raise RuntimeError(
        f"All LLM providers failed. Last error: {last_exc}"
    ) from last_exc
