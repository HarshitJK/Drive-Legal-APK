from pydantic import BaseModel
from typing import Optional


class ChatResponse(BaseModel):
    reply: str
    language: str
    parivahan_link: Optional[str] = None
    session_id: str


class CalculatorResponse(BaseModel):
    violation: str
    section: str
    vehicle_type: str
    state: str
    offense: str
    fine_min: int
    fine_max: int
    fine_display: str       # "₹1,000 – ₹2,000"
    state_note: Optional[str] = None
    parivahan_link: str


class LocationResponse(BaseModel):
    state: str
    city: str
    country: str = "India"


class LanguageResponse(BaseModel):
    session_id: str
    language: str
    message: str = "Language updated successfully"
