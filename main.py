"""
PokokNya.Bdg — Aplikasi Perbandingan Harga Bahan Pokok Kota Bandung
Entry point utama aplikasi PyQt6.
"""

import sys
import os

# Tambahkan root project ke sys.path agar semua modul bisa di-import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from gui.main_window import MainWindow
from database.db_manager import DBManager


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PokokNya.Bdg")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("POLBAN Informatika")

    # Inisialisasi database (buat tabel jika belum ada)
    db = DBManager()
    db.init_schema()

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
