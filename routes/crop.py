"""
Crop Routes – Smart crop recommendation with soil + satellite data.
"""

from fastapi import APIRouter, Query
from typing import Optional
from services.crop_service import recommend_crops, get_crop_details, get_all_crops

router = APIRouter(prefix="/api/crop", tags=["Crop"])


@router.get("/recommend")
async def recommend(
    season: Optional[str] = Query(None, description="Season: kharif, rabi, zaid"),
    soil_type: Optional[str] = Query(None, description="e.g. loamy, clay, sandy, red soil, black soil"),
    temperature: Optional[float] = Query(None, description="Current temperature in C"),
    humidity: Optional[float] = Query(None, description="Current humidity in %"),
    nitrogen: Optional[float] = Query(None, description="Soil nitrogen (N) in kg/ha"),
    phosphorus: Optional[float] = Query(None, description="Soil phosphorus (P) in kg/ha"),
    potassium: Optional[float] = Query(None, description="Soil potassium (K) in kg/ha"),
    ph: Optional[float] = Query(None, description="Soil pH value"),
    ndvi: Optional[float] = Query(None, description="Satellite NDVI index (0-1)"),
):
    """
    Get smart crop recommendations based on soil health card data,
    satellite vegetation index (NDVI), and weather conditions.

    The more parameters you provide, the more accurate the match.
    Each crop is scored out of 100 based on parameter matching.
    """
    results = recommend_crops(
        season=season,
        soil_type=soil_type,
        temperature=temperature,
        humidity=humidity,
        nitrogen=nitrogen,
        phosphorus=phosphorus,
        potassium=potassium,
        ph=ph,
        ndvi=ndvi,
    )

    if not results:
        return {
            "status": "no_match",
            "message": "No crops matched the given criteria. Try broadening your search.",
            "recommendations": [],
        }

    return {
        "status": "success",
        "count": len(results),
        "input_params": {
            "season": season,
            "soil_type": soil_type,
            "temperature": temperature,
            "humidity": humidity,
            "soil_data": {"N": nitrogen, "P": phosphorus, "K": potassium, "pH": ph},
            "satellite": {"NDVI": ndvi},
        },
        "recommendations": results,
    }


@router.get("/details/{crop_name}")
async def details(crop_name: str):
    """
    Get full details for a crop including irrigation advice
    and fertilizer schedule.
    """
    crop = get_crop_details(crop_name)
    if not crop:
        return {"status": "not_found", "message": f"Crop '{crop_name}' not found."}
    return {"status": "success", "crop": crop}


@router.get("/list")
async def list_crops():
    """List all supported crops."""
    return {"status": "success", "crops": get_all_crops()}


@router.get("/seasons")
async def list_seasons():
    """List all supported crop seasons."""
    return {
        "seasons": [
            {"name": "kharif", "months": "June - October", "description": "Monsoon crops"},
            {"name": "rabi", "months": "October - March", "description": "Winter crops"},
            {"name": "zaid", "months": "March - June", "description": "Summer crops"},
        ]
    }
