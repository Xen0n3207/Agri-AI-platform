"""
Weather Service – Localized weather + dry-spell detection + irrigation guidance.

In production, integrate with OpenWeatherMap, IMD, or Skymet APIs.
"""

from typing import Optional
from datetime import datetime, timedelta


# ── Current weather ─────────────────────────────────────────────────────────────

async def get_current_weather(location: str) -> dict:
    """Fetch current weather for a given location."""
    return {
        "location": location,
        "temperature": 32.5,
        "humidity": 68.0,
        "rainfall": 0.0,
        "wind_speed": 14.5,
        "soil_moisture_index": 42.0,
        "description": "Partly cloudy, no rain",
        "fetched_at": datetime.utcnow().isoformat(),
        "unit": "metric",
    }


# ── Multi-day forecast ──────────────────────────────────────────────────────────

async def get_weather_forecast(location: str, days: int = 7) -> dict:
    """Fetch a multi-day forecast with rainfall data for dry-spell analysis."""
    forecasts = []
    base_date = datetime.utcnow()

    # Simulate a dry spell pattern (realistic for advisory demo)
    rainfall_pattern = [0.0, 0.0, 2.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 15.5]

    for i in range(days):
        rain = rainfall_pattern[i] if i < len(rainfall_pattern) else 0.0
        forecasts.append({
            "date": (base_date + timedelta(days=i)).strftime("%Y-%m-%d"),
            "day": i + 1,
            "temperature_high": 34.0 - (i % 3),
            "temperature_low": 24.0 + (i % 2),
            "humidity": 55 + i * 3,
            "rainfall_mm": rain,
            "wind_speed": 12 + i,
            "description": "Rain likely" if rain > 1.0 else "Dry and warm",
        })

    return {
        "location": location,
        "days": days,
        "forecast": forecasts,
    }


# ── Dry-spell detection ────────────────────────────────────────────────────────

async def detect_dry_spell(
    location: str,
    consecutive_dry_days_threshold: int = 5,
    rainfall_threshold_mm: float = 2.5,
) -> dict:
    """
    Detect ongoing or upcoming dry spells based on forecast data.

    A dry spell is defined as `consecutive_dry_days_threshold` or more
    consecutive days with rainfall below `rainfall_threshold_mm`.

    Returns alert level: none / watch / warning / critical
    """
    forecast_data = await get_weather_forecast(location, days=10)
    daily = forecast_data["forecast"]

    # Count consecutive dry days
    current_streak = 0
    max_streak = 0
    streak_start = None
    max_streak_start = None

    for day in daily:
        if day["rainfall_mm"] < rainfall_threshold_mm:
            if current_streak == 0:
                streak_start = day["date"]
            current_streak += 1
            if current_streak > max_streak:
                max_streak = current_streak
                max_streak_start = streak_start
        else:
            current_streak = 0

    # Determine alert level
    if max_streak >= 7:
        level = "critical"
        message = (
            f"CRITICAL: {max_streak} consecutive dry days detected starting {max_streak_start}. "
            "Immediate protective irrigation required. Prioritize crops at flowering/fruiting stage. "
            "Apply mulch to conserve soil moisture."
        )
    elif max_streak >= consecutive_dry_days_threshold:
        level = "warning"
        message = (
            f"WARNING: {max_streak} consecutive dry days expected starting {max_streak_start}. "
            "Plan supplemental irrigation within 48 hours. "
            "Delay any fertilizer application until next rain."
        )
    elif max_streak >= 3:
        level = "watch"
        message = (
            f"WATCH: {max_streak} dry days expected starting {max_streak_start}. "
            "Monitor soil moisture levels. Keep irrigation equipment ready."
        )
    else:
        level = "none"
        message = "No dry spell expected in the forecast period. Normal irrigation schedule is fine."

    return {
        "location": location,
        "alert_level": level,
        "consecutive_dry_days": max_streak,
        "dry_spell_start": max_streak_start,
        "message": message,
        "threshold_used": {
            "min_dry_days": consecutive_dry_days_threshold,
            "rainfall_threshold_mm": rainfall_threshold_mm,
        },
        "analyzed_days": len(daily),
    }


