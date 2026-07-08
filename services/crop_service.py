"""
Crop Service – Smart crop recommendation engine.

Uses soil data (N, P, K, pH) + satellite indicators (NDVI) +
climate conditions for intelligent crop matching.
"""

from typing import Optional


# ── Crop knowledge base with soil + climate requirements ───────────────────────

CROP_DATABASE = [
    {
        "name": "Rice",
        "season": "kharif",
        "soil_type": "clay, loamy",
        "water_requirement": "high",
        "temperature_min": 20.0,
        "temperature_max": 37.0,
        "humidity_min": 60.0,
        "humidity_max": 90.0,
        "nitrogen_min": 80,
        "nitrogen_max": 150,
        "phosphorus_min": 20,
        "phosphorus_max": 60,
        "potassium_min": 30,
        "potassium_max": 80,
        "ph_min": 5.5,
        "ph_max": 7.0,
        "ndvi_min": 0.3,
        "description": "Staple cereal crop; thrives in warm, humid conditions with standing water.",
        "irrigation_advice": "Maintain 5cm standing water during tillering. Drain 10 days before harvest.",
        "fertilizer_schedule": "Basal: DAP 100kg/ha. Top dress: Urea 50kg/ha at tillering and panicle initiation.",
    },
    {
        "name": "Wheat",
        "season": "rabi",
        "soil_type": "loamy, clay loam",
        "water_requirement": "medium",
        "temperature_min": 10.0,
        "temperature_max": 25.0,
        "humidity_min": 40.0,
        "humidity_max": 70.0,
        "nitrogen_min": 60,
        "nitrogen_max": 120,
        "phosphorus_min": 25,
        "phosphorus_max": 50,
        "potassium_min": 20,
        "potassium_max": 60,
        "ph_min": 6.0,
        "ph_max": 7.5,
        "ndvi_min": 0.25,
        "description": "Cool-season cereal; requires well-drained fertile soil.",
        "irrigation_advice": "Critical irrigations at CRI, tillering, flowering, and grain filling stages.",
        "fertilizer_schedule": "Basal: NPK 120:60:40 kg/ha. Top dress: Urea 60kg/ha at first irrigation.",
    },
    {
        "name": "Maize",
        "season": "kharif",
        "soil_type": "sandy loam, loamy",
        "water_requirement": "medium",
        "temperature_min": 18.0,
        "temperature_max": 35.0,
        "humidity_min": 50.0,
        "humidity_max": 80.0,
        "nitrogen_min": 80,
        "nitrogen_max": 140,
        "phosphorus_min": 30,
        "phosphorus_max": 60,
        "potassium_min": 25,
        "potassium_max": 50,
        "ph_min": 5.5,
        "ph_max": 7.5,
        "ndvi_min": 0.25,
        "description": "Versatile grain crop with moderate water needs.",
        "irrigation_advice": "Critical water need at tasseling and silking stages. Avoid waterlogging.",
        "fertilizer_schedule": "Basal: DAP 150kg/ha + MOP 60kg/ha. Top dress: Urea in 2 splits at knee-high and tasseling.",
    },
    {
        "name": "Cotton",
        "season": "kharif",
        "soil_type": "black soil, loamy",
        "water_requirement": "medium",
        "temperature_min": 21.0,
        "temperature_max": 35.0,
        "humidity_min": 40.0,
        "humidity_max": 70.0,
        "nitrogen_min": 60,
        "nitrogen_max": 120,
        "phosphorus_min": 20,
        "phosphorus_max": 50,
        "potassium_min": 20,
        "potassium_max": 50,
        "ph_min": 6.0,
        "ph_max": 8.0,
        "ndvi_min": 0.2,
        "description": "Cash crop that prefers warm weather and deep soils.",
        "irrigation_advice": "Drip irrigation recommended. Critical at flowering and boll formation.",
        "fertilizer_schedule": "Basal: NPK 60:30:30 kg/ha. Foliar spray of 2% DAP at flowering.",
    },
    {
        "name": "Mustard",
        "season": "rabi",
        "soil_type": "loamy, sandy loam",
        "water_requirement": "low",
        "temperature_min": 10.0,
        "temperature_max": 25.0,
        "humidity_min": 30.0,
        "humidity_max": 60.0,
        "nitrogen_min": 40,
        "nitrogen_max": 80,
        "phosphorus_min": 15,
        "phosphorus_max": 40,
        "potassium_min": 10,
        "potassium_max": 30,
        "ph_min": 6.0,
        "ph_max": 7.5,
        "ndvi_min": 0.2,
        "description": "Oilseed crop suited for dry, cool climates.",
        "irrigation_advice": "1-2 irrigations sufficient. First at flowering stage.",
        "fertilizer_schedule": "Basal: NPK 60:30:20 kg/ha. Sulphur 20kg/ha improves oil content.",
    },
    {
        "name": "Sugarcane",
        "season": "kharif",
        "soil_type": "loamy, clay loam",
        "water_requirement": "high",
        "temperature_min": 20.0,
        "temperature_max": 40.0,
        "humidity_min": 60.0,
        "humidity_max": 90.0,
        "nitrogen_min": 100,
        "nitrogen_max": 200,
        "phosphorus_min": 30,
        "phosphorus_max": 80,
        "potassium_min": 40,
        "potassium_max": 100,
        "ph_min": 5.5,
        "ph_max": 7.5,
        "ndvi_min": 0.35,
        "description": "Tropical perennial; needs abundant water and sunshine.",
        "irrigation_advice": "Furrow or drip irrigation every 7-10 days. Withhold water 3 weeks before harvest.",
        "fertilizer_schedule": "NPK 250:100:120 kg/ha in splits. Micronutrients: Zinc sulphate 25kg/ha.",
    },
    {
        "name": "Tomato",
        "season": "rabi",
        "soil_type": "sandy loam, loamy",
        "water_requirement": "medium",
        "temperature_min": 15.0,
        "temperature_max": 30.0,
        "humidity_min": 40.0,
        "humidity_max": 70.0,
        "nitrogen_min": 80,
        "nitrogen_max": 120,
        "phosphorus_min": 40,
        "phosphorus_max": 80,
        "potassium_min": 50,
        "potassium_max": 100,
        "ph_min": 6.0,
        "ph_max": 7.0,
        "ndvi_min": 0.25,
        "description": "Popular vegetable crop with moderate climate needs.",
        "irrigation_advice": "Drip irrigation preferred. Consistent moisture critical during fruiting.",
        "fertilizer_schedule": "Basal: FYM 25t/ha + NPK 120:60:80 kg/ha. Calcium spray to prevent blossom end rot.",
    },
    {
        "name": "Groundnut",
        "season": "kharif",
        "soil_type": "sandy loam, red soil",
        "water_requirement": "low",
        "temperature_min": 20.0,
        "temperature_max": 35.0,
        "humidity_min": 40.0,
        "humidity_max": 65.0,
        "nitrogen_min": 10,
        "nitrogen_max": 30,
        "phosphorus_min": 30,
        "phosphorus_max": 60,
        "potassium_min": 20,
        "potassium_max": 50,
        "ph_min": 6.0,
        "ph_max": 7.0,
        "ndvi_min": 0.2,
        "description": "Legume oilseed crop; fixes nitrogen in the soil.",
        "irrigation_advice": "Light irrigation at pegging and pod development. Avoid waterlogging.",
        "fertilizer_schedule": "Basal: NPK 20:40:40 kg/ha + Gypsum 500kg/ha at pegging. Low N since it fixes nitrogen.",
    },
    {
        "name": "Red Gram (Tur)",
        "season": "kharif",
        "soil_type": "red soil, black soil, loamy",
        "water_requirement": "low",
        "temperature_min": 18.0,
        "temperature_max": 35.0,
        "humidity_min": 35.0,
        "humidity_max": 65.0,
        "nitrogen_min": 10,
        "nitrogen_max": 25,
        "phosphorus_min": 30,
        "phosphorus_max": 60,
        "potassium_min": 15,
        "potassium_max": 40,
        "ph_min": 6.0,
        "ph_max": 7.5,
        "ndvi_min": 0.2,
        "description": "Major pulse crop of Telangana/AP. Drought tolerant, fixes nitrogen.",
        "irrigation_advice": "Mostly rainfed. One protective irrigation at flowering if dry spell occurs.",
        "fertilizer_schedule": "Basal: DAP 100kg/ha. Rhizobium seed treatment. Low nitrogen as legume.",
    },
    {
        "name": "Chilli",
        "season": "kharif",
        "soil_type": "loamy, black soil, red soil",
        "water_requirement": "medium",
        "temperature_min": 20.0,
        "temperature_max": 35.0,
        "humidity_min": 50.0,
        "humidity_max": 75.0,
        "nitrogen_min": 80,
        "nitrogen_max": 120,
        "phosphorus_min": 30,
        "phosphorus_max": 60,
        "potassium_min": 40,
        "potassium_max": 80,
        "ph_min": 6.0,
        "ph_max": 7.0,
        "ndvi_min": 0.25,
        "description": "Important spice crop of Guntur/Telangana region. High market value.",
        "irrigation_advice": "Drip irrigation every 3-4 days. Mulching reduces water need by 30%.",
        "fertilizer_schedule": "NPK 120:60:60 kg/ha in splits. Foliar micronutrients at flowering.",
    },
]


