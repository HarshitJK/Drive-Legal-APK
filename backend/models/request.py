from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    session_id: str
    # Optional overrides (web/mobile send these; WhatsApp uses session)
    language: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None


class CalculatorRequest(BaseModel):
    violation: str          # "speeding" | "helmet" | "drunk_driving" | etc.
    vehicle_type: str       # "LMV" | "HMV" | "two_wheeler" | "three_wheeler"
    state: str
    offense_count: str      # "first" | "repeat"
    session_id: str = ""


class LocationRequest(BaseModel):
    session_id: str
    text: Optional[str] = None          # "I'm in Chennai"
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class LanguageRequest(BaseModel):
    session_id: str
    language: str           # "Tamil" | "Hindi" | "English" | etc.
