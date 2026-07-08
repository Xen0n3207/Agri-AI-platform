"""
WhatsApp Routes – Real Twilio WhatsApp Sandbox Integration.

Handles incoming messages (text, image, audio) from the Twilio WhatsApp Sandbox,
logs them to the database, and responds with TwiML.
"""

import os
from fastapi import APIRouter, Request, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

from database import get_db
from models import MessageLog

load_dotenv()

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp"])


@router.post("/webhook")
async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Receive an incoming WhatsApp message via Twilio webhook.
    Twilio sends data as application/x-www-form-urlencoded.
    """
    # 1. Parse incoming form data from Twilio
    form_data = await request.form()
    
    from_number = form_data.get("From", "")
    body_text = form_data.get("Body", "")
    num_media = int(form_data.get("NumMedia", 0))
    
    # Check for media (images, audio)
    media_url = None
    media_type = None
    if num_media > 0:
        media_url = form_data.get("MediaUrl0")
        media_type = form_data.get("MediaContentType0")

    # Combine text and media info for logging
    log_content = body_text
    if media_url:
        log_content += f" [Media: {media_type} - {media_url}]"

    # 2. For now, we reply with a static message
    reply_text = "Hello from Agri AI"

    # 3. Log the interaction to the database
    message_log = MessageLog(
        farmer_phone=from_number,
        channel="whatsapp",
        direction="inbound",
        content=log_content.strip(),
        response=reply_text
    )
    db.add(message_log)
    db.commit()

    # 4. Generate TwiML response
    resp = MessagingResponse()
    resp.message(reply_text)
    
    return Response(content=str(resp), media_type="application/xml")


@router.get("/status")
async def whatsapp_status():
    """Health check for the WhatsApp integration."""
    return {
        "status": "active",
        "provider": "Twilio Sandbox",
        "features": ["text_messages", "media_parsing", "db_logging"],
        "env_vars_loaded": {
            "TWILIO_ACCOUNT_SID": bool(os.getenv("TWILIO_ACCOUNT_SID")),
            "TWILIO_AUTH_TOKEN": bool(os.getenv("TWILIO_AUTH_TOKEN")),
            "TWILIO_WHATSAPP_NUMBER": bool(os.getenv("TWILIO_WHATSAPP_NUMBER"))
        }
    }
