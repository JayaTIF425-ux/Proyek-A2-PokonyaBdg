import os
import sys
import hashlib
import re
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QMessageBox,
    QStackedWidget, QWidget, QApplication, QGraphicsOpacityEffect,
    QScrollArea, QSizePolicy, QCheckBox,
)
from PyQt6.QtCore import (
    Qt, pyqtSignal, QSize, QPropertyAnimation,
    QEasingCurve, QTimer, QRect, QPoint, QByteArray
)
from PyQt6.QtGui import (
    QPixmap, QIcon, QFont, QColor, QPainter,
    QPainterPath, QLinearGradient, QBrush, QPen,
    QFontDatabase
)
from PyQt6.QtSvg import QSvgRenderer

from database.auth_manager import AuthManager


# ── Path helper ───────────────────────────────────────────────────────────────

def _asset(nama: str) -> str:
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "assets", "images", nama)


# ── SVG helper (lokal, agar tidak perlu import main_window) ──────────────────

def _svg_pixmap(svg_str: str, size: int, color: str = "#A89BA0") -> QPixmap:
    svg_colored = svg_str.replace("currentColor", color)
    renderer = QSvgRenderer(QByteArray(svg_colored.encode()))
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    renderer.render(painter)
    painter.end()
    return pix


def _svg_icon(svg_str: str, size: int, color: str = "white") -> QIcon:
    return QIcon(_svg_pixmap(svg_str, size, color))


# ── SVG Ikon ─────────────────────────────────────────────────────────────────

# [FIX] Semua ikon kini SVG vektor, menggantikan emoji ✉ 🔒 👁

_SVG_EMAIL = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="2" y="4" width="20" height="16" rx="2"/>
  <polyline points="2,4 12,13 22,4"/>
</svg>"""

_SVG_GEMBOK = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
</svg>"""

_SVG_MATA_TUTUP = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
  <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
  <line x1="1" y1="1" x2="23" y2="23"/>
</svg>"""

_SVG_MATA_BUKA = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
  <circle cx="12" cy="12" r="3"/>
</svg>"""


# ── Konstanta warna ───────────────────────────────────────────────────────────

C = {
    "maroon":       "#5C1A28",
    "maroon_deep":  "#3D0F1A",
    "maroon_light": "#7A2236",
    "gold":         "#8B9B3A",
    "gold_hover":   "#6B7A2A",
    "gold_press":   "#5A6822",
    "white":        "#FFFFFF",
    "bg":           "#F8F6F2",
    "card":         "#FFFFFF",
    "border":       "#E2D9CC",
    "border_focus": "#5C1A28",
    "text_dark":    "#1A0A0E",
    "text_mid":     "#6B5B61",
    "text_light":   "#A89BA0",
    "error":        "#C0392B",
    "success":      "#27AE60",
    "role_bg":      "#F4F0EA",
    "role_sel":     "#5C1A28",
    "role_sel_txt": "#FFFFFF",
    "role_txt":     "#5C1A28",
    "input_bg":     "#FAFAF8",
    "google_bg":    "#FFFFFF",
    "check_accent": "#5C1A28",
}


# ── RoleButton ────────────────────────────────────────────────────────────────

