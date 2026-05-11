"""
gui/components/search_card.py — Kartu hasil pencarian tanpa mini chart.
Tampilan: gambar produk di kiri, nama + harga + toko di kanan.
"""

from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import urllib.request
import os


class SearchCard(QFrame):
    """
    Kartu hasil pencarian — layout horizontal:
    [Gambar] | [Nama produk, Harga, Toko, Tanggal]
    Tidak ada chart, tidak ada tombol navigasi.
    """

    def __init__(self, nama: str, harga: float, toko: str, tanggal: str,
                 thumbnail_url: str = ""):
        super().__init__()
        self.nama          = nama
        self.harga         = harga
        self.toko          = toko
        self.tanggal       = tanggal
        self.thumbnail_url = thumbnail_url

        self.setFixedHeight(100)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            QFrame:hover {
                border: 1.5px solid #6B8E23;
                background-color: #fafff5;
            }
        """)
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 12, 0)
        layout.setSpacing(0)

        # ── Gambar produk di kiri ──────────────────────────────────────────
        self.lbl_gambar = QLabel()
        self.lbl_gambar.setFixedSize(90, 100)
        self.lbl_gambar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_gambar.setStyleSheet("""
            background-color: #f5f5f5;
            border: none;
            border-right: 1px solid #eee;
            border-top-left-radius: 7px;
            border-bottom-left-radius: 7px;
        """)

        # Coba load gambar dari URL kalau ada
        if self.thumbnail_url:
            self._load_gambar(self.thumbnail_url)
        else:
            self.lbl_gambar.setText("🛒")
            self.lbl_gambar.setStyleSheet(
                self.lbl_gambar.styleSheet() + "font-size: 28px;"
            )

        layout.addWidget(self.lbl_gambar)

        # ── Info produk di kanan ───────────────────────────────────────────
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(14, 10, 0, 10)
        info_layout.setSpacing(3)

        # Nama produk
        lbl_nama = QLabel(self.nama)
        lbl_nama.setWordWrap(True)
        lbl_nama.setStyleSheet(
            "font-size: 12px; font-weight: bold; color: #2c3e50; border: none;"
        )
        lbl_nama.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

        # Harga
        harga_fmt = f"Rp {self.harga:,.0f}".replace(",", ".")
        lbl_harga = QLabel(harga_fmt)
        lbl_harga.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #c0392b; border: none;"
        )

        # Toko
        lbl_toko = QLabel(f"📍 {self.toko}")
        lbl_toko.setStyleSheet(
            "font-size: 10px; color: #7f8c8d; border: none;"
        )

        info_layout.addWidget(lbl_nama)
        info_layout.addWidget(lbl_harga)
        info_layout.addWidget(lbl_toko)
        info_layout.addStretch()

        layout.addLayout(info_layout)

    def _load_gambar(self, url: str):
        """Load gambar dari URL — fallback ke emoji kalau gagal."""
        try:
            # Simpan sementara ke cache lokal
            cache_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "img_cache"
            )
            os.makedirs(cache_dir, exist_ok=True)

            # Nama file dari URL
            nama_file = url.split("/")[-1].split("?")[0] or "thumb.jpg"
            path_lokal = os.path.join(cache_dir, nama_file)

            # Download kalau belum ada
            if not os.path.exists(path_lokal):
                urllib.request.urlretrieve(url, path_lokal)

            pixmap = QPixmap(path_lokal)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    80, 80,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.lbl_gambar.setPixmap(pixmap)
                return
        except Exception:
            pass

        # Fallback emoji
        self.lbl_gambar.setText("🛒")
        self.lbl_gambar.setStyleSheet(
            self.lbl_gambar.styleSheet() + "font-size: 28px;"
        )