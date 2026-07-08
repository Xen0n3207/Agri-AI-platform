"""
Weather Routes – Weather data, dry-spell alerts, and irrigation guidance.
"""

from fastapi import APIRouter, Query
from typing import Optional
from services.weather_service import (
    get_current_weather,
    get_weather_forecast,
    get_farming_weather_alert,
    detect_dry_spell,
    get_irrigation_guidance,
)

router = APIRouter(prefix="/api/weather", tags=["Weather"])


@router.get("/current")
async def current_weather(
    location: str = Query(..., description="City or region name"),
):
    """Get current weather conditions for a location."""
    data = await get_current_weather(location)
    return {"status": "success", "weather": data}


@router.get("/forecast")
async def forecast(
    location: str = Query(..., description="City or region name"),
    days: int = Query(7, ge=1, le=10, description="Forecast days (1-10)"),
):
    """Get a multi-day weather forecast with daily rainfall data."""
    data = await get_weather_forecast(location, days=days)
    return {"status": "success", "forecast": data}


@router.get("/dry-spell")
async def dry_spell_check(
    location: str = Query(..., description="City or region name"),
    threshold_days: int = Query(5, ge=3, le=14, description="Min consecutive dry days to trigger alert"),
):
    """
    Detect ongoing or upcoming dry spells.

    Analyzes the 10-day forecast and flags stretches of consecutive
    days with rainfall below 2.5mm. Returns alert levels:
    none / watch / warning / critical.
    """
    result = await detect_dry_spell(
        location, consecutive_dry_days_threshold=threshold_days
    )
    return {"status": "success", "dry_spell": result}


@router.get("/irrigation")
async def irrigation_guidance(
    location: str = Query(..., description="City or region name"),
    crop: Optional[str] = Query(None, description="Crop name for specific advice"),
    soil_moisture: Optional[float] = Query(None, ge=0, le=100, description="Current soil moisture %"),
):
    """
    Get irrigation scheduling guidance based on weather forecast,
    dry-spell analysis, and soil moisture readings.

    Combines weather + sensor data to tell farmers whether to
    irrigate now, wait, or drain.
    """
    result = await get_irrigation_guidance(
        location, crop_name=crop, soil_moisture=soil_moisture
    )
    return {"status": "success", "guidance": result}


@router.get("/alerts")
async def farming_alerts(
    location: str = Query(..., description="City or region name"),
):
    """Check for active weather alerts relevant to farming."""
    alert = await get_farming_weather_alert(location)
    if alert:
        return {"status": "alert", "alert": alert}
    return {"status": "clear", "message": "No active weather alerts for this location."}
