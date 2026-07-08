"""
SQLAlchemy ORM models for Agri AI Platform.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean
from database import Base


# ── Crop ────────────────────────────────────────────────────────────────────────

class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    season = Column(String(50))
    soil_type = Column(String(100))
    water_requirement = Column(String(50))
    temperature_min = Column(Float)
    temperature_max = Column(Float)
    humidity_min = Column(Float)
    humidity_max = Column(Float)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# ── Disease ─────────────────────────────────────────────────────────────────────

class Disease(Base):
    __tablename__ = "diseases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    crop_name = Column(String(100), index=True)
    symptoms = Column(Text)
    cause = Column(String(200))
    treatment = Column(Text)
    prevention = Column(Text)
    image_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)


# ── Weather Log ─────────────────────────────────────────────────────────────────

class WeatherLog(Base):
    __tablename__ = "weather_logs"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(200), nullable=False)
    temperature = Column(Float)
    humidity = Column(Float)
    rainfall = Column(Float)
    wind_speed = Column(Float)
    description = Column(String(300))
    fetched_at = Column(DateTime, default=datetime.utcnow)


# ── Farmer / User ──────────────────────────────────────────────────────────────

class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    phone = Column(String(20), unique=True, index=True)
    language = Column(String(30), default="en")
    location = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ── Message Log (WhatsApp / SMS / Voice) ────────────────────────────────────────

class MessageLog(Base):
    __tablename__ = "message_logs"

    id = Column(Integer, primary_key=True, index=True)
    farmer_phone = Column(String(20), index=True)
    channel = Column(String(20))           # whatsapp / sms / voice
    direction = Column(String(10))         # inbound / outbound
    content = Column(Text)
    response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# ── Soil Data (from soil health cards / lab tests) ──────────────────────────────

class SoilData(Base):
    __tablename__ = "soil_data"

    id = Column(Integer, primary_key=True, index=True)
    farmer_phone = Column(String(20), index=True)
    location = Column(String(200))
    nitrogen = Column(Float)                # kg/ha
    phosphorus = Column(Float)              # kg/ha
    potassium = Column(Float)               # kg/ha
    ph = Column(Float)
    organic_carbon = Column(Float)          # percentage
    soil_type = Column(String(100))
    tested_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


# ── Sensor Readings (IoT field sensors) ─────────────────────────────────────────

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String(100), nullable=False, index=True)
    farmer_phone = Column(String(20), index=True)
    location = Column(String(200))
    soil_moisture = Column(Float)           # percentage
    soil_temperature = Column(Float)        # Celsius
    air_temperature = Column(Float)
    humidity = Column(Float)
    light_intensity = Column(Float)         # lux
    recorded_at = Column(DateTime, default=datetime.utcnow)


# ── Crop Health Log (photo + voice combined) ────────────────────────────────────

class CropHealthLog(Base):
    __tablename__ = "crop_health_logs"

    id = Column(Integer, primary_key=True, index=True)
    farmer_phone = Column(String(20), index=True)
    crop_name = Column(String(100))
    location = Column(String(200))
    image_filename = Column(String(500))     # uploaded photo
    voice_transcript = Column(Text)          # speech-to-text result
    voice_filename = Column(String(500))     # uploaded audio
    ai_diagnosis = Column(Text)              # AI result as JSON string
    status = Column(String(30), default="pending")  # pending / diagnosed / referred
    language = Column(String(20), default="en")
    created_at = Column(DateTime, default=datetime.utcnow)
