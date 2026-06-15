"""Text-to-speech. Primary: Groq PlayAI. Fallbacks: gTTS / pyttsx3.

Returns the path to a playable audio file (or None for pyttsx3, which
speaks directly). See config.tts_engine.
"""

from voice_assistant.config import config
from voice_assistant.utils.logger import get_logger

log = get_logger(__name__)


def synthesize(text: str, out_path: str | None = None) -> str | None:
    engine = config.tts_engine
    if engine == "groq":
        return _groq(text, out_path or config.output_wav)
    if engine == "gtts":
        return _gtts(text, (out_path or config.output_wav).replace(".wav", ".mp3"))
    if engine == "pyttsx3":
        return _pyttsx3(text)
    raise ValueError(f"Невідомий TTS engine: {engine}")


def _groq(text: str, out_path: str) -> str:
    client = get_client_lazy()
    audio = client.audio.speech.create(
        model=config.tts_model,
        voice=config.tts_voice,
        input=text,
        response_format="wav",
    )
    audio.write_to_file(out_path)
    return out_path


def get_client_lazy():
    from voice_assistant.groq_client import get_client

    return get_client()


def _gtts(text: str, out_path: str) -> str:
    from gtts import gTTS

    gTTS(text=text, lang=config.language).save(out_path)
    return out_path


def _pyttsx3(text: str) -> None:
    import pyttsx3

    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    return None
