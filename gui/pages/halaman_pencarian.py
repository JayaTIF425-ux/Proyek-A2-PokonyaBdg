import os
from datetime import date

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QScrollArea, QGridLayout,
    QFrame, QDialog, QFormLayout, QMessageBox,
    QFileDialog, QSizePolicy, QDateEdit, QComboBox
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

# ── SVG ikon kecil untuk tiap stat ────────────────────────────────────────────
_SVG_STAT = {
    "produk": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
        fill="none" stroke="#5C1A28" stroke-width="2" stroke-linecap="round"
        stroke-linejoin="round">
        <path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8
        a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/>
        <path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>""",

    "harga": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
        fill="none" stroke="#5C1A28" stroke-width="2" stroke-linecap="round"
        stroke-linejoin="round">
        <path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3
        a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/>
        <path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/></svg>""",

    "toko": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
        fill="none" stroke="#5C1A28" stroke-width="2" stroke-linecap="round"
        stroke-linejoin="round">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
        <polyline points="9 22 9 12 15 12 15 22"/></svg>""",

    "termahal": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
        fill="none" stroke="#5C1A28" stroke-width="2" stroke-linecap="round"
        stroke-linejoin="round">
        <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
        <polyline points="17 6 23 6 23 12"/></svg>""",
}


# ── Dialog Form (Create & Update) ──────────────────────────────────────────

