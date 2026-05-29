import json
import asyncio
import httpx
from models.session import SessionState, Turn
from config import settings

REDIS_URL = settings.UPSTASH_REDIS_REST_URL
REDIS_TOKEN = settings.UPSTASH_REDIS_REST_TOKEN

# ── In-memory fallback when Redis is not configured ──────────────────────────
_local_store: dict[str, str] = {}


def _use_redis() -> bool:
    return bool(REDIS_URL and REDIS_TOKEN)


async def _redis_get(key: str) -> str | None:
    if not _use_redis():
        return _local_store.get(key)
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(
                f"{REDIS_URL}/get/{key}",
                headers={"Authorization": f"Bearer {REDIS_TOKEN}"}
            )
            data = r.json()
            result = data.get("result")
            if result is None:
                return None
            # Upstash wraps the stored string — decode if double-encoded
            if isinstance(result, str):
                return result
            return json.dumps(result)
    except Exception:
        return _local_store.get(key)


async def _redis_set(key: str, value: str, ttl: int):
    if not _use_redis():
        _local_store[key] = value
        return
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            # Upstash REST: POST /set/KEY/VALUE with optional EX query param
            await client.post(
                f"{REDIS_URL}/set/{key}/{value}?EX={ttl}",
                headers={"Authorization": f"Bearer {REDIS_TOKEN}"}
            )
    except Exception:
        _local_store[key] = value


async def get_session(session_id: str) -> SessionState:
    raw = await _redis_get(f"session:{session_id}")
    if not raw:
        return SessionState(session_id=session_id, is_new=True)
    try:
        data = json.loads(raw)
        return SessionState(**data)
    except Exception:
        return SessionState(session_id=session_id, is_new=True)


async def save_session(state: SessionState):
    serialized = state.model_dump_json()
    # URL-encode the JSON value to avoid issues with special chars in path
    encoded = serialized.replace("/", "%2F").replace(" ", "%20")
    await _redis_set(
        f"session:{state.session_id}",
        encoded,
        settings.SESSION_TTL_SECONDS,
    )


async def append_turn(session_id: str, role: str, content: str):
    state = await get_session(session_id)
    state.history.append(Turn(role=role, content=content))
    # Keep only last MAX_HISTORY_TURNS * 2 messages (N turns = N*2 messages)
    max_msgs = settings.MAX_HISTORY_TURNS * 2
    if len(state.history) > max_msgs:
        state.history = state.history[-max_msgs:]
    await save_session(state)


async def check_duplicate_message(message_id: str) -> bool:
    """For WhatsApp — prevent duplicate processing on Twilio/Meta retries."""
    key = f"msgid:{message_id}"
    raw = await _redis_get(key)
    if raw:
        return True  # duplicate
    await _redis_set(key, "1", 60)  # expire after 60 seconds
    return False
