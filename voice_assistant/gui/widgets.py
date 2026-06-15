"""Custom widgets: live audio waveform rendered with QPainter."""

import numpy as np
from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QWidget


class WaveformWidget(QWidget):
    """Scrolling oscilloscope of the most recent microphone samples."""

    def __init__(self, buffer_len: int = 8000):
        super().__init__()
        self.setMinimumHeight(120)
        self._buf = np.zeros(buffer_len, dtype=np.float32)
        self._color = QColor("#22c55e")  # green by default (listening)

    def push(self, samples: np.ndarray) -> None:
        s = samples.astype(np.float32) / 32768.0
        n = len(s)
        if n >= len(self._buf):
            self._buf = s[-len(self._buf):].copy()
        else:
            self._buf = np.roll(self._buf, -n)
            self._buf[-n:] = s
        self.update()

    def set_color(self, hex_color: str) -> None:
        self._color = QColor(hex_color)
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 (Qt naming)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        mid = h / 2

        p.fillRect(self.rect(), QColor("#0b1020"))
        p.setPen(QPen(QColor("#1e2a44"), 1))
        p.drawLine(0, int(mid), w, int(mid))

        n = len(self._buf)
        if n == 0 or w <= 1:
            return
        poly = QPolygonF()
        for x in range(w):
            v = float(self._buf[int(x / w * n)])
            poly.append(QPointF(x, mid - v * mid * 0.9))
        pen = QPen(self._color)
        pen.setWidth(2)
        p.setPen(pen)
        p.drawPolyline(poly)
