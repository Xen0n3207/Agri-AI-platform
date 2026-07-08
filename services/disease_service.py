"""
Disease Service – Plant disease detection and lookup.

In production, integrate a trained image classification model
(e.g., TensorFlow / PyTorch plant disease classifier) here.
"""

from typing import Optional


# ── Mock disease database ───────────────────────────────────────────────────────

DISEASE_DATABASE = [
    {
        "name": "Leaf Blight",
        "crop_name": "Rice",
        "symptoms": "Brown lesions on leaves, yellowing tips, wilting",
        "cause": "Fungal infection (Helminthosporium oryzae)",
        "treatment": "Apply Mancozeb fungicide at 2g/L. Remove infected leaves.",
        "prevention": "Use resistant varieties. Maintain field hygiene.",
    },
    {
        "name": "Powdery Mildew",
        "crop_name": "Wheat",
        "symptoms": "White powdery patches on leaves and stems",
        "cause": "Fungal infection (Erysiphe graminis)",
        "treatment": "Spray Sulfur-based fungicide. Ensure proper ventilation.",
        "prevention": "Avoid dense planting. Use certified seeds.",
    },
    {
        "name": "Bacterial Wilt",
        "crop_name": "Tomato",
        "symptoms": "Sudden wilting of entire plant, brown vascular tissue",
        "cause": "Bacterial infection (Ralstonia solanacearum)",
        "treatment": "No chemical cure. Remove and destroy infected plants.",
        "prevention": "Use disease-free transplants. Practice crop rotation.",
    },
    {
        "name": "Fall Armyworm",
        "crop_name": "Maize",
        "symptoms": "Ragged holes in leaves, frass in leaf whorls",
        "cause": "Pest (Spodoptera frugiperda)",
        "treatment": "Apply Emamectin Benzoate 5% SG at 0.4g/L.",
        "prevention": "Early planting, pheromone traps, intercropping with legumes.",
    },
    {
        "name": "Bollworm",
        "crop_name": "Cotton",
        "symptoms": "Bore holes in bolls, damaged lint, frass deposits",
        "cause": "Pest (Helicoverpa armigera)",
        "treatment": "Use Bt cotton varieties. Apply neem-based insecticide.",
        "prevention": "Trap cropping, refuge planting, regular scouting.",
    },
    {
        "name": "Tikka Disease",
        "crop_name": "Groundnut",
        "symptoms": "Circular brown spots on leaves with yellow halo",
        "cause": "Fungal infection (Cercospora arachidicola)",
        "treatment": "Spray Carbendazim at 1g/L at 30-day intervals.",
        "prevention": "Use resistant varieties. Remove crop debris after harvest.",
    },
]


def search_diseases(
    crop_name: Optional[str] = None,
    keyword: Optional[str] = None,
) -> list[dict]:
    """
    Search the disease database by crop name or keyword.
    """
    results = []
    for disease in DISEASE_DATABASE:
        match = True

        if crop_name:
            match = match and (disease["crop_name"].lower() == crop_name.lower())

        if keyword:
            text_blob = " ".join(disease.values()).lower()
            match = match and (keyword.lower() in text_blob)

        if match:
            results.append(disease)
    return results


def get_disease_by_name(name: str) -> Optional[dict]:
    """Return a single disease entry by its name."""
    for disease in DISEASE_DATABASE:
        if disease["name"].lower() == name.lower():
            return disease
    return None


async def detect_disease_from_image(image_path: str) -> dict:
    """
    Run disease detection on an uploaded image.

    In production, replace this with a real model inference call.
    """
    return {
        "detected": True,
        "disease_name": "Leaf Blight",
        "crop": "Rice",
        "confidence": 0.82,
        "symptoms": "Brown lesions on leaves, yellowing tips",
        "treatment": "Apply Mancozeb fungicide at 2g/L. Remove infected leaves.",
        "prevention": "Use resistant varieties. Maintain field hygiene.",
        "note": "This is an AI-generated result. Please consult a local agronomist.",
    }
