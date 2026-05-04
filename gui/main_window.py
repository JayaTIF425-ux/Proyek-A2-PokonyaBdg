"""
gui/main_window.py — Jendela utama aplikasi dengan sidebar navigasi.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QLabel, QPushButton, QStackedWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

from gui.pages.halaman_beranda import HalamanBeranda
from gui.pages.halaman_pencarian import HalamanPencarian
from gui.pages.halaman_penghitung import HalamanPenghitung
from gui.pages.halaman_tutorial import HalamanTutorial
from gui.pages.halaman_tentang import HalamanTentang


class MainWindow(QMainWindow):
    """Jendela utama dengan sidebar + konten stacked."""

    WARNA_SIDEBAR   = "#44101A"
    WARNA_AKTIF     = "#6B1525"
    WARNA_AKSEN     = "#F1C40F"
    WARNA_TEKS      = "#FFFFFF"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PokokNya.Bdg — Harga Bahan Pokok Bandung")
        self.resize(1200, 800)
        self.setMinimumSize(900, 600)

        central = QWidget()
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Sidebar ──────────────────────────────────────────────────────
        self.sidebar = self._buat_sidebar()

        # ── Halaman ──────────────────────────────────────────────────────
        self.pages = QStackedWidget()
        self.halaman_beranda   = HalamanBeranda()
        self.halaman_pencarian = HalamanPencarian()
        self.halaman_penghitung = HalamanPenghitung()
        self.halaman_tutorial  = HalamanTutorial()
        self.halaman_tentang   = HalamanTentang()

        self.pages.addWidget(self.halaman_beranda)    # 0
        self.pages.addWidget(self.halaman_pencarian)  # 1
        self.pages.addWidget(self.halaman_penghitung) # 2
        self.pages.addWidget(self.halaman_tutorial)   # 3
        self.pages.addWidget(self.halaman_tentang)    # 4

        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(self.pages, 1)
        self.setCentralWidget(central)

        # Tampilkan beranda saat mulai
        self._set_halaman(0)

    # ── Builder Sidebar ──────────────────────────────────────────────────

    def _buat_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet(f"background-color: {self.WARNA_SIDEBAR};")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 20)
        layout.setSpacing(4)

        # Brand / Logo
        brand = QLabel("PokokNya")
        brand.setStyleSheet(
            f"color: {self.WARNA_AKSEN}; font-size: 22px; font-weight: bold; "
            "padding: 24px 20px 4px 20px;"
        )
        sub = QLabel(".Bdg")
        sub.setStyleSheet(
            f"color: {self.WARNA_TEKS}; font-size: 13px; padding: 0 20px 20px 20px;"
        )
        layout.addWidget(brand)
        layout.addWidget(sub)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {self.WARNA_AKTIF};")
        layout.addWidget(sep)
        layout.addSpacing(8)

        # Menu Utama
        self.menu_buttons: list[QPushButton] = []
        menus = [
            ("🏠  Beranda",           0),
            ("🔍  Pencarian",         1),
            ("🧮  Penghitung Belanja", 2),
        ]
        for teks, idx in menus:
            btn = self._tombol_menu(teks, idx)
            self.menu_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        # Menu Bawah
        bawah = [
            ("ℹ️  Tutorial",   3),
            ("👥  Tentang Kami", 4),
        ]
        for teks, idx in bawah:
            btn = self._tombol_menu(teks, idx)
            self.menu_buttons.append(btn)
            layout.addWidget(btn)

        return sidebar

    def _tombol_menu(self, teks: str, index: int) -> QPushButton:
        btn = QPushButton(teks)
        btn.setCheckable(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {self.WARNA_TEKS};
                text-align: left;
                padding: 12px 20px;
                border: none;
                border-left: 4px solid transparent;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {self.WARNA_AKTIF};
                border-left: 4px solid {self.WARNA_AKSEN};
            }}
            QPushButton:checked {{
                background-color: {self.WARNA_AKTIF};
                border-left: 4px solid {self.WARNA_AKSEN};
                font-weight: bold;
            }}
        """)
        btn.clicked.connect(lambda: self._set_halaman(index))
        return btn

    def _set_halaman(self, index: int):
        self.pages.setCurrentIndex(index)
        for i, btn in enumerate(self.menu_buttons):
            # Petakan urutan tombol (3 utama + 2 bawah = idx 0-4)
            btn_index = i if i < 3 else i  # sama karena append berurutan
            btn.setChecked(btn_index == index)
