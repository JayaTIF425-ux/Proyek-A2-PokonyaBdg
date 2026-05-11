"""
gui/pages/halaman_tentang.py — Tentang Kami.
"""
import urllib.request

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QGridLayout, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt

from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QByteArray

class BannerImage(QLabel):
    def __init__(self, pixmap_original: QPixmap):
        super().__init__()
        self._original = pixmap_original  # simpan pixmap asli untuk rescaling
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(220)           # tinggi tetap, mencegah overlap ke bawah
        # Expanding horizontal: gambar meregang mengisi lebar parent, bukan 700px
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        self.setStyleSheet("border-radius: 12px; background: #e8e8e8; border: none;")
 
    def resizeEvent(self, event):
        """Dipanggil otomatis setiap kali lebar widget berubah."""
        if self._original and not self._original.isNull():
            # Scale gambar agar memenuhi lebar dan tinggi widget (cover)
            scaled = self._original.scaled(
                self.width(), self.height(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            # Crop tengah supaya tidak ada sisa abu-abu di kiri/kanan
            x = max(0, (scaled.width() - self.width()) // 2)
            y = max(0, (scaled.height() - self.height()) // 2)
            cropped = scaled.copy(x, y, self.width(), self.height())
            self.setPixmap(cropped)
        super().resizeEvent(event)

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
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 16)
        layout.setSpacing(20)

        # Judul
        judul = QLabel("Tentang Kami")
        judul.setStyleSheet("font-size: 25px; font-weight: bold; color: #67823A;")
        layout.addWidget(judul)

        # Deskripsi
        deskripsi = QLabel(
            "Kami membantu warga Kota Bandung membandingkan harga bahan pokok dari "
            "pasar tradisional dan modern.\n— Semua dalam satu aplikasi, gratis."
        )
        deskripsi.setWordWrap(True)
        deskripsi.setStyleSheet("font-size: 14px; color: #555; line-height: 1.6;")
        layout.addWidget(deskripsi)

        IMAGE_URL = "https://msdconnolly.weebly.com/uploads/9/1/6/6/9166444/header_images/1502991705.jpg"
 
        gambar_label = QLabel()
        gambar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gambar_label.setFixedHeight(220)
        gambar_label.setStyleSheet(
            "border-radius: 12px; background: #e8e8e8; border: none;"
        )
 
        try:
            # Unduh data gambar dari URL menggunakan urllib
            req = urllib.request.Request(IMAGE_URL, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                image_data = response.read()
 
            # Muat data ke QPixmap lalu skalakan agar pas dengan lebar konten
            pixmap = QPixmap()
            pixmap.loadFromData(QByteArray(image_data))
 
            # Skalakan gambar: lebar 700px, tinggi mengikuti rasio, tetapi dibatasi 220px
            scaled = pixmap.scaled(
                700, 220,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            # Crop tengah agar pas di label (mirip object-fit: cover)
            x_offset = max(0, (scaled.width() - 700) // 2)
            y_offset = max(0, (scaled.height() - 220) // 2)
            cropped = scaled.copy(x_offset, y_offset, 700, 220)
            gambar_label.setPixmap(cropped)
 
        except Exception as e:
            # Jika gagal memuat (offline, URL salah, dsb.) tampilkan pesan pengganti
            gambar_label.setText("📷  Gambar tidak dapat dimuat")
            gambar_label.setStyleSheet(
                "border-radius: 12px; background: #e8e8e8; border: none; "
                "color: #aaa; font-size: 14px;"
            )
 
        layout.addWidget(gambar_label)

        # Latar Belakang
        lbl_lb = QLabel("Latar Belakang")
        lbl_lb.setStyleSheet("font-size: 25px; font-weight: bold; color: #67823A;")
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
        lbl_fitur = QLabel("Fitur")
        lbl_fitur.setStyleSheet("font-size: 25px; font-weight: bold; color: #67823A;")
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
        lbl_tim.setStyleSheet("font-size: 25px; font-weight: bold; color: #67823A;")
        layout.addWidget(lbl_tim)

        tim_layout = QHBoxLayout()
        anggota = [
            ("Hana Mardhiyyah"),
            ("Imam Miftahul U."),
            ("Iriyansyah Jaya A."),
            ("Lutfhilah Nurazizah"),
            ("Saiwa Zaida N."),
        ]
        for nama in anggota:
            tim_layout.addWidget(AnggotaCard(nama))
        tim_layout.addStretch()
        layout.addLayout(tim_layout)
        layout.addStretch()
