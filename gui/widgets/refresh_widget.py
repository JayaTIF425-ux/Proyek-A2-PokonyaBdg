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
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer


# ── Worker: jalankan scraper di background ────────────────────────────────

class ScraperWorker(QThread):
    """
    Jalankan run_all_scrapers.py sebagai subprocess agar tidak
    memblokir event loop Qt. Emit sinyal per baris output dan
    sinyal selesai ketika subprocess exit.
    """
    log_line  = pyqtSignal(str)   # satu baris output scraper
    selesai   = pyqtSignal(bool)  # True = sukses, False = error

    def __init__(self, target: str = "semua"):
        """
        target : 'semua' | 'pihps' | 'yogya' | 'borma'
        """
        super().__init__()
        self.target = target

    def run(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        script = os.path.join(base, "scripts", "run_all_scrapers.py")

        cmd = [sys.executable, script]
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


# ── Widget Utama ──────────────────────────────────────────────────────────

class RefreshWidget(QFrame):
    """
    Toolbar kecil yang bisa dipasang di bagian atas / bawah halaman mana pun.

    Sinyal:
      refresh_diminta  — user klik Refresh (reload DB, tanpa scraping)
      update_selesai   — scraper selesai berjalan (sukses atau gagal)
    """

    refresh_diminta = pyqtSignal()
    update_selesai  = pyqtSignal(bool)   # True = ok

    # Status
    STATUS_IDLE    = "idle"
    STATUS_SCRAPING = "scraping"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._status   = self.STATUS_IDLE
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

        # ── Timestamp update terakhir ──────────────────────────────────────
        self.lbl_waktu = QLabel("Terakhir diperbarui: –")
        self.lbl_waktu.setStyleSheet(
            "font-size: 11px; color: #888; border: none; background: transparent;"
        )
        layout.addWidget(self.lbl_waktu)
        layout.addStretch()

        # ── Progress bar (tersembunyi saat idle) ──────────────────────────
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)   # indeterminate
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

        # ── Label status scraper ──────────────────────────────────────────
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet(
            "font-size: 11px; color: #555; border: none; background: transparent;"
        )
        self.lbl_status.hide()
        layout.addWidget(self.lbl_status)

        # ── Tombol Refresh ─────────────────────────────────────────────────
        self.btn_refresh = QPushButton("🔄  Refresh")
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
            QPushButton:hover  { background-color: #e8e8e8; }
            QPushButton:pressed { background-color: #ddd; }
            QPushButton:disabled { color: #aaa; background: #f8f8f8; }
        """)
        self.btn_refresh.clicked.connect(self._klik_refresh)
        layout.addWidget(self.btn_refresh)

        # ── Tombol Update Data ─────────────────────────────────────────────
        self.btn_update = QPushButton("⬆  Update Data")
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
            QPushButton:hover   { background-color: #5a1522; }
            QPushButton:pressed  { background-color: #3a0e16; }
            QPushButton:disabled { background-color: #ccc; color: #888; }
        """)
        self.btn_update.clicked.connect(self._klik_update)
        layout.addWidget(self.btn_update)

    # ── Aksi ──────────────────────────────────────────────────────────────

    def _klik_refresh(self):
        """Reload tampilan dari DB yang sudah ada (tanpa scraping)."""
        self._update_timestamp()
        self.refresh_diminta.emit()

    def _klik_update(self):
        """Mulai proses scraping di background."""
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
        # Tampilkan baris terakhir yang tidak kosong
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

        # Auto-sembunyikan pesan status setelah 5 detik
        QTimer.singleShot(5000, lambda: (
            self.lbl_status.hide(),
            self.lbl_status.setStyleSheet(
                "font-size: 11px; color: #555; border: none; background: transparent;"
            )
        ))

        # Otomatis refresh tampilan setelah update sukses
        if sukses:
            self.refresh_diminta.emit()

        self.update_selesai.emit(sukses)

    # ── Helpers ───────────────────────────────────────────────────────────

    def _set_scraping(self, aktif: bool):
        self._status = self.STATUS_SCRAPING if aktif else self.STATUS_IDLE
        self.btn_refresh.setEnabled(not aktif)
        self.btn_update.setEnabled(not aktif)
        self.btn_update.setText("⏳  Mengambil data…" if aktif else "⬆  Update Data")

        if aktif:
            self.progress.show()
            self.lbl_status.show()
            self.lbl_status.setText("Menjalankan scraper…")
        else:
            self.progress.hide()
            # lbl_status disembunyikan oleh timer di _scraper_selesai

    def _update_timestamp(self):
        waktu = datetime.now().strftime("%d %b %Y, %H:%M")
        self.lbl_waktu.setText(f"Terakhir diperbarui: {waktu}")

    def log_lengkap(self) -> str:
        """Kembalikan seluruh output scraper (untuk debugging)."""
        return "\n".join(self._log_lines)
