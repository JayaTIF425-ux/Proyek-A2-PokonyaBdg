from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QLabel, QPushButton, QStackedWidget, QSizePolicy,
    QDialog, QLineEdit, QGridLayout, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, QByteArray, pyqtSignal, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QBrush, QColor
from PyQt6.QtSvg import QSvgRenderer
import os

from gui.pages.halaman_beranda import HalamanBeranda
from gui.pages.halaman_pencarian import HalamanPencarian
from gui.pages.halaman_penghitung import HalamanPenghitung
from gui.pages.halaman_tutorial import HalamanTutorial
from gui.pages.halaman_tentang import HalamanTentang
from gui.pages.halaman_admin import HalamanAdmin


# ─────────────────────────────────────────────────────────────────────────────
# SVG Helper
# ─────────────────────────────────────────────────────────────────────────────

def _svg_to_icon(svg_str: str, size: int = 20, color: str = "white") -> QIcon:
    """Render SVG string menjadi QIcon berukuran size×size px."""
    svg_colored = svg_str.replace("currentColor", color)
    renderer = QSvgRenderer(QByteArray(svg_colored.encode()))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


def _svg_to_pixmap(svg_str: str, size: int, color: str = "white") -> QPixmap:
    """Render SVG string menjadi QPixmap."""
    svg_colored = svg_str.replace("currentColor", color)
    renderer = QSvgRenderer(QByteArray(svg_colored.encode()))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap


# ─────────────────────────────────────────────────────────────────────────────
# [UBAH] Koleksi ikon SVG — semua vektor, tidak ada emoji
# ─────────────────────────────────────────────────────────────────────────────

