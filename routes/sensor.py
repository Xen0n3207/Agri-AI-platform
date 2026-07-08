"""
Sensor Routes – Ground sensor data ingestion and field analysis.
"""

from fastapi import APIRouter, Query
from typing import Optional
from services.sensor_service import (
    get_latest_reading,
    get_sensor_history,
    analyze_field_conditions,
)

router = APIRouter(prefix="/api/sensor", tags=["Sensors"])


@router.get("/latest/{sensor_id}")
async def latest_reading(sensor_id: str):
    """
    Get the most recent reading from a field sensor.

    Returns soil moisture, soil temperature, air temperature,
    humidity, and light intensity with status flags.
    """
    data = await get_latest_reading(sensor_id)
    return {"status": "success", "reading": data}


@router.get("/history/{sensor_id}")
async def sensor_history(
    sensor_id: str,
    hours: int = Query(24, ge=1, le=168, description="History period in hours (max 7 days)"),
):
    """
    Get historical sensor readings with summary statistics.

    Includes min/max/avg values and moisture trend analysis.
    """
    data = await get_sensor_history(sensor_id, hours=hours)
    return {"status": "success", "history": data}


@router.get("/analyze/{sensor_id}")
async def analyze_field(
    sensor_id: str,
    crop: Optional[str] = Query(None, description="Crop name for specific thresholds"),
):
    """
    Analyze current field conditions and generate actionable alerts.

    Combines sensor readings with trend analysis to produce:
    - Soil moisture alerts (critical/warning/ok)
    - Temperature alerts
    - Irrigation recommendations
    """
    data = await analyze_field_conditions(sensor_id, crop_name=crop)
    return {"status": "success", "analysis": data}
