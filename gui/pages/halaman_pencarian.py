"""
gui/pages/halaman_pencarian.py — Pencarian & Kelola (CRUD) harga komoditas.
Tombol Tambah Data, Edit, dan Hapus hanya tampil untuk admin.
"""

import os
from datetime import date

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QScrollArea, QGridLayout,
    QFrame, QDialog, QFormLayout, QMessageBox,
    QFileDialog, QSizePolicy, QDateEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QByteArray, QDate
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QPainter

from database.db_manager import DBManager
from gui.components.search_card import SearchCard
from gui.widgets.loading_widget import LoadingWidget
from gui.widgets.refresh_widget import RefreshWidget

def _svg_to_icon(svg_str: str, size: int = 20) -> QIcon:
    renderer = QSvgRenderer(QByteArray(svg_str.encode()))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)

_IKON_PENCARIAN = {
    "cari": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21 21-4.34-4.34"/><circle cx="11" cy="11" r="8"/></svg>""",

    "lihat_semua": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M12 11h4"/><path d="M12 16h4"/><path d="M8 11h.01"/><path d="M8 16h.01"/></svg>""",

    "tambah": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 12h8"/><path d="M12 8v8"/></svg>""",

    "ekspor": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/><path d="M12 10v6"/><path d="m15 13-3 3-3-3"/></svg>""",
}

# ── Dialog Form (Create & Update) ──────────────────────────────────────────

class DialogFormProduk(QDialog):
    def __init__(self, parent=None, data_awal: dict = None):
        super().__init__(parent)
        self.data_awal = data_awal or {}
        mode = "Edit Data" if data_awal else "Tambah Data Baru"
        
        self.setWindowTitle(mode)
        # 1. Menghapus setFixedSize yang terlalu sempit, diganti dengan minimum size yang ideal
        self.setMinimumSize(450, 420) 
        self.setStyleSheet("background-color: #ffffff; font-family: 'Segoe UI', Arial, sans-serif;")

        # Layout Utama
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Judul Form
        judul = QLabel(mode)
        judul.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(judul)

        # Garis Pembatas (Separator)
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #eaeded; background-color: #eaeded; max-height: 1px;")
        layout.addWidget(sep)

        # Form Layout
        form = QFormLayout()
        form.setSpacing(12)  # Jarak antar baris form
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Fungsi pembuat QLineEdit dengan style yang diperbaiki
        def buat_input(placeholder=""):
            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            inp.setStyleSheet(
                "QLineEdit {"
                "   padding: 6px 10px;"  # Padding disesuaikan agar teks tidak terpotong
                "   border: 1px solid #ccd1d1;"
                "   border-radius: 6px;"
                "   font-size: 13px;"
                "   color: #2c3e50;"
                "}"
                "QLineEdit:focus {"
                "   border: 1px solid #3498db;"
                "}"
            )
            return inp

        # Inisialisasi Input
        self.inp_nama     = buat_input("misal: Beras Premium")
        self.inp_harga    = buat_input("misal: 15000")
        self.inp_toko     = buat_input("misal: Yogya, Borma, ...")
        self.inp_kategori = buat_input("misal: Beras, Sayuran, ...")
        self.inp_satuan   = buat_input("misal: kg, liter, pcs")
        
        # Mengubah tanggal menjadi QDateEdit agar lebih rapi dan user-friendly
        self.inp_tanggal  = QDateEdit()
        self.inp_tanggal.setCalendarPopup(True)
        self.inp_tanggal.setDisplayFormat("yyyy-MM-dd")

        self.inp_tanggal.setMaximumDate(QDate.currentDate())
        
        # Ambil widget kalender internalnya untuk dipasang stylesheet khusus
        kalender = self.inp_tanggal.calendarWidget()
        if kalender:
            # Memaksa navigasi atas (bulan & tahun) menggunakan teks gelap
            kalender.setStyleSheet(
                "QCalendarWidget QWidget#qt_calendar_navigationbar {"
                "   background-color: #f8fafc;"
                "}"
                "QCalendarWidget QWidget {"
                "   color: #2c3e50;" # Memastikan semua teks kalender berwarna gelap
                "}"
            )

        self.inp_tanggal.setStyleSheet(
            "QDateEdit {"
            "   padding: 6px 10px;"
            "   border: 1px solid #ccd1d1;"
            "   border-radius: 6px;"
            "   font-size: 13px;"
            "   color: #2c3e50;"
            "}"
        )

        self.inp_tanggal.setStyleSheet(
            "QDateEdit {"
            "   padding: 6px 10px;"
            "   border: 1px solid #ccd1d1;"
            "   border-radius: 6px;"
            "   font-size: 13px;"
            "}"
        )

        # Set Data Awal / Default
        if data_awal:
            self.inp_nama.setText(str(data_awal.get("nama", "")))
            self.inp_harga.setText(str(data_awal.get("harga", "")))
            self.inp_toko.setText(str(data_awal.get("toko", "")))
            self.inp_kategori.setText(str(data_awal.get("kategori", "")))
            self.inp_satuan.setText(str(data_awal.get("satuan", "kg")))
            
            tgl_str = data_awal.get("tanggal", date.today().isoformat())
            self.inp_tanggal.setDate(date.fromisoformat(tgl_str))
        else:
            self.inp_tanggal.setDate(date.today())
            self.inp_satuan.setText("kg")

        # Menambahkan ke Form dengan label bergaya semi-bold
        label_style = "font-size: 13px; color: #34495e; font-weight: 500;"
        for teks_label, widget in [
            ("Nama Produk *:", self.inp_nama),
            ("Harga (Rp) *:",  self.inp_harga),
            ("Toko/Pasar *:",  self.inp_toko),
            ("Kategori:",       self.inp_kategori),
            ("Satuan:",         self.inp_satuan),
            ("Tanggal:",        self.inp_tanggal)
        ]:
            lbl = QLabel(teks_label)
            lbl.setStyleSheet(label_style)
            form.addRow(lbl, widget)
            
        layout.addLayout(form)
        layout.addSpacing(10) # Beri sedikit jarak sebelum tombol

        # Tombol Aksi
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        btn_batal = QPushButton("Batal")
        btn_batal.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_batal.setStyleSheet(
            "QPushButton {"
            "   padding: 8px 24px; border: 1px solid #cbd5e1; border-radius: 6px; "
            "   background: #ffffff; color: #475569; font-size: 13px; font-weight: 500;"
            "}"
            "QPushButton:hover { background: #f8fafc; border-color: #94a3b8; }"
        )
        btn_batal.clicked.connect(self.reject)

        warna_ok = "#e67e22" if data_awal else "#2ecc71"
        warna_ok_hover = "#d35400" if data_awal else "#27ae60"
        teks_ok  = "💾 Simpan Perubahan" if data_awal else "✅ Tambah Data"
        
        btn_simpan = QPushButton(teks_ok)
        btn_simpan.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_simpan.setStyleSheet(
            "QPushButton {"
            f"   padding: 8px 24px; border-radius: 6px; background: {warna_ok}; "
            "   color: white; font-size: 13px; font-weight: bold; border: none;"
            "}"
            f"QPushButton:hover {{ background: {warna_ok_hover}; }}"
        )
        btn_simpan.clicked.connect(self._validasi_dan_accept)

        btn_row.addStretch()
        btn_row.addWidget(btn_batal)
        btn_row.addWidget(btn_simpan)
        layout.addLayout(btn_row)

    def _validasi_dan_accept(self):
        if not self.inp_nama.text().strip():
            QMessageBox.warning(self, "Validasi", "Nama produk tidak boleh kosong!")
            return
        
        tanggal_input = self.inp_tanggal.date()
        tanggal_hari_ini = QDate.currentDate()

        if tanggal_input > tanggal_hari_ini:
            QMessageBox.warning(
                self, 
                "Validasi Tanggal", 
                "Tanggal tidak boleh melebihi hari ini! Anda tidak bisa menginput data masa depan."
            )
            return

        try:
            float(self.inp_harga.text().replace(".", "").replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Validasi", "Harga harus berupa angka!")
            return
        if not self.inp_toko.text().strip():
            QMessageBox.warning(self, "Validasi", "Nama toko tidak boleh kosong!")
            return
        self.accept()

    def get_data(self) -> dict:
        harga_str = self.inp_harga.text().replace(".", "").replace(",", ".")
        return {
            "nama":     self.inp_nama.text().strip(),
            "harga":    float(harga_str),
            "toko":     self.inp_toko.text().strip(),
            "kategori": self.inp_kategori.text().strip(),
            "satuan":   self.inp_satuan.text().strip() or "kg",
            "tanggal":  self.inp_tanggal.date().toPyDate().isoformat(), # Disesuaikan dengan QDateEdit
        }


# ── Worker Threads ─────────────────────────────────────────────────────────

class CariWorker(QThread):
    selesai = pyqtSignal(list)

    def __init__(self, keyword: str, exclude: str = ""):
        super().__init__()
        self.keyword = keyword
        self.exclude = exclude

    def run(self):
        data = DBManager().cari_produk_dengan_id(self.keyword, exclude=self.exclude)
        self.selesai.emit(list(data))

class SemuaDataWorker(QThread):
    selesai = pyqtSignal(list)

    def run(self):
        data = DBManager().fetch_semua_produk_supermarket()
        self.selesai.emit(list(data))


# ── Mapping keyword ────────────────────────────────────────────────────────

KEYWORD_MAP = {
    "telur":        ("telur",        ""),

    "bawang merah": ("bawang merah", ""),
    "bawang putih": ("bawang putih", ""),
    "cabai merah":  ("cabai merah",  ""),
    "cabai rawit":  ("cabai rawit",  ""),
    "daging ayam":  ("ayam",         "telur beras"),  # ← exclude telur
    "ayam":         ("ayam",         "telur beras"),  
    "daging sapi":  ("sapi",         ""),
    "sapi":         ("sapi",         ""),
    "beras":        ("beras",        ""),
    "minyak":       ("minyak",       ""),
    "gula":         ("gula",         ""),
}

def petakan_keyword(nama_komoditas: str) -> tuple[str, str]:
    nama_lower = nama_komoditas.lower()
    if "telur" in nama_lower:
        return ("telur", "")
    
    for kunci, nilai in KEYWORD_MAP.items():
        if kunci in nama_lower:
            return nilai  # (keyword, exclude)
    return (nama_komoditas.split()[0].lower(), "")


# ── Widget Statistik ───────────────────────────────────────────────────────

class StatistikBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            "background: #f0f7e6; border: 1px solid #c5e0a0; "
            "border-radius: 8px; padding: 4px;"
        )
        self.setMinimumHeight(80)
        self.setMaximumHeight(100)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(16, 12, 16, 12)
        self._layout.setSpacing(24)

        self.lbl_total    = self._buat_stat("Total Produk", "–")
        self.lbl_avg      = self._buat_stat("Rata-Rata Harga", "–")
        self.lbl_toko     = self._buat_stat("Jumlah Toko", "–")
        self.lbl_termahal = self._buat_stat("Paling Mahal", "–")

        self.perbarui()

    def _buat_stat(self, label: str, nilai: str) -> QLabel:
        container = QFrame()
        container.setStyleSheet("border: none; background: transparent;")
        v = QVBoxLayout(container)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(1)

        lbl_l = QLabel(label)
        lbl_l.setStyleSheet("font-size: 9px; color: #666; border: none; background: transparent;")
        lbl_v = QLabel(nilai)
        lbl_v.setStyleSheet("font-size: 12px; font-weight: bold; color: #2c3e50; border: none; background: transparent;")
        lbl_v.setWordWrap(True)

        v.addWidget(lbl_l)
        v.addWidget(lbl_v)
        self._layout.addWidget(container)
        return lbl_v

    def perbarui(self):
        try:
            stat = DBManager().statistik_harga()
            self.lbl_total.setText(str(stat.get("total", "–")))
            avg = stat.get("avg", 0)
            self.lbl_avg.setText(f"Rp {avg:,.0f}".replace(",", ".") if avg else "–")
            self.lbl_toko.setText(str(stat.get("jml_toko", "–")))
            termahal = stat.get("termahal", {})
            if termahal:
                self.lbl_termahal.setText(termahal.get("nama_produk", "")[:20])
        except Exception:
            pass


# ── Halaman Utama ──────────────────────────────────────────────────────────

class HalamanPencarian(QWidget):

    def __init__(self, is_admin: bool = False):   # ← parameter baru
        super().__init__()
        self.is_admin = is_admin
        self._data_terakhir: list = []
        self._keyword_terakhir: str = ""
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 12)
        layout.setSpacing(12)

        judul = QLabel("Kelola & Informasi Harga Bahan Pokok")
        judul.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(judul)

        self.stat_bar = StatistikBar()
        layout.addWidget(self.stat_bar)

        # Search bar
        bar = QFrame()
        bar.setStyleSheet(
            "background: #f8f9fa; border: 1px solid #e0e0e0; "
            "border-radius: 8px; padding: 4px;"
        )
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(12, 6, 12, 6)
        bl.setSpacing(8)

        self.input_cari = QLineEdit()
        self.input_cari.setPlaceholderText(
            "Ketik nama komoditas (misal: Beras, Telur, Bawang Merah)..."
        )
        self.input_cari.setStyleSheet(
            "padding: 8px 12px; border: 1px solid #ccc; border-radius: 6px; font-size: 13px;"
        )
        self.input_cari.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        bl.addWidget(self.input_cari, 1)

        def tombol(teks, warna, tooltip=""):
            b = QPushButton(teks)
            b.setFixedHeight(36)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setToolTip(tooltip)
            b.setStyleSheet(
                f"background-color: {warna}; color: white; border-radius: 6px; "
                f"padding: 0 14px; font-weight: bold; font-size: 12px; border: none;"
            )
            return b

        self.btn_cari  = tombol("Cari",        "#6B8E23", "Cari produk")
        self.btn_semua = tombol("Lihat Semua", "#8e44ad", "Tampilkan semua data supermarket")
        self.btn_ekspor = tombol("Ekspor CSV",  "#16a085", "Ekspor semua data ke CSV")

        self.btn_cari.setIcon(_svg_to_icon(_IKON_PENCARIAN["cari"]))
        self.btn_semua.setIcon(_svg_to_icon(_IKON_PENCARIAN["lihat_semua"]))
        self.btn_ekspor.setIcon(_svg_to_icon(_IKON_PENCARIAN["ekspor"]))

        bl.addWidget(self.btn_cari)
        bl.addWidget(self.btn_semua)

        # ── Tombol Tambah Data — hanya untuk admin ──────────────────────────
        if self.is_admin:
            self.btn_tambah = tombol("Tambah Data", "#2980b9", "Tambah data produk baru")
            self.btn_tambah.setIcon(_svg_to_icon(_IKON_PENCARIAN["tambah"]))
            self.btn_tambah.clicked.connect(self._tambah_data)
            bl.addWidget(self.btn_tambah)

        bl.addWidget(self.btn_ekspor)
        layout.addWidget(bar)

        self.refresh_bar = RefreshWidget()
        self.refresh_bar.refresh_diminta.connect(self._refresh_tampilan)
        layout.addWidget(self.refresh_bar)

        self.loading = LoadingWidget("Memproses data...")
        self.loading.hide()
        layout.addWidget(self.loading)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none;")

        self.grid_container = QWidget()
        self.grid = QGridLayout(self.grid_container)
        self.grid.setSpacing(10)
        self.scroll.setWidget(self.grid_container)
        layout.addWidget(self.scroll)

        self.lbl_info = QLabel("Masukkan kata kunci untuk mencari harga dari semua sumber.")
        self.lbl_info.setStyleSheet("color: #888; font-size: 11px; padding: 4px;")
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_info)

        self.btn_cari.clicked.connect(self._cari)
        self.input_cari.returnPressed.connect(self._cari)
        self.btn_semua.clicked.connect(self._tampilkan_semua)
        self.btn_ekspor.clicked.connect(self._ekspor_csv)

    # ── Pencarian ──────────────────────────────────────────────────────

    def _cari(self, exclude: str = ""):
        keyword = self.input_cari.text().strip()
        if not keyword:
            QMessageBox.information(self, "Info", "Masukkan kata kunci terlebih dahulu.")
            return
        self.loading.show()
        self._bersihkan_grid()
        self.worker = CariWorker(keyword, exclude=exclude)
        self.worker.selesai.connect(self._tampilkan_hasil)
        self.worker.start()

    def _tampilkan_semua(self):
        self.input_cari.clear()
        self.loading.show()
        self._bersihkan_grid()
        self.worker2 = SemuaDataWorker()
        self.worker2.selesai.connect(self._tampilkan_hasil_semua)
        self.worker2.start()

    def _tampilkan_hasil_semua(self, data: list):
        self.loading.hide()
        self._bersihkan_grid()
        self._data_terakhir = data

        if not data:
            self._tampilkan_kosong("Belum ada data supermarket. Jalankan scraper dulu.")
            return

        KOLOM = 2
        for i, row in enumerate(data):
            keys = row.keys()
            card = SearchCard(
                nama          = row["nama"],
                harga         = row["harga"],
                toko          = row["toko"],
                tanggal       = row["tanggal"] or "",
                thumbnail_url = row["thumbnail_url"] or "" if "thumbnail_url" in keys else "",
                id_produk     = row["id"],
                sumber        = "supermarket",
                kategori      = row["kategori"] or "" if "kategori" in keys else "",
                satuan        = row["satuan"] or "kg" if "satuan" in keys else "kg",
                is_admin      = self.is_admin,   # ← teruskan role
            )
            card.edit_diminta.connect(self._edit_data)
            card.hapus_diminta.connect(self._hapus_data)
            self.grid.addWidget(card, i // KOLOM, i % KOLOM)

        self.lbl_info.setText(f"Menampilkan {len(data)} produk supermarket.")

    def _tampilkan_hasil(self, data: list):
        self.loading.hide()
        self._bersihkan_grid()
        self._data_terakhir = data

        if not data:
            self._tampilkan_kosong("Tidak ditemukan data untuk kata kunci tersebut.")
            self.lbl_info.setText("0 hasil ditemukan.")
            return

        KOLOM = 2
        for i, row in enumerate(data):
            try:
                keys    = row.keys() if hasattr(row, "keys") else []
                id_p    = row["id"]            if "id"            in keys else -1
                nama    = row["nama"]          if "nama"          in keys else row[1]
                harga   = row["harga"]         if "harga"         in keys else row[2]
                toko    = row["toko"]          if "toko"          in keys else row[3]
                tanggal = row["tanggal"]       if "tanggal"       in keys else ""
                thumb   = row["thumbnail_url"] if "thumbnail_url" in keys else ""
                sumber  = row["sumber"]        if "sumber"        in keys else "supermarket"
            except Exception:
                continue

            card = SearchCard(
                nama=nama, harga=harga, toko=toko, tanggal=tanggal or "",
                thumbnail_url=thumb or "", id_produk=id_p, sumber=sumber,
                is_admin=self.is_admin,   # ← teruskan role
            )
            card.edit_diminta.connect(self._edit_data)
            card.hapus_diminta.connect(self._hapus_data)
            self.grid.addWidget(card, i // KOLOM, i % KOLOM)

        self.lbl_info.setText(f"{len(data)} hasil ditemukan.")

    def _tampilkan_kosong(self, pesan: str):
        lbl = QLabel(pesan)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color: #999; font-size: 14px; padding: 40px;")
        self.grid.addWidget(lbl, 0, 0, 1, 2)

    # ── CRUD (hanya dipanggil jika is_admin = True) ────────────────────

    def _tambah_data(self):
        dialog = DialogFormProduk(self)
        if dialog.exec():
            d = dialog.get_data()
            try:
                DBManager().tambah_produk(
                    nama=d["nama"], harga=d["harga"], toko=d["toko"],
                    tanggal=d["tanggal"], kategori=d["kategori"], satuan=d["satuan"]
                )
                QMessageBox.information(self, "Berhasil", f"Data '{d['nama']}' berhasil ditambahkan!")
                self.stat_bar.perbarui()
                if self.input_cari.text().strip():
                    self._cari()
                else:
                    self._tampilkan_semua()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menyimpan data:\n{e}")

    def _edit_data(self, row_data: dict):
        dialog = DialogFormProduk(self, data_awal=row_data)
        if dialog.exec():
            d = dialog.get_data()
            try:
                DBManager().update_produk(
                    id_produk=row_data["id"],
                    nama=d["nama"], harga=d["harga"], toko=d["toko"],
                    tanggal=d["tanggal"], kategori=d["kategori"], satuan=d["satuan"]
                )
                QMessageBox.information(self, "Berhasil", f"Data '{d['nama']}' berhasil diperbarui!")
                self.stat_bar.perbarui()
                self._refresh_tampilan()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal memperbarui data:\n{e}")

    def _hapus_data(self, id_produk: int):
        if id_produk < 0:
            QMessageBox.warning(self, "Info", "Data PIHPS tidak bisa dihapus dari sini.")
            return
        konfirmasi = QMessageBox.question(
            self, "Konfirmasi Hapus",
            "Apakah Anda yakin ingin menghapus data ini?\nTindakan ini tidak bisa dibatalkan.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if konfirmasi == QMessageBox.StandardButton.Yes:
            try:
                DBManager().hapus_produk(id_produk)
                QMessageBox.information(self, "Berhasil", "Data berhasil dihapus.")
                self.stat_bar.perbarui()
                self._refresh_tampilan()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menghapus data:\n{e}")

    def _refresh_tampilan(self):
        if self._keyword_terakhir:
            self.input_cari.setText(self._keyword_terakhir)
            self._cari()
        else:
            self._tampilkan_semua()

    # ── Ekspor CSV ────────────────────────────────────────────────────

    def _ekspor_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Simpan CSV", "data_harga_pangan.csv",
            "CSV Files (*.csv);;All Files (*)"
        )
        if not path:
            return
        try:
            DBManager().ekspor_csv(path)
            QMessageBox.information(self, "Ekspor Berhasil", f"Data berhasil diekspor ke:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengekspor:\n{e}")

    # ── Utilitas ──────────────────────────────────────────────────────

    def _bersihkan_grid(self):
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)

    def set_keyword_dan_cari(self, nama_komoditas: str):
        keyword, exclude = petakan_keyword(nama_komoditas)
        self.input_cari.setText(keyword)
        self._cari(exclude=exclude)