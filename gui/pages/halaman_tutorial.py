"""
gui/pages/halaman_tutorial.py — Panduan penggunaan aplikasi.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt6.QtCore import Qt


class HalamanTutorial(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 16)

        judul = QLabel("Tutorial Aplikasi")
        judul.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50; margin-bottom: 12px;")
        layout.addWidget(judul)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        konten = QWidget()
        k_layout = QVBoxLayout(konten)
        k_layout.setSpacing(16)

        langkah = [
            ("1. Pendahuluan",
             "Aplikasi ini dirancang untuk membantu masyarakat kota Bandung dalam "
             "memantau dan membandingkan harga bahan pokok dari pasar tradisional dan "
             "supermarket modern."),
            ("2. Beranda",
             "Halaman Beranda menampilkan harga rata-rata seluruh komoditas berdasarkan "
             "data dari PIHPS (Pusat Informasi Harga Pangan Strategis Nasional). "
             "Data diperbarui setiap hari secara otomatis."),
            ("3. Pencarian",
             "Gunakan fitur Pencarian untuk mencari harga komoditas tertentu. "
             "Masukkan nama bahan (misal: 'Beras') lalu klik Cari. Sistem akan "
             "menampilkan harga dari semua sumber — PIHPS maupun supermarket."),
            ("4. Penghitung Belanja",
             "Fitur ini adalah kalkulator belanja cerdas. Pilih produk dan atur "
             "jumlah (kg) yang ingin dibeli. Sistem secara otomatis menghitung "
             "estimasi total belanja dan memberikan rekomendasi toko paling hemat."),
            ("5. Memperbarui Data",
             "Untuk memperbarui data, jalankan skrip scraper dari terminal:\n"
             "  python scripts/run_all_scrapers.py\n\n"
             "Atau jalankan masing-masing:\n"
             "  python scrapers/pihps_scraper.py\n"
             "  python scrapers/yogya_scraper.py\n"
             "  python scrapers/borma_scraper.py"),
        ]

        for judul_l, isi in langkah:
            lbl_j = QLabel(judul_l)
            lbl_j.setStyleSheet("font-size: 15px; font-weight: bold; color: #44101A;")
            lbl_i = QLabel(isi)
            lbl_i.setWordWrap(True)
            lbl_i.setStyleSheet("font-size: 13px; color: #444; padding-left: 16px; padding-bottom: 8px;")
            k_layout.addWidget(lbl_j)
            k_layout.addWidget(lbl_i)

        k_layout.addStretch()
        scroll.setWidget(konten)
        layout.addWidget(scroll)