class DialogFormProduk(QDialog):
    def __init__(self, parent=None, data_awal: dict = None):
        super().__init__(parent)
        self.data_awal = data_awal or {}
        mode = "Edit Data" if data_awal else "Tambah Data Baru"

        self.setWindowTitle(mode)
        self.setMinimumSize(450, 420)
        self.setStyleSheet("background-color: #ffffff; font-family: 'Segoe UI', Arial, sans-serif;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        judul = QLabel(mode)
        judul.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(judul)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #eaeded; background-color: #eaeded; max-height: 1px;")
        layout.addWidget(sep)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        def buat_input(placeholder=""):
            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            inp.setStyleSheet(
                "QLineEdit {"
                "   padding: 6px 10px;"
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

        self.inp_nama     = buat_input("misal: Beras Premium")
        self.inp_harga    = buat_input("misal: 15000")
        self.inp_toko     = buat_input("misal: Yogya, Borma, ...")
        self.inp_kategori = buat_input("misal: Beras, Sayuran, ...")
        self.inp_satuan   = buat_input("misal: kg, liter, pcs")

        self.inp_tanggal  = QDateEdit()
        self.inp_tanggal.setCalendarPopup(True)
        self.inp_tanggal.setDisplayFormat("yyyy-MM-dd")
        self.inp_tanggal.setMaximumDate(QDate.currentDate())

        kalender = self.inp_tanggal.calendarWidget()
        if kalender:
            kalender.setStyleSheet(
                "QCalendarWidget QWidget#qt_calendar_navigationbar {"
                "   background-color: #f8fafc;"
                "}"
                "QCalendarWidget QWidget {"
                "   color: #2c3e50;"
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
        layout.addSpacing(10)

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
            "tanggal":  self.inp_tanggal.date().toPyDate().isoformat(),
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
    "daging ayam":  ("ayam",         "telur beras"),
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
            return nilai
    return (nama_komoditas.split()[0].lower(), "")


# ── Widget Statistik (desain diselaraskan dengan tema maroon) ──────────────

class StatistikBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StatistikBar")
        self.setStyleSheet("""
            #StatistikBar {
                background: #FDF8F5;
                border: 1px solid #E2D9CC;
                border-radius: 8px;
            }
        """)
        self.setMinimumHeight(65)
        self.setMaximumHeight(85)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(16, 8, 16, 8)
        self._layout.setSpacing(0)

        self.lbl_total    = self._buat_stat("Total Produk",     "–", "produk")
        self._layout.addWidget(self._sep())
        self.lbl_avg      = self._buat_stat("Rata-Rata Harga",  "–", "harga")
        self._layout.addWidget(self._sep())
        self.lbl_toko     = self._buat_stat("Jumlah Toko",      "–", "toko")
        self._layout.addWidget(self._sep())
        self.lbl_termahal = self._buat_stat("Harga Paling Mahal", "–", "termahal")

        self.perbarui()

    def _sep(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedWidth(1)
        sep.setStyleSheet("background: #E2D9CC; border: none;")
        return sep

    def _buat_stat(self, label: str, nilai: str, satuan: str = "") -> QLabel:
        container = QFrame()
        container.setStyleSheet("border: none; background: transparent;")
        
        # Layout utama HORIZONTAL (Ikon di kiri, teks di kanan)
        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(12, 0, 12, 0)
        main_layout.setSpacing(10)  # Jarak antara ikon dan tulisan
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 1. Identifikasi kunci ikon berdasarkan string label asli
        ikon_key = ""
        teks_judul = label  # Standar teks jika tidak ada kecocokan
        
        if "Produk" in label:
            ikon_key = "produk"
            teks_judul = "Total Produk"
        elif "Harga" in label:
            ikon_key = "harga"
            teks_judul = "Rata-Rata Harga"
        elif "Toko" in label:
            ikon_key = "toko"
            teks_judul = "Jumlah Toko"
        elif "Mahal" in label:
            ikon_key = "termahal"
            teks_judul = "Harga Paling Mahal"

        # Render Ikon SVG di Sebelah Kiri
        if ikon_key and ikon_key in _SVG_STAT:
            from PyQt6.QtSvg import QSvgRenderer
            from PyQt6.QtCore import QByteArray
            
            svg = _SVG_STAT[ikon_key]
            r = QSvgRenderer(QByteArray(svg.encode()))
            px = QPixmap(16, 16)  # Ukuran ikon yang pas untuk ditaruh di samping teks
            px.fill(Qt.GlobalColor.transparent)
            p = QPainter(px)
            r.render(p)
            p.end()

            lbl_ikon = QLabel()
            lbl_ikon.setPixmap(px)
            lbl_ikon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_ikon.setStyleSheet("border: none; background: transparent;")
            main_layout.addWidget(lbl_ikon)

        # 2. Layout VERTIKAL untuk Teks (Hanya 2 Baris)
        v_text_layout = QVBoxLayout()
        v_text_layout.setSpacing(2)
        v_text_layout.setContentsMargins(0, 0, 0, 0)
        v_text_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        # Baris 1: Judul Kategori (Hanya menampilkan kata kunci tunggal seperti mockup)
        lbl_label = QLabel(teks_judul)
        lbl_label.setStyleSheet(
            "font-size: 11px; color: #8B7B6B; border: none; background: transparent;"
        )

        # Baris 2: Nilai Angka / Nama Produk Termahal
        teks_tampil = f"{nilai} {satuan}".strip() if satuan else nilai
        lbl_nilai = QLabel(teks_tampil)
        lbl_nilai.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_nilai.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #5C1A28; "
            "border: none; background: transparent;"
        )

        v_text_layout.addWidget(lbl_label)
        v_text_layout.addWidget(lbl_nilai)

        # Gabungkan layout teks ke sebelah kanan ikon
        main_layout.addLayout(v_text_layout)
        
        self._layout.addWidget(container)
        return lbl_nilai

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
_SVG_BOOKMARK = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
viewBox="0 0 24 24" fill="none" stroke="#555" stroke-width="2"
stroke-linecap="round" stroke-linejoin="round">
<path d="M17 3a2 2 0 0 1 2 2v15a1 1 0 0 1-1.496.868l-4.512-2.578
a2 2 0 0 0-1.984 0l-4.512 2.578A1 1 0 0 1 5 20V5a2 2 0 0 1 2-2z"/>
</svg>"""

_SVG_STORE = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
viewBox="0 0 24 24" fill="none" stroke="#555" stroke-width="2"
stroke-linecap="round" stroke-linejoin="round">
<circle cx="8" cy="21" r="1"/>
<circle cx="19" cy="21" r="1"/>
<path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0
1.95-1.57l1.65-7.43H5.12"/></svg>"""

def _render_kecil(svg_str: str, ukuran: int = 14) -> QPixmap:
    from PyQt6.QtSvg import QSvgRenderer
    from PyQt6.QtCore import QByteArray
    r = QSvgRenderer(QByteArray(svg_str.encode()))
    px = QPixmap(ukuran, ukuran)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    r.render(p)
    p.end()
    return px

class HalamanPencarian(QWidget):

    def __init__(self, is_admin: bool = False):
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

        self.btn_cari   = tombol("Cari",        "#6B8E23", "Cari produk")
        self.btn_semua  = tombol("Lihat Semua", "#8e44ad", "Tampilkan semua data supermarket")
        self.btn_ekspor = tombol("Ekspor CSV",  "#16a085", "Ekspor semua data ke CSV")

        self.btn_cari.setIcon(_svg_to_icon(_IKON_PENCARIAN["cari"]))
        self.btn_semua.setIcon(_svg_to_icon(_IKON_PENCARIAN["lihat_semua"]))
        self.btn_ekspor.setIcon(_svg_to_icon(_IKON_PENCARIAN["ekspor"]))

        bl.addWidget(self.btn_cari)
        bl.addWidget(self.btn_semua)

        if self.is_admin:
            self.btn_tambah = tombol("Tambah Data", "#2980b9", "Tambah data produk baru")
            self.btn_tambah.setIcon(_svg_to_icon(_IKON_PENCARIAN["tambah"]))
            self.btn_tambah.clicked.connect(self._tambah_data)
            bl.addWidget(self.btn_tambah)

        bl.addWidget(self.btn_ekspor)
        layout.addWidget(bar)

        # ── Baris filter kategori & sumber ────────────────────────────────
        filter_bar_widget = QFrame()
        filter_bar_widget.setStyleSheet(
            "background: #f0f4f8; border: 1px solid #dde3ea; border-radius: 7px;"
        )
        fb_layout = QHBoxLayout(filter_bar_widget)
        fb_layout.setContentsMargins(12, 6, 12, 6)
        fb_layout.setSpacing(10)

        # Label kategori dengan ikon SVG
        lbl_kat = QLabel()
        lbl_kat.setFixedSize(14, 14)
        lbl_kat.setPixmap(_render_kecil(_SVG_BOOKMARK))
        lbl_kat.setStyleSheet("border: none; background: transparent;")
        lbl_kat_teks = QLabel("Kategori:")
        lbl_kat_teks.setStyleSheet("font-size: 12px; color: #555; border: none; background: transparent;")

        self.combo_kategori = QComboBox()
        self.combo_kategori.addItem("Semua Kategori", userData="")
        self.combo_kategori.setFixedWidth(195)
        self.combo_kategori.setStyleSheet("""
            QComboBox {
                padding: 4px 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background: white;
                font-size: 12px;
                color: #333;
            }
            QComboBox QAbstractItemView {
                background: white;
                color: #333;
                selection-background-color: #6B8E23;
                selection-color: white;
            }
        """)
        self.combo_kategori.currentIndexChanged.connect(self._on_filter_kategori)
        self._isi_combo_kategori()

        sep_line = QFrame()
        sep_line.setFrameShape(QFrame.Shape.VLine)
        sep_line.setFixedWidth(1)
        sep_line.setStyleSheet("background: #ccc; border: none;")

       # Label sumber dengan ikon SVG
        lbl_src = QLabel()
        lbl_src.setFixedSize(14, 14)
        lbl_src.setPixmap(_render_kecil(_SVG_STORE))
        lbl_src.setStyleSheet("border: none; background: transparent;")
        lbl_src_teks = QLabel("Sumber:")
        lbl_src_teks.setStyleSheet("font-size: 12px; color: #555; border: none; background: transparent;")

        self.combo_sumber = QComboBox()
        self.combo_sumber.addItems(["Semua Sumber", "PIHPS", "Supermarket"])
        self.combo_sumber.setFixedWidth(150)
        self.combo_sumber.setStyleSheet("""
            QComboBox {
                padding: 4px 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background: white;
                font-size: 12px;
                color: #333;
            }
            QComboBox QAbstractItemView {
                background: white;
                color: #333;
                selection-background-color: #8e44ad;
                selection-color: white;
            }
        """)
        self.combo_sumber.currentIndexChanged.connect(self._on_filter_kategori)

        self._lbl_count_filter = QLabel("")
        self._lbl_count_filter.setStyleSheet("font-size: 11px; color: #888; border: none; background: transparent;")

        fb_layout.addWidget(lbl_kat)
        fb_layout.addWidget(lbl_kat_teks)
        fb_layout.addWidget(self.combo_kategori)
        fb_layout.addWidget(sep_line)
        fb_layout.addWidget(lbl_src)
        fb_layout.addWidget(lbl_src_teks)
        fb_layout.addWidget(self.combo_sumber)
        fb_layout.addStretch()
        fb_layout.addWidget(self._lbl_count_filter)
        layout.addWidget(filter_bar_widget)

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

    # ── Filter Kategori & Sumber ───────────────────────────────────────

    def _isi_combo_kategori(self):
        """Isi combo kategori dari DB (harga_supermarket.kategori)."""
        try:
            with DBManager()._connect() as conn:
                rows = conn.execute(
                    "SELECT DISTINCT kategori FROM harga_supermarket "
                    "WHERE kategori IS NOT NULL AND kategori != '' "
                    "ORDER BY kategori"
                ).fetchall()
            for row in rows:
                kat = row[0]
                self.combo_kategori.addItem(kat, userData=kat)
        except Exception:
            pass

    def _on_filter_kategori(self):
        """Terapkan filter kategori & sumber ke data yang sudah ditampilkan."""
        if not self._data_terakhir:
            return
        self._terapkan_filter(self._data_terakhir)

    def _terapkan_filter(self, data: list):
        """Filter data berdasarkan pilihan kategori dan sumber, lalu render ulang."""
        kat     = self.combo_kategori.currentData() or ""
        src_idx = self.combo_sumber.currentIndex()   # 0=semua, 1=PIHPS, 2=Super

        hasil = []
        for row in data:
            keys = row.keys() if hasattr(row, "keys") else []

            # Filter sumber
            sumber = row["sumber"] if "sumber" in keys else "supermarket"
            if src_idx == 1 and sumber != "pihps":
                continue
            if src_idx == 2 and sumber == "pihps":
                continue

            # Filter kategori (hanya berlaku untuk supermarket)
            if kat:
                kategori_row = row["kategori"] if "kategori" in keys else ""
                if not kategori_row or kat.lower() not in str(kategori_row).lower():
                    continue

            hasil.append(row)

        # Render ulang grid tanpa memanggil worker baru
        self._bersihkan_grid()
        if not hasil:
            lbl = QLabel("Tidak ada produk sesuai filter.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: #999; font-size: 14px; padding: 40px;")
            self.grid.addWidget(lbl, 0, 0, 1, 2)
            self._lbl_count_filter.setText("0 hasil")
            return

        KOLOM = 2
        for i, row in enumerate(hasil):
            keys    = row.keys() if hasattr(row, "keys") else []
            id_p    = row["id"]            if "id"            in keys else -1
            nama    = row["nama"]          if "nama"          in keys else row[1]
            harga   = row["harga"]         if "harga"         in keys else row[2]
            toko    = row["toko"]          if "toko"          in keys else row[3]
            tanggal = row["tanggal"]       if "tanggal"       in keys else ""
            thumb   = row["thumbnail_url"] if "thumbnail_url" in keys else ""
            sumber  = row["sumber"]        if "sumber"        in keys else "supermarket"

            card = SearchCard(
                nama=nama, harga=harga, toko=toko, tanggal=tanggal or "",
                thumbnail_url=thumb or "", id_produk=id_p, sumber=sumber,
                is_admin=self.is_admin,
            )
            card.edit_diminta.connect(self._edit_data)
            card.hapus_diminta.connect(self._hapus_data)
            self.grid.addWidget(card, i // KOLOM, i % KOLOM)

        self._lbl_count_filter.setText(f"{len(hasil)} dari {len(data)} produk")

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

        # Reset filter sebelum tampilkan semua
        self.combo_kategori.setCurrentIndex(0)
        self.combo_sumber.setCurrentIndex(0)
        self._terapkan_filter(data)
        self.lbl_info.setText(f"Menampilkan {len(data)} produk supermarket.")

    def _tampilkan_hasil(self, data: list):
        self.loading.hide()
        self._bersihkan_grid()
        self._data_terakhir = data

        if not data:
            self._tampilkan_kosong("Tidak ditemukan data untuk kata kunci tersebut.")
            self.lbl_info.setText("0 hasil ditemukan.")
            self._lbl_count_filter.setText("")
            return

        # Reset filter & terapkan
        self.combo_kategori.setCurrentIndex(0)
        self.combo_sumber.setCurrentIndex(0)
        self._terapkan_filter(data)
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