import asyncio
import logging
import httpx
from config import settings

logger = logging.getLogger(__name__)

GROQ_URL        = "https://api.groq.com/openai/v1/chat/completions"
OPENROUTER_URL  = "https://openrouter.ai/api/v1/chat/completions"
XAI_URL         = "https://api.x.ai/v1/chat/completions"

# ── Thinking / reasoning leak stripper ───────────────────────────────────────
# Some models (Nemotron, DeepSeek-R1, QwQ, etc.) emit their chain-of-thought
# either inside <think>...</think> tags or as plain prose before the answer.
# This function removes all of that so only the final answer is returned.

_REASONING_PREFIXES = (
    "we need to", "the user asked", "let me think", "let's think",
    "i need to", "i should", "according to rules", "according to the",
    "we should", "we can", "we'll", "we will", "we are", "we must",
    "so we", "now we", "first,", "step 1", "step 2",
    "okay,", "ok,", "alright,", "sure,",
    "the question is", "the user is", "the user says", "the user wants",
    "this is a", "this is not", "this means", "that means",
    "from wiki", "from the wiki", "from context",
    "so the answer", "so i will", "so i'll",
)


def _strip_thinking(text: str) -> str:
    """Remove reasoning leakage from LLM output."""
    import re

    # 1. Remove <think>...</think> blocks (including multiline)
    text = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.IGNORECASE)

    # 2. Remove any line that looks like internal reasoning prose
    clean_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        lower = stripped.lower()
        if any(lower.startswith(prefix) for prefix in _REASONING_PREFIXES):
            continue  # drop this line
        clean_lines.append(line)

    result = "\n".join(clean_lines).strip()

    # 3. If nothing remains after stripping, return original (better than empty)
    return result if result else text.strip()


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
        return _strip_thinking(r.json()["choices"][0]["message"]["content"])


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
        return _strip_thinking(r.json()["choices"][0]["message"]["content"])


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
        return _strip_thinking(r.json()["choices"][0]["message"]["content"])


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
        return _strip_thinking(r.json()["message"]["content"])


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
