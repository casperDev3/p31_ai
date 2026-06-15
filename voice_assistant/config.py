"""Central configuration. Reads secrets from .env, never hardcodes the key."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load voice_assistant/.env explicitly (independent of the current working
# directory), then fall back to any .env discovered upward from the cwd
# (e.g. a project-root .env). override=False keeps the first one found.
load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv()


@dataclass(frozen=True)
class Config:
    # --- Secrets ---
    groq_api_key: str = os.environ.get("GROQ_API_KEY", "")

    # --- Language ---
    language: str = os.environ.get("VA_LANGUAGE", "uk")  # uk | en

    # --- Audio capture ---
    sample_rate: int = 16_000          # Whisper expects 16 kHz
    channels: int = 1                  # mono
    record_seconds: float = 5.0        # fixed-duration fallback (VAD off)
    input_wav: str = "input.wav"
    output_wav: str = "answer.wav"

    # --- VAD (energy-based, no extra deps) ---
    vad_enabled: bool = os.environ.get("VA_VAD", "1") != "0"
    vad_frame_ms: int = 30             # analysis frame size
    vad_silence_tail: float = 0.8      # stop after this much trailing silence (s)
    vad_start_timeout: float = 8.0     # give up if no speech starts within (s)
    vad_max_seconds: float = 15.0      # hard cap on one utterance
    vad_threshold_factor: float = 3.0  # threshold = ambient_rms * factor ...
    vad_threshold_floor: float = 350.0 # ... but never below this (int16 RMS)

    # --- Groq models ---
    stt_model: str = os.environ.get("VA_STT_MODEL", "whisper-large-v3")
    llm_model: str = os.environ.get("VA_LLM_MODEL", "llama-3.3-70b-versatile")
    # Groq Orpheus TTS is English-only (canopylabs/orpheus-v1-english).
    # playai-tts was decommissioned 2025-12-31.
    tts_model: str = os.environ.get("VA_TTS_MODEL", "canopylabs/orpheus-v1-english")

    # --- TTS engine: gtts | groq | pyttsx3 ---
    # Default is gtts because the assistant speaks Ukrainian and Groq Orpheus
    # only supports English/Arabic. Set VA_TTS_ENGINE=groq for English output.
    tts_engine: str = os.environ.get("VA_TTS_ENGINE", "gtts")
    tts_voice: str = os.environ.get("VA_TTS_VOICE", "troy")  # used only by groq engine

    # --- LLM behaviour ---
    system_prompt: str = (
        "Ти голосовий асистент. Відповідай коротко, ясно й українською мовою. "
        "Уникай розмітки та емодзі, бо відповідь буде озвучена."
    )
    temperature: float = 0.6

    def validate(self) -> None:
        if not self.groq_api_key:
            raise RuntimeError(
                "GROQ_API_KEY не знайдено. Скопіюй .env.example у .env і встав ключ."
            )


config = Config()
