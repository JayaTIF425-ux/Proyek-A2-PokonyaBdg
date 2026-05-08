"""
gui/pages/halaman_beranda.py — Halaman beranda: ringkasan harga + perubahan.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QGridLayout, QFrame, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from database.db_manager import DBManager
from gui.components.product_card import ProductCard
from gui.components.price_chart import PriceChartWidget
from gui.widgets.loading_widget import LoadingWidget
from gui.widgets.refresh_widget import RefreshWidget


class DataWorker(QThread):
    selesai = pyqtSignal(list)

    def run(self):
        data = DBManager().fetch_semua_produk_pihps()
        self.selesai.emit(list(data))


class HalamanBeranda(QWidget):

    # ← TAMBAH signal ini — diteruskan ke MainWindow
    navigasi_pencarian = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._init_ui()
        self._muat_data()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 12)
        layout.setSpacing(16)

        # ── Header ────────────────────────────────────────────────────────
        header = QHBoxLayout()
        judul = QLabel("Harga Rata-Rata dan Perubahan")
        judul.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        header.addWidget(judul)
        header.addStretch()

        lbl_filter = QLabel("Jenis pasar:")
        lbl_filter.setStyleSheet("font-size: 13px; color: #666;")
        self.combo_pasar = QComboBox()
        self.combo_pasar.addItems(["Pasar Tradisional/Modern", "Pasar Tradisional", "Pasar Modern"])
        self.combo_pasar.setFixedWidth(220)
        self.combo_pasar.setStyleSheet(
            "padding: 4px 8px; border: 1px solid #ccc; border-radius: 4px;"
        )
        header.addWidget(lbl_filter)
        header.addWidget(self.combo_pasar)
        layout.addLayout(header)

        # ── Refresh bar ───────────────────────────────────────────────────
        self.refresh_bar = RefreshWidget()
        self.refresh_bar.refresh_diminta.connect(self._muat_data)
        self.refresh_bar.update_selesai.connect(
            lambda ok: self.lbl_info.setText(
                "✓ Data berhasil diperbarui!" if ok else "✗ Update gagal."
            )
        )
        layout.addWidget(self.refresh_bar)

        # ── Grafik tren harga ─────────────────────────────────────────────
        self.chart = PriceChartWidget()
        self.chart.setFixedHeight(310)
        layout.addWidget(self.chart)

        # ── Grid kartu komoditas ──────────────────────────────────────────
        self.loading = LoadingWidget("Memuat data harga...")

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none; background: transparent;")

        self.grid_container = QWidget()
        self.grid = QGridLayout(self.grid_container)
        self.grid.setSpacing(12)
        self.scroll.setWidget(self.grid_container)

        layout.addWidget(self.loading)
        layout.addWidget(self.scroll)

        self.lbl_info = QLabel("")
        self.lbl_info.setStyleSheet("color: #888; font-size: 11px; padding: 4px;")
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_info)

    def _muat_data(self):
        self.loading.show()
        self.scroll.hide()
        self.worker = DataWorker()
        self.worker.selesai.connect(self._tampilkan_data)
        self.worker.start()

    def _tampilkan_data(self, data: list):
        self.loading.hide()
        self.scroll.show()
        self.chart.refresh()

        # Bersihkan grid lama
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)

        if not data:
            lbl = QLabel("Belum ada data. Jalankan scraper terlebih dahulu.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: #999; font-size: 14px; padding: 40px;")
            self.grid.addWidget(lbl, 0, 0)
            return

        KOLOM = 3
        for i, row in enumerate(data):
            card = ProductCard(
                nama=row["komoditas"] if hasattr(row, "keys") else row[0],
                harga=row["harga"]    if hasattr(row, "keys") else row[1],
                toko=row["toko"]      if hasattr(row, "keys") else row[2],
                tanggal=row["tanggal"] if hasattr(row, "keys") else row[3],
            )

            card.lihat_pencarian.connect(self.navigasi_pencarian)

            self.grid.addWidget(card, i // KOLOM, i % KOLOM)

        self.lbl_info.setText(
            f"Menampilkan {len(data)} komoditas · Sumber: PIHPS Bandung"
        )