_IKON = {
    "beranda": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M3 9.5L12 3l9 6.5V20a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9.5z"/>
  <path d="M9 21V12h6v9"/>
</svg>""",

    "pencarian": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="10" cy="10" r="6"/>
  <line x1="14.5" y1="14.5" x2="21" y2="21"/>
  <text x="7" y="13.5" font-size="7" fill="currentColor" stroke="none"
        font-family="sans-serif" font-weight="bold">Rp</text>
</svg>""",

    # [FIX] Ikon keranjang belanja — proporsional dan jelas
    "penghitung": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M6 2H3L2 7h20l-1.7 9H5.7L4 7"/>
  <circle cx="9" cy="20" r="1.5" fill="currentColor" stroke="none"/>
  <circle cx="17" cy="20" r="1.5" fill="currentColor" stroke="none"/>
</svg>""",

    "tutorial": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="3" y="3" width="18" height="18" rx="2"/>
  <polygon points="9,8 17,12 9,16" fill="currentColor" stroke="none"/>
</svg>""",

    "tentang": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="9"/>
  <line x1="12" y1="8" x2="12" y2="8.5" stroke-width="2.5"/>
  <line x1="12" y1="11" x2="12" y2="17"/>
</svg>""",

    "admin": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="8" r="4"/>
  <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
  <path d="M17 13l1.5 1.5L21 12" stroke="#F1C40F" stroke-width="2.5"/>
</svg>""",

    # [FIX] Ikon logout — tetap menggunakan ikon pintu panah keluar (bukan emoji)
    "logout": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
  <polyline points="16 17 21 12 16 7"/>
  <line x1="21" y1="12" x2="9" y2="12"/>
</svg>""",

    "tema_gelap": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
</svg>""",

    "tema_terang": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="5"/>
  <line x1="12" y1="1" x2="12" y2="3"/>
  <line x1="12" y1="21" x2="12" y2="23"/>
  <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
  <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
  <line x1="1" y1="12" x2="3" y2="12"/>
  <line x1="21" y1="12" x2="23" y2="12"/>
  <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
  <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
</svg>""",

    # [BARU] Ikon user & role (vektor, menggantikan emoji 👤 dan 🔑)
    "user": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="8" r="4"/>
  <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
</svg>""",

    "kunci": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
</svg>""",

    # [BARU] Ikon edit profil (vektor, menggantikan ✏)
    "edit": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
</svg>""",

    # [BARU] Ikon mata (untuk toggle lihat password)
    "mata_buka": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
  <circle cx="12" cy="12" r="3"/>
</svg>""",

    "mata_tutup": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
  <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
  <line x1="1" y1="1" x2="23" y2="23"/>
</svg>""",

    # [BARU] Ikon pintu (menggantikan emoji 🚪 di dialog logout)
    "pintu": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M13 3h-2a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h2"/>
  <rect x="3" y="3" width="10" height="18" rx="1"/>
  <polyline points="17 15 21 12 17 9"/>
  <line x1="21" y1="12" x2="11" y2="12"/>
</svg>""",
}


# ─────────────────────────────────────────────────────────────────────────────
# [BARU] Widget Toggle Switch (menggantikan tombol dark mode biasa)
# ─────────────────────────────────────────────────────────────────────────────

class ToggleSwitch(QWidget):
    """
    [BARU] Komponen toggle switch modern (seperti iOS toggle).
    Menggantikan tombol teks biasa untuk dark mode.
    """

    toggled = pyqtSignal(bool)  # True = aktif (dark mode on)

    # Warna track & knob
    _COLOR_ON_TRACK  = "#F1C40F"   # kuning keemasan — dark mode aktif
    _COLOR_OFF_TRACK = "rgba(255,255,255,0.25)"
    _COLOR_KNOB      = "#FFFFFF"

    def __init__(self, checked: bool = False, parent=None):
        super().__init__(parent)
        self._checked = checked
        self.setFixedSize(44, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, state: bool):
        self._checked = state
        self.update()

    def mousePressEvent(self, event):
        self._checked = not self._checked
        self.toggled.emit(self._checked)
        self.update()
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Track
        track_color = QColor(self._COLOR_ON_TRACK if self._checked else "#666688")
        painter.setBrush(QBrush(track_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 4, 44, 16, 8, 8)

        # Knob
        knob_x = 24 if self._checked else 4
        painter.setBrush(QBrush(QColor(self._COLOR_KNOB)))
        painter.drawEllipse(knob_x, 2, 20, 20)

        painter.end()


# ─────────────────────────────────────────────────────────────────────────────
# MainWindow
# ─────────────────────────────────────────────────────────────────────────────

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

        if self.is_admin:
            self.halaman_admin = HalamanAdmin(current_user=self.current_user)
            self.pages.addWidget(self.halaman_admin)  # 5

        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(self.pages, 1)
        self.setCentralWidget(central)

        self.halaman_beranda.navigasi_pencarian.connect(self.navigasi_ke_pencarian)
        self._set_halaman(0)

    # ── Builder Sidebar ───────────────────────────────────────────────────────

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

        # ── [FIX] Info user — "User/Admin" + username dalam SATU baris horizontal ──
        username = self.current_user.get("username", "guest")
        role     = self.current_user.get("role", "user")
        display  = self.current_user.get("display_name") or username
        # [FIX] Ikon vektor user/admin menggantikan emoji 👤/🔑
        role_ikon_svg = _IKON["kunci"] if role == "admin" else _IKON["user"]

        self.user_info_frame = QFrame()
        self.user_info_frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(255,255,255,0.08);
                border-radius: 8px;
                margin: 0 10px 6px 10px;
            }}
        """)
        user_info_layout = QHBoxLayout(self.user_info_frame)
        user_info_layout.setContentsMargins(10, 8, 10, 8)
        user_info_layout.setSpacing(8)

        # Ikon vektor user
        self.lbl_user_icon = QLabel()
        self.lbl_user_icon.setFixedSize(18, 18)
        self.lbl_user_icon.setPixmap(
            _svg_to_pixmap(role_ikon_svg, 18, self.WARNA_AKSEN)
        )
        self.lbl_user_icon.setStyleSheet("background: transparent; border: none;")

        # [FIX] Badge role dan username dalam satu baris
        role_label = "Admin" if role == "admin" else "User"
        self.lbl_user_role = QLabel(role_label)
        self.lbl_user_role.setStyleSheet(f"""
            color: {self.WARNA_AKSEN};
            font-size: 11px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)

        # Garis pemisah tipis
        sep_vline = QFrame()
        sep_vline.setFrameShape(QFrame.Shape.VLine)
        sep_vline.setStyleSheet(f"color: rgba(255,255,255,0.2); background: rgba(255,255,255,0.2); max-width: 1px; border: none;")
        sep_vline.setFixedHeight(14)

        self.lbl_username = QLabel(display)
        self.lbl_username.setStyleSheet("""
            color: rgba(255,255,255,0.85);
            font-size: 12px;
            font-weight: 400;
            background: transparent;
            border: none;
        """)
        self.lbl_username.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        user_info_layout.addWidget(self.lbl_user_icon)
        user_info_layout.addWidget(self.lbl_user_role)
        user_info_layout.addWidget(sep_vline)
        user_info_layout.addWidget(self.lbl_username)

        layout.addWidget(self.user_info_frame)

        # [FIX] Tombol Edit Profil dengan ikon SVG vektor (menggantikan ✏ emoji)
        self.btn_edit_profil = QPushButton()
        self.btn_edit_profil.setText("  Edit Profil")
        self.btn_edit_profil.setIcon(_svg_to_icon(_IKON["edit"], size=14, color="rgba(255,255,255,0.65)"))
        self.btn_edit_profil.setIconSize(QSize(14, 14))
        self.btn_edit_profil.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit_profil.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: rgba(255,255,255,0.65);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 6px;
                font-size: 11px;
                padding: 5px 12px;
                margin: 0 12px 8px 12px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: rgba(255,255,255,0.12);
                color: {self.WARNA_AKSEN};
                border-color: {self.WARNA_AKSEN};
            }}
        """)
        self.btn_edit_profil.clicked.connect(self._buka_edit_profil)
        layout.addWidget(self.btn_edit_profil)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {self.WARNA_AKTIF}; border: none; border-top: 1px solid {self.WARNA_AKTIF};")
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
            ("Tutorial",     3, "tutorial"),
            ("Tentang Kami", 4, "tentang"),
        ]
        for teks, idx, ikon_key in bawah:
            btn = self._tombol_menu(teks, idx, ikon_key)
            self.menu_buttons.append(btn)
            layout.addWidget(btn)

        if self.is_admin:
            sep2 = QFrame()
            sep2.setFrameShape(QFrame.Shape.HLine)
            sep2.setStyleSheet(f"color: {self.WARNA_AKTIF}; margin: 4px 0;")
            layout.addWidget(sep2)

            btn_admin = self._tombol_menu("Panel Admin", 5, "admin", aksen=True)
            self.menu_buttons.append(btn_admin)
            layout.addWidget(btn_admin)

        sep_bawah = QFrame()
        sep_bawah.setFrameShape(QFrame.Shape.HLine)
        sep_bawah.setStyleSheet(f"color: {self.WARNA_AKTIF}; margin: 4px 0;")
        layout.addWidget(sep_bawah)

        # ── [UBAH] Tombol Toggle Dark Mode → Switch modern ────────────────────
        try:
            from gui.theme_manager import ThemeManager
            tema_skrg = ThemeManager.get_theme()
            is_dark   = tema_skrg == "dark"

            tema_row = QWidget()
            tema_row.setStyleSheet("background: transparent;")
            tema_hl = QHBoxLayout(tema_row)
            tema_hl.setContentsMargins(20, 8, 16, 8)
            tema_hl.setSpacing(10)

            # Ikon tema (SVG)
            self._lbl_tema_ikon = QLabel()
            self._lbl_tema_ikon.setFixedSize(18, 18)
            ikon_key = "tema_terang" if is_dark else "tema_gelap"
            self._lbl_tema_ikon.setPixmap(
                _svg_to_pixmap(_IKON[ikon_key], 18, "rgba(255,255,255,0.75)")
            )
            self._lbl_tema_ikon.setStyleSheet("background: transparent; border: none;")

            # Label teks
            self.lbl_tema_teks = QLabel("Mode Terang" if is_dark else "Mode Gelap")
            self.lbl_tema_teks.setStyleSheet(
                "color: rgba(255,255,255,0.75); font-size: 13px; background: transparent; border: none;"
            )

            # [BARU] Toggle switch widget
            self.toggle_tema = ToggleSwitch(checked=is_dark)
            self.toggle_tema.toggled.connect(self._toggle_tema)

            tema_hl.addWidget(self._lbl_tema_ikon)
            tema_hl.addWidget(self.lbl_tema_teks)
            tema_hl.addStretch()
            tema_hl.addWidget(self.toggle_tema)

            layout.addWidget(tema_row)
            self.btn_tema = tema_row      # simpan referensi agar _toggle_sidebar bisa hide/show
        except ImportError:
            self.btn_tema = None

        sep_logout = QFrame()
        sep_logout.setFrameShape(QFrame.Shape.HLine)
        sep_logout.setStyleSheet(f"color: {self.WARNA_AKTIF}; margin: 4px 0;")
        layout.addWidget(sep_logout)

        self.btn_logout = QPushButton("  Keluar")
        self.btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_logout.setToolTip("Logout")
        if "logout" in _IKON:
            self.btn_logout.setIcon(_svg_to_icon(_IKON["logout"], size=20))
            self.btn_logout.setIconSize(QSize(20, 20))
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
        btn = QPushButton(f"  {teks}")
        btn.setCheckable(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        if ikon_key in _IKON:
            btn.setIcon(_svg_to_icon(_IKON[ikon_key], size=20))
            btn.setIconSize(QSize(20, 20))

        warna_teks = self.WARNA_AKSEN if aksen else self.WARNA_TEKS
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {warna_teks};
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
            btn.setChecked(i == index)

    # ── Collapsible sidebar ───────────────────────────────────────────────────

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
            self.user_info_frame.setVisible(True)
            self.btn_edit_profil.setVisible(True)
            self.btn_collapse.setText("◀")
            self.btn_collapse.setToolTip("Sembunyikan sidebar")
            for btn, teks in zip(self.menu_buttons, _teks_menu):
                btn.setText(f"  {teks}")
            self.btn_logout.setText("  Keluar")
            if self.btn_tema:
                self.btn_tema.setVisible(True)
        else:
            self.sidebar.setFixedWidth(self.LEBAR_COLLAPSED)
            self.lbl_logo.setVisible(False)
            self.lbl_brand.setVisible(False)
            self.user_info_frame.setVisible(False)
            self.btn_edit_profil.setVisible(False)
            self.btn_collapse.setText("▶")
            self.btn_collapse.setToolTip("Tampilkan sidebar")
            for btn, tip in zip(self.menu_buttons, _teks_menu):
                btn.setToolTip(tip)
                btn.setText("")
            self.btn_logout.setText("")
            self.btn_logout.setToolTip("Keluar")
            if self.btn_tema:
                self.btn_tema.setVisible(False)

    # ── Dark mode toggle ──────────────────────────────────────────────────────

    def _toggle_tema(self, is_dark: bool = None):
        """
        [UBAH] Dipanggil oleh ToggleSwitch.toggled signal.
        Sinkronisasi state switch dan perbarui tampilan.
        """
        try:
            from PyQt6.QtWidgets import QApplication
            from gui.theme_manager import ThemeManager
            tema_baru = ThemeManager.toggle()
            ThemeManager.apply_to_app(QApplication.instance())

            # Update ikon dan teks
            ikon_key = "tema_terang" if tema_baru == "dark" else "tema_gelap"
            teks     = "Mode Terang" if tema_baru == "dark" else "Mode Gelap"

            if hasattr(self, '_lbl_tema_ikon'):
                self._lbl_tema_ikon.setPixmap(
                    _svg_to_pixmap(_IKON[ikon_key], 18, "rgba(255,255,255,0.75)")
                )
            if hasattr(self, 'lbl_tema_teks'):
                self.lbl_tema_teks.setText(teks)
            if hasattr(self, 'toggle_tema'):
                self.toggle_tema.setChecked(tema_baru == "dark")
        except ImportError:
            pass

    # ── Navigasi ──────────────────────────────────────────────────────────────

    def navigasi_ke_pencarian(self, keyword: str):
        self.halaman_pencarian.set_keyword_dan_cari(keyword)
        self._set_halaman(1)

    # ── Logout ────────────────────────────────────────────────────────────────

    def _konfirmasi_logout(self):
        dialog = _DialogLogout(
            username=self.current_user.get("display_name")
                     or self.current_user.get("username", ""),
            parent=self,
        )
        if dialog.exec():
            self.logout_requested.emit()
            self.close()

    # ── Edit Profil ───────────────────────────────────────────────────────────

    def _buka_edit_profil(self):
        from database.auth_manager import AuthManager
        dialog = _DialogEditProfil(self.current_user, AuthManager(), parent=self)
        if dialog.exec():
            updated = dialog.get_updated_user()
            self.current_user.update(updated)
            # Update label sidebar
            display = self.current_user.get("display_name") or self.current_user.get("username", "guest")
            self.lbl_username.setText(display)


# ─────────────────────────────────────────────────────────────────────────────
# [UBAH] Dialog Konfirmasi Logout — ikon vektor, tidak ada emoji
# ─────────────────────────────────────────────────────────────────────────────

class _DialogLogout(QDialog):
    """Pop-up konfirmasi logout yang rapi dengan ikon vektor (bukan emoji)."""

    def __init__(self, username: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Konfirmasi Logout")
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(380)

        card = QFrame(self)
        card.setObjectName("LogoutCard")
        card.setStyleSheet("""
            #LogoutCard {
                background: #FFFFFF;
                border-radius: 20px;
                border: 1px solid #E8E0D4;
            }
        """)

        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 60))
        card.setGraphicsEffect(shadow)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)  # padding untuk shadow
        outer.addWidget(card)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(0)

        # [FIX] Ikon pintu SVG vektor (menggantikan emoji 🚪)
        ikon_container = QLabel()
        ikon_container.setFixedSize(56, 56)
        ikon_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ikon_pix = _svg_to_pixmap(_IKON["pintu"], 40, "#C0392B")
        ikon_container.setPixmap(ikon_pix)
        ikon_container.setStyleSheet("""
            background: #FDECEA;
            border-radius: 28px;
            border: none;
        """)
        lay.addWidget(ikon_container, alignment=Qt.AlignmentFlag.AlignCenter)
        lay.addSpacing(16)

        judul = QLabel("Keluar dari Akun?")
        judul.setAlignment(Qt.AlignmentFlag.AlignCenter)
        judul.setStyleSheet(
            "font-size: 18px; font-weight: 700; color: #1A0A0E; background: transparent;"
        )
        lay.addWidget(judul)
        lay.addSpacing(8)

        sub = QLabel(f'Yakin ingin keluar dari akun <b>{username}</b>?')
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setTextFormat(Qt.TextFormat.RichText)
        sub.setWordWrap(True)
        sub.setStyleSheet(
            "font-size: 13px; color: #6B5B61; background: transparent;"
        )
        lay.addWidget(sub)
        lay.addSpacing(28)

        row = QHBoxLayout()
        row.setSpacing(12)

        btn_batal = QPushButton("Batal")
        btn_batal.setFixedHeight(44)
        btn_batal.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_batal.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #44101A;
                border: 1.5px solid #E2D9CC;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #F4F0EA;
                border-color: #44101A;
            }
        """)
        btn_batal.clicked.connect(self.reject)

        btn_keluar = QPushButton("Ya, Keluar")
        btn_keluar.setFixedHeight(44)
        btn_keluar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_keluar.setStyleSheet("""
            QPushButton {
                background: #C0392B;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 700;
            }
            QPushButton:hover { background: #A93226; }
            QPushButton:pressed { background: #922B21; }
        """)
        btn_keluar.clicked.connect(self.accept)

        row.addWidget(btn_batal)
        row.addWidget(btn_keluar)
        lay.addLayout(row)


# ─────────────────────────────────────────────────────────────────────────────
# [UBAH] Dialog Edit Profil — redesain UI + FIX logika simpan password
# ─────────────────────────────────────────────────────────────────────────────

class _DialogEditProfil(QDialog):
    """
    Dialog untuk mengubah display name dan password.

    PERUBAHAN:
    - [FIX] Password baru kini benar-benar tersimpan ke DB
    - [BARU] Toggle "Lihat Password" dengan ikon mata SVG vektor
    - [UBAH] Redesain UI: shadow, rounded corners, padding rapi, warna senada app
    """

    def __init__(self, user: dict, auth_manager, parent=None):
        super().__init__(parent)
        self._user = user
        self._auth = auth_manager
        self._updated: dict = {}

        self.setWindowTitle("Edit Profil")
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(440)

        # Card utama
        card = QFrame(self)
        card.setObjectName("EditProfilCard")
        card.setStyleSheet("""
            #EditProfilCard {
                background: #FFFFFF;
                border-radius: 20px;
                border: 1px solid #E8E0D4;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 70))
        card.setGraphicsEffect(shadow)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.addWidget(card)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(0)

        # Header
        header_row = QHBoxLayout()
        header_row.setSpacing(12)

        # Ikon user vektor
        lbl_header_ikon = QLabel()
        lbl_header_ikon.setFixedSize(40, 40)
        lbl_header_ikon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_header_ikon.setPixmap(_svg_to_pixmap(_IKON["user"], 24, "#44101A"))
        lbl_header_ikon.setStyleSheet("""
            background: #FDF0F3;
            border-radius: 20px;
            border: none;
        """)
        header_row.addWidget(lbl_header_ikon)

        header_teks = QVBoxLayout()
        header_teks.setSpacing(2)
        judul = QLabel("Edit Profil")
        judul.setStyleSheet(
            "font-size: 18px; font-weight: 700; color: #44101A; background: transparent;"
        )
        sub = QLabel(f"Akun: {user.get('username', '')}")
        sub.setStyleSheet("font-size: 12px; color: #A89BA0; background: transparent;")
        header_teks.addWidget(judul)
        header_teks.addWidget(sub)
        header_row.addLayout(header_teks)
        header_row.addStretch()

        lay.addLayout(header_row)
        lay.addSpacing(24)

        # Garis pemisah
        garis = QFrame()
        garis.setFrameShape(QFrame.Shape.HLine)
        garis.setStyleSheet("color: #F0EBE3; border: none; border-top: 1px solid #F0EBE3;")
        lay.addWidget(garis)
        lay.addSpacing(20)

        # Display name
        lay.addWidget(self._lbl("Nama Tampilan"))
        lay.addSpacing(6)
        self.inp_display = QLineEdit()
        self.inp_display.setText(user.get("display_name") or user.get("username", ""))
        self.inp_display.setPlaceholderText("Nama yang ditampilkan")
        self._style_input(self.inp_display)
        lay.addWidget(self.inp_display)
        lay.addSpacing(20)

        # Password baru (dengan toggle lihat password)
        lay.addWidget(self._lbl("Password Baru"))
        lay.addWidget(self._lbl_hint("Kosongkan jika tidak ingin mengubah password"))
        lay.addSpacing(6)
        self.inp_pass = self._input_password("Masukkan password baru")
        lay.addWidget(self.inp_pass)
        lay.addSpacing(12)

        # Konfirmasi password
        lay.addWidget(self._lbl("Konfirmasi Password Baru"))
        lay.addSpacing(6)
        self.inp_pass_confirm = self._input_password("Ulangi password baru")
        lay.addWidget(self.inp_pass_confirm)
        lay.addSpacing(12)

        # Error label
        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet(
            "color: #C0392B; font-size: 12px; background: #FEF0F0; "
            "border-radius: 6px; padding: 6px 10px; border: none;"
        )
        self.lbl_error.setWordWrap(True)
        self.lbl_error.setVisible(False)
        lay.addWidget(self.lbl_error)

        self.lbl_sukses = QLabel("")
        self.lbl_sukses.setStyleSheet(
            "color: #27AE60; font-size: 12px; background: #F0FEF4; "
            "border-radius: 6px; padding: 6px 10px; border: none;"
        )
        self.lbl_sukses.setVisible(False)
        lay.addWidget(self.lbl_sukses)
        lay.addSpacing(20)

        # Tombol aksi
        row = QHBoxLayout()
        row.setSpacing(12)

        btn_batal = QPushButton("Batal")
        btn_batal.setFixedHeight(46)
        btn_batal.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_batal.setStyleSheet("""
            QPushButton {
                background: transparent; color: #44101A;
                border: 1.5px solid #E2D9CC; border-radius: 12px;
                font-size: 14px; font-weight: 500;
            }
            QPushButton:hover { background: #F4F0EA; border-color: #44101A; }
        """)
        btn_batal.clicked.connect(self.reject)

        btn_simpan = QPushButton("Simpan Perubahan")
        btn_simpan.setFixedHeight(46)
        btn_simpan.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_simpan.setStyleSheet("""
            QPushButton {
                background: #44101A; color: white;
                border: none; border-radius: 12px;
                font-size: 14px; font-weight: 700;
            }
            QPushButton:hover { background: #6B1525; }
            QPushButton:pressed { background: #3A0E16; }
        """)
        btn_simpan.clicked.connect(self._simpan)

        row.addWidget(btn_batal)
        row.addWidget(btn_simpan)
        lay.addLayout(row)

    def _lbl(self, teks: str) -> QLabel:
        l = QLabel(teks)
        l.setStyleSheet("font-size: 13px; font-weight: 600; color: #1A0A0E; background: transparent;")
        return l

    def _lbl_hint(self, teks: str) -> QLabel:
        l = QLabel(teks)
        l.setStyleSheet("font-size: 11px; color: #A89BA0; background: transparent; margin-top: 2px;")
        return l

    def _style_input(self, w: QLineEdit):
        w.setFixedHeight(46)
        w.setStyleSheet("""
            QLineEdit {
                background: #FAFAF8; border: 1.5px solid #E2D9CC;
                border-radius: 12px; padding: 10px 14px;
                font-size: 13px; color: #1A0A0E;
            }
            QLineEdit:focus { border: 2px solid #44101A; background: #FFFFFF; }
        """)

    def _input_password(self, placeholder: str) -> QLineEdit:
        """
        [BARU] Buat input password dengan tombol toggle lihat/sembunyikan
        menggunakan ikon mata SVG vektor (bukan emoji 👁).
        """
        container = QLineEdit()
        container.setPlaceholderText(placeholder)
        container.setEchoMode(QLineEdit.EchoMode.Password)
        container.setFixedHeight(46)
        container.setStyleSheet("""
            QLineEdit {
                background: #FAFAF8; border: 1.5px solid #E2D9CC;
                border-radius: 12px; padding: 10px 44px 10px 14px;
                font-size: 13px; color: #1A0A0E;
            }
            QLineEdit:focus { border: 2px solid #44101A; background: #FFFFFF; }
        """)

        # [BARU] Tombol mata SVG vektor di dalam input
        btn_eye = QPushButton(container)
        btn_eye.setFixedSize(32, 32)
        btn_eye.setStyleSheet(
            "border: none; background: transparent; padding: 0;"
        )
        btn_eye.setCheckable(True)
        btn_eye.setCursor(Qt.CursorShape.PointingHandCursor)

        # Set ikon mata tutup (default: password tersembunyi)
        btn_eye.setIcon(_svg_to_icon(_IKON["mata_tutup"], 18, "#A89BA0"))
        btn_eye.setIconSize(QSize(18, 18))

        def _toggle(checked, field=container, b=btn_eye):
            if checked:
                field.setEchoMode(QLineEdit.EchoMode.Normal)
                b.setIcon(_svg_to_icon(_IKON["mata_buka"], 18, "#44101A"))
            else:
                field.setEchoMode(QLineEdit.EchoMode.Password)
                b.setIcon(_svg_to_icon(_IKON["mata_tutup"], 18, "#A89BA0"))

        btn_eye.toggled.connect(_toggle)

        def _reposition(event=None, b=btn_eye, f=container):
            b.move(f.width() - 38, (f.height() - 32) // 2)

        container.resizeEvent = _reposition

        return container

    def _simpan(self):
        self.lbl_error.setVisible(False)
        self.lbl_sukses.setVisible(False)

        display  = self.inp_display.text().strip()
        new_pass = self.inp_pass.text()
        confirm  = self.inp_pass_confirm.text()

        if not display:
            self.lbl_error.setText("⚠ Nama tampilan tidak boleh kosong.")
            self.lbl_error.setVisible(True)
            return

        if new_pass:
            if len(new_pass) < 6:
                self.lbl_error.setText("⚠ Password minimal 6 karakter.")
                self.lbl_error.setVisible(True)
                return
            if new_pass != confirm:
                self.lbl_error.setText("⚠ Konfirmasi password tidak cocok.")
                self.lbl_error.setVisible(True)
                return

        # [FIX] Gunakan update_profil_lengkap() yang sekaligus update
        # display_name DAN password dalam satu transaksi.
        # Bug sebelumnya: password tidak tersimpan karena method ubah_password()
        # memerlukan verifikasi password lama yang tidak diisi.
        uid = self._user.get("id")
        berhasil, pesan = self._auth.update_profil_lengkap(
            user_id=uid,
            display_name=display,
            new_password=new_pass if new_pass else None,
        )

        if not berhasil:
            self.lbl_error.setText(f"❌ {pesan}")
            self.lbl_error.setVisible(True)
            return

        self._updated = {"display_name": display}
        self.accept()

    def get_updated_user(self) -> dict:
        return self._updated