# ── Irrigation guidance ────────────────────────────────────────────────────────

async def get_irrigation_guidance(
    location: str,
    crop_name: Optional[str] = None,
    soil_moisture: Optional[float] = None,
) -> dict:
    """
    Generate irrigation scheduling advice based on weather forecast,
    crop stage, and soil moisture data.
    """
    dry_spell = await detect_dry_spell(location)
    weather = await get_current_weather(location)

    # Determine urgency based on soil moisture
    if soil_moisture is not None:
        if soil_moisture < 20:
            moisture_status = "critically_low"
            moisture_advice = "Soil moisture is critically low. Irrigate immediately."
        elif soil_moisture < 35:
            moisture_status = "low"
            moisture_advice = "Soil moisture is low. Irrigate within 24 hours."
        elif soil_moisture < 60:
            moisture_status = "adequate"
            moisture_advice = "Soil moisture is adequate. Monitor daily."
        else:
            moisture_status = "high"
            moisture_advice = "Soil moisture is high. No irrigation needed. Ensure drainage."
    else:
        moisture_status = "unknown"
        moisture_advice = "No soil moisture data. Install sensors or check manually."

    # Combine weather + moisture + dry spell for guidance
    irrigate_now = (
        moisture_status in ("critically_low", "low")
        or dry_spell["alert_level"] in ("warning", "critical")
    )

    return {
        "location": location,
        "crop": crop_name or "general",
        "should_irrigate_now": irrigate_now,
        "soil_moisture": {
            "value": soil_moisture,
            "status": moisture_status,
            "advice": moisture_advice,
        },
        "dry_spell_alert": {
            "level": dry_spell["alert_level"],
            "message": dry_spell["message"],
        },
        "weather_summary": {
            "temperature": weather["temperature"],
            "humidity": weather["humidity"],
            "current_rainfall": weather["rainfall"],
        },
        "recommendations": _build_irrigation_recommendations(
            moisture_status, dry_spell["alert_level"], crop_name
        ),
    }


def _build_irrigation_recommendations(
    moisture_status: str, dry_spell_level: str, crop: Optional[str]
) -> list[str]:
    """Build actionable irrigation recommendations."""
    recs = []

    if moisture_status == "critically_low":
        recs.append("Apply 40-50mm irrigation immediately via flood or sprinkler.")
        recs.append("Apply organic mulch (straw/leaves) after irrigating to reduce evaporation.")
    elif moisture_status == "low":
        recs.append("Apply 25-30mm irrigation within 24 hours.")

    if dry_spell_level == "critical":
        recs.append("Dry spell active: switch to drip/sprinkler to conserve water.")
        recs.append("Postpone all fertilizer application until rainfall resumes.")
        recs.append("Consider applying anti-transpirant spray on high-value crops.")
    elif dry_spell_level == "warning":
        recs.append("Dry spell approaching: pre-irrigate fields in next 48 hours.")
        recs.append("Hold off on top-dressing fertilizers until next expected rain.")

    if moisture_status in ("adequate", "high"):
        recs.append("No irrigation needed currently. Check again tomorrow.")

    if not recs:
        recs.append("Continue normal irrigation schedule. Monitor soil moisture daily.")

    return recs


# ── Farming weather alert ──────────────────────────────────────────────────────

async def get_farming_weather_alert(location: str) -> Optional[dict]:
    """Check for weather alerts relevant to farming."""
    dry_spell = await detect_dry_spell(location)

    if dry_spell["alert_level"] in ("warning", "critical"):
        return {
            "location": location,
            "alert_type": f"Dry Spell - {dry_spell['alert_level'].upper()}",
            "severity": dry_spell["alert_level"],
            "message": dry_spell["message"],
            "valid_until": (datetime.utcnow() + timedelta(days=3)).isoformat(),
        }

    return None
