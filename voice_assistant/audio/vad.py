"""Reusable energy-based voice activity detection (VAD).

Stateful segmenter: feed it fixed-size int16 frames one at a time; it returns
a completed utterance (np.int16, shape (N, channels)) when speech ends, else
None. The noise floor adapts continuously, so it works as an always-on stream
processor (GUI) as well as a one-shot recorder (CLI).
"""

from collections import deque

import numpy as np

from voice_assistant.config import config


def rms(frame: np.ndarray) -> float:
    x = frame.astype(np.float64)
    return float(np.sqrt(np.mean(x * x))) if x.size else 0.0


class VADSegmenter:
    def __init__(
        self,
        sample_rate: int,
        frame_ms: int,
        silence_tail: float,
        max_seconds: float,
        threshold_factor: float,
        threshold_floor: float,
        preroll_s: float = 0.15,
    ):
        self.sample_rate = sample_rate
        self.frame_len = int(sample_rate * frame_ms / 1000)
        dt = frame_ms / 1000
        self.tail_frames = max(1, int(silence_tail / dt))
        self.max_frames = int(max_seconds / dt)
        self.factor = threshold_factor
        self.floor = threshold_floor
        self.preroll: deque = deque(maxlen=max(1, int(preroll_s / dt)))
        self.reset(full=True)

    @classmethod
    def from_config(cls) -> "VADSegmenter":
        return cls(
            config.sample_rate,
            config.vad_frame_ms,
            config.vad_silence_tail,
            config.vad_max_seconds,
            config.vad_threshold_factor,
            config.vad_threshold_floor,
        )

    def reset(self, full: bool = False) -> None:
        self.collecting = False
        self.buf: list[np.ndarray] = []
        self.voiced_run = 0
        self.silence_run = 0
        self.preroll.clear()
        if full:
            self.noise_floor = self.floor / max(self.factor, 1e-6)

    @property
    def is_speaking(self) -> bool:
        return self.collecting

    @property
    def threshold(self) -> float:
        return max(self.noise_floor * self.factor, self.floor)

    def feed(self, frame: np.ndarray) -> np.ndarray | None:
        level = rms(frame)
        if not self.collecting:
            # Adapt the noise floor only while no speech is in progress.
            self.noise_floor = 0.95 * self.noise_floor + 0.05 * level

        threshold = self.threshold
        if not self.collecting:
            self.preroll.append(frame)
            if level > threshold:
                self.voiced_run += 1
                if self.voiced_run >= 2:  # need 2 voiced frames to avoid clicks
                    self.collecting = True
                    self.buf = list(self.preroll)
                    self.silence_run = 0
            else:
                self.voiced_run = 0
            return None

        self.buf.append(frame)
        if level <= threshold:
            self.silence_run += 1
            if self.silence_run >= self.tail_frames:
                return self._finish()
        else:
            self.silence_run = 0
        if len(self.buf) >= self.max_frames:
            return self._finish()
        return None

    def _finish(self) -> np.ndarray:
        audio = np.concatenate(self.buf, axis=0)
        self.reset()  # keep the adapted noise_floor
        return audio
