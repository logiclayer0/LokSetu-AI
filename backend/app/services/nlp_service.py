from groq import Groq
from app.core.config import settings


client = Groq(api_key=settings.GROQ_API_KEY)


SUPPORTED_LANGUAGES = {
    "hi": "Hindi",
    "en": "English",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "or": "Odia",
    "as": "Assamese",
    "ur": "Urdu"
}


def detect_language(text: str) -> str:
    system_prompt = (
        "Detect the language of the given text. "
        "Return ONLY the ISO 639-1 two-letter language code (e.g., hi, en, ta). "
        "No explanation, no punctuation, just the code."
    )
    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.0,
            max_tokens=10
        )
        return response.choices[0].message.content.strip().lower()
    except Exception:
        return "en"


def translate_to_english(text: str, source_lang: str) -> str:
    if source_lang == "en":
        return text
    system_prompt = (
        "Translate the given text to English. "
        "Return ONLY the translated text, no explanation, no quotes."
    )
    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.1,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return text


async def transcribe_audio(audio_bytes: bytes) -> str:
    try:
        transcription = client.audio.transcriptions.create(
            file=("audio.wav", audio_bytes),
            model="whisper-large-v3",
            response_format="text"
        )
        return transcription
    except Exception:
        return ""


def get_supported_languages() -> dict:
    return SUPPORTED_LANGUAGES