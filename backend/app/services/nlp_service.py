from groq import Groq
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

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
                {"role": "user", "content": text[:500]}
            ],
            temperature=0.0,
            max_tokens=10
        )
        code = response.choices[0].message.content.strip().lower()
        # Clean any extra text
        code = code.split()[0] if code else "en"
        code = code.replace(".", "").replace(",", "")[:2]
        if code in SUPPORTED_LANGUAGES:
            return code
        return "en"
    except Exception as e:
        logger.error(f"detect_language failed: {e}")
        return "en"


def translate_to_english(text: str, source_lang: str) -> str:
    if source_lang == "en" or not text.strip():
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
        translated = response.choices[0].message.content.strip()
        return translated if translated else text
    except Exception as e:
        logger.error(f"translate_to_english failed: {e}")
        return text


async def transcribe_audio(audio_bytes: bytes) -> str:
    try:
        transcription = client.audio.transcriptions.create(
            file=("audio.wav", audio_bytes),
            model="whisper-large-v3",
            response_format="text"
        )
        return transcription if isinstance(transcription, str) else str(transcription)
    except Exception as e:
        logger.error(f"transcribe_audio failed: {e}")
        return ""


def get_supported_languages() -> dict:
    return SUPPORTED_LANGUAGES
