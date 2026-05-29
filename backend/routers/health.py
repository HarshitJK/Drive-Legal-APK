import logging
from fastapi import APIRouter, Request
from services.llm import _groq_call
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health(request: Request):
    wiki = request.app.state.wiki
    groq_ok = False
    ollama_ok = False

    # Test Groq connectivity
    if not settings.OLLAMA_BASE_URL and settings.GROQ_API_KEY:
        try:
            response = await _groq_call(
                [{"role": "user", "content": "ping"}],
                system="Reply with exactly: pong",
            )
            groq_ok = "pong" in response.lower()
        except Exception as e:
            logger.warning(f"Groq health check failed: {e}")

    # Test Ollama connectivity
    if settings.OLLAMA_BASE_URL:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
                ollama_ok = r.status_code == 200
        except Exception:
            pass

    return {
        "status": "ok",
        "groq_ok": groq_ok,
        "ollama_mode": bool(settings.OLLAMA_BASE_URL),
        "ollama_ok": ollama_ok,
        "wiki_articles": len(wiki.articles),
        "wiki_articles_list": sorted(wiki.articles.keys()),
        "redis_configured": bool(settings.UPSTASH_REDIS_REST_URL),
    }
