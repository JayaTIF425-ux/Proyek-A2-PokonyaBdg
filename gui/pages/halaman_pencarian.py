"""
gui/pages/halaman_pencarian.py — Pencarian & Kelola (CRUD) harga komoditas.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QScrollArea, QGridLayout,
    QFrame, QComboBox, QDialog, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from database.db_manager import DBManager
from gui.components.product_card import ProductCard
from gui.widgets.loading_widget import LoadingWidget
from gui.widgets.refresh_widget import RefreshWidget

# ── Class Dialog Form untuk Create & Update ───────────────────────
class DialogFormProduk(QDialog):
    def __init__(self, parent=None, data_awal=None):
        super().__init__(parent)
        self.setWindowTitle("Form Data Produk")
        self.setFixedSize(350, 250)
        
        self.data_awal = data_awal # Jika None -> Create, Jika ada isinya -> Update
        
        layout = QFormLayout(self)
        
        self.input_nama = QLineEdit()
        self.input_harga = QLineEdit()
        self.input_toko = QLineEdit()
        self.input_tanggal = QLineEdit()
        self.input_tanggal.setPlaceholderText("YYYY-MM-DD")
        
        # Isi form jika sedang mode Edit (Update)
        if self.data_awal:
            self.input_nama.setText(self.data_awal[1])
            self.input_harga.setText(str(self.data_awal[2]))
            self.input_toko.setText(self.data_awal[3])
            self.input_tanggal.setText(self.data_awal[4])
            
        layout.addRow("Nama Komoditas:", self.input_nama)
        layout.addRow("Harga (Rp):", self.input_harga)
        layout.addRow("Toko/Pasar:", self.input_toko)
        layout.addRow("Tanggal:", self.input_tanggal)
        
        btn_layout = QHBoxLayout()
        btn_simpan = QPushButton("Simpan")
        btn_simpan.setStyleSheet("background-color: #3498db; color: white; padding: 6px;")
        btn_simpan.clicked.connect(self.accept)
        
        btn_batal = QPushButton("Batal")
        btn_batal.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_batal)
        btn_layout.addWidget(btn_simpan)
        
        layout.addRow(btn_layout)

    def get_data(self):
        return {
            "nama": self.input_nama.text(),
            "harga": self.input_harga.text(),
            "toko": self.input_toko.text(),
            "tanggal": self.input_tanggal.text()
        }


# ── Thread Pencarian ──────────────────────────────────────────────
class CariWorker(QThread):
    selesai = pyqtSignal(list)

    def __init__(self, keyword: str):
        super().__init__()
        self.keyword = keyword

    def run(self):
        data = DBManager().cari_produk(self.keyword)
        self.selesai.emit(list(data))


# ── Halaman Utama Pencarian & CRUD ────────────────────────────────
class HalamanPencarian(QWidget):

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 12)
        layout.setSpacing(16)

        # ── Header ────────────────────────────────────────────────────────
        judul = QLabel("Kelola & Informasi Harga Bahan Pokok")
        judul.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(judul)

        # ── Filter bar ────────────────────────────────────────────────────
        filter_frame = QFrame()
        filter_frame.setStyleSheet(
            "background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 8px; padding: 8px;"
        )
        fl = QHBoxLayout(filter_frame)
        fl.setContentsMargins(12, 8, 12, 8)

        fl.addStretch()

        # Tombol cari
        self.btn_cari = QPushButton("Cari  🔍")
        self.btn_cari.setFixedHeight(36)
        self.btn_cari.setStyleSheet(
            "background-color: #6B8E23; color: white; border-radius: 6px; padding: 0 16px; font-weight: bold;"
        )
        fl.addWidget(self.btn_cari)
        
        # +++ TAMBAHAN CRUD (CREATE): Tombol Tambah Data +++
        self.btn_tambah = QPushButton("Tambah Data ➕")
        self.btn_tambah.setFixedHeight(36)
        self.btn_tambah.setStyleSheet(
            "background-color: #2980b9; color: white; border-radius: 6px; padding: 0 16px; font-weight: bold;"
        )
        fl.addWidget(self.btn_tambah)

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
        self.loading = LoadingWidget("Memproses data...")
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
        self.btn_tambah.clicked.connect(self._tambah_data) # Koneksi tombol tambah

    # ── Aksi CRUD ─────────────────────────────────────────────────────────

    def _cari(self):
        keyword = self.input_cari.text().strip()
        if not keyword:
            return

        self.loading.show()
        self._bersihkan_grid()

        self.worker = CariWorker(keyword)
        self.worker.selesai.connect(self._tampilkan_hasil)
        self.worker.start()

    def _tambah_data(self):
        """Logika CREATE Data"""
        dialog = DialogFormProduk(self)
        if dialog.exec():
            data_baru = dialog.get_data()
            # Asumsi Jaya sudah membuat fungsi tambah_produk() di DBManager
            DBManager().tambah_produk(data_baru['nama'], data_baru['harga'], data_baru['toko'], data_baru['tanggal'])
            self._cari() # Refresh tampilan setelah menambah data

    def _edit_data(self, row_data):
        """Logika UPDATE Data"""
        dialog = DialogFormProduk(self, data_awal=row_data)
        if dialog.exec():
            data_update = dialog.get_data()
            # Asumsi index 0 adalah ID produk di database
            id_produk = row_data[0] 
            # Asumsi Jaya sudah membuat fungsi update_produk() di DBManager
            DBManager().update_produk(id_produk, data_update['nama'], data_update['harga'], data_update['toko'], data_update['tanggal'])
            self._cari() # Refresh tampilan

    def _hapus_data(self, id_produk):
        """Logika DELETE Data"""
        konfirmasi = QMessageBox.question(
            self, "Konfirmasi Hapus", 
            "Apakah Anda yakin ingin menghapus data ini?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if konfirmasi == QMessageBox.StandardButton.Yes:
            # Asumsi Jaya sudah membuat fungsi hapus_produk() di DBManager
            DBManager().hapus_produk(id_produk)
            self._cari() # Refresh tampilan

    # ── Menampilkan Data ──────────────────────────────────────────────────

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
            # Asumsi format query dari Jaya: (id, nama, harga, toko, tanggal)
            card = ProductCard(
                nama=row[0], harga=row[1], toko=row[2], tanggal=row[3]
            )
            
            # --- CATATAN UNTUK HANA ---
            # Hana harus menambahkan 'btn_edit' dan 'btn_hapus' di dalam ProductCard.py
            # Jika sudah ada, Upi bisa menghubungkannya dengan fungsi CRUD di sini:
            try:
                card.btn_edit.clicked.connect(lambda checked, r=row: self._edit_data(r))
                card.btn_hapus.clicked.connect(lambda checked, id_p=row[0]: self._hapus_data(id_p))
            except AttributeError:
                pass # Jika Hana belum merenovasi ProductCard, sistem tetap aman dan tidak error
                
            self.grid.addWidget(card, i // KOLOM, i % KOLOM)

        self.lbl_info.setText(f"{len(data)} hasil ditemukan.")

    def _bersihkan_grid(self):
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)