def recommend_crops(
    season: Optional[str] = None,
    soil_type: Optional[str] = None,
    temperature: Optional[float] = None,
    humidity: Optional[float] = None,
    nitrogen: Optional[float] = None,
    phosphorus: Optional[float] = None,
    potassium: Optional[float] = None,
    ph: Optional[float] = None,
    ndvi: Optional[float] = None,
) -> list[dict]:
    """
    Recommend crops based on soil data, satellite indicators, and climate.

    Scoring weights:
        Season:      20 pts
        Soil type:   15 pts
        Temperature: 15 pts
        Humidity:    10 pts
        Nitrogen:    10 pts
        Phosphorus:   8 pts
        Potassium:    7 pts
        pH:          10 pts
        NDVI:         5 pts
        ─────────────────
        Total:      100 pts
    """
    results = []

    for crop in CROP_DATABASE:
        score = 0
        matched = []
        total_possible = 0

        # Season match (20 pts)
        if season:
            total_possible += 20
            if crop["season"].lower() == season.lower():
                score += 20
                matched.append("season")

        # Soil type match (15 pts)
        if soil_type:
            total_possible += 15
            if soil_type.lower() in crop["soil_type"].lower():
                score += 15
                matched.append("soil_type")

        # Temperature range (15 pts)
        if temperature is not None:
            total_possible += 15
            if crop["temperature_min"] <= temperature <= crop["temperature_max"]:
                score += 15
                matched.append("temperature")

        # Humidity range (10 pts)
        if humidity is not None:
            total_possible += 10
            if crop["humidity_min"] <= humidity <= crop["humidity_max"]:
                score += 10
                matched.append("humidity")

        # Nitrogen (10 pts)
        if nitrogen is not None:
            total_possible += 10
            if crop["nitrogen_min"] <= nitrogen <= crop["nitrogen_max"]:
                score += 10
                matched.append("nitrogen")

        # Phosphorus (8 pts)
        if phosphorus is not None:
            total_possible += 8
            if crop["phosphorus_min"] <= phosphorus <= crop["phosphorus_max"]:
                score += 8
                matched.append("phosphorus")

        # Potassium (7 pts)
        if potassium is not None:
            total_possible += 7
            if crop["potassium_min"] <= potassium <= crop["potassium_max"]:
                score += 7
                matched.append("potassium")

        # pH (10 pts)
        if ph is not None:
            total_possible += 10
            if crop["ph_min"] <= ph <= crop["ph_max"]:
                score += 10
                matched.append("ph")

        # NDVI — satellite vegetation index (5 pts)
        if ndvi is not None:
            total_possible += 5
            if ndvi >= crop["ndvi_min"]:
                score += 5
                matched.append("ndvi")

        if score > 0:
            match_pct = round((score / total_possible) * 100) if total_possible > 0 else 0
            results.append({
                "name": crop["name"],
                "season": crop["season"],
                "soil_type": crop["soil_type"],
                "water_requirement": crop["water_requirement"],
                "description": crop["description"],
                "irrigation_advice": crop["irrigation_advice"],
                "fertilizer_schedule": crop["fertilizer_schedule"],
                "match_score": score,
                "match_percentage": match_pct,
                "matched_params": matched,
            })

    results.sort(key=lambda c: c["match_score"], reverse=True)
    return results


def get_crop_details(crop_name: str) -> Optional[dict]:
    """Return full details for a specific crop by name."""
    for crop in CROP_DATABASE:
        if crop["name"].lower() == crop_name.lower():
            return crop
    return None


def get_all_crops() -> list[str]:
    """Return all crop names."""
    return [c["name"] for c in CROP_DATABASE]
