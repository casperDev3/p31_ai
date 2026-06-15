"""Microphone capture -> WAV file (16-bit PCM, mono, 16 kHz).

Default mode is energy-based VAD (see audio/vad.py): no fixed wait — it records
until a short trailing silence. Set VA_VAD=0 to fall back to fixed-duration.
"""

import wave

import numpy as np
import sounddevice as sd

from voice_assistant.audio.vad import VADSegmenter
from voice_assistant.config import config
from voice_assistant.utils.logger import get_logger

log = get_logger(__name__)


def write_wav(path: str, audio: np.ndarray) -> None:
    with wave.open(path, "wb") as wf:
        wf.setnchannels(config.channels)
        wf.setsampwidth(2)  # int16 -> 2 bytes
        wf.setframerate(config.sample_rate)
        wf.writeframes(audio.tobytes())


def listen(out_path: str | None = None) -> str | None:
    """Record one utterance. Returns the WAV path, or None if nothing was said."""
    out_path = out_path or config.input_wav
    if config.vad_enabled:
        return _listen_vad(out_path)
    return _listen_fixed(out_path)


def _listen_vad(out_path: str) -> str | None:
    seg = VADSegmenter.from_config()
    frame_dt = config.vad_frame_ms / 1000
    start_timeout_frames = int(config.vad_start_timeout / frame_dt)

    log.info("Слухаю (говоріть)...")
    waited = 0
    with sd.InputStream(
        samplerate=config.sample_rate,
        channels=config.channels,
        dtype="int16",
        blocksize=seg.frame_len,
    ) as stream:
        while True:
            frame = stream.read(seg.frame_len)[0]
            utt = seg.feed(frame)
            if utt is not None:
                write_wav(out_path, utt)
                return out_path
            if seg.is_speaking:
                waited = 0
            else:
                waited += 1
                if waited >= start_timeout_frames:
                    log.info("Мовлення не виявлено.")
                    return None


def _listen_fixed(out_path: str) -> str:
    seconds = config.record_seconds
    log.info("Слухаю %.1f с...", seconds)
    frames = sd.rec(
        int(seconds * config.sample_rate),
        samplerate=config.sample_rate,
        channels=config.channels,
        dtype="int16",
    )
    sd.wait()
    write_wav(out_path, frames)
    return out_path
