"""
LLM Service – AI-powered agricultural advisory with Indic language support.

In production, replace mock responses with calls to Google Gemini / OpenAI GPT.
"""

from typing import Optional


# ── Indic language response templates ──────────────────────────────────────────

INDIC_TEMPLATES = {
    "te": {  # Telugu
        "greeting": "నమస్కారం! మీ వ్యవసాయ సహాయకుడు ఇక్కడ ఉన్నాను.",
        "crop_advice_prefix": "మీ ప్రశ్నకు సమాధానం:",
        "weather_alert": "వాతావరణ హెచ్చరిక:",
        "dry_spell": "పొడి వాతావరణ హెచ్చరిక: రాబోయే {days} రోజులు వర్షం లేకపోవచ్చు. మీ పంటలకు నీరు పెట్టండి.",
        "irrigate_now": "ఇప్పుడు నీరు పెట్టండి! నేల తేమ చాలా తక్కువగా ఉంది.",
        "disease_detected": "మీ పంటలో {disease} వ్యాధి కనుగొనబడింది. చికిత్స: {treatment}",
        "no_disease": "మీ పంట ఆరోగ్యంగా ఉంది. ఏ వ్యాధి కనుగొనబడలేదు.",
        "thank_you": "ధన్యవాదాలు! మరింత సహాయం కావాలంటే మమ్మల్ని సంప్రదించండి.",
    },
    "hi": {  # Hindi
        "greeting": "नमस्ते! आपका कृषि सहायक यहाँ है.",
        "crop_advice_prefix": "आपके सवाल का जवाब:",
        "weather_alert": "मौसम चेतावनी:",
        "dry_spell": "सूखे की चेतावनी: अगले {days} दिनों तक बारिश नहीं हो सकती. अपनी फसलों को पानी दें.",
        "irrigate_now": "अभी सिंचाई करें! मिट्टी की नमी बहुत कम है.",
        "disease_detected": "आपकी फसल में {disease} रोग पाया गया है. उपचार: {treatment}",
        "no_disease": "आपकी फसल स्वस्थ है. कोई रोग नहीं पाया गया.",
        "thank_you": "धन्यवाद! और सहायता के लिए हमसे संपर्क करें.",
    },
    "ta": {  # Tamil
        "greeting": "வணக்கம்! உங்கள் விவசாய உதவியாளர் இங்கே இருக்கிறார்.",
        "crop_advice_prefix": "உங்கள் கேள்விக்கான பதில்:",
        "weather_alert": "வானிலை எச்சரிக்கை:",
        "dry_spell": "வறட்சி எச்சரிக்கை: அடுத்த {days} நாட்களுக்கு மழை இல்லாமல் இருக்கலாம். பயிர்களுக்கு நீர் பாய்ச்சுங்கள்.",
        "irrigate_now": "இப்போதே நீர் பாய்ச்சுங்கள்! மண் ஈரப்பதம் மிகவும் குறைவாக உள்ளது.",
        "disease_detected": "உங்கள் பயிரில் {disease} நோய் கண்டறியப்பட்டது. சிகிச்சை: {treatment}",
        "no_disease": "உங்கள் பயிர் ஆரோக்கியமாக உள்ளது. நோய் எதுவும் கண்டறியப்படவில்லை.",
        "thank_you": "நன்றி! மேலும் உதவி தேவைப்பட்டால் தொடர்பு கொள்ளுங்கள்.",
    },
    "kn": {  # Kannada
        "greeting": "ನಮಸ್ಕಾರ! ನಿಮ್ಮ ಕೃಷಿ ಸಹಾಯಕ ಇಲ್ಲಿದ್ದಾನೆ.",
        "crop_advice_prefix": "ನಿಮ್ಮ ಪ್ರಶ್ನೆಗೆ ಉತ್ತರ:",
        "weather_alert": "ಹವಾಮಾನ ಎಚ್ಚರಿಕೆ:",
        "dry_spell": "ಬರ ಎಚ್ಚರಿಕೆ: ಮುಂದಿನ {days} ದಿನಗಳಲ್ಲಿ ಮಳೆ ಇಲ್ಲದಿರಬಹುದು. ಬೆಳೆಗಳಿಗೆ ನೀರು ಹಾಕಿ.",
        "irrigate_now": "ಈಗಲೇ ನೀರು ಹಾಕಿ! ಮಣ್ಣಿನ ತೇವಾಂಶ ತುಂಬಾ ಕಡಿಮೆಯಿದೆ.",
        "disease_detected": "ನಿಮ್ಮ ಬೆಳೆಯಲ್ಲಿ {disease} ರೋಗ ಪತ್ತೆಯಾಗಿದೆ. ಚಿಕಿತ್ಸೆ: {treatment}",
        "no_disease": "ನಿಮ್ಮ ಬೆಳೆ ಆರೋಗ್ಯವಾಗಿದೆ. ಯಾವುದೇ ರೋಗ ಕಂಡುಬಂದಿಲ್ಲ.",
        "thank_you": "ಧನ್ಯವಾದಗಳು! ಹೆಚ್ಚಿನ ಸಹಾಯಕ್ಕಾಗಿ ನಮ್ಮನ್ನು ಸಂಪರ್ಕಿಸಿ.",
    },
    "mr": {  # Marathi
        "greeting": "नमस्कार! तुमचा कृषी सहाय्यक येथे आहे.",
        "crop_advice_prefix": "तुमच्या प्रश्नाचे उत्तर:",
        "weather_alert": "हवामान इशारा:",
        "dry_spell": "दुष्काळ इशारा: पुढील {days} दिवस पाऊस नसू शकतो. पिकांना पाणी द्या.",
        "irrigate_now": "आत्ता पाणी द्या! जमिनीतील ओलावा खूप कमी आहे.",
        "disease_detected": "तुमच्या पिकात {disease} रोग आढळला. उपचार: {treatment}",
        "no_disease": "तुमचे पीक निरोगी आहे. कोणताही रोग आढळला नाही.",
        "thank_you": "धन्यवाद! अधिक मदतीसाठी आमच्याशी संपर्क साधा.",
    },
    "en": {  # English (default)
        "greeting": "Hello! Your agricultural assistant is here.",
        "crop_advice_prefix": "Here's the advice for your query:",
        "weather_alert": "Weather Alert:",
        "dry_spell": "Dry Spell Alert: No rain expected for the next {days} days. Irrigate your crops.",
        "irrigate_now": "Irrigate now! Soil moisture is critically low.",
        "disease_detected": "Disease detected in your crop: {disease}. Treatment: {treatment}",
        "no_disease": "Your crop looks healthy. No disease detected.",
        "thank_you": "Thank you! Contact us for more help.",
    },
}

