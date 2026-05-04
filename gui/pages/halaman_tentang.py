"""
gui/pages/halaman_tentang.py — Tentang Kami.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt


class AnggotaCard(QFrame):
    def __init__(self, nama: str, tugas: str):
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

        lbl_tugas = QLabel(tugas)
        lbl_tugas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_tugas.setStyleSheet("font-size: 11px; color: #777; border: none;")

        lay.addWidget(avatar)
        lay.addWidget(lbl_nama)
        lay.addWidget(lbl_tugas)


class HalamanTentang(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 16)
        layout.setSpacing(20)

        # Judul
        judul = QLabel("Tentang Kami")
        judul.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(judul)

        # Deskripsi
        deskripsi = QLabel(
            "Kami membantu warga Kota Bandung membandingkan harga bahan pokok dari "
            "pasar tradisional dan modern.\n— Semua dalam satu aplikasi, gratis."
        )
        deskripsi.setWordWrap(True)
        deskripsi.setStyleSheet("font-size: 14px; color: #555; line-height: 1.6;")
        layout.addWidget(deskripsi)

        # Latar Belakang
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

        # Fitur
        lbl_fitur = QLabel("Fitur Utama")
        lbl_fitur.setStyleSheet("font-size: 16px; font-weight: bold; color: #44101A;")
        layout.addWidget(lbl_fitur)

        fitur_layout = QHBoxLayout()
        fitur_items = [
            ("🔍", "Cari & bandingkan harga", "Filter berdasarkan komoditas, jenis pasar, dan tanggal."),
            ("🧮", "Hitung anggaran belanja", "Input produk & qty, sistem kalkulasi total + rekomendasi toko terhemat."),
            ("📈", "Pantau tren harga", "Lihat grafik perubahan harga dari waktu ke waktu."),
        ]
        for ikon, judul_f, desc_f in fitur_items:
            card = QFrame()
            card.setStyleSheet("background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 8px; padding: 8px;")
            c_lay = QVBoxLayout(card)
            QLabel(ikon, card).setStyleSheet("font-size: 28px; border: none;")
            lbl_j = QLabel(judul_f)
            lbl_j.setStyleSheet("font-weight: bold; font-size: 13px; border: none;")
            lbl_d = QLabel(desc_f)
            lbl_d.setWordWrap(True)
            lbl_d.setStyleSheet("font-size: 11px; color: #666; border: none;")
            c_lay.addWidget(QLabel(ikon))
            c_lay.addWidget(lbl_j)
            c_lay.addWidget(lbl_d)
            fitur_layout.addWidget(card)
        layout.addLayout(fitur_layout)

        # Tim
        lbl_tim = QLabel("Tim")
        lbl_tim.setStyleSheet("font-size: 16px; font-weight: bold; color: #44101A;")
        layout.addWidget(lbl_tim)

        tim_layout = QHBoxLayout()
        anggota = [
            ("Hana Mardhiyyah", "Tugas"),
            ("Imam Miftahul U.", "Tugas"),
            ("Iriyansyah Jaya A.", "Tugas"),
            ("Lutfhilah Nurazizah", "Tugas"),
            ("Saiwa Zaida N.", "Tugas"),
        ]
        for nama, tugas in anggota:
            tim_layout.addWidget(AnggotaCard(nama, tugas))
        tim_layout.addStretch()
        layout.addLayout(tim_layout)
        layout.addStretch()
