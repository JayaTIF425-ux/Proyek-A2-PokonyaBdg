"""
PokokNya.Bdg — Entry point utama aplikasi PyQt6.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from gui.halaman_login import HalamanLogin
from gui.main_window import MainWindow
from database.db_manager import DBManager
from database.auth_manager import AuthManager


def _asset(nama: str) -> str:
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "assets", nama)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PokokNya.Bdg")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("POLBAN Informatika")

    # ── Icon aplikasi (taskbar & title bar) ──────────────────────────────
    icon_path = _asset("app_icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # ── Inisialisasi database ─────────────────────────────────────────────
    db = DBManager()
    db.init_schema()

    auth = AuthManager()
    auth.init_schema()

    # ── Tampilkan dialog login ────────────────────────────────────────────
    login_dialog = HalamanLogin()
    if login_dialog.exec() != HalamanLogin.DialogCode.Accepted:
        sys.exit(0)

    user_data = login_dialog.get_user()

    # ── Buka jendela utama fullscreen ─────────────────────────────────────
    window = MainWindow(current_user=user_data)
    window.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()