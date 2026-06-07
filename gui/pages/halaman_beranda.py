from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QGridLayout, QFrame, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter

from database.db_manager import DBManager
from gui.components.product_card import ProductCard
from gui.widgets.loading_widget import LoadingWidget
from gui.widgets.refresh_widget import RefreshWidget

_SVG_CART_STR = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
viewBox="0 0 24 24" fill="none" stroke="{warna}" stroke-width="2"
stroke-linecap="round" stroke-linejoin="round">
<circle cx="8" cy="21" r="1"/>
<circle cx="19" cy="21" r="1"/>
<path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0
1.95-1.57l1.65-7.43H5.12"/></svg>"""

def _render_svg_cart(warna: str, ukuran: int = 22) -> QPixmap:
    from PyQt6.QtSvg import QSvgRenderer
    from PyQt6.QtCore import QByteArray
    svg = _SVG_CART_STR.replace("{warna}", warna)
    r = QSvgRenderer(QByteArray(svg.encode()))
    px = QPixmap(ukuran, ukuran)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    r.render(p)
    p.end()
    return px

class DataWorker(QThread):
    selesai = pyqtSignal(list, list)   # (data_tradisional, data_modern)

    def __init__(self, jenis_pasar: str = "semua"):
        super().__init__()
        self.jenis_pasar = jenis_pasar

    def run(self):
        if self.jenis_pasar == "semua":
            data_t = list(DBManager().fetch_produk_pihps_by_pasar("tradisional"))
            data_m = list(DBManager().fetch_produk_pihps_by_pasar("modern"))
            self.selesai.emit(data_t, data_m)
        elif self.jenis_pasar == "tradisional":
            data = list(DBManager().fetch_produk_pihps_by_pasar("tradisional"))
            self.selesai.emit(data, [])
        else:
            data = list(DBManager().fetch_produk_pihps_by_pasar("modern"))
            self.selesai.emit([], data)


