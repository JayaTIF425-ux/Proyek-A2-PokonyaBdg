from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QGridLayout, QFrame, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QLineEdit, QAbstractItemView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor

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
        self.keranjang: dict[str, dict] = {}
        self._semua_cards: list[CalculatorCard] = []
        self.lbl_kosong: QLabel | None = None

        self._init_ui()
        self._muat_produk()

    def _init_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Panel Kiri ─────────────────────────────────────────────────────
        panel_kiri = QFrame()
        panel_kiri.setStyleSheet("background: #f0f2f5; border: none;")
        layout_kiri = QVBoxLayout(panel_kiri)
        layout_kiri.setContentsMargins(25, 25, 25, 25)

        kotak_putih = QFrame()
        kotak_putih.setStyleSheet("""
            background: white;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
        """)
        layout_isi = QVBoxLayout(kotak_putih)
        layout_isi.setContentsMargins(20, 20, 20, 20)
        layout_isi.setSpacing(12)
        layout_kiri.addWidget(kotak_putih)

        lbl_anggaran = QLabel("Estimasi Anggaran-mu")
        lbl_anggaran.setStyleSheet(
            "font-size: 16px; font-weight: 600; color: #6B8E23; background: #f1f1f1; "
            "padding: 6px 15px 10px 15px; border-radius: 8px; border: 1px solid #f1f1f1;"
        )
        lbl_anggaran.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_isi.addWidget(lbl_anggaran, alignment=Qt.AlignmentFlag.AlignCenter)

        # Tabel keranjang (read-only)
        self.tabel_keranjang = QTableWidget(0, 3)
        self.tabel_keranjang.setHorizontalHeaderLabels(["Bahan Pangan", "Jumlah", "Subtotal"])
        self.tabel_keranjang.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabel_keranjang.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.tabel_keranjang.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.tabel_keranjang.setColumnWidth(1, 90)
        self.tabel_keranjang.setColumnWidth(2, 120)
        self.tabel_keranjang.horizontalHeader().setDefaultAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        header_sub = self.tabel_keranjang.horizontalHeaderItem(2)
        if header_sub:
            header_sub.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.tabel_keranjang.verticalHeader().setVisible(False)
        self.tabel_keranjang.setFrameShape(QFrame.Shape.NoFrame)
        self.tabel_keranjang.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabel_keranjang.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.tabel_keranjang.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tabel_keranjang.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: transparent;
                border: none;
                font-size: 13px;
                color: #555;
            }
            QHeaderView::section {
                background-color: white;
                border: none;
                border-bottom: 1px solid #E0E0E0;
                padding-left: 15px;
                padding-right: 15px;
                padding-top: 10px;
                padding-bottom: 5px;
                font-weight: bold;
                color: #828282;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 10px;
                color: #6B8E23;
                border-bottom: 1px solid #E0E0E0;
            }
        """)
        layout_isi.addWidget(self.tabel_keranjang)

        # ── Tabel rekomendasi ─────────────────────────────────────────────
        lbl_rekom = QLabel("Rekomendasi Toko Terhemat")
        lbl_rekom.setStyleSheet("font-size: 14px; font-weight: 600; color: #6B8E23; border: none;")
        layout_isi.addWidget(lbl_rekom)

        self.tabel_rekom = QTableWidget(0, 3)
        self.tabel_rekom.setHorizontalHeaderLabels(["Nama Toko", "Merk & Spesifikasi Barang", "Harga"])
        self.tabel_rekom.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tabel_rekom.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabel_rekom.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tabel_rekom.verticalHeader().setVisible(False)
        self.tabel_rekom.setFrameShape(QFrame.Shape.NoFrame)
        self.tabel_rekom.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabel_rekom.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.tabel_rekom.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tabel_rekom.setMinimumHeight(170)
        self.tabel_rekom.setStyleSheet("""
            QTableWidget {
                background: white;
                border: none;
                font-size: 12px;
                color: #444;
            }
            QHeaderView::section {
                background: #fafafa;
                border: none;
                border-bottom: 1px solid #E0E0E0;
                padding: 8px;
                font-weight: bold;
                color: #777;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F0F0F0;
            }
        """)
        layout_isi.addWidget(self.tabel_rekom)

        # Total
        self.lbl_total = QLabel("Total: Rp 0")
        self.lbl_total.setStyleSheet(
            "background-color: #6B8E23; color: white; font-size: 16px; "
            "font-weight: bold; padding: 14px; border-radius: 6px;"
        )
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_isi.addWidget(self.lbl_total)

        layout_isi.addSpacing(6)

        btn_reset = QPushButton("🗑  Reset Keranjang")
        btn_reset.setStyleSheet("background: #e74c3c; color: white; padding: 8px; border-radius: 6px;")
        btn_reset.clicked.connect(self._reset_keranjang)
        layout_isi.addWidget(btn_reset)

        # ── Panel Kanan ────────────────────────────────────────────────────
        panel_kanan = QWidget()
        layout_kanan = QVBoxLayout(panel_kanan)
        layout_kanan.setContentsMargins(16, 16, 16, 16)
        layout_kanan.setSpacing(12)

        header_kanan = QHBoxLayout()
        lbl_mau = QLabel("Mau Belanja Apa Hari Ini?")
        lbl_mau.setStyleSheet("font-size: 16px; font-weight: 550; color: #6B8E23")
        self.input_filter = QLineEdit()
        self.input_filter.setPlaceholderText("Filter produk...")
        self.input_filter.setStyleSheet("padding: 6px; border: 1px solid #ccc; border-radius: 4px;")
        self.input_filter.textChanged.connect(self._filter_produk)
        header_kanan.addWidget(lbl_mau)
        header_kanan.addStretch()
        header_kanan.addWidget(self.input_filter)
        layout_kanan.addLayout(header_kanan)

        self.loading_kanan = LoadingWidget("Memuat produk...")
        layout_kanan.addWidget(self.loading_kanan)

        self.refresh_bar = RefreshWidget()
        self.refresh_bar.refresh_diminta.connect(self._muat_produk)
        layout_kanan.addWidget(self.refresh_bar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        self.grid_container = QWidget()
        self.grid = QGridLayout(self.grid_container)
        self.grid.setSpacing(12)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(self.grid_container)
        layout_kanan.addWidget(scroll)

        root.addWidget(panel_kiri, 5)
        root.addWidget(panel_kanan, 5)

    # ── Load Data ─────────────────────────────────────────────────────────

    def _muat_produk(self):
        self.worker = KalkulatorWorker()
        self.worker.selesai.connect(self._tampilkan_produk)
        self.worker.start()

    def _tampilkan_produk(self, data: list):
        self.loading_kanan.hide()

        # Lepas card lama dari grid
        for card in self._semua_cards:
            self.grid.removeWidget(card)
            card.deleteLater()
        self._semua_cards = []

        # Bersihkan item non-card
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        produk_dict: dict[str, dict] = {}
        for row in data:
            nama = row[0]
            kategori = row[1]
            harga = row[2]
            toko = row[3]
            gambar_url = row[4] if len(row) > 4 else None

            if nama not in produk_dict:
                produk_dict[nama] = {
                    "kategori": kategori,
                    "harga_toko": {},
                    "gambar_url": gambar_url,
                }
            produk_dict[nama]["harga_toko"][toko] = harga

        for nama, info in produk_dict.items():
            harga_min = min(info["harga_toko"].values()) if info["harga_toko"] else 0
            card = CalculatorCard(
                nama=nama,
                harga=harga_min,
                harga_per_toko=info["harga_toko"],
                callback_update=self._update_keranjang,
                gambar_url=info.get("gambar_url"),
            )
            self._semua_cards.append(card)

        self._susun_grid_produk(self._semua_cards, kolom=2)

    # ── Grid Produk ───────────────────────────────────────────────────────

    def _susun_grid_produk(self, cards: list[CalculatorCard], kolom: int = 2):
        # Lepas semua card dari grid dulu + sembunyikan
        for card in self._semua_cards:
            self.grid.removeWidget(card)
            card.setVisible(False)

        # Bersihkan item non-card
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w and w not in self._semua_cards:
                w.deleteLater()

        self.lbl_kosong = None

        # Tambahkan lagi hasil filter dari index 0 -> selalu kiri-atas
        for i, card in enumerate(cards):
            row = i // kolom
            col = i % kolom
            self.grid.addWidget(card, row, col)
            card.setVisible(True)

        if not cards:
            self.lbl_kosong = QLabel("Produk tidak ditemukan")
            self.lbl_kosong.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lbl_kosong.setStyleSheet("color: #999; padding: 30px; font-size: 13px;")
            self.grid.addWidget(self.lbl_kosong, 0, 0, 1, kolom)

        self.grid_container.updateGeometry()
        self.grid_container.adjustSize()

    # ── Keranjang ─────────────────────────────────────────────────────────

    def _update_keranjang(self, nama: str, harga_per_toko: dict, qty: int):
        if qty == 0:
            self.keranjang.pop(nama, None)
        else:
            self.keranjang[nama] = {"harga_per_toko": harga_per_toko, "qty": qty}
        self._refresh_tabel_keranjang()

    def _buat_item_readonly(self, text: str, align: Qt.AlignmentFlag | None = None):
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        if align is not None:
            item.setTextAlignment(align)
        return item

    def _refresh_tabel_keranjang(self):
        self.tabel_keranjang.setRowCount(0)
        grand_total = 0

        for baris, (nama, info) in enumerate(self.keranjang.items()):
            qty = info["qty"]
            harga = min(info["harga_per_toko"].values()) if info["harga_per_toko"] else 0
            subtot = harga * qty

            self.tabel_keranjang.insertRow(baris)
            self.tabel_keranjang.setRowHeight(baris, 40)

            self.tabel_keranjang.setItem(baris, 0, self._buat_item_readonly(nama))
            self.tabel_keranjang.setItem(baris, 1, self._buat_item_readonly(f"× {qty}"))
            self.tabel_keranjang.setItem(
                baris,
                2,
                self._buat_item_readonly(
                    f"Rp {subtot:,.0f}".replace(",", "."),
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                ),
            )

            grand_total += subtot

        self.lbl_total.setText(f"Total: Rp {grand_total:,.0f}".replace(",", "."))
        self._refresh_tabel_rekomendasi()

    def _refresh_tabel_rekomendasi(self):
        self.tabel_rekom.setRowCount(0)

        if not self.keranjang:
            return

        # 1 barang: list toko yang jual barang tsb, urut termurah
        if len(self.keranjang) == 1:
            nama_barang, info = next(iter(self.keranjang.items()))
            data = sorted(info["harga_per_toko"].items(), key=lambda x: x[1])
            if not data:
                return

            harga_terendah = data[0][1]
            for row_idx, (toko, harga) in enumerate(data):
                self.tabel_rekom.insertRow(row_idx)
                self.tabel_rekom.setItem(row_idx, 0, self._buat_item_readonly(toko))
                self.tabel_rekom.setItem(row_idx, 1, self._buat_item_readonly(nama_barang))
                self.tabel_rekom.setItem(
                    row_idx,
                    2,
                    self._buat_item_readonly(
                        f"Rp {harga:,.0f}".replace(",", "."),
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                    ),
                )
                if harga == harga_terendah:
                    self._highlight_row(row_idx)
            return

        # banyak barang: bandingkan total antar toko yang menjual SEMUA barang di keranjang
        semua_toko = set()
        for info in self.keranjang.values():
            semua_toko.update(info["harga_per_toko"].keys())

        total_per_toko: list[tuple[str, int, str]] = []
        for toko in semua_toko:
            total = 0
            daftar_barang = []
            valid = True

            for nama_barang, info in self.keranjang.items():
                qty = info["qty"]
                harga_toko = info["harga_per_toko"].get(toko)
                if harga_toko is None:
                    valid = False
                    break

                total += harga_toko * qty
                daftar_barang.append(f"{nama_barang} ×{qty}")

            if valid:
                total_per_toko.append((toko, total, ", ".join(daftar_barang)))

        total_per_toko.sort(key=lambda x: x[1])

        if not total_per_toko:
            self.tabel_rekom.insertRow(0)
            self.tabel_rekom.setItem(0, 0, self._buat_item_readonly("-"))
            self.tabel_rekom.setItem(0, 1, self._buat_item_readonly("Tidak ada toko yang menjual semua barang"))
            self.tabel_rekom.setItem(0, 2, self._buat_item_readonly("-"))
            return

        termurah = total_per_toko[0][1]
        for row_idx, (toko, total, detail) in enumerate(total_per_toko):
            self.tabel_rekom.insertRow(row_idx)
            self.tabel_rekom.setItem(row_idx, 0, self._buat_item_readonly(toko))
            self.tabel_rekom.setItem(row_idx, 1, self._buat_item_readonly(detail))
            self.tabel_rekom.setItem(
                row_idx,
                2,
                self._buat_item_readonly(
                    f"Rp {total:,.0f}".replace(",", "."),
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                ),
            )
            if total == termurah:
                self._highlight_row(row_idx)

    def _highlight_row(self, row_idx: int):
        for col in range(self.tabel_rekom.columnCount()):
            item = self.tabel_rekom.item(row_idx, col)
            if item:
                item.setBackground(QColor("#E8F7E8"))
                if col == 2:
                    item.setForeground(QColor("#1B8A3A"))
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)

    def _reset_keranjang(self):
        self.keranjang.clear()
        for card in self._semua_cards:
            card.reset_qty()
        self._refresh_tabel_keranjang()

    # ── Filter ────────────────────────────────────────────────────────────

    def _filter_produk(self, keyword: str):
        kw = keyword.lower().strip()
        if not kw:
            hasil = self._semua_cards
        else:
            hasil = [card for card in self._semua_cards if kw in card.nama.lower()]

        self._susun_grid_produk(hasil, kolom=2)