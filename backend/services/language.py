SUPPORTED_LANGUAGES = [
    "Tamil", "Telugu", "Kannada", "Malayalam",
    "Hindi", "Marathi", "Gujarati", "Bengali", "Odia", "English"
]

# Unicode script ranges for auto-detection
SCRIPT_MAP = {
    (0x0B80, 0x0BFF): "Tamil",
    (0x0C00, 0x0C7F): "Telugu",
    (0x0C80, 0x0CFF): "Kannada",
    (0x0D00, 0x0D7F): "Malayalam",
    (0x0900, 0x097F): "Hindi",     # Devanagari — also Marathi
    (0x0A80, 0x0AFF): "Gujarati",
    (0x0980, 0x09FF): "Bengali",
    (0x0B00, 0x0B7F): "Odia",
}

LANGUAGE_NUMBER_MAP = {
    "1": "Tamil", "2": "Telugu", "3": "Kannada",
    "4": "Malayalam", "5": "Hindi", "6": "Marathi",
    "7": "Gujarati", "8": "Bengali", "9": "Odia", "10": "English",
}

# Greeting messages per language
WELCOME_MESSAGES = {
    "Tamil": "வணக்கம்! DriveLegal-க்கு வருக! நான் உங்களுக்கு இந்திய போக்குவரத்து சட்டங்கள் மற்றும் அபராதங்கள் பற்றி உதவுவேன்.",
    "Telugu": "నమస్కారం! DriveLegal కి స్వాగతం! భారతీయ ట్రాఫిక్ చట్టాలు మరియు జరిమానాలు గురించి నేను మీకు సహాయం చేస్తాను.",
    "Kannada": "ನಮಸ್ಕಾರ! DriveLegal ಗೆ ಸ್ವಾಗತ! ಭಾರತೀಯ ಸಂಚಾರ ನಿಯಮಗಳು ಮತ್ತು ದಂಡಗಳ ಬಗ್ಗೆ ನಾನು ನಿಮಗೆ ಸಹಾಯ ಮಾಡುತ್ತೇನೆ.",
    "Malayalam": "നമസ്കാരം! DriveLegal-ലേക്ക് സ്വാഗതം! ഇന്ത്യൻ ഗതാഗത നിയമങ്ങളും പിഴകളും ഞാൻ നിങ്ങളെ സഹായിക്കും.",
    "Hindi": "नमस्ते! DriveLegal में आपका स्वागत है! मैं भारतीय यातायात कानूनों और जुर्माने के बारे में आपकी मदद करूंगा।",
    "Marathi": "नमस्कार! DriveLegal मध्ये आपले स्वागत आहे! भारतीय वाहतूक कायदे आणि दंड याबद्दल मी तुम्हाला मदत करेन.",
    "Gujarati": "નમસ્તે! DriveLegal માં આપનું સ્વાગત છે! ભારતીય ટ્રાફિક કાયદા અને દંડ વિશે હું તમને મદદ કરીશ.",
    "Bengali": "নমস্কার! DriveLegal-এ স্বাগতম! ভারতীয় ট্রাফিক আইন এবং জরিমানা সম্পর্কে আমি আপনাকে সাহায্য করব।",
    "Odia": "ନମସ୍କାର! DriveLegal ରେ ଆପଣଙ୍କୁ ସ୍ୱାଗତ! ଭାରତୀୟ ଯାନ ଚଳାଚଳ ନିୟମ ଏବଂ ଜୋରିମାନା ବିଷୟରେ ମୁଁ ଆପଣଙ୍କୁ ସାହାଯ୍ୟ କରିବି।",
    "English": "Hello! Welcome to DriveLegal. I'll help you with Indian traffic laws, fines, and challans.",
}

LOCATION_ASK_MESSAGES = {
    "Tamil": "நீங்கள் எந்த மாநிலத்தில் / நகரத்தில் இருக்கிறீர்கள்? (எ.கா. Chennai, Tamil Nadu)",
    "Telugu": "మీరు ఏ రాష్ట్రంలో / నగరంలో ఉన్నారు? (ఉదా. Hyderabad, Telangana)",
    "Kannada": "ನೀವು ಯಾವ ರಾಜ್ಯದಲ್ಲಿ / ನಗರದಲ್ಲಿ ಇದ್ದೀರಿ? (ಉದಾ. Bangalore, Karnataka)",
    "Malayalam": "നിങ്ങൾ ഏത് സംസ്ഥാനത്ത് / നഗരത്തിലാണ്? (ഉദാ. Kochi, Kerala)",
    "Hindi": "आप किस राज्य/शहर में हैं? (जैसे Delhi, Mumbai, Chennai)",
    "Marathi": "तुम्ही कोणत्या राज्यात/शहरात आहात? (उदा. Mumbai, Maharashtra)",
    "Gujarati": "તમે કયા રાજ્ય/શહેરમાં છો? (દા.ત. Ahmedabad, Gujarat)",
    "Bengali": "আপনি কোন রাজ্যে/শহরে আছেন? (যেমন Kolkata, West Bengal)",
    "Odia": "ଆପଣ କେଉଁ ରାଜ୍ୟ/ସହରରେ ଅଛନ୍ତି? (ଯେ.ଗ. Bhubaneswar, Odisha)",
    "English": "Which state or city are you in? (e.g. Delhi, Mumbai, Chennai)",
}


def detect_language_from_script(text: str) -> str | None:
    """
    Check if majority of characters fall in a known script range.
    Returns language name or None if ambiguous (Latin/mixed).
    """
    script_counts: dict[str, int] = {}

    for char in text:
        cp = ord(char)
        for (start, end), lang in SCRIPT_MAP.items():
            if start <= cp <= end:
                script_counts[lang] = script_counts.get(lang, 0) + 1

    if not script_counts:
        return None     # Latin or unknown — ask user

    # Need at least 3 characters to be sure
    total = sum(script_counts.values())
    if total < 3:
        return None

    return max(script_counts, key=script_counts.get)


def is_valid_language(lang: str) -> bool:
    return lang in SUPPORTED_LANGUAGES


def get_language_picker_message() -> str:
    return (
        "🇮🇳 Welcome to DriveLegal!\n\n"
        "Choose your language / भाषा चुनें:\n"
        "1. Tamil | 2. Telugu | 3. Kannada | 4. Malayalam\n"
        "5. Hindi | 6. Marathi | 7. Gujarati | 8. Bengali\n"
        "9. Odia  | 10. English\n\n"
        "Reply with the number (1–10)."
    )


def get_welcome_message(language: str) -> str:
    return WELCOME_MESSAGES.get(language, WELCOME_MESSAGES["English"])


def get_location_ask_message(language: str) -> str:
    return LOCATION_ASK_MESSAGES.get(language, LOCATION_ASK_MESSAGES["English"])