# ── Widget Statistik Ringkasan Beranda ────────────────────────────────────────
_SVG_STAT_BERANDA = {
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

    "waktu": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
        fill="none" stroke="#5C1A28" stroke-width="2" stroke-linecap="round"
        stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"/>
        <path d="M12 6v6l4 2"/></svg>""",
}

class StatistikBeranda(QFrame):
    """Tiga kotak statistik ringkasan di bagian atas Beranda."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StatistikBeranda")
        self.setStyleSheet("""
            #StatistikBeranda {
                background: #FDF8F5;
                border: 1px solid #E2D9CC;
                border-radius: 10px;
            }
        """)
        self.setMinimumHeight(65)
        self.setMaximumHeight(85)

        # Tetap gunakan variabel layout bawaan kodemu (tanpa _)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(0)

        self.lbl_produk     = self._buat_stat("Produk", "–")
        layout.addWidget(self._separator())
        self.lbl_terendah   = self._buat_stat("Harga", "–")
        layout.addWidget(self._separator())
        self.lbl_diperbarui = self._buat_stat("Diperbarui", "–")

        self.perbarui()

    def _buat_stat(self, label: str, nilai: str, satuan: str = "") -> QLabel:
        container = QFrame()
        container.setStyleSheet("border: none; background: transparent;")
        
        # Layout utama HORIZONTAL (Ikon di kiri, teks di kanan)
        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(12, 0, 12, 0)
        main_layout.setSpacing(8)  # Jarak rapat antara ikon dan tulisan
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 1. Identifikasi kunci ikon berdasarkan string label asli
        ikon_key = ""
        teks_judul = label 
        
        if "Produk" in label:
            ikon_key = "produk"
            teks_judul = "Total Produk"
        elif "Harga" in label:
            ikon_key = "harga"
            teks_judul = "Rata-Rata Harga"
        elif "Diperbarui" in label:
            ikon_key = "waktu"
            teks_judul = "Terakhir Diperbarui"

        # Render Ikon SVG di Sebelah Kiri (Menggunakan _SVG_STAT_BERANDA)
        if ikon_key and ikon_key in _SVG_STAT_BERANDA: 
            from PyQt6.QtSvg import QSvgRenderer
            from PyQt6.QtCore import QByteArray
            
            svg = _SVG_STAT_BERANDA[ikon_key]  
            r = QSvgRenderer(QByteArray(svg.encode()))
            px = QPixmap(16, 16)  # Ukuran ikon pas dan kecil
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

        # Baris 1: Judul Kategori
        lbl_label = QLabel(teks_judul) 
        lbl_label.setStyleSheet(
            "font-size: 11px; color: #8B7B6B; border: none; background: transparent;"
        )

        # Baris 2: Nilai Angka / Teks
        teks_tampil = f"{nilai} {satuan}".strip() if satuan else nilai
        lbl_nilai = QLabel(teks_tampil)
        lbl_nilai.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Set rata tengah
        lbl_nilai.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #5C1A28; "
            "border: none; background: transparent;"
        )

        v_text_layout.addWidget(lbl_label)
        v_text_layout.addWidget(lbl_nilai)

        # Gabungkan layout teks ke sebelah kanan ikon
        main_layout.addLayout(v_text_layout)
        
        # Masukkan ke layout horizontal utama StatistikBar (Tanpa tanda kurung)
        self.layout().addWidget(container)
        return lbl_nilai

    def _separator(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("color: #E2D9CC; background: #E2D9CC; max-width: 1px;")
        return sep

    def perbarui(self, data_t: list | None = None, data_m: list | None = None):
        try:
            db = DBManager()
            stat = db.statistik_harga()

            total = stat.get("total", 0)
            self.lbl_produk.setText(str(total) if total else "–")

            all_data = (data_t or []) + (data_m or [])
            if all_data:
                harga_list = []
                for row in all_data:
                    h = row["harga"] if hasattr(row, "keys") else row[1]
                    if h and h > 0:
                        harga_list.append(h)
                if harga_list:
                    terendah = min(harga_list)
                    self.lbl_terendah.setText(f"Rp {terendah:,.0f}".replace(",", "."))
                else:
                    self.lbl_terendah.setText("–")
            else:
                avg = stat.get("avg", 0)
                if avg:
                    self.lbl_terendah.setText(f"Rp {avg:,.0f}".replace(",", "."))
                else:
                    self.lbl_terendah.setText("–")

            from datetime import datetime
            waktu = datetime.now().strftime("%d %b %Y, %H:%M")
            self.lbl_diperbarui.setText(waktu)
        except Exception:
            pass


# ── Section Header (pemisah Tradisional / Modern) ─────────────────────────────

class SectionHeader(QFrame):
    """Header divider dengan label dan aksen warna untuk tiap jenis pasar."""

    STYLE_TRADISIONAL = {
        "bg":     "#FFF8EC",
        "border": "#D4A017",
        "accent": "#8B5E00",
        "icon":   "🏪",
        "label":  "Pasar Tradisional",
        "sub":    "Data harga dari pasar tradisional Bandung (PIHPS)",
    }
    STYLE_MODERN = {
        "bg":     "#EEF4FF",
        "border": "#3B82F6",
        "accent": "#1E3A8A",
        "icon":   "🛒",
        "label":  "Pasar Modern / Supermarket",
        "sub":    "Data harga dari pasar modern Bandung (PIHPS)",
    }

    def __init__(self, jenis: str, jumlah: int = 0, parent=None):
        super().__init__(parent)
        st = self.STYLE_TRADISIONAL if jenis == "tradisional" else self.STYLE_MODERN
        self.setStyleSheet(f"""
            QFrame {{
                background: {st['bg']};
                border-left: 4px solid {st['border']};
                border-radius: 6px;
            }}
        """)
        self.setFixedHeight(52)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 6, 14, 6)
        lay.setSpacing(10)

        lbl_icon = QLabel()
        lbl_icon.setFixedSize(28, 28)
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icon.setStyleSheet("border: none; background: transparent;")
        lbl_icon.setPixmap(_render_svg_cart(st["border"], ukuran=22))
        col = QVBoxLayout()
        col.setSpacing(1)
        lbl_judul = QLabel(f"<b>{st['label']}</b>  <span style='font-size:11px;color:#666;font-weight:normal;'>— {jumlah} komoditas</span>")
        lbl_judul.setStyleSheet(f"font-size: 14px; color: {st['accent']}; border: none; background: transparent;")
        lbl_sub = QLabel(st["sub"])
        lbl_sub.setStyleSheet("font-size: 10px; color: #888; border: none; background: transparent;")
        col.addWidget(lbl_judul)
        col.addWidget(lbl_sub)

        lay.addWidget(lbl_icon)
        lay.addLayout(col)
        lay.addStretch()


# ── Halaman Beranda ───────────────────────────────────────────────────────────

