"""
gui/pages/halaman_pencarian.py — Pencarian harga per komoditas dari semua sumber.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QScrollArea, QGridLayout,
    QFrame, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from database.db_manager import DBManager
from gui.components.product_card import ProductCard
from gui.widgets.loading_widget import LoadingWidget
from gui.widgets.refresh_widget import RefreshWidget


class CariWorker(QThread):
    selesai = pyqtSignal(list)

    def __init__(self, keyword: str):
        super().__init__()
        self.keyword = keyword

    def run(self):
        data = DBManager().cari_produk(self.keyword)
        self.selesai.emit(list(data))


class HalamanPencarian(QWidget):

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 12)
        layout.setSpacing(16)

        # ── Header ────────────────────────────────────────────────────────
        judul = QLabel("Informasi Harga Bahan Pokok")
        judul.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(judul)

        # ── Filter bar ────────────────────────────────────────────────────
        filter_frame = QFrame()
        filter_frame.setStyleSheet(
            "background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 8px; padding: 8px;"
        )
        fl = QHBoxLayout(filter_frame)
        fl.setContentsMargins(12, 8, 12, 8)

        # Komoditas
        fl.addWidget(QLabel("Komoditas"))
        self.combo_komoditas = QComboBox()
        self.combo_komoditas.addItem("bahan pokok")
        self.combo_komoditas.setFixedWidth(160)
        fl.addWidget(self.combo_komoditas)

        # Jenis info
        fl.addWidget(QLabel("Jenis Informasi Harga"))
        self.combo_jenis = QComboBox()
        self.combo_jenis.addItems(["harga", "stok", "perubahan"])
        self.combo_jenis.setFixedWidth(130)
        fl.addWidget(self.combo_jenis)

        # Jenis pasar
        fl.addWidget(QLabel("Jenis pasar"))
        self.combo_pasar = QComboBox()
        self.combo_pasar.addItem("pasar")
        self.combo_pasar.setFixedWidth(120)
        fl.addWidget(self.combo_pasar)

        # Tanggal
        fl.addWidget(QLabel("Tanggal"))
        self.combo_tanggal = QComboBox()
        self.combo_tanggal.addItem("tgl/bln/thn")
        self.combo_tanggal.setFixedWidth(120)
        fl.addWidget(self.combo_tanggal)

        fl.addStretch()

        # Tombol cari
        self.btn_cari = QPushButton("Cari  🔍")
        self.btn_cari.setFixedHeight(36)
        self.btn_cari.setStyleSheet(
            "background-color: #6B8E23; color: white; border-radius: 6px; "
            "padding: 0 16px; font-weight: bold;"
        )
        fl.addWidget(self.btn_cari)

        layout.addWidget(filter_frame)

        # ── Search box teks bebas ──────────────────────────────────────────
        self.input_cari = QLineEdit()
        self.input_cari.setPlaceholderText("Ketik nama komoditas (misal: Beras, Telur, Bawang Merah)...")
        self.input_cari.setStyleSheet(
            "padding: 10px 14px; border: 1px solid #ccc; border-radius: 6px; font-size: 14px;"
        )
        layout.addWidget(self.input_cari)

        # ── Refresh / Update toolbar ──────────────────────────────────────
        self.refresh_bar = RefreshWidget()
        self.refresh_bar.refresh_diminta.connect(self._bersihkan_grid)
        layout.addWidget(self.refresh_bar)

        # ── Loading ───────────────────────────────────────────────────────
        self.loading = LoadingWidget("Mencari data...")
        self.loading.hide()
        layout.addWidget(self.loading)

        # ── Hasil pencarian ───────────────────────────────────────────────
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none;")

        self.grid_container = QWidget()
        self.grid = QGridLayout(self.grid_container)
        self.grid.setSpacing(12)
        self.scroll.setWidget(self.grid_container)
        layout.addWidget(self.scroll)

        # Footer
        self.lbl_info = QLabel("Masukkan kata kunci untuk mencari harga dari semua sumber.")
        self.lbl_info.setStyleSheet("color: #888; font-size: 11px; padding: 4px;")
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_info)

        # Koneksi
        self.btn_cari.clicked.connect(self._cari)
        self.input_cari.returnPressed.connect(self._cari)

    # ── Aksi ──────────────────────────────────────────────────────────────

    def _cari(self):
        keyword = self.input_cari.text().strip()
        if not keyword:
            return

        self.loading.show()
        self._bersihkan_grid()

        self.worker = CariWorker(keyword)
        self.worker.selesai.connect(self._tampilkan_hasil)
        self.worker.start()

    def _tampilkan_hasil(self, data: list):
        self.loading.hide()
        self._bersihkan_grid()

        if not data:
            lbl = QLabel(f"Tidak ditemukan data untuk kata kunci tersebut.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: #999; font-size: 14px; padding: 40px;")
            self.grid.addWidget(lbl, 0, 0)
            self.lbl_info.setText("0 hasil ditemukan.")
            return

        KOLOM = 3
        for i, row in enumerate(data):
            card = ProductCard(
                nama=row[0], harga=row[1], toko=row[2], tanggal=row[3]
            )
            self.grid.addWidget(card, i // KOLOM, i % KOLOM)

        self.lbl_info.setText(f"{len(data)} hasil ditemukan.")

    def _bersihkan_grid(self):
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)