SUPPORTED_LANGUAGES = {
    "en": "English",
    "te": "Telugu",
    "hi": "Hindi",
    "ta": "Tamil",
    "kn": "Kannada",
    "mr": "Marathi",
}


def get_template(language: str, key: str, **kwargs) -> str:
    """Get a localized template string, with placeholder substitution."""
    lang = language if language in INDIC_TEMPLATES else "en"
    template = INDIC_TEMPLATES[lang].get(key, INDIC_TEMPLATES["en"].get(key, ""))
    try:
        return template.format(**kwargs) if kwargs else template
    except KeyError:
        return template


# ── AI Advisory ────────────────────────────────────────────────────────────────

async def get_crop_advice(
    query: str,
    location: Optional[str] = None,
    language: str = "en",
) -> str:
    """
    Generate AI-powered crop advice based on a farmer's query.
    Responds in the farmer's preferred Indic language.
    """
    lang = language if language in INDIC_TEMPLATES else "en"
    templates = INDIC_TEMPLATES[lang]

    context = f" ({location})" if location else ""

    # In production, send `query` + `location` + `language` to a real LLM
    # and ask it to respond in the target language.
    advice_lines = [
        templates["greeting"],
        "",
        f"{templates['crop_advice_prefix']}",
        f'"{query}"{context}',
        "",
    ]

    # Add generic actionable advice (replace with LLM output in production)
    if lang == "en":
        advice_lines.extend([
            "Recommendations:",
            "1. Consider crop rotation to maintain soil fertility.",
            "2. Use organic compost to improve yield.",
            "3. Monitor weather for optimal planting windows.",
            "4. Ensure proper irrigation scheduling.",
            "",
            "For specific advice, share your soil test report (N, P, K, pH values).",
        ])
    elif lang == "te":
        advice_lines.extend([
            "సిఫారసులు:",
            "1. నేల సారాన్ని కాపాడటానికి పంట మార్పిడి చేయండి.",
            "2. దిగుబడి పెంచడానికి సేంద్రియ ఎరువులు వాడండి.",
            "3. నాట్లు వేయడానికి వాతావరణాన్ని గమనించండి.",
            "4. సరైన నీటిపారుదల షెడ్యూల్ పాటించండి.",
            "",
            "నిర్దిష్ట సలహా కోసం, మీ నేల పరీక్ష నివేదిక (N, P, K, pH) పంపండి.",
        ])
    elif lang == "hi":
        advice_lines.extend([
            "सिफारिशें:",
            "1. मिट्टी की उर्वरता बनाए रखने के लिए फसल चक्र अपनाएं.",
            "2. उपज बढ़ाने के लिए जैविक खाद का उपयोग करें.",
            "3. बुवाई के लिए मौसम की निगरानी करें.",
            "4. उचित सिंचाई शेड्यूल सुनिश्चित करें.",
            "",
            "विशिष्ट सलाह के लिए अपनी मृदा परीक्षण रिपोर्ट (N, P, K, pH) भेजें.",
        ])
    else:
        advice_lines.extend([
            "1. Practice crop rotation.",
            "2. Use organic compost.",
            "3. Monitor weather patterns.",
            "4. Schedule irrigation properly.",
        ])

    advice_lines.append("")
    advice_lines.append(templates["thank_you"])

    return "\n".join(advice_lines)


# ── Disease diagnosis ─────────────────────────────────────────────────────────

async def diagnose_disease(
    crop_name: str,
    symptoms: str,
    language: str = "en",
    image_path: Optional[str] = None,
) -> dict:
    """
    Use AI to diagnose a potential crop disease.
    Returns localized results.
    """
    templates = INDIC_TEMPLATES.get(language, INDIC_TEMPLATES["en"])

    return {
        "crop": crop_name,
        "diagnosis": "Leaf Blight (suspected)",
        "confidence": 0.82,
        "symptoms_matched": symptoms,
        "treatment": [
            "Apply copper-based fungicide.",
            "Remove and destroy infected leaves.",
            "Ensure adequate spacing between plants.",
        ],
        "prevention": [
            "Use disease-resistant seed varieties.",
            "Avoid overhead irrigation.",
            "Practice crop rotation.",
        ],
        "localized_message": templates["disease_detected"].format(
            disease="Leaf Blight", treatment="Apply copper-based fungicide"
        ),
        "language": language,
        "note": "AI-generated suggestion. Consult an agronomist for confirmation.",
    }


async def translate_response(text: str, target_language: str) -> str:
    """
    Translate response to target language.
    In production, use Google Translate API or LLM-based translation.
    """
    if target_language == "en":
        return text

    # In production, call translation API here
    return f"[{SUPPORTED_LANGUAGES.get(target_language, target_language)}]\n{text}"
