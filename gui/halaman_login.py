"""
gui/halaman_login.py — Dialog login + registrasi untuk PokokNya.Bdg.
Desain ulang mengikuti screenshot: panel kiri maroon + panel kanan putih
dengan kartu form, pemilih peran Admin/User, dan animasi transisi halus.
"""

import os
import sys
import hashlib
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QMessageBox,
    QStackedWidget, QWidget, QApplication, QGraphicsOpacityEffect,
    QScrollArea, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, pyqtSignal, QSize, QPropertyAnimation,
    QEasingCurve, QTimer, QRect, QPoint
)
from PyQt6.QtGui import (
    QPixmap, QIcon, QFont, QColor, QPainter,
    QPainterPath, QLinearGradient, QBrush, QPen,
    QFontDatabase
)

from database.auth_manager import AuthManager


# ── Path helper ───────────────────────────────────────────────────────────────

def _asset(nama: str) -> str:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "assets", nama)


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
}


# ══════════════════════════════════════════════════════════════════════════════
class RoleButton(QPushButton):
    """Tombol pemilih peran Admin / User dengan ikon SVG sederhana."""

    def __init__(self, label: str, icon_type: str, parent=None):
        super().__init__(parent)
        self._label = label
        self._icon_type = icon_type  # "admin" atau "user"
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(80)
        self._apply_style(False)

    def _apply_style(self, checked: bool):
        if checked:
            bg   = C["role_sel"]
            fg   = C["role_sel_txt"]
            bord = C["role_sel"]
        else:
            bg   = C["role_bg"]
            fg   = C["role_txt"]
            bord = C["border"]

        self.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                color: {fg};
                border: 2px solid {bord};
                border-radius: 10px;
                font-size: 13px;
                font-weight: 600;
                padding-top: 6px;
            }}
            QPushButton:hover {{
                border-color: {C["maroon"]};
            }}
        """)

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        checked = self.isChecked()
        icon_color = QColor(C["white"] if checked else C["maroon"])

        cx = self.width() // 2
        # Gambar ikon manusia sederhana
        # Kepala
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(icon_color))
        p.drawEllipse(cx - 10, 8, 20, 20)
        # Badan
        p.drawRoundedRect(cx - 14, 30, 28, 18, 6, 6)

        if self._icon_type == "admin":
            # Roda gigi kecil di pojok kanan atas kepala
            gear_color = QColor(C["gold"] if checked else C["gold"])
            p.setBrush(QBrush(gear_color))
            p.drawEllipse(cx + 2, 10, 12, 12)
            p.setBrush(QBrush(QColor(C["white"] if checked else C["role_bg"])))
            p.drawEllipse(cx + 5, 13, 6, 6)

        # Label
        p.setPen(QPen(icon_color))
        font = QFont()
        font.setPointSize(10)
        font.setWeight(QFont.Weight.DemiBold)
        p.setFont(font)
        p.drawText(QRect(0, 52, self.width(), 22),
                   Qt.AlignmentFlag.AlignCenter, self._label)
        p.end()

    def setChecked(self, checked: bool):
        super().setChecked(checked)
        self._apply_style(checked)
        self.update()


# ══════════════════════════════════════════════════════════════════════════════
class GoogleButton(QPushButton):
    """Tombol login Google dengan logo G dari file gambar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setText("Lanjut dengan Google")
        self.setStyleSheet(f"""
            QPushButton {{
                background: {C["google_bg"]};
                border: 1.5px solid {C["border"]};
                border-radius: 10px;
                font-size: 13px;
                color: {C["text_mid"]};
                text-align: center;
                padding-left: 8px;
            }}
            QPushButton:hover {{
                background: #F8F4EE;
                border-color: #C0A88A;
            }}
            QPushButton:pressed {{
                background: #F0EAE0;
            }}
        """)

        # Set ikon Google dari file gambar
        google_logo_path = _asset("google_logo.png")
        if os.path.exists(google_logo_path):
            icon = QIcon(google_logo_path)
            self.setIcon(icon)
            self.setIconSize(QSize(22, 22))


# ══════════════════════════════════════════════════════════════════════════════
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


