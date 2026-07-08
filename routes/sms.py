"""
SMS Routes – Endpoints for SMS-based farmer notifications and queries.

In production, integrate with an SMS gateway (e.g., Twilio SMS,
MSG91, or Textlocal).
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from services.llm_service import get_crop_advice

router = APIRouter(prefix="/api/sms", tags=["SMS"])


# ── Request schemas ─────────────────────────────────────────────────────────────

class SMSIncoming(BaseModel):
    """Incoming SMS message from a farmer."""
    from_number: str
    message: str
    language: Optional[str] = "en"


class SMSBulk(BaseModel):
    """Bulk SMS notification payload."""
    to_numbers: list[str]
    message: str


# ── Endpoints ───────────────────────────────────────────────────────────────────

@router.post("/receive")
async def receive_sms(payload: SMSIncoming):
    """
    Receive an incoming SMS query and respond with AI advice.
    """
    advice = await get_crop_advice(
        query=payload.message,
        language=payload.language,
    )

    # Trim for SMS character limit (160 chars for basic SMS)
    sms_response = advice[:155] + "..." if len(advice) > 160 else advice

    return {
        "status": "success",
        "channel": "sms",
        "incoming": {
            "from": payload.from_number,
            "message": payload.message,
        },
        "response": {
            "to": payload.from_number,
            "message": sms_response,
            "full_message": advice,
            "truncated": len(advice) > 160,
        },
    }


@router.post("/send-bulk")
async def send_bulk_sms(payload: SMSBulk):
    """
    Send a bulk SMS notification to multiple farmers.

    Use cases:
    - Weather alerts
    - Market price updates
    - Seasonal crop advisories
    """
    # In production, call the SMS gateway API here
    return {
        "status": "queued",
        "channel": "sms",
        "recipients_count": len(payload.to_numbers),
        "message_preview": payload.message[:100],
        "note": "In production, messages are queued and delivered via SMS gateway.",
    }


@router.post("/weather-alert")
async def send_weather_alert(
    location: str,
    numbers: list[str],
):
    """
    Send a weather alert SMS to farmers in a specific location.
    """
    alert_message = (
        f"⚠️ Weather Alert for {location}: "
        "Heavy rain expected in the next 48hrs. "
        "Secure your harvest and ensure proper field drainage. "
        "– Agri AI Platform"
    )

    return {
        "status": "queued",
        "channel": "sms",
        "alert_type": "weather",
        "location": location,
        "recipients_count": len(numbers),
        "message": alert_message,
    }


@router.get("/status")
async def sms_status():
    """Health check for the SMS integration."""
    return {
        "status": "active",
        "provider": "mock (configure SMS gateway in production)",
        "features": ["receive_sms", "send_reply", "bulk_notifications", "weather_alerts"],
    }
