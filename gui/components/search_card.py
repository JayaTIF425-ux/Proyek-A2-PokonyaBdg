"""
gui/components/search_card.py — Kartu hasil pencarian dengan tombol CRUD.
"""

from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
import urllib.request
import os


class SearchCard(QFrame):
    edit_diminta  = pyqtSignal(object)
    hapus_diminta = pyqtSignal(int)

    def __init__(self, nama: str, harga: float, toko: str, tanggal: str,
                 thumbnail_url: str = "", id_produk: int = -1,
                 sumber: str = "supermarket", kategori: str = "", satuan: str = "kg"):
        super().__init__()
        self.nama          = nama
        self.harga         = harga
        self.toko          = toko
        self.tanggal       = tanggal
        self.thumbnail_url = thumbnail_url
        self.id_produk     = id_produk
        self.sumber        = sumber
        self.kategori      = kategori
        self.satuan        = satuan

        self.setFixedHeight(110)
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
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(0)

        # Gambar kiri
        self.lbl_gambar = QLabel()
        self.lbl_gambar.setFixedSize(90, 110)
        self.lbl_gambar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_gambar.setStyleSheet("""
            background-color: #f5f5f5;
            border: none;
            border-right: 1px solid #eee;
            border-top-left-radius: 7px;
            border-bottom-left-radius: 7px;
        """)

        if self.thumbnail_url:
            self._load_gambar(self.thumbnail_url)
        else:
            emoji = "🌾" if self.sumber == "pihps" else "🛒"
            self.lbl_gambar.setText(emoji)
            self.lbl_gambar.setStyleSheet(self.lbl_gambar.styleSheet() + "font-size: 28px;")

        layout.addWidget(self.lbl_gambar)

        # Info tengah
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(14, 10, 0, 10)
        info_layout.setSpacing(3)

        badge_warna = "#27AE60" if self.sumber == "pihps" else "#2980b9"
        badge_teks  = "PIHPS Nasional" if self.sumber == "pihps" else "Supermarket"
        lbl_badge = QLabel(badge_teks)
        lbl_badge.setFixedWidth(90)
        lbl_badge.setStyleSheet(
            f"font-size: 9px; font-weight: bold; color: white; "
            f"background-color: {badge_warna}; border-radius: 3px; "
            f"padding: 1px 5px; border: none;"
        )

        lbl_nama = QLabel(self.nama)
        lbl_nama.setWordWrap(True)
        lbl_nama.setStyleSheet("font-size: 12px; font-weight: bold; color: #2c3e50; border: none;")
        lbl_nama.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        harga_fmt = f"Rp {self.harga:,.0f}".replace(",", ".")
        lbl_harga = QLabel(harga_fmt)
        lbl_harga.setStyleSheet("font-size: 16px; font-weight: bold; color: #c0392b; border: none;")

        lbl_toko = QLabel(f"📍 {self.toko}  ·  🗓 {self.tanggal or '-'}")
        lbl_toko.setStyleSheet("font-size: 10px; color: #7f8c8d; border: none;")

        info_layout.addWidget(lbl_badge)
        info_layout.addWidget(lbl_nama)
        info_layout.addWidget(lbl_harga)
        info_layout.addWidget(lbl_toko)
        info_layout.addStretch()
        layout.addLayout(info_layout, 1)

        # Tombol kanan
        btn_layout = QVBoxLayout()
        btn_layout.setContentsMargins(8, 12, 4, 12)
        btn_layout.setSpacing(6)

        self.btn_edit = QPushButton("✏️ Edit")
        self.btn_edit.setFixedSize(72, 32)
        self.btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit.setStyleSheet("""
            QPushButton { background-color: #f39c12; color: white; border-radius: 5px;
                          font-size: 11px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #e67e22; }
            QPushButton:pressed { background-color: #d35400; }
        """)

        self.btn_hapus = QPushButton("🗑 Hapus")
        self.btn_hapus.setFixedSize(72, 32)
        self.btn_hapus.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_hapus.setStyleSheet("""
            QPushButton { background-color: #e74c3c; color: white; border-radius: 5px;
                          font-size: 11px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #c0392b; }
            QPushButton:pressed { background-color: #962d22; }
        """)

        if self.sumber == "pihps":
            self.btn_edit.setEnabled(False)
            self.btn_hapus.setEnabled(False)
            for btn in [self.btn_edit, self.btn_hapus]:
                btn.setStyleSheet("QPushButton { background-color: #bdc3c7; color: #fff; border-radius: 5px; font-size: 11px; border: none; }")
            self.btn_edit.setToolTip("Data PIHPS dikelola scraper otomatis")
            self.btn_hapus.setToolTip("Data PIHPS dikelola scraper otomatis")

        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_hapus)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.btn_edit.clicked.connect(lambda: self.edit_diminta.emit(self._as_row()))
        self.btn_hapus.clicked.connect(lambda: self.hapus_diminta.emit(self.id_produk))

    def _as_row(self):
        return {
            "id": self.id_produk,
            "nama": self.nama,
            "harga": self.harga,
            "toko": self.toko,
            "tanggal": self.tanggal,
            "kategori": self.kategori,
            "satuan": self.satuan,
        }

    def _load_gambar(self, url: str):
        try:
            cache_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "img_cache"
            )
            os.makedirs(cache_dir, exist_ok=True)
            import hashlib
            nama_file = hashlib.md5(url.encode()).hexdigest() + ".jpg"
            path_lokal = os.path.join(cache_dir, nama_file)
            if not os.path.exists(path_lokal):
                urllib.request.urlretrieve(url, path_lokal)
            pixmap = QPixmap(path_lokal)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(80, 80,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation)
                self.lbl_gambar.setPixmap(pixmap)
                return
        except Exception:
            pass
        self.lbl_gambar.setText("🛒")
        self.lbl_gambar.setStyleSheet(self.lbl_gambar.styleSheet() + "font-size: 28px;")