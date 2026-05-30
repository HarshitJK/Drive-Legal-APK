import json
import logging
from pathlib import Path
from typing import Optional, Tuple
from services.llm import call_llm

logger = logging.getLogger(__name__)

# ── All Indian states & union territories (canonical → list of lowercase aliases)
# Sorted so that longer aliases are matched before shorter substrings.
_INDIA_STATES: list[tuple[str, list[str]]] = [
    ("Andhra Pradesh",          ["andhra pradesh", "andhra"]),
    ("Arunachal Pradesh",       ["arunachal pradesh", "arunachal"]),
    ("Assam",                   ["assam"]),
    ("Bihar",                   ["bihar"]),
    ("Chhattisgarh",            ["chhattisgarh", "chattisgarh"]),
    ("Goa",                     ["goa"]),
    ("Gujarat",                 ["gujarat"]),
    ("Haryana",                 ["haryana"]),
    ("Himachal Pradesh",        ["himachal pradesh", "himachal"]),
    ("Jharkhand",               ["jharkhand"]),
    ("Karnataka",               ["karnataka"]),
    ("Kerala",                  ["kerala"]),
    ("Madhya Pradesh",          ["madhya pradesh"]),
    ("Maharashtra",             ["maharashtra"]),
    ("Manipur",                 ["manipur"]),
    ("Meghalaya",               ["meghalaya"]),
    ("Mizoram",                 ["mizoram"]),
    ("Nagaland",                ["nagaland"]),
    ("Odisha",                  ["odisha", "orissa"]),
    ("Punjab",                  ["punjab"]),
    ("Rajasthan",               ["rajasthan"]),
    ("Sikkim",                  ["sikkim"]),
    ("Tamil Nadu",              ["tamil nadu", "tamilnadu"]),
    ("Telangana",               ["telangana"]),
    ("Tripura",                 ["tripura"]),
    ("Uttar Pradesh",           ["uttar pradesh"]),
    ("Uttarakhand",             ["uttarakhand", "uttaranchal"]),
    ("West Bengal",             ["west bengal", "bengal"]),
    # Union Territories
    ("Delhi",                   ["new delhi", "delhi", "ncr"]),
    ("Jammu and Kashmir",       ["jammu and kashmir", "kashmir", "jammu"]),
    ("Ladakh",                  ["ladakh"]),
    ("Puducherry",              ["puducherry", "pondicherry"]),
    ("Chandigarh",              ["chandigarh"]),
    ("Andaman and Nicobar",     ["andaman and nicobar", "andaman"]),
    ("Dadra and Nagar Haveli",  ["dadra and nagar haveli", "dadra"]),
    ("Daman and Diu",           ["daman and diu", "daman"]),
    ("Lakshadweep",             ["lakshadweep"]),
]

