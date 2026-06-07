"""
PokokNya.Bdg — Entry point utama aplikasi PyQt6.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from gui.halaman_login import HalamanLogin
from gui.main_window import MainWindow
from database.db_manager import DBManager
from database.auth_manager import AuthManager
from gui.widgets.scraper_dialog import ScraperDialog
from gui.workers.scraper_worker import ScraperWorker


def cek_data_tersedia():
    """Cek apakah database sudah memiliki data produk dari supermarket."""
    try:
        db = DBManager()
        with db._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM harga_supermarket")
            count = cursor.fetchone()[0]
            print(f"[INFO] Data di harga_supermarket: {count}")
            return count > 0
    except Exception as e:
        print(f"[ERROR] Gagal cek data: {e}")
        return False


def jalankan_scraper_otomatis(parent=None):
    """Jalankan scraper dengan dialog progress."""
    dialog = ScraperDialog(parent)
    worker = ScraperWorker()
    
    # Connect signals
    worker.progress.connect(dialog.update_progress)
    worker.finished.connect(lambda success, msg: dialog.set_finished(success, msg))
    
    def handle_cancel():
        dialog.update_progress("Menghentikan scraper...")
        worker.stop()
    
    dialog.cancel_requested.connect(handle_cancel)
    
    # Mulai worker
    worker.start()
    
    # Tampilkan dialog (blocking)
    dialog.exec()
    
    # Pastikan worker berhenti
    if worker.isRunning():
        worker.stop()
        if not worker.wait(2000):  # Tunggu 2 detik
            worker.terminate()  # Paksa terminate
            worker.wait()


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

    # ── Cek dan jalankan scraper HANYA jika data belum ada ────────────────
    data_ada = cek_data_tersedia()
    
    if not data_ada:
        print("[INFO] Database kosong, menjalankan scraper otomatis...")
        msg = QMessageBox()
        msg.setWindowTitle("Data Belum Tersedia")
        msg.setText("Database masih kosong. Aplikasi akan mengambil data harga dari berbagai toko.")
        msg.setInformativeText("Proses ini membutuhkan koneksi internet dan memakan waktu 5-10 menit.\n\nAnda bisa membatalkan proses ini dan data akan dimuat saat refresh manual dari menu Admin.")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        msg.setDefaultButton(QMessageBox.StandardButton.Ok)
        
        if msg.exec() == QMessageBox.StandardButton.Ok:
            jalankan_scraper_otomatis()
        else:
            print("[INFO] User membatalkan scraping awal")
    else:
        print(f"[INFO] Database sudah memiliki data, skip scraping otomatis")

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

    sys.exit(0)


if __name__ == "__main__":
    main()