"""
gui/main_window.py — Jendela utama aplikasi dengan sidebar navigasi + collapsible.
Versi ini mendukung role user/admin: menu Admin hanya muncul untuk admin.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QLabel, QPushButton, QStackedWidget, QSizePolicy
)
from PyQt6.QtCore import QSize, Qt, QByteArray, pyqtSignal, QRectF
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QPainter
import os

from gui.pages.halaman_beranda import HalamanBeranda
from gui.pages.halaman_pencarian import HalamanPencarian
from gui.pages.halaman_penghitung import HalamanPenghitung
from gui.pages.halaman_tutorial import HalamanTutorial
from gui.pages.halaman_tentang import HalamanTentang
from gui.pages.halaman_admin import HalamanAdmin


# SVG icon helper 

def _svg_to_icon(svg_str: str, size: int = 20) -> QIcon:
    """Render SVG string menjadi QIcon berukuran size×size px."""
    ba = QByteArray(svg_str.strip().encode('utf-8'))
    renderer = QSvgRenderer(ba)

    ukuran_master = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.end()
    return QIcon(pixmap)


# Definisi SVG ikon sidebar 

_IKON = {
    "beranda": """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
     stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M3 9.5L12 3l9 6.5V20a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9.5z"/>
  <path d="M9 21V12h6v9"/>
</svg>""",

    "pencarian": """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
     stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="10" cy="10" r="6"/>
  <line x1="14.5" y1="14.5" x2="21" y2="21"/>
  <text x="7" y="13.5" font-size="7" fill="white" stroke="none"
        font-family="sans-serif" font-weight="bold">Rp</text>
</svg>""",

    "penghitung": """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
     stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M6 2h12a1 1 0 0 1 1 1v3H5V3a1 1 0 0 1 1-1z"/>
  <path d="M5 6h14l-1.5 14H6.5L5 6z"/>
  <line x1="9" y1="11" x2="9" y2="16"/>
  <line x1="12" y1="11" x2="12" y2="16"/>
  <line x1="15" y1="11" x2="15" y2="16"/>
</svg>""",

    "tutorial": """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
     stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="3" y="3" width="18" height="18" rx="2"/>
  <polygon points="9,8 17,12 9,16" fill="white" stroke="none"/>
</svg>""",

    "tentang": """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
     stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="9"/>
  <line x1="12" y1="8" x2="12" y2="8.5" stroke-width="2.5"/>
  <line x1="12" y1="11" x2="12" y2="17"/>
</svg>""",

    "admin": """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
     stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="8" r="4"/>
  <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
  <path d="M17 13l1.5 1.5L21 12" stroke="#F1C40F" stroke-width="2.5"/>
</svg>""",

    "logout": """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
     stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
  <polyline points="16 17 21 12 16 7"/>
  <line x1="21" y1="12" x2="9" y2="12"/>