class HalamanBeranda(QWidget):

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
        self.combo_pasar.addItems([
            "Pasar Tradisional/Modern",
            "Pasar Tradisional",
            "Pasar Modern"
        ])
        self.combo_pasar.setFixedWidth(220)
        self.combo_pasar.setStyleSheet("""
            QComboBox {
                padding: 4px 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
                color: #333;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #333;
                selection-background-color: #6B8E23;
                selection-color: white;
                border: 1px solid #ccc;
            }
        """)
        self.combo_pasar.currentIndexChanged.connect(self._on_filter_pasar_berubah)

        header.addWidget(lbl_filter)
        header.addWidget(self.combo_pasar)
        layout.addLayout(header)

        # ── Statistik Ringkasan ───────────────────────────────────────────
        self.stat_beranda = StatistikBeranda()
        layout.addWidget(self.stat_beranda)

        # ── Refresh bar ───────────────────────────────────────────────────
        self.refresh_bar = RefreshWidget()
        self.refresh_bar.refresh_diminta.connect(self._muat_data)
        self.refresh_bar.update_selesai.connect(
            lambda ok: self.lbl_info.setText(
                "✓ Data berhasil diperbarui!" if ok else "✗ Update gagal."
            )
        )
        layout.addWidget(self.refresh_bar)

        # ── Grid kartu komoditas ──────────────────────────────────────────
        self.loading = LoadingWidget("Memuat data harga...")

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none; background: transparent;")

        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background: transparent;")
        self.main_layout_grid = QVBoxLayout(self.grid_container)
        self.main_layout_grid.setSpacing(16)
        self.main_layout_grid.setContentsMargins(0, 0, 0, 0)
        self.scroll.setWidget(self.grid_container)

        layout.addWidget(self.loading)
        layout.addWidget(self.scroll)

        self.lbl_info = QLabel("")
        self.lbl_info.setStyleSheet("color: #888; font-size: 11px; padding: 4px;")
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_info)

    def _get_jenis_pasar(self) -> str:
        idx = self.combo_pasar.currentIndex()
        mapping = {0: "semua", 1: "tradisional", 2: "modern"}
        return mapping.get(idx, "semua")

    def _on_filter_pasar_berubah(self):
        self._muat_data()

    def _muat_data(self):
        self.loading.show()
        self.scroll.hide()
        self.worker = DataWorker(jenis_pasar=self._get_jenis_pasar())
        self.worker.selesai.connect(self._tampilkan_data)
        self.worker.start()

    def _tampilkan_data(self, data_t: list, data_m: list):
        self.loading.hide()
        self.scroll.show()

        # Bersihkan layout lama
        while self.main_layout_grid.count():
            item = self.main_layout_grid.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
            sub = item.layout()
            if sub:
                while sub.count():
                    it2 = sub.takeAt(0)
                    w2 = it2.widget()
                    if w2:
                        w2.setParent(None)

        # Perbarui statistik
        self.stat_beranda.perbarui(data_t, data_m)

        jenis = self._get_jenis_pasar()
        total = 0

        if not data_t and not data_m:
            lbl = QLabel("Belum ada data. Jalankan scraper terlebih dahulu.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: #999; font-size: 14px; padding: 40px;")
            self.main_layout_grid.addWidget(lbl)
            self.lbl_info.setText("Tidak ada data.")
            return

        KOLOM = 3

        def _buat_grid_section(data: list, jenis_pasar: str) -> QWidget:
            """Buat widget grid kartu dengan jenis_pasar terpisah."""
            container = QWidget()
            container.setStyleSheet("background: transparent;")
            grid = QGridLayout(container)
            grid.setSpacing(12)
            for i, row in enumerate(data):
                card = ProductCard(
                    nama        = row["komoditas"] if hasattr(row, "keys") else row[0],
                    harga       = row["harga"]     if hasattr(row, "keys") else row[1],
                    toko        = row["toko"]      if hasattr(row, "keys") else row[3],
                    tanggal     = row["tanggal"]   if hasattr(row, "keys") else row[4],
                    jenis_pasar = jenis_pasar,
                )
                card.lihat_pencarian.connect(self.navigasi_pencarian)
                grid.addWidget(card, i // KOLOM, i % KOLOM)
            return container

        # ── Tampilkan berdasarkan filter ──────────────────────────────────
        if jenis == "semua":
            if data_t:
                self.main_layout_grid.addWidget(SectionHeader("tradisional", len(data_t)))
                self.main_layout_grid.addWidget(
                    _buat_grid_section(data_t, "tradisional")
                )
            if data_m:
                self.main_layout_grid.addWidget(SectionHeader("modern", len(data_m)))
                self.main_layout_grid.addWidget(
                    _buat_grid_section(data_m, "modern")
                )
            total = len(data_t) + len(data_m)
            sumber = "PIHPS Bandung — Tradisional & Modern (ditampilkan terpisah)"

        elif jenis == "tradisional":
            if data_t:
                self.main_layout_grid.addWidget(SectionHeader("tradisional", len(data_t)))
                self.main_layout_grid.addWidget(
                    _buat_grid_section(data_t, "tradisional")
                )
            total = len(data_t)
            sumber = "PIHPS Bandung — Pasar Tradisional"

        else:  # modern
            if data_m:
                self.main_layout_grid.addWidget(SectionHeader("modern", len(data_m)))
                self.main_layout_grid.addWidget(
                    _buat_grid_section(data_m, "modern")
                )
            total = len(data_m)
            sumber = "PIHPS Bandung — Pasar Modern"

        self.main_layout_grid.addStretch()
        self.lbl_info.setText(f"Menampilkan {total} komoditas · Sumber: {sumber}")