import logging
from fastapi import APIRouter, Request, Response
from fastapi.responses import PlainTextResponse
from services.session import check_duplicate_message
from config import settings
import httpx

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Main webhook dispatcher ───────────────────────────────────────────────────
@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    if settings.WHATSAPP_PROVIDER == "twilio":
        return await _handle_twilio(request)
    return await _handle_meta(request)


# ── Twilio ────────────────────────────────────────────────────────────────────
async def _handle_twilio(request: Request):
    form = await request.form()
    message_sid = form.get("MessageSid", "")
    from_number = str(form.get("From", "")).replace("whatsapp:", "")
    body = str(form.get("Body", "")).strip()

    if not from_number or not body:
        return PlainTextResponse("", status_code=200)

    # Deduplicate Twilio retries
    if await check_duplicate_message(message_sid):
        return PlainTextResponse("", status_code=200)

    reply = await _get_chat_reply(body, session_id=from_number, request=request)

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response><Message>{_escape_xml(reply)}</Message></Response>"""
    return Response(content=twiml, media_type="application/xml")


# ── Meta Cloud API ────────────────────────────────────────────────────────────
@router.get("/webhook")
async def meta_verify(request: Request):
    """Meta webhook verification handshake."""
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == settings.META_VERIFY_TOKEN
    ):
        return PlainTextResponse(params.get("hub.challenge", ""))
    return Response(status_code=403)


async def _handle_meta(request: Request):
    try:
        body = await request.json()
        entry = body["entry"][0]["changes"][0]["value"]
        msg = entry["messages"][0]
        from_number = msg["from"]
        message_id = msg["id"]
        # Phone number ID needed for sending replies
        phone_number_id = entry["metadata"]["phone_number_id"]
        text = msg["text"]["body"]
    except (KeyError, IndexError, Exception) as e:
        logger.warning(f"Meta webhook parse error: {e}")
        return Response(status_code=200)

    if await check_duplicate_message(message_id):
        return Response(status_code=200)

    reply = await _get_chat_reply(text, session_id=from_number, request=request)

    # Send reply via Meta Graph API (use phone_number_id, not from_number)
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                f"https://graph.facebook.com/v19.0/{phone_number_id}/messages",
                headers={"Authorization": f"Bearer {settings.META_ACCESS_TOKEN}"},
                json={
                    "messaging_product": "whatsapp",
                    "to": from_number,
                    "type": "text",
                    "text": {"body": reply},
                },
            )
    except Exception as e:
        logger.error(f"Meta send failed: {e}")

    return Response(status_code=200)


# ── Shared helper ─────────────────────────────────────────────────────────────
async def _get_chat_reply(message: str, session_id: str, request: Request) -> str:
    """Forward message to /chat and return formatted reply string."""
    try:
        base_url = str(request.base_url).rstrip("/")
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                f"{base_url}/chat",
                json={"message": message, "session_id": session_id},
            )
            chat_resp = r.json()

        reply = chat_resp.get("reply", "Sorry, I could not process your request.")
        if chat_resp.get("parivahan_link"):
            reply += f"\n\nCheck & pay your challan: {chat_resp['parivahan_link']}"
        return reply
    except Exception as e:
        logger.error(f"Chat forwarding failed: {e}")
        return "Sorry, I'm temporarily unavailable. Please try again shortly."


def _escape_xml(text: str) -> str:
    """Escape special chars for TwiML XML."""
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
    )
