"""Speech-to-text via Groq Whisper."""

import os

from voice_assistant.config import config
from voice_assistant.groq_client import get_client
from voice_assistant.utils.logger import get_logger

log = get_logger(__name__)


def transcribe(path: str, language: str | None = None) -> str:
    language = language or config.language
    client = get_client()

    with open(path, "rb") as f:
        result = client.audio.transcriptions.create(
            file=(os.path.basename(path), f.read()),
            model=config.stt_model,
            language=language,
        )

    text = (result.text or "").strip()
    log.info("Розпізнано: %s", text or "<тиша>")
    return text
