import json
import logging
from pathlib import Path
from typing import Optional, Tuple
from services.llm import call_llm

logger = logging.getLogger(__name__)

async def extract_location_from_text(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extracts state and city from text using LLM.
    Returns (state, city).
    """
    prompt_path = Path("prompts/location_extract.txt")
    if prompt_path.exists():
        prompt = prompt_path.read_text(encoding="utf-8")
    else:
        prompt = 'Extract state and city. Return JSON: {"state": "...", "city": "..."}'

    try:
        raw = await call_llm(
            [{"role": "user", "content": text}],
            system=prompt,
        )
        # Handle case where LLM wraps JSON in markdown blocks
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()
            
        data = json.loads(raw)
        return data.get("state"), data.get("city")
    except Exception as e:
        logger.warning(f"LLM location extraction failed: {e}")
        return None, None

async def extract_location_from_coordinates(latitude: float, longitude: float) -> Tuple[Optional[str], Optional[str]]:
    """
    Reverse geocodes coordinates to find state and city.
    Returns (state, city).
    """
    try:
        from geopy.geocoders import Nominatim
        from geopy.adapters import AioHTTPAdapter

        async with Nominatim(
            user_agent="drivelegal_app",
            adapter_factory=AioHTTPAdapter,
        ) as geolocator:
            location = await geolocator.reverse(
                f"{latitude}, {longitude}",
                language="en",
                exactly_one=True,
            )
            if location:
                addr = location.raw.get("address", {})
                state = addr.get("state", "")
                city = (
                    addr.get("city")
                    or addr.get("town")
                    or addr.get("village")
                    or ""
                )
                return state, city
    except Exception as e:
        logger.warning(f"Reverse geocode failed: {e}")
        
    return None, None