class RoleButton(QFrame):
    clicked = pyqtSignal()

    def __init__(self, label: str, icon_type: str, parent=None):
        super().__init__(parent)
        self._label = label
        self._icon_type = icon_type
        self._checked = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(100)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 10, 8, 10)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_icon = QLabel()
        self.lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_icon.setFixedSize(56, 56)
        self.lbl_icon.setStyleSheet("background: transparent;")
        layout.addWidget(self.lbl_icon)

        self.lbl_text = QLabel(label)
        self.lbl_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_text.setStyleSheet("background: transparent; font-size: 13px; font-weight: 600;")
        layout.addWidget(self.lbl_text)

        self._apply_style(False)

    def _apply_style(self, checked: bool):
        if checked:
            bg     = C["role_sel"]
            fg     = C["role_sel_txt"]
            bord   = C["role_sel"]
            suffix = "aktif"
        else:
            bg     = C["role_bg"]
            fg     = C["role_txt"]
            bord   = C["border"]
            suffix = "normal"

        icon_path = _asset(f"{self._icon_type}_{suffix}.png")
        if os.path.exists(icon_path):
            pix = QPixmap(icon_path).scaled(
                56, 56,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            canvas = QPixmap(56, 56)
            canvas.fill(Qt.GlobalColor.transparent)
            painter = QPainter(canvas)
            x = (56 - pix.width()) // 2
            y = (56 - pix.height()) // 2
            painter.drawPixmap(x, y, pix)
            painter.end()
            self.lbl_icon.setPixmap(canvas)

        self.lbl_text.setStyleSheet(f"background: transparent; color: {fg}; font-size: 13px; font-weight: 600;")
        self.setStyleSheet(f"""
            RoleButton {{
                background: {bg};
                border: 2px solid {bord};
                border-radius: 10px;
            }}
            RoleButton:hover {{
                border-color: {C["maroon"]};
            }}
        """)

    def setChecked(self, checked: bool):
        self._checked = checked
        self._apply_style(checked)

    def isChecked(self) -> bool:
        return self._checked

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


# ── AnimatedStack ─────────────────────────────────────────────────────────────

class AnimatedStack(QStackedWidget):
    """QStackedWidget dengan animasi fade saat ganti halaman."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._animating = False
        self._anim_out = None
        self._anim_in  = None
        self._effect   = None
        self._effect2  = None

    def slide_to(self, index: int):
        if self._animating or index == self.currentIndex():
            return
        self._animating = True

        current_widget = self.currentWidget()

        self._effect = QGraphicsOpacityEffect(current_widget)
        current_widget.setGraphicsEffect(self._effect)

        self._anim_out = QPropertyAnimation(self._effect, b"opacity")
        self._anim_out.setDuration(160)
        self._anim_out.setStartValue(1.0)
        self._anim_out.setEndValue(0.0)
        self._anim_out.setEasingCurve(QEasingCurve.Type.OutCubic)

        def on_out_done():
            current_widget.setGraphicsEffect(None)
            self.setCurrentIndex(index)
            new_widget = self.currentWidget()

            self._effect2 = QGraphicsOpacityEffect(new_widget)
            new_widget.setGraphicsEffect(self._effect2)
            self._effect2.setOpacity(0.0)

            self._anim_in = QPropertyAnimation(self._effect2, b"opacity")
            self._anim_in.setDuration(200)
            self._anim_in.setStartValue(0.0)
            self._anim_in.setEndValue(1.0)
            self._anim_in.setEasingCurve(QEasingCurve.Type.InCubic)

            def on_in_done():
                new_widget.setGraphicsEffect(None)
                self._animating = False

            self._anim_in.finished.connect(on_in_done)
            self._anim_in.start()

        self._anim_out.finished.connect(on_out_done)
        self._anim_out.start()


# ── HalamanLogin ──────────────────────────────────────────────────────────────

class HalamanLogin(QDialog):
    """
    Dialog login fullscreen.

    PERUBAHAN:
    - [BARU] Fitur "Ingat Login" checkbox di form login
    - [BARU] Checkbox Syarat & Ketentuan (SnK) di form daftar
    - [FIX] Semua ikon input field menggunakan SVG vektor (bukan emoji)
    """

    login_berhasil = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth = AuthManager()
        self.auth.init_schema()
        self._current_user: Optional[dict] = None
        self._peran_dipilih = "user"

        # [BARU] Atribut publik untuk dibaca oleh main.py
        self.ingat_login: bool = False

        self.setWindowTitle("PokokNya.Bdg — Masuk")
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint
        )

        icon_path = _asset("app_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setMinimumSize(900, 600)
        self.resize(1280, 720)
        self.showMaximized()

        self.setStyleSheet(f"background: {C['bg']};")
        self._build_ui()

    # ── UI Utama ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._panel_kiri(), 42)
        root.addWidget(self._panel_kanan(), 58)

    # ── Panel Kiri ────────────────────────────────────────────────────────────

    def _panel_kiri(self) -> QFrame:
        panel = QFrame()
        panel.setStyleSheet(f"background: {C['maroon']};")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(60, 0, 60, 60)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addStretch(2)

        logo_path = _asset("logo_app.png")
        lbl_logo = QLabel()
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_logo.setStyleSheet("background: transparent;")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(
                180, 180,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            lbl_logo.setPixmap(pix)
        else:
            # [FIX] Fallback bukan emoji, tapi teks ASCII sederhana
            lbl_logo.setText("🥬")
            lbl_logo.setStyleSheet("font-size: 90px; background: transparent;")

        layout.addWidget(lbl_logo, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(4)

        lbl_nama = QLabel("Pokoknya.Bdg")
        lbl_nama.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_nama.setStyleSheet(f"""
            color: {C["gold"]};
            font-size: 28px;
            font-weight: 800;
            background: transparent;
            letter-spacing: 1px;
        """)
        layout.addWidget(lbl_nama)
        layout.addSpacing(5)

        lbl_tagline = QLabel("Perbandingan Harga\nBahan Pokok Kota Bandung")
        lbl_tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_tagline.setStyleSheet(f"""
            color: rgba(255, 255, 255, 0.65);
            font-size: 14px;
            line-height: 1.7;
            background: transparent;
        """)
        layout.addWidget(lbl_tagline)

        layout.addStretch(3)

        lbl_credit = QLabel("© 2025 POLBAN Informatika")
        lbl_credit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_credit.setStyleSheet(f"""
            color: rgba(255, 255, 255, 0.30);
            font-size: 11px;
            background: transparent;
        """)
        layout.addWidget(lbl_credit)

        return panel

    # ── Panel Kanan ───────────────────────────────────────────────────────────

    def _panel_kanan(self) -> QWidget:
        panel = QWidget()
        panel.setStyleSheet("background: #FFFFFF;")

        outer = QVBoxLayout(panel)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setObjectName("LoginCard")
        card.setStyleSheet(f"""
            #LoginCard {{
                background: {C["card"]};
                border-radius: 20px;
                border: 1px solid {C["border"]};
            }}
        """)
        card.setMinimumWidth(460)
        card.setMaximumWidth(520)
        card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(44, 40, 44, 44)
        card_layout.setSpacing(0)

        # Buat form daftar DULU agar atribut sudah ada saat form login dipakai
        form_daftar = self._form_daftar()
        form_login  = self._form_login()

        self.stack = AnimatedStack()
        self.stack.addWidget(form_login)
        self.stack.addWidget(form_daftar)
        card_layout.addWidget(self.stack)

        outer.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        return panel

    # ── Form Login ────────────────────────────────────────────────────────────

    def _form_login(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        lbl_judul = QLabel("Selamat Datang")
        lbl_judul.setStyleSheet(f"""
            color: {C["text_dark"]};
            font-size: 24px; font-weight: 700;
            background: transparent;
        """)
        layout.addWidget(lbl_judul)

        lbl_sub = QLabel("Masuk untuk melanjutkan ke akun Anda")
        lbl_sub.setStyleSheet(f"""
            color: {C["text_light"]};
            font-size: 13px; background: transparent;
        """)
        layout.addWidget(lbl_sub)
        layout.addSpacing(24)

        # [FIX] Email dengan ikon SVG vektor (bukan emoji ✉)
        layout.addWidget(self._label_field("Alamat Email"))
        layout.addSpacing(6)
        self.inp_email_login = self._input_field(
            "you@example.com", icon_svg=_SVG_EMAIL, icon_color="#A89BA0"
        )
        self.inp_email_login.returnPressed.connect(self._aksi_login)
        layout.addWidget(self.inp_email_login)
        layout.addSpacing(14)

        # [FIX] Password dengan ikon gembok SVG vektor (bukan emoji 🔒)
        layout.addWidget(self._label_field("Kata Sandi"))
        layout.addSpacing(6)
        self.inp_pass_login = self._input_field(
            "Masukkan kata sandi",
            icon_svg=_SVG_GEMBOK, icon_color="#A89BA0",
            password=True
        )
        self.inp_pass_login.returnPressed.connect(self._aksi_login)
        layout.addWidget(self.inp_pass_login)
        layout.addSpacing(20)

        # Pilih kategori
        layout.addWidget(self._label_field("Pilih kategori akun anda"))
        layout.addSpacing(8)
        role_row = QHBoxLayout()
        role_row.setSpacing(12)
        self.btn_admin_login = RoleButton("Admin", "admin")
        self.btn_user_login  = RoleButton("User",  "user")
        self.btn_user_login.setChecked(True)
        self.btn_admin_login.clicked.connect(lambda: self._pilih_peran("admin", "login"))
        self.btn_user_login.clicked.connect(lambda: self._pilih_peran("user",  "login"))
        role_row.addWidget(self.btn_admin_login)
        role_row.addWidget(self.btn_user_login)
        layout.addLayout(role_row)
        layout.addSpacing(14)

        # [BARU] Checkbox "Ingat Login"
        self.chk_ingat = QCheckBox("Ingat Login (tetap masuk)")
        self.chk_ingat.setStyleSheet(f"""
            QCheckBox {{
                color: {C["text_mid"]};
                font-size: 12px;
                spacing: 8px;
                background: transparent;
            }}
            QCheckBox::indicator {{
                width: 16px; height: 16px;
                border: 2px solid {C["border"]};
                border-radius: 4px;
                background: {C["input_bg"]};
            }}
            QCheckBox::indicator:checked {{
                background: {C["check_accent"]};
                border-color: {C["check_accent"]};
            }}
        """)
        layout.addWidget(self.chk_ingat)
        layout.addSpacing(8)

        # Error label
        self.lbl_login_error = QLabel("")
        self.lbl_login_error.setStyleSheet(f"color: {C['error']}; font-size: 12px; background: transparent;")
        self.lbl_login_error.setWordWrap(True)
        layout.addWidget(self.lbl_login_error)
        layout.addSpacing(12)

        btn_masuk = self._btn_utama("Masuk")
        btn_masuk.clicked.connect(self._aksi_login)
        layout.addWidget(btn_masuk)
        layout.addSpacing(12)

        btn_daftar = self._btn_sekunder("Buat Akun Baru")
        btn_daftar.clicked.connect(lambda: self.stack.slide_to(1))
        btn_daftar.clicked.connect(lambda: self._pilih_peran("user", "daftar"))
        layout.addWidget(btn_daftar)
        layout.addSpacing(16)

        layout.addStretch()
        return w

    # ── Form Daftar ───────────────────────────────────────────────────────────

    def _form_daftar(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        lbl_judul = QLabel("Buat akun kamu")
        lbl_judul.setStyleSheet(f"""
            color: {C["gold"]};
            font-size: 24px; font-weight: 700;
            background: transparent;
        """)
        layout.addWidget(lbl_judul)

        lbl_sub = QLabel("Mulai jelajahi harga pangan bersama kami")
        lbl_sub.setStyleSheet(f"""
            color: {C["text_light"]};
            font-size: 13px; background: transparent;
        """)
        layout.addWidget(lbl_sub)
        layout.addSpacing(22)

        # [FIX] Email SVG vektor
        layout.addWidget(self._label_field("Alamat Email"))
        layout.addSpacing(6)
        self.inp_email_daftar = self._input_field(
            "you@example.com", icon_svg=_SVG_EMAIL, icon_color="#A89BA0"
        )
        layout.addWidget(self.inp_email_daftar)
        layout.addSpacing(14)

        # [FIX] Password SVG vektor
        layout.addWidget(self._label_field("Kata Sandi"))
        layout.addSpacing(6)
        self.inp_pass_daftar = self._input_field(
            "Masukkan kata sandi",
            icon_svg=_SVG_GEMBOK, icon_color="#A89BA0",
            password=True
        )
        self.inp_pass_daftar.returnPressed.connect(self._aksi_daftar)
        layout.addWidget(self.inp_pass_daftar)
        layout.addSpacing(20)

        # Pilih kategori
        layout.addWidget(self._label_field("Pilih kategori akun anda"))
        layout.addSpacing(8)
        role_row2 = QHBoxLayout()
        role_row2.setSpacing(12)
        self.btn_admin_daftar = RoleButton("Admin", "admin")
        self.btn_user_daftar  = RoleButton("User",  "user")
        self.btn_user_daftar.setChecked(True)
        self.btn_admin_daftar.clicked.connect(lambda: self._pilih_peran("admin", "daftar"))
        self.btn_user_daftar.clicked.connect(lambda: self._pilih_peran("user",  "daftar"))
        role_row2.addWidget(self.btn_admin_daftar)
        role_row2.addWidget(self.btn_user_daftar)
        layout.addLayout(role_row2)
        layout.addSpacing(14)

        # [BARU] Checkbox Syarat & Ketentuan
        self.chk_snk = QCheckBox("Saya menyetujui Syarat & Ketentuan penggunaan")
        self.chk_snk.setStyleSheet(f"""
            QCheckBox {{
                color: {C["text_mid"]};
                font-size: 12px;
                spacing: 8px;
                background: transparent;
            }}
            QCheckBox::indicator {{
                width: 16px; height: 16px;
                border: 2px solid {C["border"]};
                border-radius: 4px;
                background: {C["input_bg"]};
            }}
            QCheckBox::indicator:checked {{
                background: {C["check_accent"]};
                border-color: {C["check_accent"]};
            }}
        """)
        layout.addWidget(self.chk_snk)
        layout.addSpacing(10)

        self.lbl_daftar_error  = QLabel("")
        self.lbl_daftar_sukses = QLabel("")
        self.lbl_daftar_error.setStyleSheet(f"color: {C['error']}; font-size: 12px; background: transparent;")
        self.lbl_daftar_sukses.setStyleSheet(f"color: {C['success']}; font-size: 12px; background: transparent;")
        self.lbl_daftar_error.setWordWrap(True)
        self.lbl_daftar_sukses.setWordWrap(True)
        layout.addWidget(self.lbl_daftar_error)
        layout.addWidget(self.lbl_daftar_sukses)
        layout.addSpacing(12)

        btn_buat = self._btn_utama("Buat Akun")
        btn_buat.clicked.connect(self._aksi_daftar)
        layout.addWidget(btn_buat)
        layout.addSpacing(12)

        btn_kembali = self._btn_sekunder("Sudah punya akun? Masuk")
        btn_kembali.clicked.connect(lambda: self.stack.slide_to(0))
        btn_kembali.clicked.connect(lambda: self._pilih_peran("user", "login"))
        layout.addWidget(btn_kembali)
        layout.addSpacing(16)

        layout.addStretch()
        return w

    # ── Aksi ──────────────────────────────────────────────────────────────────

    def _pilih_peran(self, peran: str, form: str):
        if isinstance(peran, bool):
            return
        self._peran_dipilih = peran
        if form == "login":
            self.btn_admin_login.setChecked(peran == "admin")
            self.btn_user_login.setChecked(peran == "user")
        else:
            self.btn_admin_daftar.setChecked(peran == "admin")
            self.btn_user_daftar.setChecked(peran == "user")

    def _aksi_login(self):
        email    = self.inp_email_login.text().strip()
        password = self.inp_pass_login.text()
        self.lbl_login_error.setText("")

        if not email or not password:
            self.lbl_login_error.setText("⚠ Email dan kata sandi tidak boleh kosong.")
            return

        pola_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pola_email, email):
            self.lbl_login_error.setText("❌ Format email tidak valid.")
            return

        username = email.split("@")[0].replace(".", "_") if "@" in email else email
        user = self.auth.login(username, password)
        if user:
            if user["role"] != self._peran_dipilih:
                role_seharusnya = "Admin" if user["role"] == "admin" else "User"
                self.lbl_login_error.setText(
                    f"❌ Akun ini terdaftar sebagai {role_seharusnya}. "
                    f"Pilih '{role_seharusnya}' untuk masuk."
                )
                return
            # [BARU] Simpan status ingat login
            self.ingat_login = self.chk_ingat.isChecked()
            self._masuk(user)
        else:
            self.lbl_login_error.setText("❌ Email atau kata sandi salah.")

    def _aksi_daftar(self):
        email    = self.inp_email_daftar.text().strip()
        password = self.inp_pass_daftar.text()
        self.lbl_daftar_error.setText("")
        self.lbl_daftar_sukses.setText("")

        if not email or not password:
            self.lbl_daftar_error.setText("⚠ Email dan kata sandi tidak boleh kosong.")
            return

        pola_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pola_email, email):
            self.lbl_daftar_error.setText("⚠ Format email tidak valid.")
            return

        # [BARU] Validasi SnK harus dicentang
        if not self.chk_snk.isChecked():
            self.lbl_daftar_error.setText("⚠ Anda harus menyetujui Syarat & Ketentuan untuk mendaftar.")
            return

        username = email.split("@")[0].replace(".", "_")
        berhasil, pesan = self.auth.register(
            username=username,
            password=password,
            email=email,
            display_name=username,
            role=self._peran_dipilih
        )
        if berhasil:
            self.lbl_daftar_sukses.setText(
                f"✅ Akun berhasil dibuat sebagai {self._peran_dipilih}! Silakan masuk."
            )
            def _ke_login():
                self.inp_email_login.setText(email)
                self.inp_pass_login.clear()
                self._pilih_peran(self._peran_dipilih, "login")
                self.stack.slide_to(0)
            QTimer.singleShot(1200, _ke_login)
        else:
            self.lbl_daftar_error.setText(f"❌ {pesan}")

    def _masuk(self, user: dict):
        self._current_user = user
        self.login_berhasil.emit(user)
        self.accept()

    # ── Widget Helpers ────────────────────────────────────────────────────────

    def _label_field(self, teks: str) -> QLabel:
        lbl = QLabel(teks)
        lbl.setStyleSheet(f"""
            color: {C["text_dark"]};
            font-size: 13px; font-weight: 500;
            background: transparent;
        """)
        return lbl

    def _input_field(
        self,
        placeholder: str,
        icon_svg: str = "",
        icon_color: str = "#A89BA0",
        password: bool = False,
    ) -> QLineEdit:
        """
        [FIX] Input field dengan ikon SVG vektor (bukan emoji).
        icon_svg: string SVG lengkap dengan currentColor sebagai placeholder warna.
        """
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setFixedHeight(48)
        if password:
            inp.setEchoMode(QLineEdit.EchoMode.Password)

        padding_left  = "40px" if icon_svg else "14px"
        padding_right = "44px" if password else "14px"

        inp.setStyleSheet(f"""
            QLineEdit {{
                background: {C["input_bg"]};
                border: 1.5px solid {C["border"]};
                border-radius: 10px;
                padding: 10px {padding_right} 10px {padding_left};
                font-size: 13px;
                color: {C["text_dark"]};
            }}
            QLineEdit:focus {{
                border: 2px solid {C["border_focus"]};
                background: {C["white"]};
            }}
            QLineEdit::placeholder {{
                color: {C["text_light"]};
            }}
        """)

        # [FIX] Ikon kiri — SVG vektor bukan emoji label
        if icon_svg:
            lbl_icon = QLabel(inp)
            lbl_icon.setFixedSize(20, 20)
            lbl_icon.setStyleSheet("background: transparent; border: none;")
            lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_icon.setPixmap(_svg_pixmap(icon_svg, 16, icon_color))
            lbl_icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            lbl_icon.move(12, 14)

        # [FIX] Toggle mata — SVG vektor bukan emoji 👁
        if password:
            btn_eye = QPushButton(inp)
            btn_eye.setFixedSize(32, 32)
            btn_eye.setStyleSheet("border: none; background: transparent; padding: 0;")
            btn_eye.setCheckable(True)
            btn_eye.setCursor(Qt.CursorShape.PointingHandCursor)

            btn_eye.setIcon(_svg_icon(_SVG_MATA_TUTUP, 18, "#A89BA0"))
            btn_eye.setIconSize(QSize(18, 18))

            def _toggle(checked, field=inp, b=btn_eye):
                if checked:
                    field.setEchoMode(QLineEdit.EchoMode.Normal)
                    b.setIcon(_svg_icon(_SVG_MATA_BUKA, 18, C["maroon"]))
                else:
                    field.setEchoMode(QLineEdit.EchoMode.Password)
                    b.setIcon(_svg_icon(_SVG_MATA_TUTUP, 18, "#A89BA0"))

            btn_eye.toggled.connect(_toggle)

            def _reposition_eye(event=None, b=btn_eye, f=inp):
                b.move(f.width() - 38, (f.height() - 32) // 2)

            inp.resizeEvent = _reposition_eye

        return inp

    def _btn_utama(self, teks: str) -> QPushButton:
        btn = QPushButton(teks)
        btn.setFixedHeight(50)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {C["gold"]};
                color: {C["white"]};
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{ background: {C["gold_hover"]}; }}
            QPushButton:pressed {{ background: {C["gold_press"]}; }}
        """)
        return btn

    def _btn_sekunder(self, teks: str) -> QPushButton:
        btn = QPushButton(teks)
        btn.setFixedHeight(48)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {C["text_dark"]};
                border: 1.5px solid {C["border"]};
                border-radius: 10px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {C["role_bg"]};
                border-color: {C["maroon"]};
                color: {C["maroon"]};
            }}
            QPushButton:pressed {{ background: #E8E0D4; }}
        """)
        return btn

    # ── Public ────────────────────────────────────────────────────────────────

    def get_user(self) -> Optional[dict]:
        return self._current_user