"""Play an audio file (WAV or MP3) through the default output device."""

import os
import platform
import shutil
import subprocess

from voice_assistant.utils.logger import get_logger

log = get_logger(__name__)


def play(path: str) -> None:
    if not path or not os.path.exists(path):
        log.warning("Немає файлу для відтворення: %s", path)
        return

    # macOS: afplay handles both WAV and MP3 reliably, no extra deps.
    if platform.system() == "Darwin" and shutil.which("afplay"):
        subprocess.run(["afplay", path], check=False)
        return

    if path.lower().endswith(".wav"):
        _play_wav(path)
    else:
        _play_mp3(path)


def _play_wav(path: str) -> None:
    try:
        import simpleaudio as sa

        sa.WaveObject.from_wave_file(path).play().wait_done()
    except Exception as exc:  # pragma: no cover - depends on local audio stack
        log.error("Не вдалося відтворити WAV %s: %s", path, exc)


def _play_mp3(path: str) -> None:
    """Fallback for mp3 (e.g. gTTS output) on non-macOS systems."""
    try:
        from playsound import playsound

        playsound(path)
    except Exception as exc:  # pragma: no cover - depends on local audio stack
        log.error("Не вдалося відтворити %s: %s", path, exc)