# ── Major Indian cities → (display_name, state) ────────────────────────────────
# Listed longest-key-first so multi-word cities (e.g. "new delhi") win over "delhi".
_INDIA_CITIES: list[tuple[str, str, str]] = [
    ("new delhi",           "New Delhi",             "Delhi"),
    ("thiruvananthapuram",  "Thiruvananthapuram",    "Kerala"),
    ("visakhapatnam",       "Visakhapatnam",         "Andhra Pradesh"),
    ("vijayawada",          "Vijayawada",            "Andhra Pradesh"),
    ("west bengal",         "West Bengal",           "West Bengal"),
    ("bengaluru",           "Bengaluru",             "Karnataka"),
    ("bangalore",           "Bangalore",             "Karnataka"),
    ("coimbatore",          "Coimbatore",            "Tamil Nadu"),
    ("bhubaneswar",         "Bhubaneswar",           "Odisha"),
    ("ahmedabad",           "Ahmedabad",             "Gujarat"),
    ("hyderabad",           "Hyderabad",             "Telangana"),
    ("chandigarh",          "Chandigarh",            "Chandigarh"),
    ("gurugram",            "Gurugram",              "Haryana"),
    ("faridabad",           "Faridabad",             "Haryana"),
    ("gurgaon",             "Gurgaon",               "Haryana"),
    ("varanasi",            "Varanasi",              "Uttar Pradesh"),
    ("ludhiana",            "Ludhiana",              "Punjab"),
    ("amritsar",            "Amritsar",              "Punjab"),
    ("guwahati",            "Guwahati",              "Assam"),
    ("dehradun",            "Dehradun",              "Uttarakhand"),
    ("srinagar",            "Srinagar",              "Jammu and Kashmir"),
    ("agartala",            "Agartala",              "Tripura"),
    ("itanagar",            "Itanagar",              "Arunachal Pradesh"),
    ("shillong",            "Shillong",              "Meghalaya"),
    ("gangtok",             "Gangtok",               "Sikkim"),
    ("imphal",              "Imphal",                "Manipur"),
    ("varanasi",            "Varanasi",              "Uttar Pradesh"),
    ("jodhpur",             "Jodhpur",               "Rajasthan"),
    ("madurai",             "Madurai",               "Tamil Nadu"),
    ("chennai",             "Chennai",               "Tamil Nadu"),
    ("kolkata",             "Kolkata",               "West Bengal"),
    ("lucknow",             "Lucknow",               "Uttar Pradesh"),
    ("kanpur",              "Kanpur",                "Uttar Pradesh"),
    ("nagpur",              "Nagpur",                "Maharashtra"),
    ("nashik",              "Nashik",                "Maharashtra"),
    ("mumbai",              "Mumbai",                "Maharashtra"),
    ("indore",              "Indore",                "Madhya Pradesh"),
    ("bhopal",              "Bhopal",                "Madhya Pradesh"),
    ("jaipur",              "Jaipur",                "Rajasthan"),
    ("raipur",              "Raipur",                "Chhattisgarh"),
    ("ranchi",              "Ranchi",                "Jharkhand"),
    ("patna",               "Patna",                 "Bihar"),
    ("dispur",              "Dispur",                "Assam"),
    ("aizawl",              "Aizawl",                "Mizoram"),
    ("kohima",              "Kohima",                "Nagaland"),
    ("panaji",              "Panaji",                "Goa"),
    ("shimla",              "Shimla",                "Himachal Pradesh"),
    ("kochi",               "Kochi",                 "Kerala"),
    ("noida",               "Noida",                 "Uttar Pradesh"),
    ("agra",                "Agra",                  "Uttar Pradesh"),
    ("surat",               "Surat",                 "Gujarat"),
    ("pune",                "Pune",                  "Maharashtra"),
    ("jammu",               "Jammu",                 "Jammu and Kashmir"),
    ("delhi",               "Delhi",                 "Delhi"),
]


def _regex_location(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract an Indian state and/or city from user text without an LLM.
    Checks city names first (longest key first to avoid partial matches),
    then state names.
    """
    lower = text.lower()

    found_state: Optional[str] = None
    found_city: Optional[str] = None

    # 1. Match a city (implies state too)
    for key, city_display, state_display in _INDIA_CITIES:
        if key in lower:
            found_city = city_display
            found_state = state_display
            break

    # 2. Also check for an explicit state name mention
    for state_canonical, aliases in _INDIA_STATES:
        for alias in sorted(aliases, key=lambda a: -len(a)):   # longest alias first
            if alias in lower:
                found_state = state_canonical
                break
        else:
            continue
        break

    return found_state, found_city


async def extract_location_from_text(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extracts state and city from text.

    Strategy:
      1. Fast keyword/regex match against all Indian states & cities (no LLM, always works).
      2. If that fails, call the LLM for free-form interpretation.

    Returns (state, city).
    """
    # ── Step 1: keyword match (no API required) ────────────────────────────────
    state, city = _regex_location(text)
    if state:
        logger.info(f"Location extracted via keyword match: state={state!r}, city={city!r}")
        return state, city

    # ── Step 2: LLM fallback ──────────────────────────────────────────────────
    prompt_path = Path("prompts/location_extract.txt")
    if prompt_path.exists():
        prompt = prompt_path.read_text(encoding="utf-8")
    else:
        prompt = (
            'Extract the Indian state and city from the user message. '
            'Return JSON only, no extra text: {"state": "...", "city": "..."}'
        )

    try:
        raw = await call_llm(
            [{"role": "user", "content": text}],
            system=prompt,
        )
        # Strip markdown code fences if present
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        data = json.loads(raw)
        llm_state = data.get("state") or None
        llm_city  = data.get("city")  or None
        if llm_state:
            logger.info(f"Location extracted via LLM: state={llm_state!r}, city={llm_city!r}")
            return llm_state, llm_city
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
