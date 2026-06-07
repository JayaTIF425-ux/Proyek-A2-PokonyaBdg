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


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PokokNya.Bdg")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("POLBAN Informatika")

     # ── Terapkan tema awal dari ThemeManager ─────────────────────────────
    ThemeManager.apply_to_app(app)

    # ── Icon aplikasi (taskbar & title bar) ──────────────────────────────
    icon_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "gui", "assets", "images", "logo_app.png"
    )
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("PokokNya.Bdg")
        except Exception:
            pass  # Bukan Windows, lewati saja

    # ── Terapkan tema awal (light / dark) ─────────────────────────────────
    theme = ThemeManager()
    theme.apply_to_app(app)

    # ── Inisialisasi database ─────────────────────────────────────────────
    db = DBManager()
    db.init_schema()

    auth = AuthManager()
    auth.init_schema()

    session = SessionManager()

    # ── Cek sesi tersimpan ────────────────────────────────────────────────
    user_data = session.muat_sesi()

    while True:
        if user_data is None:
            # Tidak ada sesi → tampilkan login
            login_dialog = HalamanLogin()
            if login_dialog.exec() != HalamanLogin.DialogCode.Accepted:
                break
            user_data = login_dialog.get_user()
            # Simpan sesi jika user memilih "Ingat Login"
            if login_dialog.ingat_login:
                session.simpan_sesi(user_data)

        window = MainWindow(current_user=user_data, theme_manager=theme)

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

        # Logout → hapus sesi & kembali ke login
        session.hapus_sesi()
        user_data = None

    sys.exit(0)


if __name__ == "__main__":
    main()