</svg>""",
}

class MainWindow(QMainWindow):
    """Jendela utama dengan sidebar collapsible + konten stacked."""

    logout_requested = pyqtSignal()

    WARNA_SIDEBAR   = "#44101A"
    WARNA_AKTIF     = "#6B1525"
    WARNA_AKSEN     = "#F1C40F"
    WARNA_TEKS      = "#FFFFFF"
    LEBAR_EXPANDED  = 230
    LEBAR_COLLAPSED = 56

    def __init__(self, current_user: dict = None):
        super().__init__()
        # current_user: {"id": int, "username": str, "role": "admin"|"user"}
        self.current_user = current_user or {"id": 0, "username": "guest", "role": "user"}
        self.is_admin = self.current_user.get("role") == "admin"

        self.setWindowTitle("PokokNya.Bdg — Harga Bahan Pokok Bandung")
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gui", "assets", "images", "logo_app.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.resize(1200, 800)
        self.setMinimumSize(900, 600)
        self._sidebar_expanded = True

        central = QWidget()
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.sidebar = self._buat_sidebar()

        self.pages = QStackedWidget()
        self.halaman_beranda    = HalamanBeranda()
        self.halaman_pencarian  = HalamanPencarian(is_admin=self.is_admin)
        self.halaman_penghitung = HalamanPenghitung()
        self.halaman_tutorial   = HalamanTutorial()
        self.halaman_tentang    = HalamanTentang()

        self.pages.addWidget(self.halaman_beranda)    # 0
        self.pages.addWidget(self.halaman_pencarian)  # 1
        self.pages.addWidget(self.halaman_penghitung) # 2
        self.pages.addWidget(self.halaman_tutorial)   # 3
        self.pages.addWidget(self.halaman_tentang)    # 4

        # Halaman admin hanya dibuat jika role = admin
        if self.is_admin:
            self.halaman_admin = HalamanAdmin(current_user=self.current_user)
            self.pages.addWidget(self.halaman_admin)  # 5

        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(self.pages, 1)
        self.setCentralWidget(central)

        self.halaman_beranda.navigasi_pencarian.connect(self.navigasi_ke_pencarian)
        self._set_halaman(0)

    # Builder Sidebar 

    def _buat_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setFixedWidth(self.LEBAR_EXPANDED)
        sidebar.setStyleSheet(f"background-color: {self.WARNA_SIDEBAR};")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 20)
        layout.setSpacing(4)

        # Baris brand + tombol collapse
        brand_row = QHBoxLayout()
        brand_row.setContentsMargins(12, 16, 8, 0)

        # Buat btn_collapse DULU sebelum brand_row.addWidget
        self.btn_collapse = QPushButton("◀")
        self.btn_collapse.setFixedSize(28, 28)
        self.btn_collapse.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_collapse.setToolTip("Sembunyikan sidebar")
        self.btn_collapse.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.WARNA_AKTIF};
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #8B1E30; }}
        """)
        self.btn_collapse.clicked.connect(self._toggle_sidebar)

        # Logo bulat
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(BASE_DIR, "gui", "assets", "images", "logo_app.png")
        self.lbl_logo = QLabel()
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation)
            rounded = QPixmap(48, 48)
            rounded.fill(Qt.GlobalColor.transparent)
            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            from PyQt6.QtGui import QBrush
            from PyQt6.QtCore import QRect
            painter.setBrush(QBrush(pixmap))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QRect(0, 0, 48, 48))
            painter.end()
            self.lbl_logo.setPixmap(rounded)
        self.lbl_logo.setFixedSize(48, 48)

        # Teks brand
        brand_teks = QVBoxLayout()
        brand_teks.setSpacing(0)
        self.lbl_brand = QLabel("PokokNya.Bdg")
        self.lbl_brand.setStyleSheet(
            "color: #6B8E23; font-size: 16px; font-weight: bold;"
        )
        brand_teks.addWidget(self.lbl_brand)

        brand_row.addWidget(self.lbl_logo)
        brand_row.addSpacing(6)
        brand_row.addLayout(brand_teks)
        brand_row.addStretch()
        brand_row.addWidget(self.btn_collapse)
        layout.addLayout(brand_row)
        layout.addSpacing(8)

        # Info user yang login 
        username = self.current_user.get("username", "guest")
        role     = self.current_user.get("role", "user")
        badge    = "Admin" if role == "admin" else "User"

        self.user_frame = QFrame()
        self.user_frame.setStyleSheet("""
            QFrame#userFrame {
                background: rgba(255,255,255,0.08);
                border-radius: 6px;
            }
        """)
        self.user_frame.setObjectName("userFrame")  # ← pakai objectName agar selector spesifik

        # Atur margin lewat layout, bukan stylesheet
        user_layout = QHBoxLayout(self.user_frame)
        user_layout.setContentsMargins(8, 8, 8, 8)
        user_layout.setSpacing(8)
        user_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Tambah margin dari luar lewat parent layout
        layout.addSpacing(0)
        layout.addWidget(self.user_frame)
        # Ganti addWidget dengan ini agar ada margin kiri-kanan:
        layout.setContentsMargins(0, 0, 0, 20)

        # SVG user icon
        svg_user = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#F1C40F" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.925 20.056a6 6 0 0 0-11.851.001"/><circle cx="12" cy="11" r="4"/><circle cx="12" cy="12" r="10"/></svg>"""

        renderer = QSvgRenderer(QByteArray(svg_user.encode()))
        pm = QPixmap(18, 18)
        pm.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pm)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        renderer.render(painter, QRectF(0, 0, 18, 18))
        painter.end()

        lbl_ikon = QLabel()
        lbl_ikon.setFixedSize(18, 18)
        lbl_ikon.setPixmap(pm)
        lbl_ikon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_ikon.setStyleSheet("border: none; background: transparent;")
        
        self.lbl_user_teks = QLabel(f"{badge}\n{username}")
        self.lbl_user_teks.setStyleSheet(f"""
            color: {self.WARNA_AKSEN};
            font-size: 11px;
            font-weight: bold;
            border: none;
            background: transparent;
        """)
        self.lbl_user_teks.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        user_layout.addWidget(lbl_ikon)
        user_layout.addWidget(self.lbl_user_teks)
        layout.addWidget(self.user_frame)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {self.WARNA_AKTIF};")
        layout.addWidget(sep)
        layout.addSpacing(8)

        self.menu_buttons: list[QPushButton] = []
        menus = [
            ("Beranda",            0, "beranda"),
            ("Pencarian",          1, "pencarian"),
            ("Penghitung Belanja", 2, "penghitung"),
        ]
        for teks, idx, ikon_key in menus:
            btn = self._tombol_menu(teks, idx, ikon_key)
            self.menu_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        bawah = [
            ("Tutorial",    3, "tutorial"),
            ("Tentang Kami", 4, "tentang"),
        ]
        for teks, idx, ikon_key in bawah:
            btn = self._tombol_menu(teks, idx, ikon_key)
            self.menu_buttons.append(btn)
            layout.addWidget(btn)

        # Menu Admin (hanya untuk admin) 
        if self.is_admin:
            sep2 = QFrame()
            sep2.setFrameShape(QFrame.Shape.HLine)
            sep2.setStyleSheet(f"color: {self.WARNA_AKTIF}; margin: 4px 0;")
            layout.addWidget(sep2)

            btn_admin = self._tombol_menu("Panel Admin", 5, "admin", aksen=True)
            self.menu_buttons.append(btn_admin)
            layout.addWidget(btn_admin)

        # Tombol Logout
        sep_logout = QFrame()
        sep_logout.setFrameShape(QFrame.Shape.HLine)
        sep_logout.setStyleSheet(f"color: {self.WARNA_AKTIF}; margin: 4px 0;")
        layout.addWidget(sep_logout)

        self.btn_logout = QPushButton("Keluar")
        self.btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_logout.setToolTip("Logout")
        if "logout" in _IKON:
            self.btn_logout.setIcon(_svg_to_icon(_IKON["logout"], size=20))
            self.btn_logout.setIconSize(QPixmap(20, 20).size())
        self.btn_logout.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: #FF6B6B;
                text-align: left;
                padding: 12px 20px;
                border: none;
                border-left: 4px solid transparent;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 107, 107, 0.15);
                border-left: 4px solid #FF6B6B;
            }}
        """)
        self.btn_logout.clicked.connect(self._konfirmasi_logout)
        layout.addWidget(self.btn_logout)

        return sidebar

    def _tombol_menu(self, teks: str, index: int, ikon_key: str,
                     aksen: bool = False) -> QPushButton:
        btn = QPushButton(teks)
        btn.setCheckable(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        if ikon_key in _IKON:
            icon_master = _svg_to_icon(_IKON[ikon_key])
            btn.setIcon(_svg_to_icon(_IKON[ikon_key], size=20))
            btn.setIconSize(QSize(20, 20))

        warna_teks = self.WARNA_AKSEN if aksen else self.WARNA_TEKS
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {warna_teks};
                text-align: left;
                padding: 12px 10px;
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
            btn.setChecked(i == index)

    # Collapsible sidebar 

    def _toggle_sidebar(self):
        self._sidebar_expanded = not self._sidebar_expanded
        _teks_menu = ["Beranda", "Pencarian", "Penghitung Belanja",
                      "Tutorial", "Tentang Kami"]
        if self.is_admin:
            _teks_menu.append("Panel Admin")

        if self._sidebar_expanded:
            self.sidebar.setFixedWidth(self.LEBAR_EXPANDED)
            self.lbl_logo.setVisible(True)
            self.lbl_brand.setVisible(True)
            self.user_frame.setVisible(True)
            self.btn_collapse.setText("◀")
            self.btn_collapse.setToolTip("Sembunyikan sidebar")

            for btn, teks in zip(self.menu_buttons, _teks_menu):
                btn.setText(teks)
                btn.setToolTip("")
            self.btn_logout.setText("Keluar")
        else:
            self.sidebar.setFixedWidth(self.LEBAR_COLLAPSED)
            self.lbl_logo.setVisible(False)
            self.lbl_brand.setVisible(False)
            self.user_frame.setVisible(False)
            self.btn_collapse.setText("▶")
            self.btn_collapse.setToolTip("Tampilkan sidebar")
            
            for btn, tip in zip(self.menu_buttons, _teks_menu):
                btn.setToolTip(tip)
                btn.setText("")
            self.btn_logout.setText("")
            self.btn_logout.setToolTip("Keluar")

    # Navigasi dari beranda ke pencarian 

    def navigasi_ke_pencarian(self, keyword: str):
        self.halaman_pencarian.set_keyword_dan_cari(keyword)
        self._set_halaman(1)
    # ── Logout ────────────────────────────────────────────────────────────────

    def _konfirmasi_logout(self):
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Konfirmasi Logout")
        msg.setText(
            f"Yakin ingin keluar dari akun "
            f"<b>{self.current_user.get('username', '')}</b>?"
        )
        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        msg.button(QMessageBox.StandardButton.Yes).setText("Ya, Keluar")
        msg.button(QMessageBox.StandardButton.No).setText("Batal")
        msg.setStyleSheet("""
            QMessageBox { background-color: #FFFFFF; }
            QLabel { color: #1A0A0E; font-size: 13px; }
            QPushButton {
                padding: 8px 20px;
                border-radius: 6px;
                font-size: 13px;
                min-width: 80px;
            }
        """)
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.logout_requested.emit()
            self.close()