# ══════════════════════════════════════════════════════════════════════════════
class HalamanLogin(QDialog):
    """
    Dialog login fullscreen — desain mengikuti screenshot Figma:
    • Panel kiri: maroon gelap + logo + nama app
    • Panel kanan: latar PUTIH + kartu form melayang
    • Pemilih peran Admin / User
    • Animasi fade antar form Login ↔ Daftar
    """

    login_berhasil = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth = AuthManager()
        self.auth.init_schema()
        self._current_user: Optional[dict] = None
        self._peran_dipilih = "user"

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

    # ── UI Utama ─────────────────────────────────────────────────────────────

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

        # Logo — gunakan logo_app.png yang dikirim user
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
            lbl_logo.setText("🥬")
            lbl_logo.setStyleSheet("font-size: 90px; background: transparent;")

        logo_wrap = QWidget()
        logo_wrap.setStyleSheet("background: transparent;")
        logo_wrap.setFixedSize(200, 200)
        logo_inner = QVBoxLayout(logo_wrap)
        logo_inner.setContentsMargins(10, 10, 10, 10)
        logo_inner.addWidget(lbl_logo)
        layout.addWidget(logo_wrap, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(28)

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

        layout.addSpacing(12)

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

        # Kartu tengah
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

        # ── PENTING: Buat _form_daftar() DULU agar self.btn_admin_daftar
        #    dan self.btn_user_daftar sudah ada sebelum _form_login() dipakai.
        form_daftar = self._form_daftar()
        form_login  = self._form_login()

        # Stack: login (index 0) + daftar (index 1)
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

        # Judul
        lbl_judul = QLabel("Selamat Datang")
        lbl_judul.setStyleSheet(f"""
            color: {C["text_dark"]};
            font-size: 24px;
            font-weight: 700;
            background: transparent;
        """)
        layout.addWidget(lbl_judul)

        lbl_sub = QLabel("Masuk untuk melanjutkan ke akun Anda")
        lbl_sub.setStyleSheet(f"""
            color: {C["text_light"]};
            font-size: 13px;
            background: transparent;
        """)
        layout.addWidget(lbl_sub)
        layout.addSpacing(24)

        # Email
        layout.addWidget(self._label_field("Alamat Email"))
        layout.addSpacing(6)
        self.inp_email_login = self._input_field("you@example.com", icon="✉")
        layout.addWidget(self.inp_email_login)
        layout.addSpacing(14)

        # Password
        layout.addWidget(self._label_field("Kata Sandi"))
        layout.addSpacing(6)
        self.inp_pass_login = self._input_field("Masukkan kata sandi", icon="🔒", password=True)
        layout.addWidget(self.inp_pass_login)
        self.inp_pass_login.returnPressed.connect(self._aksi_login)
        layout.addSpacing(20)

        # Pilih kategori
        layout.addWidget(self._label_field("Pilih kategori akun anda"))
        layout.addSpacing(8)
        role_row = QHBoxLayout()
        role_row.setSpacing(12)
        self.btn_admin_login = RoleButton("Admin", "admin")
        self.btn_user_login  = RoleButton("User",  "user")
        self.btn_user_login.setChecked(True)

        # FIX: connect hanya untuk form "login" — tidak ada referensi ke btn_daftar di sini
        self.btn_admin_login.clicked.connect(lambda: self._pilih_peran("admin", "login"))
        self.btn_user_login.clicked.connect(lambda: self._pilih_peran("user",  "login"))
        role_row.addWidget(self.btn_admin_login)
        role_row.addWidget(self.btn_user_login)
        layout.addLayout(role_row)
        layout.addSpacing(6)

        # Error
        self.lbl_login_error = QLabel("")
        self.lbl_login_error.setStyleSheet(f"color: {C['error']}; font-size: 12px; background: transparent;")
        self.lbl_login_error.setWordWrap(True)
        layout.addWidget(self.lbl_login_error)
        layout.addSpacing(16)

        # Tombol Masuk
        btn_masuk = self._btn_utama("Masuk")
        btn_masuk.clicked.connect(self._aksi_login)
        layout.addWidget(btn_masuk)
        layout.addSpacing(12)

        # Tombol Buat Akun Baru
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

        # Judul
        lbl_judul = QLabel("Buat akun kamu")
        lbl_judul.setStyleSheet(f"""
            color: {C["gold"]};
            font-size: 24px;
            font-weight: 700;
            background: transparent;
        """)
        layout.addWidget(lbl_judul)

        lbl_sub = QLabel("Mulai jelajahi harga pangan bersama kami")
        lbl_sub.setStyleSheet(f"""
            color: {C["text_light"]};
            font-size: 13px;
            background: transparent;
        """)
        layout.addWidget(lbl_sub)
        layout.addSpacing(22)

        # Email
        layout.addWidget(self._label_field("Alamat Email"))
        layout.addSpacing(6)
        self.inp_email_daftar = self._input_field("you@example.com", icon="✉")
        layout.addWidget(self.inp_email_daftar)
        layout.addSpacing(14)

        # Password
        layout.addWidget(self._label_field("Kata Sandi"))
        layout.addSpacing(6)
        self.inp_pass_daftar = self._input_field("Masukkan kata sandi", icon="🔒", password=True)
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
        layout.addSpacing(6)

        # Error / Sukses
        self.lbl_daftar_error  = QLabel("")
        self.lbl_daftar_sukses = QLabel("")
        self.lbl_daftar_error.setStyleSheet(f"color: {C['error']}; font-size: 12px; background: transparent;")
        self.lbl_daftar_sukses.setStyleSheet(f"color: {C['success']}; font-size: 12px; background: transparent;")
        self.lbl_daftar_error.setWordWrap(True)
        self.lbl_daftar_sukses.setWordWrap(True)
        layout.addWidget(self.lbl_daftar_error)
        layout.addWidget(self.lbl_daftar_sukses)
        layout.addSpacing(16)

        # Tombol submit daftar
        btn_buat = self._btn_utama("Buat Akun")
        btn_buat.clicked.connect(self._aksi_daftar)
        layout.addWidget(btn_buat)
        layout.addSpacing(12)

        # Tombol kembali ke login
        btn_kembali = self._btn_sekunder("Sudah punya akun? Masuk")
        btn_kembali.clicked.connect(lambda: self.stack.slide_to(0))
        btn_kembali.clicked.connect(lambda: self._pilih_peran("user", "login"))
        layout.addWidget(btn_kembali)
        layout.addSpacing(16)

        layout.addStretch()
        return w

    # ── Aksi ─────────────────────────────────────────────────────────────────

    def _pilih_peran(self, peran: str, form: str):
        # Pastikan 'peran' yang masuk berupa string murni, bukan boolean dari PyQt
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
        """Login menggunakan email sebagai username (ambil bagian sebelum @)."""
        email    = self.inp_email_login.text().strip()
        password = self.inp_pass_login.text()
        self.lbl_login_error.setText("")

        if not email or not password:
            self.lbl_login_error.setText("⚠ Email dan kata sandi tidak boleh kosong.")
            return

        # Derive username dari email (sama seperti saat registrasi)
        username = email.split("@")[0].replace(".", "_") if "@" in email else email

        user = self.auth.login(username, password)
        if user:
            if user["role"] != self._peran_dipilih:
                role_seharusnya = "Admin" if user["role"] == "admin" else "User"
                self.lbl_login_error.setText(
                    f"❌ Akun ini terdaftar sebagai {role_seharusnya}. "
                    f"Pilih kategori '{role_seharusnya}' untuk masuk."
                )
                return
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
        if "@" not in email:
            self.lbl_daftar_error.setText("⚠ Format email tidak valid.")
            return

        username = email.split("@")[0].replace(".", "_")

        # FIX: teruskan self._peran_dipilih sebagai role
        berhasil, pesan = self.auth.register(
            username=username,
            password=password,
            email=email,
            display_name=username,
            role=self._peran_dipilih   # ← role yang dipilih user (admin/user)
        )
        if berhasil:
            self.lbl_daftar_sukses.setText(f"✅ Akun berhasil dibuat sebagai {self._peran_dipilih}!")
            user = self.auth.login(username, password)
            if user:
                QTimer.singleShot(800, lambda: self._masuk(user))
        else:
            self.lbl_daftar_error.setText(f"❌ {pesan}")

    def _aksi_google(self):
        from PyQt6.QtWidgets import QInputDialog
        email, ok = QInputDialog.getText(
            self, "Masuk dengan Google",
            "Masukkan email Google Anda:",
        )
        if not ok or not email.strip():
            return
        email = email.strip().lower()
        if "@" not in email:
            QMessageBox.warning(self, "Format Salah", "Email tidak valid.")
            return

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

    # ── Widget Helpers ────────────────────────────────────────────────────────

    def _label_field(self, teks: str) -> QLabel:
        lbl = QLabel(teks)
        lbl.setStyleSheet(f"""
            color: {C["text_dark"]};
            font-size: 13px;
            font-weight: 500;
            background: transparent;
        """)
        return lbl

    def _input_field(self, placeholder: str, icon: str = "", password: bool = False) -> QLineEdit:
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setFixedHeight(48)
        if password:
            inp.setEchoMode(QLineEdit.EchoMode.Password)

        padding_left = "38px" if icon else "14px"

        inp.setStyleSheet(f"""
            QLineEdit {{
                background: {C["input_bg"]};
                border: 1.5px solid {C["border"]};
                border-radius: 10px;
                padding: 10px 14px 10px {padding_left};
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

        if icon:
            icon_lbl = QLabel(icon, inp)
            icon_lbl.setStyleSheet("background: transparent; font-size: 14px;")
            icon_lbl.setGeometry(10, 14, 20, 20)
            icon_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

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
            QPushButton:hover {{
                background: {C["gold_hover"]};
            }}
            QPushButton:pressed {{
                background: {C["gold_press"]};
            }}
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
            QPushButton:pressed {{
                background: #E8E0D4;
            }}
        """)
        return btn

    def _divider(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 4, 0, 4)
        row.setSpacing(12)

        def garis():
            f = QFrame()
            f.setFrameShape(QFrame.Shape.HLine)
            f.setStyleSheet(f"color: {C['border']};")
            return f

        lbl = QLabel("Atau lanjut dengan")
        lbl.setStyleSheet(f"""
            color: {C["text_light"]};
            font-size: 12px;
            background: transparent;
        """)
        row.addWidget(garis(), 1)
        row.addWidget(lbl)
        row.addWidget(garis(), 1)
        return w

    # ── Public ────────────────────────────────────────────────────────────────

    def get_user(self) -> Optional[dict]:
        return self._current_user