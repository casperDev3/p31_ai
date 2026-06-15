"""Microphone capture -> WAV file (16-bit PCM, mono, 16 kHz).

Default mode is energy-based VAD: it calibrates to ambient noise, waits for
speech to start, then records until a short trailing silence — so there's no
fixed wait. Set VA_VAD=0 to fall back to fixed-duration capture.
"""

import wave
from collections import deque

import numpy as np
import sounddevice as sd

from voice_assistant.config import config
from voice_assistant.utils.logger import get_logger

log = get_logger(__name__)


def listen(out_path: str | None = None) -> str | None:
    """Record one utterance. Returns the WAV path, or None if nothing was said."""
    out_path = out_path or config.input_wav
    if config.vad_enabled:
        return _listen_vad(out_path)
    return _listen_fixed(out_path)


def _rms(block: np.ndarray) -> float:
    x = block.astype(np.float64)
    return float(np.sqrt(np.mean(x * x))) if x.size else 0.0


def _write_wav(path: str, audio: np.ndarray) -> None:
    with wave.open(path, "wb") as wf:
        wf.setnchannels(config.channels)
        wf.setsampwidth(2)  # int16 -> 2 bytes
        wf.setframerate(config.sample_rate)
        wf.writeframes(audio.tobytes())


def _listen_vad(out_path: str) -> str | None:
    sr = config.sample_rate
    frame_len = int(sr * config.vad_frame_ms / 1000)
    frame_dt = config.vad_frame_ms / 1000
    tail_needed = max(1, int(config.vad_silence_tail / frame_dt))
    max_frames = int(config.vad_max_seconds / frame_dt)
    start_timeout_frames = int(config.vad_start_timeout / frame_dt)
    preroll = deque(maxlen=max(1, int(0.15 / frame_dt)))  # keep speech onset

    log.info("Слухаю (говоріть)...")
    collected: list[np.ndarray] = []
    started = False
    voiced_run = 0
    silence_run = 0
    waited = 0

    with sd.InputStream(
        samplerate=sr, channels=config.channels, dtype="int16", blocksize=frame_len
    ) as stream:
        # Calibrate to ambient noise (~0.3 s) to set a dynamic threshold.
        ambient = [_rms(stream.read(frame_len)[0]) for _ in range(int(0.3 / frame_dt))]
        baseline = sum(ambient) / len(ambient) if ambient else 0.0
        threshold = max(baseline * config.vad_threshold_factor, config.vad_threshold_floor)
        log.debug("VAD baseline=%.0f threshold=%.0f", baseline, threshold)

        while True:
            block = stream.read(frame_len)[0]
            level = _rms(block)

            if not started:
                preroll.append(block)
                if level > threshold:
                    voiced_run += 1
                    if voiced_run >= 2:  # need 2 voiced frames to avoid clicks
                        started = True
                        collected.extend(preroll)
                else:
                    voiced_run = 0
                    waited += 1
                    if waited >= start_timeout_frames:
                        log.info("Мовлення не виявлено.")
                        return None
            else:
                collected.append(block)
                if level <= threshold:
                    silence_run += 1
                    if silence_run >= tail_needed:
                        break
                else:
                    silence_run = 0
                if len(collected) >= max_frames:
                    log.info("Досягнуто ліміту запису (%.0f с).", config.vad_max_seconds)
                    break

    _write_wav(out_path, np.concatenate(collected, axis=0))
    return out_path


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
    _write_wav(out_path, frames)
    return out_path
