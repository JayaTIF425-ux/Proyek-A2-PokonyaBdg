"""
gui/pages/halaman_tentang.py — Tentang Kami.
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def _path_aset(nama: str) -> str:
    return os.path.join(BASE_DIR, "gui", "assets", "images", nama)


class AnggotaCard(QFrame):
    def __init__(self, nama: str):
        super().__init__()
        self.setFixedSize(160, 130)
        self.setStyleSheet(
            "background: white; border: 1px solid #ddd; border-radius: 8px;"
        )
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        avatar = QLabel("👤")
        avatar.setStyleSheet("font-size: 36px; border: none;")
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_nama = QLabel(nama)
        lbl_nama.setWordWrap(True)
        lbl_nama.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_nama.setStyleSheet("font-weight: bold; font-size: 12px; border: none; color: #2c3e50;")

        lay.addWidget(avatar)
        lay.addWidget(lbl_nama)


class HalamanTentang(QWidget):
    def __init__(self):
        super().__init__()

        # ── Scroll area ───────────────────────────────────────────────────
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        outer.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        # ── Judul ─────────────────────────────────────────────────────────
        judul = QLabel("Tentang Kami")
        judul.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(judul)

        # ── Deskripsi ─────────────────────────────────────────────────────
        deskripsi = QLabel(
            "Kami membantu warga Kota Bandung membandingkan harga bahan pokok dari "
            "pasar tradisional dan modern. Semua dalam satu aplikasi, gratis."
        )
        deskripsi.setWordWrap(True)
        deskripsi.setStyleSheet("font-size: 14px; color: #555;")
        layout.addWidget(deskripsi)

        # ── Gambar sayuran ────────────────────────────────────────────────
        lbl_gambar = QLabel()
        lbl_gambar.setFixedHeight(200)
        lbl_gambar.setMinimumWidth(100)
        lbl_gambar.setScaledContents(True)
        pixmap = QPixmap(_path_aset("sayuran.png"))
        if not pixmap.isNull():
           lbl_gambar.setPixmap(pixmap)
        else:
            lbl_gambar.setText("[ Gambar tidak ditemukan ]")
            lbl_gambar.setStyleSheet("color: #aaa; font-size: 12px;")
        layout.addWidget(lbl_gambar)

        # ── Latar Belakang ────────────────────────────────────────────────
        lbl_lb = QLabel("Latar Belakang")
        lbl_lb.setStyleSheet("font-size: 16px; font-weight: bold; color: #44101A;")
        layout.addWidget(lbl_lb)

        lb_text = QLabel(
            "Harga bahan pokok di Bandung bisa berbeda jauh antara pasar tradisional dan "
            "pasar modern, tetapi selama ini tidak ada yang menyajikannya secara berdampingan. "
            "PokokNya.Bdg hadir untuk membantu berbelanja lebih cerdas dengan melihat perbandingan "
            "harga dari pasar tradisional maupun pasar modern di sekitar."
        )
        lb_text.setWordWrap(True)
        lb_text.setStyleSheet("font-size: 13px; color: #555; padding-left: 8px;")
        layout.addWidget(lb_text)

        # ── Fitur ─────────────────────────────────────────────────────────
        lbl_fitur = QLabel("Fitur")
        lbl_fitur.setStyleSheet("font-size: 16px; font-weight: bold; color: #44101A;")
        layout.addWidget(lbl_fitur)

        fitur_layout = QHBoxLayout()
        fitur_layout.setSpacing(12)
        fitur_items = [
            ("🔍", "Cari & bandingkan harga",
             "Lihat harga komoditas dari berbagai pasar dan supermarket secara berdampingan. "
             "Filter berdasarkan jenis pasar dan tanggal."),
            ("🧮", "Hitung anggaran belanja",
             "Masukkan daftar belanjaan, pilih toko, dan lihat total estimasi otomatis. "
             "Rencanakan budget sebelum ke pasar."),
            ("📈", "Pantau tren harga",
             "Lihat pergerakan harga mingguan, termasuk komoditas mana yang sedang "
             "naik atau turun di pasaran."),
        ]
        for ikon, judul_f, desc_f in fitur_items:
            card = QFrame()
            card.setStyleSheet(
                "background: white; border: 1px solid #e0e0e0; "
                "border-radius: 8px; padding: 4px;"
            )
            c_lay = QVBoxLayout(card)
            c_lay.setSpacing(6)

            lbl_ikon = QLabel(ikon)
            lbl_ikon.setStyleSheet("font-size: 24px; border: none; background: transparent;")
            lbl_j = QLabel(judul_f)
            lbl_j.setStyleSheet("font-weight: bold; font-size: 13px; border: none; background: transparent;")
            lbl_d = QLabel(desc_f)
            lbl_d.setWordWrap(True)
            lbl_d.setStyleSheet("font-size: 11px; color: #666; border: none; background: transparent;")

            c_lay.addWidget(lbl_ikon)
            c_lay.addWidget(lbl_j)
            c_lay.addWidget(lbl_d)
            c_lay.addStretch()
            fitur_layout.addWidget(card)

        layout.addLayout(fitur_layout)

        # ── Tim ───────────────────────────────────────────────────────────
        lbl_tim = QLabel("Tim")
        lbl_tim.setStyleSheet("font-size: 16px; font-weight: bold; color: #44101A;")
        layout.addWidget(lbl_tim)

        tim_layout = QHBoxLayout()
        tim_layout.setSpacing(12)
        anggota = [
            ("Hana Mardhiyyah"),
            ("Imam Miftahul U."),
            ("Iryansyah Jaya A."),
            ("Lutfhiah Nurazizah"),
            ("Salwa Zaida N."),
        ]
        for nama in anggota:
            tim_layout.addWidget(AnggotaCard(nama))
        tim_layout.addStretch()
        layout.addLayout(tim_layout)
        layout.addStretch()