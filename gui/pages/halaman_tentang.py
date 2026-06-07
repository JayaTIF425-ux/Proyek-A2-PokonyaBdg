"""
gui/pages/halaman_tentang.py — Tentang Kami.
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def _path_aset(nama: str) -> str:
    return os.path.join(BASE_DIR, "gui", "assets", "images", nama)


class AnggotaCard(QFrame):
    def __init__(self, nama: str, nim: str = ""):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumWidth(140)
        self.setFixedHeight(150)
        self.setStyleSheet("""
            AnggotaCard {
                background: white;
                border: 1.5px solid #E8E0D4;
                border-radius: 12px;
            }
            AnggotaCard:hover {
                border: 2px solid #44101A;
                background: #FDF8F4;
            }
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 16, 12, 12)
        lay.setSpacing(6)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Avatar lingkaran
        avatar_frame = QFrame()
        avatar_frame.setFixedSize(52, 52)
        avatar_frame.setStyleSheet("""
            background: #F4EBE8;
            border-radius: 26px;
            border: 2px solid #E0C8C0;
        """)
        av_lay = QVBoxLayout(avatar_frame)
        av_lay.setContentsMargins(0, 0, 0, 0)
        av_icon = QLabel("👤")
        av_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        av_icon.setStyleSheet("font-size: 24px; border: none; background: transparent;")
        av_lay.addWidget(av_icon)

        lbl_nama = QLabel(nama)
        lbl_nama.setWordWrap(True)
        lbl_nama.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_nama.setStyleSheet(
            "font-weight: 700; font-size: 12px; border: none; "
            "color: #2c3e50; background: transparent; line-height: 1.4;"
        )

        lay.addWidget(avatar_frame, alignment=Qt.AlignmentFlag.AlignCenter)
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

        anggota = [
            "Hana Mardhiyyah",
            "Imam Miftahul U.",
            "Iryansyah Jaya A.",
            "Lutfhiah Nurazizah",
            "Salwa Zaida N.",
        ]

        # Grid: 3 kolom baris pertama, 2 kolom baris kedua (rata tengah)
        # Pakai wrapper agar bisa di-center
        tim_outer = QHBoxLayout()
        tim_outer.setContentsMargins(0, 0, 0, 0)

        tim_widget = QWidget()
        tim_widget.setStyleSheet("background: transparent;")
        tim_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        grid = QGridLayout(tim_widget)
        grid.setSpacing(14)
        grid.setContentsMargins(0, 0, 0, 0)

        cols = 3
        for i, nama in enumerate(anggota):
            row_i = i // cols
            col_i = i % cols
            card = AnggotaCard(nama)
            grid.addWidget(card, row_i, col_i)

        # Kolom stretch sama rata
        for c in range(cols):
            grid.setColumnStretch(c, 1)

        tim_outer.addWidget(tim_widget)
        layout.addLayout(tim_outer)
        layout.addStretch()