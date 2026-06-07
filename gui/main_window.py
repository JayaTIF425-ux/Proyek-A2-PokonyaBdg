from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QLabel, QPushButton, QStackedWidget, QSizePolicy,
    QDialog, QLineEdit, QGridLayout,
)
from PyQt6.QtCore import Qt, QByteArray, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer
import os

from gui.pages.halaman_beranda import HalamanBeranda
from gui.pages.halaman_pencarian import HalamanPencarian
from gui.pages.halaman_penghitung import HalamanPenghitung
from gui.pages.halaman_tutorial import HalamanTutorial
from gui.pages.halaman_tentang import HalamanTentang
from gui.pages.halaman_admin import HalamanAdmin


def _svg_to_icon(svg_str: str, size: int = 20) -> QIcon:
    renderer = QSvgRenderer(QByteArray(svg_str.encode()))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


_IKON = {
    "beranda": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M3 9.5L12 3l9 6.5V20a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9.5z"/>
  <path d="M9 21V12h6v9"/>
</svg>""",

    "pencarian": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="10" cy="10" r="6"/>
  <line x1="14.5" y1="14.5" x2="21" y2="21"/>
  <text x="7" y="13.5" font-size="7" fill="white" stroke="none"
        font-family="sans-serif" font-weight="bold">Rp</text>
</svg>""",

    "penghitung": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M6 2h12a1 1 0 0 1 1 1v3H5V3a1 1 0 0 1 1-1z"/>
  <path d="M5 6h14l-1.5 14H6.5L5 6z"/>
  <line x1="9" y1="11" x2="9" y2="16"/>
  <line x1="12" y1="11" x2="12" y2="16"/>
  <line x1="15" y1="11" x2="15" y2="16"/>
</svg>""",

    "tutorial": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="3" y="3" width="18" height="18" rx="2"/>
  <polygon points="9,8 17,12 9,16" fill="white" stroke="none"/>
</svg>""",

    "tentang": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="9"/>
  <line x1="12" y1="8" x2="12" y2="8.5" stroke-width="2.5"/>
  <line x1="12" y1="11" x2="12" y2="17"/>
</svg>""",

    "admin": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="8" r="4"/>
  <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
  <path d="M17 13l1.5 1.5L21 12" stroke="#F1C40F" stroke-width="2.5"/>
</svg>""",

    "logout": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
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

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(BASE_DIR, "gui", "assets", "images", "logo_app.png")
        self.lbl_logo = QLabel()
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation)
            self.lbl_logo.setPixmap(pixmap)
        self.lbl_logo.setFixedSize(48, 48)
        self.lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_logo.setStyleSheet("background: transparent;")

        self.lbl_brand = QLabel("PokokNya.Bdg")
        self.lbl_brand.setStyleSheet("color: #8B9B3A; font-size: 15px; font-weight: bold;")

        brand_row.addWidget(self.lbl_logo)
        brand_row.addSpacing(6)
        brand_row.addWidget(self.lbl_brand)
        brand_row.addStretch()
        brand_row.addWidget(self.btn_collapse)
        layout.addLayout(brand_row)
        layout.addSpacing(10)

        username    = self.current_user.get("display_name") or self.current_user.get("username", "guest")
        role        = self.current_user.get("role", "user")
        badge_teks  = "Admin" if role == "admin" else "User"
        badge_color = "#F1C40F" if role == "admin" else "#90CAF9"

        user_frame = QFrame()
        user_frame.setStyleSheet("""
            background: rgba(255,255,255,0.09);
            border-radius: 8px;
            margin: 0 10px 6px 10px;
        """)
        user_row = QHBoxLayout(user_frame)
        user_row.setContentsMargins(10, 6, 10, 6)
        user_row.setSpacing(6)

        self.lbl_badge = QLabel(badge_teks)
        self.lbl_badge.setStyleSheet(f"""
            background: {badge_color};
            color: #1A0A0E;
            font-size: 10px; font-weight: 700;
            border-radius: 4px; padding: 1px 5px;
        """)
        self.lbl_username = QLabel(username)
        self.lbl_username.setStyleSheet("color: white; font-size: 12px; background: transparent;")
        self.lbl_username.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        user_row.addWidget(self.lbl_badge)
        user_row.addWidget(self.lbl_username)

        _SVG_EDIT = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
            stroke="rgba(255,255,255,0.7)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
        </svg>"""
        renderer = QSvgRenderer(QByteArray(_SVG_EDIT.encode()))
        pix_edit = QPixmap(16, 16)
        pix_edit.fill(Qt.GlobalColor.transparent)
        pp = QPainter(pix_edit)
        renderer.render(pp)
        pp.end()

        self.btn_edit_profil = QPushButton()
        self.btn_edit_profil.setIcon(QIcon(pix_edit))
        self.btn_edit_profil.setIconSize(QPixmap(16, 16).size())
        self.btn_edit_profil.setFixedSize(24, 24)
        self.btn_edit_profil.setToolTip("Edit Profil")
        self.btn_edit_profil.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit_profil.setStyleSheet("""
            QPushButton { background: transparent; border: none; border-radius: 4px; }
            QPushButton:hover { background: rgba(255,255,255,0.15); }
        """)
        self.btn_edit_profil.clicked.connect(self._buka_edit_profil)
        user_row.addWidget(self.btn_edit_profil)

        self.lbl_user_info = user_frame
        layout.addWidget(user_frame)

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
            btn.setIcon(_svg_to_icon(_IKON[ikon_key], size=20))
            btn.setIconSize(QPixmap(20, 20).size())

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

    # ── Collapsible Sidebar ───────────────────────────────────────────────────

    def _toggle_sidebar(self):
        self._sidebar_expanded = not self._sidebar_expanded
        _teks_menu = ["Beranda", "Pencarian", "Penghitung Belanja", "Tutorial", "Tentang Kami"]
        if self.is_admin:
            _teks_menu.append("Panel Admin")

        if self._sidebar_expanded:
            self.sidebar.setFixedWidth(self.LEBAR_EXPANDED)
            self.lbl_logo.setVisible(True)
            self.lbl_brand.setVisible(True)
            self.lbl_user_info.setVisible(True)
            self.btn_edit_profil.setVisible(True)
            self.btn_collapse.setText("◀")
            self.btn_collapse.setToolTip("Sembunyikan sidebar")
            for btn, teks in zip(self.menu_buttons, _teks_menu):
                btn.setText(teks)
            self.btn_logout.setText("Keluar")
        else:
            self.sidebar.setFixedWidth(self.LEBAR_COLLAPSED)
            self.lbl_logo.setVisible(False)
            self.lbl_brand.setVisible(False)
            self.lbl_user_info.setVisible(False)
            self.btn_edit_profil.setVisible(False)
            self.btn_collapse.setText("▶")
            self.btn_collapse.setToolTip("Tampilkan sidebar")
            for btn, tip in zip(self.menu_buttons, _teks_menu):
                btn.setToolTip(tip)
                btn.setText("")
            self.btn_logout.setText("")
            self.btn_logout.setToolTip("Keluar")

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
            display = self.current_user.get("display_name") or self.current_user.get("username", "guest")
            self.lbl_username.setText(display)


# ══════════════════════════════════════════════════════════════════════════════
# Dialog Konfirmasi Logout
# ══════════════════════════════════════════════════════════════════════════════

class _DialogLogout(QDialog):
    def __init__(self, username: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Konfirmasi Logout")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(380)

        card = QFrame(self)
        card.setObjectName("LogoutCard")
        card.setStyleSheet("""
            #LogoutCard {
                background: #FFFFFF;
                border-radius: 16px;
                border: 1px solid #E8E0D4;
            }
        """)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(card)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(0)

        ikon = QLabel("🚪")
        ikon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ikon.setStyleSheet("font-size: 40px; background: transparent;")
        lay.addWidget(ikon)
        lay.addSpacing(12)

        judul = QLabel("Keluar dari Akun?")
        judul.setAlignment(Qt.AlignmentFlag.AlignCenter)
        judul.setStyleSheet("font-size: 18px; font-weight: 700; color: #1A0A0E; background: transparent;")
        lay.addWidget(judul)
        lay.addSpacing(8)

        sub = QLabel(f'Yakin ingin keluar dari akun <b>{username}</b>?')
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setTextFormat(Qt.TextFormat.RichText)
        sub.setWordWrap(True)
        sub.setStyleSheet("font-size: 13px; color: #6B5B61; background: transparent;")
        lay.addWidget(sub)
        lay.addSpacing(24)

        row = QHBoxLayout()
        row.setSpacing(12)

        btn_batal = QPushButton("Batal")
        btn_batal.setFixedHeight(44)
        btn_batal.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_batal.setStyleSheet("""
            QPushButton {
                background: transparent; color: #44101A;
                border: 1.5px solid #E2D9CC; border-radius: 10px;
                font-size: 14px; font-weight: 500;
            }
            QPushButton:hover { background: #F4F0EA; border-color: #44101A; }
        """)
        btn_batal.clicked.connect(self.reject)

        btn_keluar = QPushButton("Ya, Keluar")
        btn_keluar.setFixedHeight(44)
        btn_keluar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_keluar.setStyleSheet("""
            QPushButton {
                background: #C0392B; color: white;
                border: none; border-radius: 10px;
                font-size: 14px; font-weight: 700;
            }
            QPushButton:hover { background: #A93226; }
            QPushButton:pressed { background: #922B21; }
        """)
        btn_keluar.clicked.connect(self.accept)

        row.addWidget(btn_batal)
        row.addWidget(btn_keluar)
        lay.addLayout(row)


# ══════════════════════════════════════════════════════════════════════════════
# Dialog Edit Profil
# ══════════════════════════════════════════════════════════════════════════════

class _DialogEditProfil(QDialog):
    _SVG_EYE_OPEN = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
      stroke="#A89BA0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
      <circle cx="12" cy="12" r="3"/>
    </svg>"""
    _SVG_EYE_OFF = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
      stroke="#A89BA0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
      <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
      <line x1="1" y1="1" x2="23" y2="23"/>
    </svg>"""

    def __init__(self, user: dict, auth_manager, parent=None):
        super().__init__(parent)
        self._user = user
        self._auth = auth_manager
        self._updated: dict = {}

        self.setWindowTitle("Edit Profil")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self.setFixedWidth(440)
        self.setStyleSheet("background: #F8F6F2;")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet("background: #5C1A28; border-radius: 0px;")
        header.setFixedHeight(72)
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(24, 0, 24, 0)
        lbl_h = QLabel("Edit Profil")
        lbl_h.setStyleSheet("color: white; font-size: 18px; font-weight: 700; background: transparent;")
        lbl_sub = QLabel(f"@{user.get('username', '')}")
        lbl_sub.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 12px; background: transparent;")
        hv = QVBoxLayout()
        hv.setSpacing(2)
        hv.addWidget(lbl_h)
        hv.addWidget(lbl_sub)
        h_lay.addLayout(hv)
        lay.addWidget(header)

        # Body
        body = QFrame()
        body.setStyleSheet("background: #F8F6F2;")
        b_lay = QVBoxLayout(body)
        b_lay.setContentsMargins(28, 24, 28, 24)
        b_lay.setSpacing(0)

        b_lay.addWidget(self._lbl("Nama Tampilan"))
        b_lay.addSpacing(4)
        lbl_nama_hint = QLabel("Nama ini yang akan ditampilkan di aplikasi")
        lbl_nama_hint.setStyleSheet("font-size: 11px; color: #A89BA0;")
        b_lay.addWidget(lbl_nama_hint)
        b_lay.addSpacing(6)
        self.inp_display = self._mk_input(
            user.get("display_name") or user.get("username", ""),
            "Nama yang ditampilkan"
        )
        b_lay.addWidget(self.inp_display)
        b_lay.addSpacing(18)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #E2D9CC;")
        b_lay.addWidget(sep)
        b_lay.addSpacing(14)

        lbl_pass_sec = QLabel("Ubah Password")
        lbl_pass_sec.setStyleSheet("font-size: 13px; font-weight: 600; color: #5C1A28;")
        b_lay.addWidget(lbl_pass_sec)
        b_lay.addSpacing(4)
        lbl_hint = QLabel("Kosongkan jika tidak ingin mengubah password")
        lbl_hint.setStyleSheet("font-size: 11px; color: #A89BA0;")
        b_lay.addWidget(lbl_hint)
        b_lay.addSpacing(10)

        b_lay.addWidget(self._lbl("Password Lama"))
        b_lay.addSpacing(5)
        self.inp_pass_lama = self._mk_input("", "••••••••", password=True)
        b_lay.addWidget(self.inp_pass_lama)
        b_lay.addSpacing(10)

        b_lay.addWidget(self._lbl("Password Baru"))
        b_lay.addSpacing(5)
        self.inp_pass_baru = self._mk_input("", "••••••••", password=True)
        b_lay.addWidget(self.inp_pass_baru)
        b_lay.addSpacing(10)

        b_lay.addWidget(self._lbl("Konfirmasi Password Baru"))
        b_lay.addSpacing(5)
        self.inp_pass_confirm = self._mk_input("", "Ulangi password baru", password=True)
        b_lay.addWidget(self.inp_pass_confirm)
        b_lay.addSpacing(10)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #C0392B; font-size: 12px;")
        self.lbl_error.setWordWrap(True)
        b_lay.addWidget(self.lbl_error)
        self.lbl_sukses = QLabel("")
        self.lbl_sukses.setStyleSheet("color: #27AE60; font-size: 12px;")
        b_lay.addWidget(self.lbl_sukses)
        b_lay.addSpacing(20)

        row = QHBoxLayout()
        row.setSpacing(12)

        btn_batal = QPushButton("Batal")
        btn_batal.setFixedHeight(46)
        btn_batal.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_batal.setStyleSheet("""
            QPushButton { background:transparent; color:#5C1A28;
                border:1.5px solid #E2D9CC; border-radius:10px; font-size:14px; }
            QPushButton:hover { background:#F4F0EA; border-color:#5C1A28; }
        """)
        btn_batal.clicked.connect(self.reject)

        btn_simpan = QPushButton("Simpan Perubahan")
        btn_simpan.setFixedHeight(46)
        btn_simpan.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_simpan.setStyleSheet("""
            QPushButton { background:#5C1A28; color:white;
                border:none; border-radius:10px; font-size:14px; font-weight:700; }
            QPushButton:hover { background:#7A2236; }
            QPushButton:pressed { background:#3D0F1A; }
        """)
        btn_simpan.clicked.connect(self._simpan)

        row.addWidget(btn_batal)
        row.addWidget(btn_simpan)
        b_lay.addLayout(row)
        lay.addWidget(body)

    def _lbl(self, teks: str) -> QLabel:
        l = QLabel(teks)
        l.setStyleSheet("font-size: 13px; font-weight: 500; color: #1A0A0E;")
        return l

    def _mk_input(self, value: str = "", placeholder: str = "",
                  password: bool = False) -> QLineEdit:
        inp = QLineEdit()
        inp.setText(value)
        inp.setPlaceholderText(placeholder)
        inp.setFixedHeight(46)
        if password:
            inp.setEchoMode(QLineEdit.EchoMode.Password)

        pr = "44px" if password else "14px"
        inp.setStyleSheet(f"""
            QLineEdit {{
                background:#FAFAF8; border:1.5px solid #E2D9CC;
                border-radius:10px; padding:10px {pr} 10px 14px;
                font-size:13px; color:#1A0A0E;
            }}
            QLineEdit:focus {{ border:2px solid #5C1A28; background:#FFFFFF; }}
            QLineEdit::placeholder {{ color:#A89BA0; }}
        """)

        if password:
            def _mk_pix(svg_str):
                r = QSvgRenderer(QByteArray(svg_str.encode()))
                px = QPixmap(20, 20)
                px.fill(Qt.GlobalColor.transparent)
                pp = QPainter(px)
                r.render(pp)
                pp.end()
                return px

            pix_open = _mk_pix(self._SVG_EYE_OPEN)
            pix_off  = _mk_pix(self._SVG_EYE_OFF)

            btn_eye = QPushButton(inp)
            btn_eye.setFixedSize(32, 32)
            btn_eye.setCheckable(True)
            btn_eye.setStyleSheet("border:none; background:transparent; padding:0;")
            btn_eye.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_eye.setIcon(QIcon(pix_open))
            btn_eye.setIconSize(QSize(20, 20))

            def _toggle(checked, b=btn_eye, f=inp):
                f.setEchoMode(QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password)
                b.setIcon(QIcon(pix_off if checked else pix_open))
            btn_eye.toggled.connect(_toggle)
            inp.setTextMargins(0, 0, 36, 0)

            def _repos(ev=None, b=btn_eye, f=inp):
                b.move(f.width() - 38, (f.height() - 32) // 2)
            inp.resizeEvent = _repos

        return inp

    def _simpan(self):
        self.lbl_error.setText("")
        self.lbl_sukses.setText("")
        display   = self.inp_display.text().strip()
        pass_lama = self.inp_pass_lama.text()
        pass_baru = self.inp_pass_baru.text()
        pass_conf = self.inp_pass_confirm.text()

        if not display:
            self.lbl_error.setText("⚠ Nama tampilan tidak boleh kosong.")
            return

        user_id = self._user.get("id")

        ok, pesan = self._auth.update_profil(
            user_id=user_id,
            display_name=display,
            username=self._user.get("username", display),
        )
        if not ok:
            self.lbl_error.setText(f"❌ {pesan}")
            return

        if pass_baru:
            if not pass_lama:
                self.lbl_error.setText("⚠ Masukkan password lama untuk mengubah password.")
                return
            if len(pass_baru) < 6:
                self.lbl_error.setText("⚠ Password baru minimal 6 karakter.")
                return
            if pass_baru != pass_conf:
                self.lbl_error.setText("⚠ Konfirmasi password tidak cocok.")
                return
            ok2, pesan2 = self._auth.ubah_password(user_id, pass_lama, pass_baru)
            if not ok2:
                self.lbl_error.setText(f"❌ {pesan2}")
                return

        self._updated = {"display_name": display}
        self.lbl_sukses.setText("✅ Profil berhasil diperbarui!")
        QTimer.singleShot(800, self.accept)

    def get_updated_user(self) -> dict:
        return self._updated