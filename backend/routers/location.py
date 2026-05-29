import json
import logging
from fastapi import APIRouter
from models.request import LocationRequest
from models.response import LocationResponse
from services.session import get_session, save_session
from services.location import extract_location_from_text, extract_location_from_coordinates
from utils.text import normalize_state_name

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", response_model=LocationResponse)
async def set_location(req: LocationRequest):
    session = await get_session(req.session_id)
    state = ""
    city = ""

    if req.latitude is not None and req.longitude is not None:
        state, city = await extract_location_from_coordinates(req.latitude, req.longitude)
        state = state or ""
        city = city or ""

    elif req.text:
        state, city = await extract_location_from_text(req.text)
        state = state or ""
        city = city or ""

    # Normalize state name
    if state:
        state = normalize_state_name(state)

    if state or city:
        session.state = state
        session.city = city
        if session.onboarding_step == "location":
            session.onboarding_step = "done"
        await save_session(session)

    return LocationResponse(state=state, city=city)
