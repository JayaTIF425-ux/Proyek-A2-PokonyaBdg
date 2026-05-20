"""
gui/halaman_login.py — Dialog login + registrasi untuk PokokNya.Bdg.
Fitur: logo, fullscreen, register, login Google (simulasi), tanpa info akun default.
"""

import os
import sys
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QMessageBox,
    QStackedWidget, QWidget, QCheckBox, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QIcon, QFont

from database.auth_manager import AuthManager

# ── Path helper ───────────────────────────────────────────────────────────────

def _asset(nama: str) -> str:
    """Cari file asset (logo dll) di folder assets/ relatif ke root project."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "assets", nama)


# ══════════════════════════════════════════════════════════════════════════════
class HalamanLogin(QDialog):
    """
    Dialog login fullscreen dengan tab Login & Daftar.
    Emit sinyal login_berhasil(dict_user) jika sukses.
    """

    login_berhasil = pyqtSignal(dict)

    BG          = "#FDFAF6"
    PRIMARY     = "#44101A"
    PRIMARY_HVR = "#6B1525"
    AKSEN       = "#F1C40F"
    BORDER      = "#D4C5A9"
    CARD_BG     = "#FFFFFF"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth = AuthManager()
        self.auth.init_schema()
        self._current_user: Optional[dict] = None

        self.setWindowTitle("PokokNya.Bdg")
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint
        )

        # ── Icon window & taskbar ─────────────────────────────────────────
        icon_path = _asset("app_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # ── Fullscreen ────────────────────────────────────────────────────
        screen = QApplication.primaryScreen().availableGeometry()
        self.resize(screen.width(), screen.height())
        self.showMaximized()

        self.setStyleSheet(f"background-color: {self.BG};")
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Panel kiri: ilustrasi / branding ─────────────────────────────
        panel_kiri = QFrame()
        panel_kiri.setStyleSheet(f"background-color: {self.PRIMARY};")
        panel_kiri.setFixedWidth(480)
        kiri_layout = QVBoxLayout(panel_kiri)
        kiri_layout.setContentsMargins(48, 60, 48, 60)
        kiri_layout.setSpacing(24)
        kiri_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo
        logo_path = _asset("logo_app.png")
        lbl_logo = QLabel()
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(
                220, 220,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            lbl_logo.setPixmap(pix)
        else:
            lbl_logo.setText("🛒")
            lbl_logo.setStyleSheet("font-size: 80px;")
        kiri_layout.addWidget(lbl_logo)

        lbl_nama = QLabel("PokokNya.Bdg")
        lbl_nama.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_nama.setStyleSheet(
            f"color: {self.AKSEN}; font-size: 32px; font-weight: bold;"
        )
        kiri_layout.addWidget(lbl_nama)

        lbl_tagline = QLabel("Perbandingan Harga\nBahan Pokok Kota Bandung")
        lbl_tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_tagline.setStyleSheet("color: rgba(255,255,255,0.75); font-size: 15px; line-height: 1.6;")
        kiri_layout.addWidget(lbl_tagline)

        kiri_layout.addStretch()

        lbl_credit = QLabel("© 2025 POLBAN Informatika")
        lbl_credit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_credit.setStyleSheet("color: rgba(255,255,255,0.35); font-size: 11px;")
        kiri_layout.addWidget(lbl_credit)

        root.addWidget(panel_kiri)

        # ── Panel kanan: form login/daftar ────────────────────────────────
        panel_kanan = QWidget()
        panel_kanan.setStyleSheet(f"background-color: {self.BG};")
        kanan_layout = QVBoxLayout(panel_kanan)
        kanan_layout.setContentsMargins(80, 60, 80, 60)
        kanan_layout.setSpacing(0)
        kanan_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Tab selector
        tab_row = QHBoxLayout()
        tab_row.setSpacing(0)

        self.btn_tab_login = QPushButton("Masuk")
        self.btn_tab_daftar = QPushButton("Daftar")
        for btn in [self.btn_tab_login, self.btn_tab_daftar]:
            btn.setFixedHeight(44)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_tab_login.setChecked(True)
        self._update_tab_style()

        self.btn_tab_login.clicked.connect(lambda: self._ganti_tab(0))
        self.btn_tab_daftar.clicked.connect(lambda: self._ganti_tab(1))

        tab_row.addWidget(self.btn_tab_login)
        tab_row.addWidget(self.btn_tab_daftar)
        kanan_layout.addLayout(tab_row)
        kanan_layout.addSpacing(32)

        # Stacked: halaman login & daftar
        self.stack = QStackedWidget()
        self.stack.addWidget(self._buat_form_login())
        self.stack.addWidget(self._buat_form_daftar())
        kanan_layout.addWidget(self.stack)

        root.addWidget(panel_kanan, 1)

    # ── Form Login ────────────────────────────────────────────────────────────

    def _buat_form_login(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        lbl = QLabel("Selamat Datang Kembali 👋")
        lbl.setStyleSheet(f"color: {self.PRIMARY}; font-size: 22px; font-weight: bold;")
        layout.addWidget(lbl)

        lbl_sub = QLabel("Masuk untuk melanjutkan ke PokokNya.Bdg")
        lbl_sub.setStyleSheet("color: #888; font-size: 13px;")
        layout.addWidget(lbl_sub)
        layout.addSpacing(8)

        # Username
        layout.addWidget(self._lbl_field("Username"))
        self.inp_login_user = self._input("Masukkan username")
        layout.addWidget(self.inp_login_user)

        # Password
        layout.addWidget(self._lbl_field("Password"))
        pass_row = QHBoxLayout()
        pass_row.setSpacing(8)
        self.inp_login_pass = self._input("Masukkan password", password=True)
        self.inp_login_pass.returnPressed.connect(self._coba_login)
        self.btn_show_pass = self._btn_mata()
        self.btn_show_pass.clicked.connect(
            lambda: self._toggle_password(self.inp_login_pass, self.btn_show_pass)
        )
        pass_row.addWidget(self.inp_login_pass, 1)
        pass_row.addWidget(self.btn_show_pass)
        layout.addLayout(pass_row)

        # Error label
        self.lbl_login_error = QLabel("")
        self.lbl_login_error.setStyleSheet("color: #c0392b; font-size: 12px;")
        layout.addWidget(self.lbl_login_error)

        # Tombol Masuk
        btn_masuk = QPushButton("Masuk")
        btn_masuk.setFixedHeight(46)
        btn_masuk.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_masuk.setStyleSheet(self._style_btn_primary())
        btn_masuk.clicked.connect(self._coba_login)
        layout.addWidget(btn_masuk)

        # Divider
        layout.addWidget(self._divider("atau"))

        # Tombol Google
        btn_google = self._btn_google("Masuk dengan Google")
        btn_google.clicked.connect(self._login_google)
        layout.addWidget(btn_google)

        layout.addStretch()
        return w

    # ── Form Daftar ───────────────────────────────────────────────────────────

    def _buat_form_daftar(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        lbl = QLabel("Buat Akun Baru")
        lbl.setStyleSheet(f"color: {self.PRIMARY}; font-size: 22px; font-weight: bold;")
        layout.addWidget(lbl)

        lbl_sub = QLabel("Daftar untuk mulai menggunakan PokokNya.Bdg")
        lbl_sub.setStyleSheet("color: #888; font-size: 13px;")
        layout.addWidget(lbl_sub)
        layout.addSpacing(4)

        # Display name
        layout.addWidget(self._lbl_field("Nama Lengkap"))
        self.inp_reg_nama = self._input("Masukkan nama lengkap")
        layout.addWidget(self.inp_reg_nama)

        # Username
        layout.addWidget(self._lbl_field("Username"))
        self.inp_reg_user = self._input("Minimal 3 karakter")
        layout.addWidget(self.inp_reg_user)

        # Email (opsional)
        layout.addWidget(self._lbl_field("Email (opsional)"))
        self.inp_reg_email = self._input("contoh@email.com")
        layout.addWidget(self.inp_reg_email)

        # Password
        layout.addWidget(self._lbl_field("Password"))
        pass_row = QHBoxLayout()
        pass_row.setSpacing(8)
        self.inp_reg_pass = self._input("Minimal 6 karakter", password=True)
        self.btn_show_reg = self._btn_mata()
        self.btn_show_reg.clicked.connect(
            lambda: self._toggle_password(self.inp_reg_pass, self.btn_show_reg)
        )
        pass_row.addWidget(self.inp_reg_pass, 1)
        pass_row.addWidget(self.btn_show_reg)
        layout.addLayout(pass_row)

        # Error label
        self.lbl_reg_error = QLabel("")
        self.lbl_reg_error.setStyleSheet("color: #c0392b; font-size: 12px;")
        self.lbl_reg_sukses = QLabel("")
        self.lbl_reg_sukses.setStyleSheet("color: #27ae60; font-size: 12px;")
        layout.addWidget(self.lbl_reg_error)
        layout.addWidget(self.lbl_reg_sukses)

        # Tombol Daftar
        btn_daftar = QPushButton("Buat Akun")
        btn_daftar.setFixedHeight(46)
        btn_daftar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_daftar.setStyleSheet(self._style_btn_primary())
        btn_daftar.clicked.connect(self._coba_register)
        layout.addWidget(btn_daftar)

        # Divider
        layout.addWidget(self._divider("atau"))

        # Tombol Google
        btn_google = self._btn_google("Daftar dengan Google")
        btn_google.clicked.connect(self._login_google)
        layout.addWidget(btn_google)

        layout.addStretch()
        return w

    # ── Aksi Login ────────────────────────────────────────────────────────────

    def _coba_login(self):
        username = self.inp_login_user.text().strip()
        password = self.inp_login_pass.text()

        self.lbl_login_error.setText("")

        if not username or not password:
            self.lbl_login_error.setText("⚠ Username dan password tidak boleh kosong.")
            return

        user = self.auth.login(username, password)
        if user:
            self._masuk(user)
        else:
            self.lbl_login_error.setText("❌ Username atau password salah.")
            self.inp_login_pass.clear()
            self.inp_login_pass.setFocus()

    def _coba_register(self):
        nama     = self.inp_reg_nama.text().strip()
        username = self.inp_reg_user.text().strip()
        email    = self.inp_reg_email.text().strip()
        password = self.inp_reg_pass.text()

        self.lbl_reg_error.setText("")
        self.lbl_reg_sukses.setText("")

        berhasil, pesan = self.auth.register(
            username=username, password=password,
            email=email, display_name=nama
        )
        if berhasil:
            self.lbl_reg_sukses.setText("✅ Akun berhasil dibuat! Silakan masuk.")
            # Auto-login
            user = self.auth.login(username, password)
            if user:
                self._masuk(user)
        else:
            self.lbl_reg_error.setText(f"❌ {pesan}")

    def _login_google(self):
        """
        Simulasi login Google — di production, ganti dengan OAuth2 flow sungguhan.
        Di sini tampilkan dialog input email Google untuk demo.
        """
        from PyQt6.QtWidgets import QInputDialog
        email, ok = QInputDialog.getText(
            self, "Login dengan Google",
            "Masukkan email Google Anda:",
        )
        if not ok or not email.strip():
            return

        email = email.strip().lower()
        if "@" not in email:
            QMessageBox.warning(self, "Format Salah", "Email tidak valid.")
            return

        # Buat google_id simulasi dari email
        import hashlib
        fake_google_id = "google_" + hashlib.md5(email.encode()).hexdigest()[:12]
        display_name   = email.split("@")[0].replace(".", " ").title()

        user = self.auth.login_or_register_google(
            google_id=fake_google_id,
            email=email,
            display_name=display_name
        )
        self._masuk(user)

    def _masuk(self, user: dict):
        self._current_user = user
        self.login_berhasil.emit(user)
        self.accept()

    # ── Helpers UI ────────────────────────────────────────────────────────────

    def _ganti_tab(self, index: int):
        self.stack.setCurrentIndex(index)
        self.btn_tab_login.setChecked(index == 0)
        self.btn_tab_daftar.setChecked(index == 1)
        self._update_tab_style()

    def _update_tab_style(self):
        for btn, aktif in [
            (self.btn_tab_login,  self.btn_tab_login.isChecked()),
            (self.btn_tab_daftar, self.btn_tab_daftar.isChecked()),
        ]:
            if aktif:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {self.PRIMARY};
                        color: white;
                        border: none;
                        font-size: 14px;
                        font-weight: bold;
                        border-radius: 0;
                        border-bottom: 3px solid {self.AKSEN};
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: #EEE8DF;
                        color: #888;
                        border: none;
                        font-size: 14px;
                        border-radius: 0;
                    }}
                    QPushButton:hover {{ background: #E0D9CF; color: {self.PRIMARY}; }}
                """)

    def _lbl_field(self, teks: str) -> QLabel:
        lbl = QLabel(teks)
        lbl.setStyleSheet("color: #444; font-size: 13px; font-weight: 500;")
        return lbl

    def _input(self, placeholder: str, password: bool = False) -> QLineEdit:
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setFixedHeight(44)
        if password:
            inp.setEchoMode(QLineEdit.EchoMode.Password)
        inp.setStyleSheet(f"""
            QLineEdit {{
                border: 1.5px solid {self.BORDER};
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 13px;
                background: #FAFAFA;
            }}
            QLineEdit:focus {{
                border: 2px solid {self.PRIMARY};
                background: white;
            }}
        """)
        return inp

    def _btn_mata(self) -> QPushButton:
        btn = QPushButton("👁")
        btn.setFixedSize(44, 44)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setCheckable(True)
        btn.setStyleSheet(f"""
            QPushButton {{
                border: 1.5px solid {self.BORDER};
                border-radius: 8px;
                background: #FAFAFA;
                font-size: 16px;
            }}
            QPushButton:checked {{ background: #EEE; }}
        """)
        return btn

    def _toggle_password(self, inp: QLineEdit, btn: QPushButton):
        if btn.isChecked():
            inp.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            inp.setEchoMode(QLineEdit.EchoMode.Password)

    def _style_btn_primary(self) -> str:
        return f"""
            QPushButton {{
                background-color: {self.PRIMARY};
                color: white;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{ background-color: {self.PRIMARY_HVR}; }}
            QPushButton:pressed {{ background-color: #2D0A10; }}
        """

    def _btn_google(self, teks: str) -> QPushButton:
        btn = QPushButton(f"  {teks}")
        btn.setFixedHeight(46)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: white;
                color: #333;
                border: 1.5px solid {self.BORDER};
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
                text-align: center;
            }}
            QPushButton:hover {{ background: #F5F5F5; border-color: #AAA; }}
        """)
        # Pasang ikon Google (teks G berwarna jika tidak ada gambar)
        btn.setText("  🌐  " + teks)
        return btn

    def _divider(self, teks: str = "atau") -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 8, 0, 8)
        row.setSpacing(12)

        def garis():
            f = QFrame()
            f.setFrameShape(QFrame.Shape.HLine)
            f.setStyleSheet(f"color: {self.BORDER};")
            return f

        lbl = QLabel(teks)
        lbl.setStyleSheet("color: #AAA; font-size: 12px;")
        row.addWidget(garis(), 1)
        row.addWidget(lbl)
        row.addWidget(garis(), 1)
        return w

    # ── Public ────────────────────────────────────────────────────────────────

    def get_user(self) -> Optional[dict]:
        return self._current_user
