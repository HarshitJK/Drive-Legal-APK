from config import settings

# Full state code map
STATE_PARIVAHAN_CODES = {
    "Andhra Pradesh": "AP",
    "Arunachal Pradesh": "AR",
    "Assam": "AS",
    "Bihar": "BR",
    "Chhattisgarh": "CG",
    "Goa": "GA",
    "Gujarat": "GJ",
    "Haryana": "HR",
    "Himachal Pradesh": "HP",
    "Jharkhand": "JH",
    "Karnataka": "KA",
    "Kerala": "KL",
    "Madhya Pradesh": "MP",
    "Maharashtra": "MH",
    "Manipur": "MN",
    "Meghalaya": "ML",
    "Mizoram": "MZ",
    "Nagaland": "NL",
    "Odisha": "OD",
    "Punjab": "PB",
    "Rajasthan": "RJ",
    "Sikkim": "SK",
    "Tamil Nadu": "TN",
    "Telangana": "TS",
    "Tripura": "TR",
    "Uttar Pradesh": "UP",
    "Uttarakhand": "UK",
    "West Bengal": "WB",
    "Delhi": "DL",
    "Jammu and Kashmir": "JK",
    "Ladakh": "LA",
    "Chandigarh": "CH",
    "Puducherry": "PY",
}


def build_parivahan_link(state: str = None) -> str:
    """Build a Parivahan echallan URL, optionally state-specific."""
    base = settings.PARIVAHAN_BASE_URL
    return f"{base}/index/accused-challan"


def build_challan_check_link() -> str:
    return f"{settings.PARIVAHAN_BASE_URL}/index/accused-challan"


def should_append_parivahan(text: str) -> bool:
    keywords = ["fine", "challan", "₹", "penalty", "pay", "amount", "fee"]
    return any(kw in text.lower() for kw in keywords)


def get_state_code(state: str) -> str | None:
    return STATE_PARIVAHAN_CODES.get(state)
