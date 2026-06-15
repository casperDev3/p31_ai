"""Main window: webcam view + conversation transcript + live waveform.

Run:  python -m voice_assistant.gui
"""

import html
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from voice_assistant.config import config
from voice_assistant.gui.threads import AssistantWorker, AudioEngine, CameraThread
from voice_assistant.gui.widgets import WaveformWidget

# state -> (label, dot/waveform colour)
_STATES = {
    "idle": ("Очікування", "#64748b"),
    "listening": ("Слухаю…", "#22c55e"),
    "thinking": ("Думаю…", "#f59e0b"),
    "speaking": ("Говорю…", "#3b82f6"),
}


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.window_title)
        self.resize(1040, 620)
        self._running = False
        self._exiting = False
        self.camera: CameraThread | None = None
        self.audio: AudioEngine | None = None
        self.worker: AssistantWorker | None = None

        self._build_ui()
        self._apply_style()
        self.set_status("idle")

    # ---------- UI ----------
    def _build_ui(self) -> None:
        self.camera_view = QLabel("Камера вимкнена")
        self.camera_view.setObjectName("camera")
        self.camera_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_view.setMinimumSize(480, 360)

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setMinimumWidth(360)

        top = QHBoxLayout()
        top.addWidget(self.camera_view, 3)
        top.addWidget(self.chat, 2)

        self.status = QLabel()
        self.status.setObjectName("status")
        self.waveform = WaveformWidget()
        self.toggle_btn = QPushButton("▶  Старт")
        self.toggle_btn.clicked.connect(self.toggle)

        root = QVBoxLayout(self)
        root.addLayout(top, 1)
        root.addWidget(self.status)
        root.addWidget(self.waveform)
        root.addWidget(self.toggle_btn)

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            QWidget { background:#0f172a; color:#e2e8f0; font-size:14px; }
            QLabel#camera { background:#0b1020; border:1px solid #1e2a44; border-radius:8px; }
            QLabel#status { font-size:15px; font-weight:600; padding:4px 2px; }
            QTextEdit { background:#0b1020; border:1px solid #1e2a44; border-radius:8px; padding:6px; }
            QPushButton { background:#2563eb; border:none; border-radius:8px; padding:10px; font-weight:600; }
            QPushButton:hover { background:#1d4ed8; }
            """
        )

    # ---------- lifecycle ----------
    def toggle(self) -> None:
        self.stop() if self._running else self.start()

    def start(self) -> None:
        try:
            config.validate()
        except Exception as exc:
            QMessageBox.critical(self, "Помилка конфігурації", str(exc))
            return

        self._running = True
        self._exiting = False
        self.toggle_btn.setText("⏸  Стоп")
        self._system_message("Сесію запущено. Зачекайте на привітання…")

        self.camera = CameraThread()
        self.camera.frame_ready.connect(self._on_frame)
        self.camera.error.connect(self._on_error)
        self.camera.start()

        self.audio = AudioEngine()
        self.audio.levels.connect(self.waveform.push)
        self.audio.utterance.connect(self._on_utterance)
        self.audio.error.connect(self._on_error)
        self.audio.start()

        self.worker = AssistantWorker()
        self.worker.user_text.connect(lambda t: self._append("Ви", t, mine=True))
        self.worker.assistant_text.connect(lambda t: self._append("Асистент", t, mine=False))
        self.worker.state.connect(self.set_status)
        self.worker.turn_finished.connect(self._on_turn_finished)
        self.worker.quit_requested.connect(self._on_quit_requested)
        self.worker.error.connect(self._on_error)
        self.worker.start()

        self.worker.say("Вітаю! Чим можу допомогти?")

    def stop(self) -> None:
        self._running = False
        for thread in (self.audio, self.camera, self.worker):
            if thread is not None:
                thread.stop()
        self.audio = self.camera = self.worker = None
        self.camera_view.setText("Камера вимкнена")
        self.camera_view.setPixmap(QPixmap())
        self.toggle_btn.setText("▶  Старт")
        self.set_status("idle")

    # ---------- slots ----------
    def _on_frame(self, image: QImage) -> None:
        pix = QPixmap.fromImage(image).scaled(
            self.camera_view.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.camera_view.setPixmap(pix)

    def _on_utterance(self, _audio) -> None:
        if self.worker is not None:
            self.worker.submit(_audio)

    def _on_turn_finished(self) -> None:
        if not self._running or self._exiting:
            return
        if self.audio is not None:
            self.audio.listening = True
        self.set_status("listening")

    def _on_quit_requested(self) -> None:
        self._exiting = True
        self.stop()

    def _on_error(self, message: str) -> None:
        self._system_message(f"⚠️ {message}")

    def set_status(self, state: str) -> None:
        label, color = _STATES.get(state, _STATES["idle"])
        self.status.setText(f"● {label}")
        self.status.setStyleSheet(f"color:{color}; font-size:15px; font-weight:600; padding:4px 2px;")
        self.waveform.set_color(color)

    # ---------- chat ----------
    def _append(self, sender: str, text: str, mine: bool) -> None:
        color = "#1d4ed8" if mine else "#334155"
        align = "right" if mine else "left"
        safe = html.escape(text).replace("\n", "<br>")
        bubble = (
            f'<div style="text-align:{align}; margin:6px 0;">'
            f'<span style="background:{color}; color:#fff; padding:7px 11px;'
            f' border-radius:10px; display:inline-block; max-width:80%;">'
            f"<b>{sender}:</b> {safe}</span></div>"
        )
        self.chat.append(bubble)
        self.chat.verticalScrollBar().setValue(self.chat.verticalScrollBar().maximum())

    def _system_message(self, text: str) -> None:
        self.chat.append(f'<div style="text-align:center; color:#94a3b8; margin:6px 0;"><i>{html.escape(text)}</i></div>')

    # ---------- window ----------
    def closeEvent(self, event) -> None:  # noqa: N802 (Qt naming)
        self.stop()
        super().closeEvent(event)


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
