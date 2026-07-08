"""
Agri AI Platform – Main Application Entry Point

Voice-and-SMS agricultural intelligence platform in Indic languages.
Features:
  - Smart crop recommendation using soil data + satellite NDVI
  - Real-time dry-spell alerts + irrigation/fertilization guidance
  - Crop health logging via photo + voice for AI diagnosis
  - Ground sensor data analysis for field conditions
  - Multi-channel communication (Voice, SMS, WhatsApp)
  - Indic language support (Telugu, Hindi, Tamil, Kannada, Marathi)

Run with:
    uvicorn app:app --reload --host 0.0.0.0 --port 8000
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routes import crop, weather, disease, whatsapp, voice, sms, sensor


# ── Lifespan (startup / shutdown) ──────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup tasks before the app begins serving requests."""
    # Initialize database tables
    init_db()
    print("[OK] Database initialized")

    # Ensure upload & static directories exist
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    print("[OK] Directories ready")

    print("[READY] Agri AI Platform is running!")
    yield
    print("[STOP] Shutting down Agri AI Platform")


# ── App instance ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Agri AI Platform",
    description=(
        "Voice-and-SMS agricultural intelligence platform in Indic languages. "
        "Smart crop recommendations (soil + satellite data), dry-spell alerts, "
        "irrigation guidance, and crop health logging via photo/voice for AI diagnosis."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ── CORS (allow all origins for development) ───────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Static files ───────────────────────────────────────────────────────────────

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# ── Register routers ──────────────────────────────────────────────────────────

app.include_router(crop.router)
app.include_router(weather.router)
app.include_router(disease.router)
app.include_router(sensor.router)
app.include_router(voice.router)
app.include_router(sms.router)
app.include_router(whatsapp.router)


# ── Root endpoints ─────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    """Root health check endpoint."""
    return {
        "name": "Agri AI Platform",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "components": {
            "1_crop_recommendation": {
                "description": "Smart crop engine using soil + satellite data",
                "endpoint": "/api/crop/recommend",
            },
            "2_weather_advisory": {
                "description": "Dry-spell alerts + irrigation guidance",
                "endpoints": ["/api/weather/dry-spell", "/api/weather/irrigation"],
            },
            "3_crop_health": {
                "description": "Photo + voice crop health logging for AI diagnosis",
                "endpoint": "/api/voice/health-log",
            },
            "sensors": "/api/sensor/analyze/{sensor_id}",
            "voice": "/api/voice/process",
            "sms": "/api/sms/receive",
        },
        "languages": ["en", "te", "hi", "ta", "kn", "mr"],
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "services": {
            "database": "connected",
            "crop_engine": "active (soil + satellite scoring)",
            "dry_spell_detector": "active",
            "irrigation_advisor": "active",
            "disease_detector": "active (mock model)",
            "sensor_analytics": "active",
            "llm_service": "active (mock - swap for Gemini/GPT)",
            "indic_languages": "te, hi, ta, kn, mr",
            "voice": "ready",
            "sms": "ready",
        },
    }
