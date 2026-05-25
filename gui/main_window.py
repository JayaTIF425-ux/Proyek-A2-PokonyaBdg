"""
gui/main_window.py — Jendela utama aplikasi dengan sidebar navigasi + collapsible.
Versi ini mendukung role user/admin: menu Admin hanya muncul untuk admin.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QLabel, QPushButton, QStackedWidget, QSizePolicy,
    QDialog, QLineEdit, QGridLayout,
)
from PyQt6.QtCore import Qt, QByteArray, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QPainter

from gui.pages.halaman_beranda import HalamanBeranda
from gui.pages.halaman_pencarian import HalamanPencarian
from gui.pages.halaman_penghitung import HalamanPenghitung
from gui.pages.halaman_tutorial import HalamanTutorial
from gui.pages.halaman_tentang import HalamanTentang
from gui.pages.halaman_admin import HalamanAdmin


# SVG icon helper 

def _svg_to_icon(svg_str: str, size: int = 20) -> QIcon:
    """Render SVG string menjadi QIcon berukuran size×size px."""
    renderer = QSvgRenderer(QByteArray(svg_str.encode()))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


# Definisi SVG ikon sidebar 

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
        # current_user: {"id": int, "username": str, "role": "admin"|"user"}
        self.current_user = current_user or {"id": 0, "username": "guest", "role": "user"}
        self.is_admin = self.current_user.get("role") == "admin"

        self.setWindowTitle("PokokNya.Bdg — Harga Bahan Pokok Bandung")
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
        brand_row.setContentsMargins(20, 24, 8, 0)

        self.lbl_brand = QLabel("PokokNya")
        self.lbl_brand.setStyleSheet(
            f"color: {self.WARNA_AKSEN}; font-size: 22px; font-weight: bold;"
        )

        self.btn_collapse = QPushButton("◀")
        self.btn_collapse.setFixedSize(28, 28)
        self.btn_collapse.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_collapse.setToolTip("Sembunyikan sidebar")
        self.btn_collapse.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.WARNA_AKTIF};
                color: {self.WARNA_AKSEN};
                border: none;
                border-radius: 14px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #8B1E30; }}
        """)
        self.btn_collapse.clicked.connect(self._toggle_sidebar)

        brand_row.addWidget(self.lbl_brand)
        brand_row.addStretch()
        brand_row.addWidget(self.btn_collapse)
        layout.addLayout(brand_row)

        self.lbl_sub = QLabel(".Bdg")
        self.lbl_sub.setStyleSheet(
            f"color: {self.WARNA_TEKS}; font-size: 13px; padding: 0 20px 10px 20px;"
        )
        layout.addWidget(self.lbl_sub)

        # Info user yang login 
        username = self.current_user.get("username", "guest")
        role     = self.current_user.get("role", "user")
        badge    = "🔑 Admin" if role == "admin" else "👤 User"

        self.lbl_user_info = QLabel(f"{badge}\n{username}")
        self.lbl_user_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_user_info.setStyleSheet(f"""
            color: {self.WARNA_AKSEN};
            font-size: 11px;
            background: rgba(255,255,255,0.08);
            border-radius: 6px;
            padding: 6px 10px;
            margin: 0 12px 8px 12px;
        """)
        layout.addWidget(self.lbl_user_info)

        # Tombol Edit Profil
        self.btn_edit_profil = QPushButton("✏ Edit Profil")
        self.btn_edit_profil.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit_profil.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: rgba(255,255,255,0.65);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 6px;
                font-size: 11px;
                padding: 4px 10px;
                margin: 0 12px 8px 12px;
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

    # Collapsible sidebar 

    def _toggle_sidebar(self):
        self._sidebar_expanded = not self._sidebar_expanded
        _teks_menu = ["Beranda", "Pencarian", "Penghitung Belanja",
                      "Tutorial", "Tentang Kami"]
        if self.is_admin:
            _teks_menu.append("Panel Admin")

        if self._sidebar_expanded:
            self.sidebar.setFixedWidth(self.LEBAR_EXPANDED)
            self.lbl_brand.setVisible(True)
            self.lbl_sub.setVisible(True)
            self.lbl_user_info.setVisible(True)
            self.btn_edit_profil.setVisible(True)
            self.btn_collapse.setText("◀")
            self.btn_collapse.setToolTip("Sembunyikan sidebar")
            for btn, teks in zip(self.menu_buttons, _teks_menu):
                btn.setText(teks)
            self.btn_logout.setText("Keluar")
        else:
            self.sidebar.setFixedWidth(self.LEBAR_COLLAPSED)
            self.lbl_brand.setVisible(False)
            self.lbl_sub.setVisible(False)
            self.lbl_user_info.setVisible(False)
            self.btn_edit_profil.setVisible(False)
            self.btn_collapse.setText("▶")
            self.btn_collapse.setToolTip("Tampilkan sidebar")
            for btn, tip in zip(self.menu_buttons, _teks_menu):
                btn.setToolTip(tip)
                btn.setText("")
            self.btn_logout.setText("")
            self.btn_logout.setToolTip("Keluar")

    # Navigasi dari beranda ke pencarian 

    def navigasi_ke_pencarian(self, keyword: str):
        if "telur" in keyword.lower():
            keyword_final = "Telur"
        elif "ayam" in keyword.lower():
            keyword_final = "Daging Ayam"
        else:
            keyword_final = keyword

        self.halaman_pencarian.set_keyword_dan_cari(keyword_final)
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
            username = self.current_user.get("username", "guest")
            role     = self.current_user.get("role", "user")
            display  = self.current_user.get("display_name") or username
            badge    = "🔑 Admin" if role == "admin" else "👤 User"
            self.lbl_user_info.setText(f"{badge}\n{display}")

