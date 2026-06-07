import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from gui.halaman_login import HalamanLogin
from gui.main_window import MainWindow
from database.db_manager import DBManager
from database.auth_manager import AuthManager
from database.session_manager import SessionManager
from gui.theme_manager import ThemeManager


def _asset_root(nama: str) -> str:
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, nama)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PokokNya.Bdg")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("POLBAN Informatika")

    # ── Terapkan tema awal dari ThemeManager ─────────────────────────────
    ThemeManager.apply_to_app(app)

    # ── Icon aplikasi (taskbar & title bar) ──────────────────────────────
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gui", "assets", "images", "logo_app.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("PokokNya.Bdg")
        except Exception:
            pass  # Tidak crash di Linux/Mac

    # ── Inisialisasi database ─────────────────────────────────────────────
    db = DBManager()
    db.init_schema()

    auth = AuthManager()
    auth.init_schema()

    # ── Cek sesi tersimpan (fitur Ingat Login) ────────────────────────────
    sesi = SessionManager.muat_sesi()
    if sesi:
        # Langsung buka MainWindow tanpa dialog login
        window = MainWindow(current_user=sesi)

        did_logout = False

        def on_logout():
            nonlocal did_logout
            did_logout = True
            SessionManager.hapus_sesi()

        window.logout_requested.connect(on_logout)
        window.showMaximized()
        app.exec()

        if not did_logout:
            sys.exit(0)
        # Jika logout → lanjut ke loop login di bawah

    # ── Loop login → main window (mendukung logout) ───────────────────────
    while True:
        login_dialog = HalamanLogin()
        if login_dialog.exec() != HalamanLogin.DialogCode.Accepted:
            break

        user_data = login_dialog.get_user()

        # Simpan sesi jika user mencentang "Ingat Login"
        ingat = getattr(login_dialog, "ingat_login", False)
        if ingat:
            SessionManager.simpan_sesi(user_data)

        window = MainWindow(current_user=user_data)

        did_logout = False

        def on_logout():
            nonlocal did_logout
            did_logout = True
            SessionManager.hapus_sesi()

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