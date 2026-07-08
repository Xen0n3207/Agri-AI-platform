"""
Sensor Service – Ground sensor data ingestion and analysis.

Handles soil moisture, temperature, and humidity readings from
field-deployed IoT sensors. In production, connect to actual
sensor gateways (e.g., ThingSpeak, AWS IoT, or custom MQTT).
"""

from datetime import datetime, timedelta
from typing import Optional


# ── Mock sensor readings ───────────────────────────────────────────────────────

def _generate_mock_readings(sensor_id: str, hours: int = 24) -> list[dict]:
    """Generate realistic mock sensor readings for demo."""
    readings = []
    base_time = datetime.utcnow() - timedelta(hours=hours)

    for i in range(hours):
        timestamp = base_time + timedelta(hours=i)
        # Simulate daily variation
        hour_of_day = (timestamp.hour + 5) % 24  # IST offset
        temp_variation = 8 * (1 - abs(hour_of_day - 14) / 14)  # Peak at 2 PM

        readings.append({
            "sensor_id": sensor_id,
            "timestamp": timestamp.isoformat(),
            "soil_moisture": max(15, 55 - i * 1.5 + (5 if i % 8 == 0 else 0)),
            "soil_temperature": 24 + temp_variation,
            "air_temperature": 26 + temp_variation + 2,
            "humidity": max(30, 75 - i * 0.8),
            "light_intensity": 800 if 6 <= hour_of_day <= 18 else 0,
        })

    return readings


async def get_latest_reading(sensor_id: str) -> dict:
    """Get the most recent sensor reading."""
    readings = _generate_mock_readings(sensor_id, hours=1)
    latest = readings[-1]

    # Add status flags
    latest["status"] = {
        "soil_moisture": _classify_soil_moisture(latest["soil_moisture"]),
        "soil_temperature": _classify_temperature(latest["soil_temperature"]),
        "battery": "good",
        "signal": "strong",
    }

    return latest


async def get_sensor_history(
    sensor_id: str,
    hours: int = 24,
) -> dict:
    """Get historical sensor readings."""
    readings = _generate_mock_readings(sensor_id, hours=hours)

    # Calculate summary statistics
    moistures = [r["soil_moisture"] for r in readings]
    temps = [r["soil_temperature"] for r in readings]

    return {
        "sensor_id": sensor_id,
        "period_hours": hours,
        "readings_count": len(readings),
        "summary": {
            "soil_moisture": {
                "min": round(min(moistures), 1),
                "max": round(max(moistures), 1),
                "avg": round(sum(moistures) / len(moistures), 1),
                "trend": "declining" if moistures[-1] < moistures[0] else "stable",
            },
            "soil_temperature": {
                "min": round(min(temps), 1),
                "max": round(max(temps), 1),
                "avg": round(sum(temps) / len(temps), 1),
            },
        },
        "readings": readings,
    }


async def analyze_field_conditions(
    sensor_id: str,
    crop_name: Optional[str] = None,
) -> dict:
    """
    Analyze field conditions and generate actionable alerts
    based on sensor data trends.
    """
    history = await get_sensor_history(sensor_id, hours=24)
    summary = history["summary"]
    latest_moisture = history["readings"][-1]["soil_moisture"]

    alerts = []
    recommendations = []

    # Soil moisture analysis
    if latest_moisture < 20:
        alerts.append({
            "type": "critical",
            "parameter": "soil_moisture",
            "message": f"Soil moisture critically low at {latest_moisture:.0f}%. Irrigate immediately.",
        })
        recommendations.append("Apply 40-50mm irrigation via drip or sprinkler.")
    elif latest_moisture < 35:
        alerts.append({
            "type": "warning",
            "parameter": "soil_moisture",
            "message": f"Soil moisture low at {latest_moisture:.0f}%. Plan irrigation within 24hrs.",
        })
        recommendations.append("Apply 25-30mm irrigation within 24 hours.")

    # Moisture trend analysis
    if summary["soil_moisture"]["trend"] == "declining":
        alerts.append({
            "type": "info",
            "parameter": "soil_moisture_trend",
            "message": "Soil moisture is on a declining trend over the last 24 hours.",
        })
        recommendations.append("Monitor closely. May need irrigation sooner than scheduled.")

    # Temperature analysis
    if summary["soil_temperature"]["max"] > 38:
        alerts.append({
            "type": "warning",
            "parameter": "soil_temperature",
            "message": f"High soil temperature detected: {summary['soil_temperature']['max']}C.",
        })
        recommendations.append("Apply mulch to reduce soil temperature and moisture loss.")

    if not alerts:
        alerts.append({
            "type": "ok",
            "parameter": "overall",
            "message": "All field conditions are within normal range.",
        })

    return {
        "sensor_id": sensor_id,
        "crop": crop_name or "general",
        "timestamp": datetime.utcnow().isoformat(),
        "current_moisture": latest_moisture,
        "alerts": alerts,
        "recommendations": recommendations,
        "summary": summary,
    }


# ── Helpers ────────────────────────────────────────────────────────────────────

def _classify_soil_moisture(value: float) -> str:
    if value < 20:
        return "critically_low"
    elif value < 35:
        return "low"
    elif value < 60:
        return "adequate"
    else:
        return "high"


def _classify_temperature(value: float) -> str:
    if value < 15:
        return "cold"
    elif value < 25:
        return "optimal"
    elif value < 35:
        return "warm"
    else:
        return "hot"
