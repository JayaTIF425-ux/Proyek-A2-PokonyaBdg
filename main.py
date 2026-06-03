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


def _asset_root(nama: str) -> str:
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, nama)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PokokNya.Bdg")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("POLBAN Informatika")

    # ── Icon aplikasi (taskbar & title bar) ──────────────────────────────
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gui", "assets", "images", "logo_app.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("PokokNya.Bdg")

    # ── Inisialisasi database ─────────────────────────────────────────────
    db = DBManager()
    db.init_schema()

    auth = AuthManager()
    auth.init_schema()

    # ── Loop login → main window (mendukung logout) ───────────────────────
    while True:
        login_dialog = HalamanLogin()
        if login_dialog.exec() != HalamanLogin.DialogCode.Accepted:
            break

        user_data = login_dialog.get_user()

        window = MainWindow(current_user=user_data)

        # Flag untuk mendeteksi apakah user menekan logout
        did_logout = False
        def on_logout():
            nonlocal did_logout
            did_logout = True

        window.logout_requested.connect(on_logout)
        window.showMaximized()
        app.exec()

        if not did_logout:
            # User menutup window biasa (bukan logout) → keluar aplikasi
            break
        # Jika logout → ulangi loop, tampilkan login lagi

    sys.exit(0)


if __name__ == "__main__":
    main()