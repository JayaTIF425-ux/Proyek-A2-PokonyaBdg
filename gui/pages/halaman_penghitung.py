"""
gui/pages/halaman_penghitung.py — Kalkulator Belanja:
  User memilih produk + qty → sistem hitung estimasi total per toko
  dan merekomendasikan toko paling hemat.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QGridLayout, QFrame, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QLineEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont

from database.db_manager import DBManager
from gui.components.calculator_card import CalculatorCard
from gui.widgets.loading_widget import LoadingWidget
from gui.widgets.refresh_widget import RefreshWidget


class KalkulatorWorker(QThread):
    selesai = pyqtSignal(list)

    def run(self):
        data = DBManager().fetch_produk_untuk_kalkulator()
        self.selesai.emit(list(data))


class HalamanPenghitung(QWidget):

    def __init__(self):
        super().__init__()
        # keranjang: {nama_produk: {harga_per_toko: {toko: harga}, qty: int}}
        self.keranjang: dict[str, dict] = {}
        self._init_ui()
        self._muat_produk()

    def _init_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Panel Kiri: Anggaran ──────────────────────────────────────────
        panel_kiri = QFrame()
        panel_kiri.setStyleSheet("background: #fafafa; border-right: 1px solid #e0e0e0;")
        layout_kiri = QVBoxLayout(panel_kiri)
        layout_kiri.setContentsMargins(16, 16, 16, 16)
        layout_kiri.setSpacing(12)

        lbl_anggaran = QLabel("Estimasi Anggaran")
        lbl_anggaran.setStyleSheet(
            "font-size: 16px; font-weight: bold; background: #f1f1f1; "
            "padding: 10px; border-radius: 6px;"
        )
        lbl_anggaran.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_kiri.addWidget(lbl_anggaran)

        # Tabel keranjang
        self.tabel_keranjang = QTableWidget(0, 3)
        self.tabel_keranjang.setHorizontalHeaderLabels(["Bahan Pangan", "Qty", "Subtotal"])
        self.tabel_keranjang.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabel_keranjang.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tabel_keranjang.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tabel_keranjang.setStyleSheet("background: white; border-radius: 6px;")
        self.tabel_keranjang.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout_kiri.addWidget(self.tabel_keranjang)

        # Total
        self.lbl_total = QLabel("Total: Rp 0")
        self.lbl_total.setStyleSheet(
            "background-color: #6B8E23; color: white; font-size: 16px; "
            "font-weight: bold; padding: 14px; border-radius: 6px;"
        )
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_kiri.addWidget(self.lbl_total)

        # ── Perbandingan Toko ─────────────────────────────────────────────
        lbl_compare = QLabel("Rekomendasi Toko Terhemat")
        lbl_compare.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 8px;")
        layout_kiri.addWidget(lbl_compare)

        self.tabel_toko = QTableWidget(0, 3)
        self.tabel_toko.setHorizontalHeaderLabels(["Toko", "Est. Total", "Item Tersedia"])
        self.tabel_toko.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabel_toko.setMaximumHeight(180)
        self.tabel_toko.setStyleSheet("background: white; border-radius: 6px;")
        self.tabel_toko.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout_kiri.addWidget(self.tabel_toko)

        btn_reset = QPushButton("🗑  Reset Keranjang")
        btn_reset.setStyleSheet(
            "background: #e74c3c; color: white; padding: 8px; border-radius: 6px;"
        )
        btn_reset.clicked.connect(self._reset_keranjang)
        layout_kiri.addWidget(btn_reset)

        # ── Panel Kanan: Daftar Produk ────────────────────────────────────
        panel_kanan = QWidget()
        layout_kanan = QVBoxLayout(panel_kanan)
        layout_kanan.setContentsMargins(16, 16, 16, 16)
        layout_kanan.setSpacing(12)

        header_kanan = QHBoxLayout()
        lbl_mau = QLabel("Mau Belanja Apa Hari Ini?")
        lbl_mau.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.input_filter = QLineEdit()
        self.input_filter.setPlaceholderText("Filter produk...")
        self.input_filter.setFixedWidth(200)
        self.input_filter.setStyleSheet("padding: 6px; border: 1px solid #ccc; border-radius: 4px;")
        self.input_filter.textChanged.connect(self._filter_produk)
        header_kanan.addWidget(lbl_mau)
        header_kanan.addStretch()
        header_kanan.addWidget(self.input_filter)
        layout_kanan.addLayout(header_kanan)

        self.loading_kanan = LoadingWidget("Memuat produk...")
        layout_kanan.addWidget(self.loading_kanan)

        # ── Refresh / Update toolbar ──────────────────────────────────────
        self.refresh_bar = RefreshWidget()
        self.refresh_bar.refresh_diminta.connect(self._muat_produk)
        layout_kanan.addWidget(self.refresh_bar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        self.grid_container = QWidget()
        self.grid = QGridLayout(self.grid_container)
        self.grid.setSpacing(10)
        scroll.setWidget(self.grid_container)
        layout_kanan.addWidget(scroll)

        # Rakit layout utama: kiri 40%, kanan 60%
        root.addWidget(panel_kiri, 4)
        root.addWidget(panel_kanan, 6)

        self._semua_cards: list[CalculatorCard] = []

    # ── Load Data ─────────────────────────────────────────────────────────

    def _muat_produk(self):
        self.worker = KalkulatorWorker()
        self.worker.selesai.connect(self._tampilkan_produk)
        self.worker.start()

    def _tampilkan_produk(self, data: list):
        self.loading_kanan.hide()

        # Kelompokkan produk: ambil harga rata-rata per nama produk
        produk_dict: dict[str, dict] = {}
        for row in data:
            nama    = row[0]
            kategori = row[1]
            harga   = row[2]
            toko    = row[3]
            if nama not in produk_dict:
                produk_dict[nama] = {"kategori": kategori, "harga_toko": {}}
            produk_dict[nama]["harga_toko"][toko] = harga

        KOLOM = 2
        self._semua_cards = []
        for i, (nama, info) in enumerate(produk_dict.items()):
            # Gunakan harga terendah sebagai tampilan utama
            harga_min = min(info["harga_toko"].values()) if info["harga_toko"] else 0
            card = CalculatorCard(
                nama=nama,
                harga=harga_min,
                harga_per_toko=info["harga_toko"],
                callback_update=self._update_keranjang,
            )
            self._semua_cards.append(card)
            self.grid.addWidget(card, i // KOLOM, i % KOLOM)

        if not produk_dict:
            lbl = QLabel("Belum ada data produk. Jalankan scraper.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: #999; padding: 40px;")
            self.grid.addWidget(lbl, 0, 0)

    # ── Keranjang ─────────────────────────────────────────────────────────

    def _update_keranjang(self, nama: str, harga_per_toko: dict, qty: int):
        if qty == 0:
            self.keranjang.pop(nama, None)
        else:
            self.keranjang[nama] = {"harga_per_toko": harga_per_toko, "qty": qty}
        self._refresh_tabel_keranjang()
        self._refresh_rekomendasi_toko()

    def _refresh_tabel_keranjang(self):
        self.tabel_keranjang.setRowCount(0)
        grand_total = 0

        for baris, (nama, info) in enumerate(self.keranjang.items()):
            qty    = info["qty"]
            # Harga terendah dari semua toko
            harga  = min(info["harga_per_toko"].values()) if info["harga_per_toko"] else 0
            subtot = harga * qty

            self.tabel_keranjang.insertRow(baris)
            self.tabel_keranjang.setItem(baris, 0, QTableWidgetItem(nama))
            self.tabel_keranjang.setItem(baris, 1, QTableWidgetItem(f"{qty} kg"))

            item_sub = QTableWidgetItem(f"Rp {subtot:,.0f}".replace(",", "."))
            item_sub.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabel_keranjang.setItem(baris, 2, item_sub)

            grand_total += subtot

        self.lbl_total.setText(f"Total: Rp {grand_total:,.0f}".replace(",", "."))

    def _refresh_rekomendasi_toko(self):
        """Hitung estimasi total per toko untuk semua item di keranjang."""
        if not self.keranjang:
            self.tabel_toko.setRowCount(0)
            return

        # Kumpulkan estimasi per toko
        estimasi_toko: dict[str, float] = {}
        item_count: dict[str, int] = {}

        for nama, info in self.keranjang.items():
            qty = info["qty"]
            for toko, harga in info["harga_per_toko"].items():
                estimasi_toko[toko] = estimasi_toko.get(toko, 0) + harga * qty
                item_count[toko] = item_count.get(toko, 0) + 1

        # Urutkan dari terhemat
        urut = sorted(estimasi_toko.items(), key=lambda x: x[1])

        self.tabel_toko.setRowCount(0)
        for baris, (toko, total) in enumerate(urut):
            self.tabel_toko.insertRow(baris)

            # Tandai toko terhemat dengan warna hijau
            warna = QColor("#d5f5e3") if baris == 0 else QColor("white")

            item_toko = QTableWidgetItem(f"{'🏆 ' if baris == 0 else ''}{toko}")
            item_toko.setBackground(warna)

            item_total = QTableWidgetItem(f"Rp {total:,.0f}".replace(",", "."))
            item_total.setBackground(warna)
            item_total.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            item_count_cell = QTableWidgetItem(f"{item_count.get(toko, 0)} item")
            item_count_cell.setBackground(warna)
            item_count_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.tabel_toko.setItem(baris, 0, item_toko)
            self.tabel_toko.setItem(baris, 1, item_total)
            self.tabel_toko.setItem(baris, 2, item_count_cell)

    def _reset_keranjang(self):
        self.keranjang.clear()
        for card in self._semua_cards:
            card.reset_qty()
        self._refresh_tabel_keranjang()
        self.tabel_toko.setRowCount(0)

    # ── Filter ────────────────────────────────────────────────────────────

    def _filter_produk(self, keyword: str):
        kw = keyword.lower()
        for card in self._semua_cards:
            visible = kw in card.nama.lower() if kw else True
            card.setVisible(visible)