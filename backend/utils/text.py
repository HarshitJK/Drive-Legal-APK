import re


def clean_json_response(raw: str) -> str:
    """Strip markdown code fences from LLM JSON output."""
    raw = raw.strip()
    raw = re.sub(r'^```(?:json)?\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return raw.strip()


def truncate(text: str, max_chars: int = 500) -> str:
    """Truncate text to max_chars, appending ellipsis if needed."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "…"


def normalize_state_name(state: str) -> str:
    """Normalize common state name variants."""
    mapping = {
        "tamilnadu": "Tamil Nadu",
        "tn": "Tamil Nadu",
        "maha": "Maharashtra",
        "mh": "Maharashtra",
        "kar": "Karnataka",
        "ka": "Karnataka",
        "dl": "Delhi",
        "new delhi": "Delhi",
        "up": "Uttar Pradesh",
        "wb": "West Bengal",
        "kl": "Kerala",
        "gj": "Gujarat",
        "ts": "Telangana",
        "ap": "Andhra Pradesh",
    }
    key = state.lower().strip()
    return mapping.get(key, state.title())
