"""
gui/widgets/refresh_widget.py — Widget tombol Refresh + Update Data.

Terdiri dari dua aksi:
  1. Refresh  : reload data dari database (cepat, tanpa scraping)
  2. Update   : jalankan semua scraper lalu reload (bisa makan waktu beberapa menit)

Dipakai di semua halaman sebagai toolbar bersama.
"""
import subprocess
import sys
import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel,
    QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QByteArray
from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer


def _svg_to_icon(svg_str: str, size: int = 18) -> QIcon:
    renderer = QSvgRenderer(QByteArray(svg_str.encode()))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)

_IKON_REFRESH = {
    "refresh": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 16h5v5"/></svg>""",
    "update": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a10 10 0 0 1 7.38 16.75"/><path d="m16 12-4-4-4 4"/><path d="M12 16V8"/><path d="M2.5 8.875a10 10 0 0 0-.5 3"/><path d="M2.83 16a10 10 0 0 0 2.43 3.4"/><path d="M4.636 5.235a10 10 0 0 1 .891-.857"/><path d="M8.644 21.42a10 10 0 0 0 7.631-.38"/></svg>""",
}


class ScraperWorker(QThread):
    log_line = pyqtSignal(str)
    selesai  = pyqtSignal(bool)

    def __init__(self, target: str = "semua"):
        super().__init__()
        self.target = target

    def run(self):
        base   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        script = os.path.join(base, "scripts", "run_all_scrapers.py")
        cmd    = [sys.executable, script]
        if self.target != "semua":
            cmd += ["--hanya", self.target]
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=base,
            )
            for line in proc.stdout:
                self.log_line.emit(line.rstrip())
            proc.wait()
            self.selesai.emit(proc.returncode == 0)
        except Exception as e:
            self.log_line.emit(f"ERROR: {e}")
            self.selesai.emit(False)


class RefreshWidget(QFrame):
    refresh_diminta = pyqtSignal()
    update_selesai  = pyqtSignal(bool)

    STATUS_IDLE     = "idle"
    STATUS_SCRAPING = "scraping"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._status    = self.STATUS_IDLE
        self._log_lines: list[str] = []
        self._init_ui()
        self._update_timestamp()

    def _init_ui(self):
        self.setStyleSheet("""
            QFrame {
                background: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        # ── Timestamp ────────────────────────────────────────────────────
        self.lbl_waktu = QLabel("Terakhir diperbarui: –")
        self.lbl_waktu.setStyleSheet(
            "font-size: 11px; color: #888; border: none; background: transparent;"
        )
        layout.addWidget(self.lbl_waktu)
        layout.addStretch()

        # ── Progress bar ──────────────────────────────────────────────────
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedWidth(160)
        self.progress.setFixedHeight(14)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 6px;
                background: #eee;
            }
            QProgressBar::chunk {
                background-color: #6B8E23;
                border-radius: 6px;
            }
        """)
        self.progress.hide()
        layout.addWidget(self.progress)

        # ── Label status ──────────────────────────────────────────────────
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet(
            "font-size: 11px; color: #555; border: none; background: transparent;"
        )
        self.lbl_status.hide()
        layout.addWidget(self.lbl_status)

        # ── Tombol Refresh ────────────────────────────────────────────────
        self.btn_refresh = QPushButton("  Refresh")
        self.btn_refresh.setFixedHeight(32)
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #f1f1f1;
                color: #333;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 0 14px;
                font-size: 13px;
            }
            QPushButton:hover   { background-color: #e8e8e8; }
            QPushButton:pressed { background-color: #ddd; }
            QPushButton:disabled { color: #aaa; background: #f8f8f8; }
        """)
        self.btn_refresh.setIcon(_svg_to_icon(_IKON_REFRESH["refresh"]))
        self.btn_refresh.clicked.connect(self._klik_refresh)
        layout.addWidget(self.btn_refresh)

        # ── Tombol Update Data ────────────────────────────────────────────
        self.btn_update = QPushButton("  Update Data")
        self.btn_update.setFixedHeight(32)
        self.btn_update.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_update.setToolTip(
            "Jalankan semua scraper (PIHPS + Yogya + Borma) dan perbarui database.\n"
            "Proses ini bisa memakan waktu 2–5 menit."
        )
        self.btn_update.setStyleSheet("""
            QPushButton {
                background-color: #44101A;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0 14px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover    { background-color: #5a1522; }
            QPushButton:pressed  { background-color: #3a0e16; }
            QPushButton:disabled { background-color: #ccc; color: #888; }
        """)
        self.btn_update.setIcon(_svg_to_icon(_IKON_REFRESH["update"]))
        self.btn_update.clicked.connect(self._klik_update)
        layout.addWidget(self.btn_update)

    def _klik_refresh(self):
        self._update_timestamp()
        self.refresh_diminta.emit()

    def _klik_update(self):
        if self._status == self.STATUS_SCRAPING:
            return
        self._set_scraping(True)
        self._log_lines.clear()
        self.worker = ScraperWorker(target="semua")
        self.worker.log_line.connect(self._terima_log)
        self.worker.selesai.connect(self._scraper_selesai)
        self.worker.start()

    def _terima_log(self, line: str):
        self._log_lines.append(line)
        if line.strip():
            singkat = line.strip()[:50] + ("…" if len(line.strip()) > 50 else "")
            self.lbl_status.setText(singkat)

    def _scraper_selesai(self, sukses: bool):
        self._set_scraping(False)
        self._update_timestamp()

        if sukses:
            self.lbl_status.setText("✓ Data berhasil diperbarui")
            self.lbl_status.setStyleSheet(
                "font-size: 11px; color: #27ae60; border: none; background: transparent;"
            )
        else:
            self.lbl_status.setText("✗ Ada kesalahan saat update")
            self.lbl_status.setStyleSheet(
                "font-size: 11px; color: #e74c3c; border: none; background: transparent;"
            )

        QTimer.singleShot(5000, lambda: (
            self.lbl_status.hide(),
            self.lbl_status.setStyleSheet(
                "font-size: 11px; color: #555; border: none; background: transparent;"
            )
        ))

        if sukses:
            self.refresh_diminta.emit()

        self.update_selesai.emit(sukses)

    def _set_scraping(self, aktif: bool):
        self._status = self.STATUS_SCRAPING if aktif else self.STATUS_IDLE
        self.btn_refresh.setEnabled(not aktif)
        self.btn_update.setEnabled(not aktif)
        self.btn_update.setText("⏳  Mengambil data…" if aktif else "  Update Data")

        if aktif:
            self.progress.show()
            self.lbl_status.show()
            self.lbl_status.setText("Menjalankan scraper…")
        else:
            self.progress.hide()

    def _update_timestamp(self):
        waktu = datetime.now().strftime("%d %b %Y, %H:%M")
        self.lbl_waktu.setText(f"Terakhir diperbarui: {waktu}")

    def log_lengkap(self) -> str:
        return "\n".join(self._log_lines)