# ══════════════════════════════════════════════════════════════════════════════
# Dialog Konfirmasi Logout — desain custom
# ══════════════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════════════
# Dialog Konfirmasi Logout — custom, tanpa QMessageBox
# ══════════════════════════════════════════════════════════════════════════════



class _DialogLogout(QDialog):
    """Pop-up konfirmasi logout yang rapi dengan dua tombol bergaya."""

    def __init__(self, username: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Konfirmasi Logout")
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(380)

        # Card utama
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

        # Ikon
        ikon = QLabel("🚪")
        ikon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ikon.setStyleSheet("font-size: 40px; background: transparent;")
        lay.addWidget(ikon)
        lay.addSpacing(12)

        # Judul
        judul = QLabel("Keluar dari Akun?")
        judul.setAlignment(Qt.AlignmentFlag.AlignCenter)
        judul.setStyleSheet(
            "font-size: 18px; font-weight: 700; color: #1A0A0E; background: transparent;"
        )
        lay.addWidget(judul)
        lay.addSpacing(8)

        # Sub-teks
        sub = QLabel(f'Yakin ingin keluar dari akun <b>{username}</b>?')
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setTextFormat(Qt.TextFormat.RichText)
        sub.setWordWrap(True)
        sub.setStyleSheet(
            "font-size: 13px; color: #6B5B61; background: transparent;"
        )
        lay.addWidget(sub)
        lay.addSpacing(24)

        # Tombol
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


# ══════════════════════════════════════════════════════════════════════════════
# Dialog Edit Profil
# ══════════════════════════════════════════════════════════════════════════════

class _DialogEditProfil(QDialog):
    """Dialog untuk mengubah display name dan password."""

    def __init__(self, user: dict, auth_manager, parent=None):
        super().__init__(parent)
        self._user = user
        self._auth = auth_manager
        self._updated: dict = {}

        self.setWindowTitle("Edit Profil")
        self.setFixedWidth(400)
        self.setStyleSheet("background: #FFFFFF;")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(0)

        # Judul
        judul = QLabel("Edit Profil")
        judul.setStyleSheet(
            "font-size: 20px; font-weight: 700; color: #44101A;"
        )
        lay.addWidget(judul)
        lay.addSpacing(4)

        sub = QLabel(f"Akun: {user.get('username', '')}")
        sub.setStyleSheet("font-size: 12px; color: #A89BA0;")
        lay.addWidget(sub)
        lay.addSpacing(20)

        # Display name
        lay.addWidget(self._lbl("Nama Tampilan"))
        lay.addSpacing(6)
        self.inp_display = QLineEdit()
        self.inp_display.setText(user.get("display_name") or user.get("username", ""))
        self.inp_display.setPlaceholderText("Nama yang ditampilkan")
        self._style_input(self.inp_display)
        lay.addWidget(self.inp_display)
        lay.addSpacing(16)

        # Password baru
        lay.addWidget(self._lbl("Password Baru (kosongkan jika tidak diubah)"))
        lay.addSpacing(6)
        self.inp_pass = QLineEdit()
        self.inp_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_pass.setPlaceholderText("••••••••")
        self._style_input(self.inp_pass)
        lay.addWidget(self.inp_pass)
        lay.addSpacing(8)

        self.inp_pass_confirm = QLineEdit()
        self.inp_pass_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_pass_confirm.setPlaceholderText("Konfirmasi password baru")
        self._style_input(self.inp_pass_confirm)
        lay.addWidget(self.inp_pass_confirm)
        lay.addSpacing(8)

        # Pesan error
        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #C0392B; font-size: 12px;")
        self.lbl_error.setWordWrap(True)
        lay.addWidget(self.lbl_error)
        lay.addSpacing(16)

        # Tombol
        row = QHBoxLayout()
        row.setSpacing(12)

        btn_batal = QPushButton("Batal")
        btn_batal.setFixedHeight(44)
        btn_batal.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_batal.setStyleSheet("""
            QPushButton {
                background: transparent; color: #44101A;
                border: 1.5px solid #E2D9CC; border-radius: 10px;
                font-size: 14px;
            }
            QPushButton:hover { background: #F4F0EA; }
        """)
        btn_batal.clicked.connect(self.reject)

        btn_simpan = QPushButton("Simpan")
        btn_simpan.setFixedHeight(44)
        btn_simpan.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_simpan.setStyleSheet("""
            QPushButton {
                background: #44101A; color: white;
                border: none; border-radius: 10px;
                font-size: 14px; font-weight: 700;
            }
            QPushButton:hover { background: #6B1525; }
        """)
        btn_simpan.clicked.connect(self._simpan)

        row.addWidget(btn_batal)
        row.addWidget(btn_simpan)
        lay.addLayout(row)

    def _lbl(self, teks: str) -> QLabel:
        l = QLabel(teks)
        l.setStyleSheet("font-size: 13px; font-weight: 500; color: #1A0A0E;")
        return l

    def _style_input(self, w: QLineEdit):
        w.setFixedHeight(44)
        w.setStyleSheet("""
            QLineEdit {
                background: #FAFAF8; border: 1.5px solid #E2D9CC;
                border-radius: 10px; padding: 10px 14px;
                font-size: 13px; color: #1A0A0E;
            }
            QLineEdit:focus { border: 2px solid #44101A; background: #FFFFFF; }
        """)

    def _simpan(self):
        self.lbl_error.setText("")
        display = self.inp_display.text().strip()
        new_pass = self.inp_pass.text()
        confirm  = self.inp_pass_confirm.text()

        if not display:
            self.lbl_error.setText("⚠ Nama tampilan tidak boleh kosong.")
            return

        if new_pass:
            if len(new_pass) < 6:
                self.lbl_error.setText("⚠ Password minimal 6 karakter.")
                return
            if new_pass != confirm:
                self.lbl_error.setText("⚠ Konfirmasi password tidak cocok.")
                return

        # Simpan ke DB jika auth_manager punya method update_profile
        try:
            if hasattr(self._auth, "update_profile"):
                self._auth.update_profile(
                    user_id=self._user.get("id"),
                    display_name=display,
                    new_password=new_pass if new_pass else None,
                )
        except Exception:
            pass  # Jika method belum ada, skip saja

        self._updated = {"display_name": display}
        self.accept()

    def get_updated_user(self) -> dict:
        return self._updated
