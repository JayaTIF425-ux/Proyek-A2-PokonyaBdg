"""
gui/halaman_login.py — Dialog login untuk user dan admin.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from database.auth_manager import AuthManager


class HalamanLogin(QDialog):
    """Dialog login. Emit sinyal login_berhasil(dict_user) jika sukses."""

    login_berhasil = pyqtSignal(dict)

    WARNA_BG      = "#FDFAF6"
    WARNA_PRIMARY = "#44101A"
    WARNA_AKSEN   = "#F1C40F"
    WARNA_BORDER  = "#D4C5A9"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth = AuthManager()
        self.auth.init_schema()
        self._current_user = None

        self.setWindowTitle("PokokNya.Bdg — Login")
        self.setFixedSize(400, 480)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self.setStyleSheet(f"background-color: {self.WARNA_BG};")

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)

        # ── Header ───────────────────────────────────────────────────────────
        lbl_judul = QLabel("PokokNya.Bdg")
        lbl_judul.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_judul.setStyleSheet(
            f"color: {self.WARNA_PRIMARY}; font-size: 28px; font-weight: bold;"
        )
        layout.addWidget(lbl_judul)

        lbl_sub = QLabel("Perbandingan Harga Bahan Pokok Bandung")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_sub.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(lbl_sub)

        layout.addSpacing(10)

        # ── Card login ───────────────────────────────────────────────────────
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 12px;
                border: 1px solid {self.WARNA_BORDER};
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(14)

        lbl_masuk = QLabel("Masuk ke Akun Anda")
        lbl_masuk.setStyleSheet(
            f"color: {self.WARNA_PRIMARY}; font-size: 16px; font-weight: bold;"
            " border: none;"
        )
        card_layout.addWidget(lbl_masuk)

        # Username
        lbl_user = QLabel("Username")
        lbl_user.setStyleSheet("color: #333; font-size: 13px; border: none;")
        card_layout.addWidget(lbl_user)

        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Masukkan username")
        self.input_username.setStyleSheet(self._style_input())
        self.input_username.setFixedHeight(40)
        card_layout.addWidget(self.input_username)

        # Password
        lbl_pass = QLabel("Password")
        lbl_pass.setStyleSheet("color: #333; font-size: 13px; border: none;")
        card_layout.addWidget(lbl_pass)

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Masukkan password")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setStyleSheet(self._style_input())
        self.input_password.setFixedHeight(40)
        self.input_password.returnPressed.connect(self._coba_login)
        card_layout.addWidget(self.input_password)

        # Label error
        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #c0392b; font-size: 12px; border: none;")
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.lbl_error)

        # Tombol Login
        self.btn_login = QPushButton("Masuk")
        self.btn_login.setFixedHeight(42)
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.WARNA_PRIMARY};
                color: white;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{ background-color: #6B1525; }}
            QPushButton:pressed {{ background-color: #2D0A10; }}
        """)
        self.btn_login.clicked.connect(self._coba_login)
        card_layout.addWidget(self.btn_login)

        layout.addWidget(card)

        # ── Info akun default ─────────────────────────────────────────────────
        lbl_info = QLabel(
            "<b>Akun default:</b><br>"
            "🔑 Admin → username: <b>admin</b> / password: <b>admin123</b><br>"
            "👤 User &nbsp;→ username: <b>user</b> &nbsp;/ password: <b>user123</b>"
        )
        lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_info.setStyleSheet(
            "color: #666; font-size: 11px; line-height: 1.6;"
        )
        lbl_info.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(lbl_info)

        layout.addStretch()

    def _style_input(self) -> str:
        return f"""
            QLineEdit {{
                border: 1px solid {self.WARNA_BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                background: #FAFAFA;
            }}
            QLineEdit:focus {{
                border: 2px solid {self.WARNA_PRIMARY};
                background: white;
            }}
        """

    def _coba_login(self):
        username = self.input_username.text().strip()
        password = self.input_password.text()

        if not username or not password:
            self.lbl_error.setText("⚠ Username dan password tidak boleh kosong.")
            return

        user = self.auth.login(username, password)
        if user:
            self._current_user = user
            self.login_berhasil.emit(user)
            self.accept()
        else:
            self.lbl_error.setText("❌ Username atau password salah.")
            self.input_password.clear()
            self.input_password.setFocus()

    def get_user(self) -> Optional[dict]:
        """Kembalikan data user yang berhasil login."""
        return self._current_user
