"""
PokokNya.Bdg — Aplikasi Perbandingan Harga Bahan Pokok Kota Bandung
Entry point utama aplikasi PyQt6 — dengan sistem login user/admin.
"""

import sys
import os

# Tambahkan root project ke sys.path agar semua modul bisa di-import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from gui.halaman_login import HalamanLogin
from gui.main_window import MainWindow
from database.db_manager import DBManager
from database.auth_manager import AuthManager


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PokokNya.Bdg")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("POLBAN Informatika")

    # Inisialisasi database (buat tabel jika belum ada)
    db = DBManager()
    db.init_schema()

    # Inisialisasi tabel users + akun default
    auth = AuthManager()
    auth.init_schema()

    # Tampilkan dialog login 
    login_dialog = HalamanLogin()
    if login_dialog.exec() != HalamanLogin.DialogCode.Accepted:
        # Pengguna menutup dialog tanpa login → keluar
        sys.exit(0)

    user_data = login_dialog.get_user()  # {"id": ..., "username": ..., "role": ...}

    # Buka jendela utama dengan konteks user 
    window = MainWindow(current_user=user_data)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()