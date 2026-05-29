from fastapi import APIRouter
from models.request import LanguageRequest
from models.response import LanguageResponse
from services.session import get_session, save_session
from services.language import is_valid_language, get_welcome_message

router = APIRouter()


@router.post("", response_model=LanguageResponse)
async def set_language(req: LanguageRequest):
    session = await get_session(req.session_id)

    if is_valid_language(req.language):
        session.language = req.language
        if session.onboarding_step == "language":
            session.onboarding_step = "location"
        await save_session(session)
        return LanguageResponse(
            session_id=req.session_id,
            language=req.language,
            message=get_welcome_message(req.language),
        )

    return LanguageResponse(
        session_id=req.session_id,
        language=session.language,
        message=f"Language '{req.language}' is not supported. Current language: {session.language}",
    )
