from pydantic import BaseModel
from typing import Optional, List


class Turn(BaseModel):
    role: str               # "user" | "assistant"
    content: str


class SessionState(BaseModel):
    session_id: str
    language: str = "English"
    state: Optional[str] = None
    city: Optional[str] = None
    history: List[Turn] = []
    is_new: bool = True     # True until language + location confirmed
    onboarding_step: str = "language"   # "language" | "location" | "done"
