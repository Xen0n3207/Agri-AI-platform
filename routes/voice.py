"""
Voice Routes – Voice-based farmer interactions + crop health logging.

Combines photo upload and voice description for crop health reports.
In production, integrate Whisper for Indic speech-to-text and
a telephony provider (Twilio/Exotel) for IVR.
"""

import os
import uuid
import json

from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from services.llm_service import (
    get_crop_advice,
    translate_response,
    diagnose_disease,
    get_template,
    SUPPORTED_LANGUAGES,
)
from services.disease_service import detect_disease_from_image

router = APIRouter(prefix="/api/voice", tags=["Voice"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")


# ── Voice query processing ─────────────────────────────────────────────────────

@router.post("/process")
async def process_voice_query(
    caller_number: str = Form(..., description="Farmer phone number"),
    transcription: str = Form(..., description="Speech-to-text result"),
    language: str = Form("en", description="Language code: en, te, hi, ta, kn, mr"),
    location: Optional[str] = Form(None, description="Farmer location"),
):
    """
    Process a voice query from a farmer.

    Flow: Receive STT transcription -> AI advisory -> localized response for TTS.
    """
    advice = await get_crop_advice(
        query=transcription,
        location=location,
        language=language,
    )

    return {
        "status": "success",
        "channel": "voice",
        "caller": caller_number,
        "language": SUPPORTED_LANGUAGES.get(language, language),
        "transcription": transcription,
        "response_text": advice,
        "tts_ready": True,
    }


# ── Crop health logging (photo + voice combo) ──────────────────────────────────

@router.post("/health-log")
async def crop_health_log(
    farmer_phone: str = Form(..., description="Farmer phone number"),
    crop_name: str = Form(..., description="Name of the crop"),
    voice_transcript: str = Form("", description="Voice description of symptoms (STT result)"),
    language: str = Form("en", description="Language code"),
    location: Optional[str] = Form(None, description="Farm location"),
    photo: Optional[UploadFile] = File(None, description="Photo of affected crop"),
    audio: Optional[UploadFile] = File(None, description="Voice recording (.wav/.mp3)"),
):
    """
    Log a crop health report combining photo and voice description.

    Farmers can:
    1. Upload a photo of the affected crop
    2. Describe symptoms in their language via voice
    3. Get AI-powered diagnosis in their preferred Indic language

    This is the core crop health logging endpoint that feeds into
    disease detection and expert referral workflows.
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    photo_filename = None
    audio_filename = None

    # Save photo if provided
    if photo and photo.filename:
        ext = photo.filename.split(".")[-1] if "." in photo.filename else "jpg"
        photo_filename = f"health_{uuid.uuid4().hex[:12]}.{ext}"
        filepath = os.path.join(UPLOAD_DIR, photo_filename)
        contents = await photo.read()
        with open(filepath, "wb") as f:
            f.write(contents)

    # Save audio if provided
    if audio and audio.filename:
        ext = audio.filename.split(".")[-1] if "." in audio.filename else "wav"
        audio_filename = f"voice_{uuid.uuid4().hex[:12]}.{ext}"
        filepath = os.path.join(UPLOAD_DIR, audio_filename)
        contents = await audio.read()
        with open(filepath, "wb") as f:
            f.write(contents)

    # Run AI diagnosis
    diagnosis = None
    if photo_filename:
        diagnosis = await detect_disease_from_image(
            os.path.join(UPLOAD_DIR, photo_filename)
        )
    elif voice_transcript:
        diagnosis = await diagnose_disease(
            crop_name=crop_name,
            symptoms=voice_transcript,
            language=language,
        )

    # Build localized response
    if diagnosis and diagnosis.get("detected", diagnosis.get("diagnosis")):
        disease_name = diagnosis.get("disease_name", diagnosis.get("diagnosis", "Unknown"))
        treatment = diagnosis.get("treatment", "Consult an expert.")
        if isinstance(treatment, list):
            treatment = treatment[0]
        localized_msg = get_template(
            language, "disease_detected",
            disease=disease_name, treatment=treatment
        )
    else:
        localized_msg = get_template(language, "no_disease")

    # Create health log entry (would persist to DB in production)
    health_log = {
        "id": uuid.uuid4().hex[:16],
        "farmer_phone": farmer_phone,
        "crop_name": crop_name,
        "location": location,
        "photo": photo_filename,
        "audio": audio_filename,
        "voice_transcript": voice_transcript,
        "language": language,
        "diagnosis": diagnosis,
        "localized_response": localized_msg,
        "status": "diagnosed" if diagnosis else "pending",
    }

    return {
        "status": "success",
        "channel": "voice",
        "health_log": health_log,
    }


# ── IVR Menu ───────────────────────────────────────────────────────────────────

@router.post("/ivr-menu")
async def ivr_menu(language: str = "en"):
    """Return the IVR menu structure in the farmer's language."""
    menus = {
        "en": {
            "welcome": "Welcome to Agri AI Platform. Please select an option.",
            "options": [
                {"key": "1", "label": "Crop Recommendations"},
                {"key": "2", "label": "Weather and Dry Spell Alerts"},
                {"key": "3", "label": "Report Crop Disease (Photo/Voice)"},
                {"key": "4", "label": "Irrigation Guidance"},
                {"key": "5", "label": "Speak to an Expert"},
                {"key": "0", "label": "Repeat Menu"},
            ],
        },
        "te": {
            "welcome": "Agri AI Platform ki swaagatham. Dayachesi oka option select cheyandi.",
            "options": [
                {"key": "1", "label": "Panta sifarasulu"},
                {"key": "2", "label": "Vaataavarana mariyu podi vaataavarana hechcharikalu"},
                {"key": "3", "label": "Panta vyaadhi nivedana (Photo/Voice)"},
                {"key": "4", "label": "Neetiparudaral margadarshanam"},
                {"key": "5", "label": "Nithidaarunitho maatlaadandi"},
                {"key": "0", "label": "Menu malli vinandi"},
            ],
        },
        "hi": {
            "welcome": "Agri AI Platform mein aapka swagat hai. Kripya ek option chune.",
            "options": [
                {"key": "1", "label": "Fasal ki sifarish"},
                {"key": "2", "label": "Mausam aur sukhe ki chetavani"},
                {"key": "3", "label": "Fasal rog ki report (Photo/Voice)"},
                {"key": "4", "label": "Sinchai margdarshan"},
                {"key": "5", "label": "Visheshagya se baat karein"},
                {"key": "0", "label": "Menu dobara sunein"},
            ],
        },
    }

    menu = menus.get(language, menus["en"])
    menu["language"] = language
    menu["supported_languages"] = list(SUPPORTED_LANGUAGES.keys())

    return {"status": "success", "menu": menu}


@router.get("/languages")
async def list_languages():
    """List all supported Indic languages."""
    return {"status": "success", "languages": SUPPORTED_LANGUAGES}


@router.get("/status")
async def voice_status():
    """Health check for the voice integration."""
    return {
        "status": "active",
        "provider": "mock (configure Twilio/Exotel in production)",
        "features": [
            "speech_to_text",
            "text_to_speech",
            "ivr_menu",
            "crop_health_logging",
            "photo_voice_combo",
            "indic_languages",
        ],
        "supported_languages": SUPPORTED_LANGUAGES,
    }
