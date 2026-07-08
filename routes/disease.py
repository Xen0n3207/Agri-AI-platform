"""
Disease Routes – Endpoints for disease detection and lookup.
"""

import os
import uuid

from fastapi import APIRouter, Query, UploadFile, File
from typing import Optional
from services.disease_service import (
    search_diseases,
    get_disease_by_name,
    detect_disease_from_image,
)

router = APIRouter(prefix="/api/disease", tags=["Disease"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")


@router.get("/search")
async def search(
    crop: Optional[str] = Query(None, description="Filter by crop name"),
    keyword: Optional[str] = Query(None, description="Search keyword"),
):
    """
    Search the disease database by crop and/or keyword.
    """
    results = search_diseases(crop_name=crop, keyword=keyword)
    return {
        "status": "success",
        "count": len(results),
        "diseases": results,
    }


@router.get("/details/{disease_name}")
async def details(disease_name: str):
    """
    Get detailed info about a specific disease.
    """
    disease = get_disease_by_name(disease_name)
    if not disease:
        return {"status": "not_found", "message": f"Disease '{disease_name}' not found."}
    return {"status": "success", "disease": disease}


@router.post("/detect")
async def detect_from_image(
    file: UploadFile = File(..., description="Image of the affected plant"),
    crop: Optional[str] = Query(None, description="Crop name (optional hint)"),
):
    """
    Upload a plant image for AI-powered disease detection.

    Accepts JPEG/PNG images. Returns a diagnosis with treatment suggestions.
    """
    # Validate file type
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed_types:
        return {
            "status": "error",
            "message": f"Unsupported file type: {file.content_type}. Use JPEG, PNG, or WebP.",
        }

    # Save uploaded file
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = file.filename.split(".")[-1] if file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    contents = await file.read()
    with open(filepath, "wb") as f:
        f.write(contents)

    # Run detection
    result = await detect_disease_from_image(filepath)
    result["uploaded_file"] = filename

    return {"status": "success", "detection": result}
