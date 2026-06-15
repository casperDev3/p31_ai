"""Background workers, each communicating with the UI via Qt signals.

- CameraThread:   grabs webcam frames -> QImage
- AudioEngine:    one shared mic stream -> live waveform + VAD utterances
- AssistantWorker: utterance -> Groq STT -> process -> Groq LLM -> TTS
"""

import queue

import numpy as np
import sounddevice as sd
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

from voice_assistant.audio.recorder import write_wav
from voice_assistant.audio.vad import VADSegmenter
from voice_assistant.config import config
from voice_assistant.processor import commands, llm
from voice_assistant.stt import groq_stt
from voice_assistant.tts import groq_tts
from voice_assistant.audio import player
from voice_assistant.utils.logger import get_logger

log = get_logger(__name__)


class CameraThread(QThread):
    frame_ready = Signal(QImage)
    error = Signal(str)

    def __init__(self, index: int | None = None):
        super().__init__()
        self.index = config.camera_index if index is None else index
        self._run = True

    def run(self) -> None:
        import cv2

        cap = cv2.VideoCapture(self.index)
        if not cap.isOpened():
            self.error.emit("Не вдалося відкрити вебкамеру (перевір дозвіл у Системних налаштуваннях).")
            return
        try:
            while self._run:
                ok, frame = cap.read()
                if not ok:
                    self.msleep(30)
                    continue
                rgb = np.ascontiguousarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                h, w, ch = rgb.shape
                img = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888).copy()
                self.frame_ready.emit(img)
                self.msleep(30)
        finally:
            cap.release()

    def stop(self) -> None:
        self._run = False
        self.wait(1500)


class AudioEngine(QThread):
    """Always-on mic stream. Emits raw samples for the waveform, and complete
    utterances (when `listening` is True) for the assistant."""

    levels = Signal(object)      # np.int16 mono frame
    utterance = Signal(object)   # np.int16 utterance (N, channels)
    error = Signal(str)

    def __init__(self):
        super().__init__()
        self._run = True
        self.listening = False

    def run(self) -> None:
        seg = VADSegmenter.from_config()
        try:
            with sd.InputStream(
                samplerate=config.sample_rate,
                channels=config.channels,
                dtype="int16",
                blocksize=seg.frame_len,
            ) as stream:
                while self._run:
                    frame, _ = stream.read(seg.frame_len)
                    self.levels.emit(frame[:, 0].copy())
                    if self.listening:
                        utt = seg.feed(frame)
                        if utt is not None:
                            self.listening = False  # pause until the turn is done
                            self.utterance.emit(utt)
                    else:
                        seg.reset()  # don't accumulate while paused
        except Exception as exc:  # pragma: no cover - depends on audio stack
            self.error.emit(f"Помилка мікрофона: {exc}")

    def stop(self) -> None:
        self._run = False
        self.wait(1500)


class AssistantWorker(QThread):
    """Processes one task at a time from a queue: an utterance to handle, or
    a line to speak (e.g. the greeting)."""

    user_text = Signal(str)
    assistant_text = Signal(str)
    state = Signal(str)          # "thinking" | "speaking" | "idle"
    turn_finished = Signal()
    quit_requested = Signal()
    error = Signal(str)

    def __init__(self):
        super().__init__()
        self._run = True
        self._q: queue.Queue = queue.Queue()

    def submit(self, audio: np.ndarray) -> None:
        self._q.put(("audio", audio))

    def say(self, text: str) -> None:
        self._q.put(("say", text))

    def run(self) -> None:
        while self._run:
            try:
                kind, payload = self._q.get(timeout=0.2)
            except queue.Empty:
                continue
            try:
                if kind == "say":
                    self._speak(payload)
                elif kind == "audio":
                    self._handle_audio(payload)
            except Exception as exc:
                log.error("Помилка обробки: %s", exc)
                self.error.emit(str(exc))
            finally:
                self.state.emit("idle")
                self.turn_finished.emit()

    def _handle_audio(self, audio: np.ndarray) -> None:
        self.state.emit("thinking")
        write_wav(config.input_wav, audio)
        text = groq_stt.transcribe(config.input_wav)
        if not text:
            return
        self.user_text.emit(text)

        if commands.is_exit_command(text):
            self.assistant_text.emit("До побачення!")
            self._speak("До побачення!")
            self.quit_requested.emit()
            return

        answer = commands.handle(text) or llm.process(text)
        self.assistant_text.emit(answer)
        self._speak(answer)

    def _speak(self, text: str) -> None:
        self.state.emit("speaking")
        path = groq_tts.synthesize(text)
        if path:
            player.play(path)

    def stop(self) -> None:
        self._run = False
        self.wait(3000)
