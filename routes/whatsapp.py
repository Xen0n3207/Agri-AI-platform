"""
WhatsApp Routes – Webhook for WhatsApp-based farmer interactions.

In production, integrate with the WhatsApp Business API (via Twilio,
Meta Cloud API, or a similar provider).
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional
from services.llm_service import get_crop_advice

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp"])


# ── Request / Response schemas ──────────────────────────────────────────────────

class WhatsAppIncoming(BaseModel):
    """Simplified incoming WhatsApp message payload."""
    from_number: str
    message: str
    language: Optional[str] = "en"
    location: Optional[str] = None


class WhatsAppOutgoing(BaseModel):
    """Response to send back via WhatsApp."""
    to_number: str
    message: str


# ── Endpoints ───────────────────────────────────────────────────────────────────

@router.post("/webhook")
async def whatsapp_webhook(payload: WhatsAppIncoming):
    """
    Receive an incoming WhatsApp message, process it with AI,
    and return a response.

    In production, this would be the webhook URL registered with
    the WhatsApp Business API provider.
    """
    # Generate AI response
    advice = await get_crop_advice(
        query=payload.message,
        location=payload.location,
        language=payload.language,
    )

    return {
        "status": "success",
        "channel": "whatsapp",
        "incoming": {
            "from": payload.from_number,
            "message": payload.message,
        },
        "response": {
            "to": payload.from_number,
            "message": advice,
        },
    }


@router.get("/status")
async def whatsapp_status():
    """Health check for the WhatsApp integration."""
    return {
        "status": "active",
        "provider": "mock (configure WhatsApp Business API in production)",
        "features": ["text_messages", "ai_advisory", "disease_detection"],
    }
