"""
gui/widgets/loading_widget.py — Widget animasi loading sederhana.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QMovie


class LoadingWidget(QWidget):
    """Spinner teks sederhana, tanpa dependensi file gif eksternal."""

    FRAMES = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]

    def __init__(self, pesan: str = "Memuat..."):
        super().__init__()
        self._pesan  = pesan
        self._frame  = 0

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl = QLabel(f"{self.FRAMES[0]}  {pesan}")
        self.lbl.setStyleSheet("font-size: 16px; color: #6B8E23; padding: 40px;")
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(100)

    def _tick(self):
        self._frame = (self._frame + 1) % len(self.FRAMES)
        self.lbl.setText(f"{self.FRAMES[self._frame]}  {self._pesan}")

    def show(self):
        self._timer.start(100)
        super().show()

    def hide(self):
        self._timer.stop()
        super().hide()
