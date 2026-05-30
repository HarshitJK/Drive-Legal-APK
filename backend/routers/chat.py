import json
import logging
from pathlib import Path
from fastapi import APIRouter, Request
from models.request import ChatRequest
from models.response import ChatResponse
from services.session import get_session, save_session, append_turn
from services.wiki import WikiService
from services.llm import call_llm
from services.language import (
    detect_language_from_script,
    LANGUAGE_NUMBER_MAP,
    get_language_picker_message,
    get_welcome_message,
    get_location_ask_message,
)
from services.location import extract_location_from_text
from utils.parivahan import build_parivahan_link

logger = logging.getLogger(__name__)

router = APIRouter()

SYSTEM_TEMPLATE = Path("prompts/system.txt").read_text(encoding="utf-8")

FINE_KEYWORDS = [
    "fine", "challan", "penalty", "speeding", "helmet", "drunk",
    "license", "insurance", "puc", "seatbelt", "mobile", "signal",
    "₹", "rs", "rupee", "amount", "pay", "fee", "section",
]


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request):
    wiki: WikiService = request.app.state.wiki
    session = await get_session(req.session_id)

    # ── Override from request (web/mobile direct params) ─────────────────────
    if req.language and req.language != session.language:
        session.language = req.language
        if session.onboarding_step == "language":
            session.onboarding_step = "location" if not session.state else "done"
    if req.state:
        session.state = req.state
        if session.onboarding_step == "location":
            session.onboarding_step = "done"
    if req.city:
        session.city = req.city

    # ── ONBOARDING STEP 1: Language selection ─────────────────────────────────
    if session.onboarding_step == "language":
        # Check if message is in a detectable script
        detected = detect_language_from_script(req.message)
        if detected:
            session.language = detected
            session.onboarding_step = "location"
            await save_session(session)
            return ChatResponse(
                reply=get_welcome_message(detected) + "\n\n" + get_location_ask_message(detected),
                language=detected,
                session_id=req.session_id,
            )

        # Check if user replied with a number
        stripped = req.message.strip()
        if stripped in LANGUAGE_NUMBER_MAP:
            lang = LANGUAGE_NUMBER_MAP[stripped]
            session.language = lang
            session.onboarding_step = "location"
            await save_session(session)
            return ChatResponse(
                reply=get_welcome_message(lang) + "\n\n" + get_location_ask_message(lang),
                language=lang,
                session_id=req.session_id,
            )

        # Show language picker
        await save_session(session)
        return ChatResponse(
            reply=get_language_picker_message(),
            language="English",
            session_id=req.session_id,
        )

    # ── ONBOARDING STEP 2: Location ───────────────────────────────────────────
    if session.onboarding_step == "location" and not session.state:
        state, city = await extract_location_from_text(req.message)
        if state:
            session.state = state
            session.city = city or ""
            session.onboarding_step = "done"
            session.is_new = False

        if not session.state:
            await save_session(session)
            return ChatResponse(
                reply=get_location_ask_message(session.language),
                language=session.language,
                session_id=req.session_id,
            )

    # ── NORMAL CHAT ───────────────────────────────────────────────────────────
    session.onboarding_step = "done"
    session.is_new = False

    # Wiki search
    relevant_articles = wiki.search(req.message, state=session.state)
    wiki_context = "\n\n---\n\n".join(relevant_articles) if relevant_articles else "No specific wiki articles found."

    # Build system prompt
    system = SYSTEM_TEMPLATE.format(
        language=session.language,
        state=session.state or "India",
        city=session.city or "",
        wiki_context=wiki_context,
    )

    # Build message history for LLM
    messages = [
        {"role": t.role, "content": t.content}
        for t in session.history
    ]
    messages.append({"role": "user", "content": req.message})

    # LLM call
    try:
        reply = await call_llm(messages, system)
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        reply = "Sorry, I'm having trouble connecting right now. Please try again in a moment."

    # Append Parivahan link if fine-related
    parivahan_link = None
    combined_lower = (req.message + " " + reply).lower()
    if any(kw in combined_lower for kw in FINE_KEYWORDS):
        parivahan_link = build_parivahan_link(session.state)

    # Save session and append turns
    await save_session(session)
    await append_turn(req.session_id, "user", req.message)
    await append_turn(req.session_id, "assistant", reply)

    return ChatResponse(
        reply=reply,
        language=session.language,
        parivahan_link=parivahan_link,
        session_id=req.session_id,
    )
