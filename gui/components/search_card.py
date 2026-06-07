"""
gui/components/search_card.py — Kartu hasil pencarian dengan tombol CRUD.
Tombol Edit & Hapus hanya tampil jika is_admin=True.
"""

from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QByteArray as _B
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer as _R
from gui.components.icon_helper import apply_icon_to_label
import urllib.request
import os

_SVG_MAP_STR = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
viewBox="0 0 24 24" fill="none" stroke="#7f8c8d" stroke-width="2"
stroke-linecap="round" stroke-linejoin="round">
<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0
C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/>
<circle cx="12" cy="10" r="3"/></svg>"""

_SVG_DATE_STR = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
viewBox="0 0 24 24" fill="none" stroke="#7f8c8d" stroke-width="2"
stroke-linecap="round" stroke-linejoin="round">
<path d="M16 14v2.2l1.6 1"/><path d="M16 2v4"/>
<path d="M21 7.5V6a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h3.5"/>
<path d="M3 10h5"/><path d="M8 2v4"/>
<circle cx="16" cy="16" r="6"/></svg>"""

def _render_svg(svg_str, ukuran=13):
    r = _R(_B(svg_str.encode()))
    px = QPixmap(ukuran, ukuran)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    r.render(p)
    p.end()
    return px

class SearchCard(QFrame):
    edit_diminta  = pyqtSignal(object)
    hapus_diminta = pyqtSignal(int)

    def __init__(self, nama: str, harga: float, toko: str, tanggal: str,
                 thumbnail_url: str = "", id_produk: int = -1,
                 sumber: str = "supermarket", kategori: str = "", satuan: str = "kg",
                 is_admin: bool = False):   # ← parameter baru
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
        self.is_admin      = is_admin      # ← simpan role

        print(f"nama={self.nama}, sumber='{self.sumber}', toko='{self.toko}'")

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
            apply_icon_to_label(self.lbl_gambar, self.nama, kategori=self.kategori)

        layout.addWidget(self.lbl_gambar)

        # Info tengah
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(14, 10, 0, 10)
        info_layout.setSpacing(3)

        badge_warna = "#2980b9"

        if self.toko.lower() == "pasar tradisional":
            badge_teks  = "Pasar Tradisional"
            teks_toko   = "PIHPS Nasional"
        else:
            badge_teks  = "Supermarket"
            teks_toko   = self.toko
        
        lbl_badge = QLabel(badge_teks)
        lbl_badge.setFixedWidth(110)
        lbl_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
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

        # Baris toko
        toko_row = QHBoxLayout()
        toko_row.setSpacing(4)
        toko_row.setContentsMargins(0, 0, 0, 0)
        lbl_map_ikon = QLabel()
        lbl_map_ikon.setPixmap(_render_svg(_SVG_MAP_STR))
        lbl_map_ikon.setStyleSheet("border: none; background: transparent;")

        lbl_map_teks = QLabel(teks_toko)
        lbl_map_teks.setStyleSheet("font-size: 10px; color: #7f8c8d; border: none;")
        toko_row.addWidget(lbl_map_ikon)
        toko_row.addWidget(lbl_map_teks)
        toko_row.addStretch()

        # Baris tanggal
        date_row = QHBoxLayout()
        date_row.setSpacing(4)
        date_row.setContentsMargins(0, 0, 0, 0)
        lbl_date_ikon = QLabel()
        lbl_date_ikon.setPixmap(_render_svg(_SVG_DATE_STR))
        lbl_date_ikon.setStyleSheet("border: none; background: transparent;")
        lbl_date_teks = QLabel(self.tanggal or "-")
        lbl_date_teks.setStyleSheet("font-size: 10px; color: #7f8c8d; border: none;")
        date_row.addWidget(lbl_date_ikon)
        date_row.addWidget(lbl_date_teks)
        date_row.addStretch()

        info_layout.addWidget(lbl_badge)
        info_layout.addWidget(lbl_nama)
        info_layout.addWidget(lbl_harga)
        info_layout.addLayout(toko_row)
        info_layout.addLayout(date_row)
        info_layout.addStretch()
        layout.addLayout(info_layout, 1)

        # ── Tombol Edit & Hapus — hanya tampil untuk admin ─────────────────
        if self.is_admin:
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

            # Data PIHPS tidak bisa diedit manual
            if self.sumber == "pihps":
                self.btn_edit.setEnabled(False)
                self.btn_hapus.setEnabled(False)
                _style_nonaktif = (
                    "QPushButton { background-color: #bdc3c7; color: #fff; "
                    "border-radius: 5px; font-size: 11px; border: none; }"
                )
                self.btn_edit.setStyleSheet(_style_nonaktif)
                self.btn_hapus.setStyleSheet(_style_nonaktif)
                self.btn_edit.setToolTip("Data PIHPS dikelola scraper otomatis")
                self.btn_hapus.setToolTip("Data PIHPS dikelola scraper otomatis")

            self.btn_edit.clicked.connect(lambda: self.edit_diminta.emit(self._as_row()))
            self.btn_hapus.clicked.connect(lambda: self.hapus_diminta.emit(self.id_produk))

            btn_layout.addWidget(self.btn_edit)
            btn_layout.addWidget(self.btn_hapus)
            btn_layout.addStretch()
            layout.addLayout(btn_layout)
        # Jika bukan admin, tidak ada tombol apapun di kanan

    def _as_row(self):
        return {
            "id":       self.id_produk,
            "nama":     self.nama,
            "harga":    self.harga,
            "toko":     self.toko,
            "tanggal":  self.tanggal,
            "kategori": self.kategori,
            "satuan":   self.satuan,
        }

    def _load_gambar(self, url: str):
        try:
            cache_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "img_cache"
            )
            os.makedirs(cache_dir, exist_ok=True)
            import hashlib
            nama_file  = hashlib.md5(url.encode()).hexdigest() + ".jpg"
            path_lokal = os.path.join(cache_dir, nama_file)
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
        self.lbl_gambar.setText("🛒")
        self.lbl_gambar.setStyleSheet(self.lbl_gambar.styleSheet() + "font-size: 28px;")
