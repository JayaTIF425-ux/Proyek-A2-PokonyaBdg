from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QGridLayout, QFrame, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QByteArray
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer

from database.db_manager import DBManager
from gui.components.product_card import ProductCard
from gui.widgets.loading_widget import LoadingWidget
from gui.widgets.refresh_widget import RefreshWidget


def _svg_pix(svg: str, w: int, h: int) -> QPixmap:
    renderer = QSvgRenderer(QByteArray(svg.encode()))
    pix = QPixmap(w, h)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    renderer.render(p)
    p.end()
    return pix


# ── SVG ikon untuk StatistikBeranda ──────────────────────────────────────────
_SVG_PRODUK = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
  stroke="#5C1A28" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
  <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
  <line x1="12" y1="22.08" x2="12" y2="12"/>
</svg>"""

_SVG_HARGA = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
  stroke="#27AE60" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <line x1="12" y1="1" x2="12" y2="23"/>
  <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
</svg>"""

_SVG_WAKTU = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
  stroke="#5C1A28" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10"/>
  <polyline points="12 6 12 12 16 14"/>
</svg>"""

# SVG untuk SectionHeader (ganti emoji 🏪 dan 🛒)
_SVG_PASAR_TRADISIONAL = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
  stroke="#8B5E00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
  <polyline points="9 22 9 12 15 12 15 22"/>
</svg>"""

_SVG_PASAR_MODERN = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
  stroke="#1E3A8A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="9" cy="21" r="1"/>
  <circle cx="20" cy="21" r="1"/>
  <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
</svg>"""


class DataWorker(QThread):
    selesai = pyqtSignal(list, list)

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


# ── Widget Statistik Ringkasan ────────────────────────────────────────────────

class StatistikBeranda(QFrame):
    """Tiga kotak statistik di atas Beranda — semua ikon SVG vektor."""

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
        self.setFixedHeight(90)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.lbl_produk     = self._buat_kartu(_SVG_PRODUK, "Produk Terpantau", "–",  "#5C1A28")
        layout.addWidget(self._sep())
        self.lbl_terendah   = self._buat_kartu(_SVG_HARGA,  "Harga Terendah",   "–",  "#27AE60")
        layout.addWidget(self._sep())
        self.lbl_diperbarui = self._buat_kartu(_SVG_WAKTU,  "Diperbarui",       "–",  "#5C1A28")

        self.perbarui()

    def _sep(self) -> QFrame:
        s = QFrame()
        s.setFrameShape(QFrame.Shape.VLine)
        s.setStyleSheet("background: #E2D9CC; border: none; max-width: 1px;")
        return s

    def _buat_kartu(self, svg: str, label: str, nilai: str, warna: str) -> QLabel:
        """Buat satu kartu statistik, return ref ke QLabel nilai."""
        container = QFrame()
        container.setStyleSheet("border: none; background: transparent;")
        h = QHBoxLayout(container)
        h.setContentsMargins(18, 0, 18, 0)
        h.setSpacing(12)
        h.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        lbl_ikon = QLabel()
        lbl_ikon.setPixmap(_svg_pix(svg, 26, 26))
        lbl_ikon.setFixedSize(26, 26)
        lbl_ikon.setStyleSheet("background: transparent;")
        h.addWidget(lbl_ikon)

        col = QVBoxLayout()
        col.setSpacing(2)
        lbl_l = QLabel(label)
        lbl_l.setStyleSheet("font-size: 11px; color: #8B7B6B; background: transparent;")
        lbl_v = QLabel(nilai)
        lbl_v.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {warna}; background: transparent;"
        )
        col.addWidget(lbl_l)
        col.addWidget(lbl_v)
        h.addLayout(col)
        h.addStretch()

        self.layout().addWidget(container, 1)
        return lbl_v

    def perbarui(self, data_t: list | None = None, data_m: list | None = None):
        try:
            stat = DBManager().statistik_harga()

            total = stat.get("total", 0)
            self.lbl_produk.setText(str(total) if total else "–")

            all_data = (data_t or []) + (data_m or [])
            if all_data:
                harga_list = [
                    (row["harga"] if hasattr(row, "keys") else row[1])
                    for row in all_data
                    if (row["harga"] if hasattr(row, "keys") else row[1]) and
                       (row["harga"] if hasattr(row, "keys") else row[1]) > 0
                ]
                if harga_list:
                    terendah = min(harga_list)
                    self.lbl_terendah.setText(f"Rp {terendah:,.0f}".replace(",", "."))
                else:
                    self.lbl_terendah.setText("–")
            else:
                avg = stat.get("avg", 0)
                self.lbl_terendah.setText(
                    f"Rp {avg:,.0f}".replace(",", ".") if avg else "–"
                )

            from datetime import datetime
            self.lbl_diperbarui.setText(datetime.now().strftime("%d %b, %H:%M"))

        except Exception:
            pass


# ── Section Header — ikon SVG (ganti emoji 🏪/🛒) ────────────────────────────

class SectionHeader(QFrame):
    STYLE_TRADISIONAL = {
        "bg": "#FFF8EC", "border": "#D4A017", "accent": "#8B5E00",
        "svg": _SVG_PASAR_TRADISIONAL,
        "label": "Pasar Tradisional",
        "sub": "Data harga dari pasar tradisional Bandung (PIHPS)",
    }
    STYLE_MODERN = {
        "bg": "#EEF4FF", "border": "#3B82F6", "accent": "#1E3A8A",
        "svg": _SVG_PASAR_MODERN,
        "label": "Pasar Modern / Supermarket",
        "sub": "Data harga dari pasar modern Bandung (PIHPS)",
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

        # Ikon SVG vektor (ganti emoji)
        lbl_icon = QLabel()
        lbl_icon.setPixmap(_svg_pix(st["svg"], 22, 22))
        lbl_icon.setFixedSize(22, 22)
        lbl_icon.setStyleSheet("background: transparent; border: none;")

        col = QVBoxLayout()
        col.setSpacing(1)
        lbl_judul = QLabel(
            f"<b>{st['label']}</b>"
            f"  <span style='font-size:11px;color:#666;font-weight:normal;'>"
            f"— {jumlah} komoditas</span>"
        )
        lbl_judul.setStyleSheet(
            f"font-size: 14px; color: {st['accent']}; border: none; background: transparent;"
        )
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
                "Data berhasil diperbarui!" if ok else "Update gagal."
            )
        )
        layout.addWidget(self.refresh_bar)

        # ── Grid ──────────────────────────────────────────────────────────
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
        return {0: "semua", 1: "tradisional", 2: "modern"}.get(
            self.combo_pasar.currentIndex(), "semua"
        )

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

        while self.main_layout_grid.count():
            item = self.main_layout_grid.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

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

        if jenis == "semua":
            if data_t:
                self.main_layout_grid.addWidget(SectionHeader("tradisional", len(data_t)))
                self.main_layout_grid.addWidget(_buat_grid_section(data_t, "tradisional"))
            if data_m:
                self.main_layout_grid.addWidget(SectionHeader("modern", len(data_m)))
                self.main_layout_grid.addWidget(_buat_grid_section(data_m, "modern"))
            total  = len(data_t) + len(data_m)
            sumber = "PIHPS Bandung — Tradisional & Modern"

        elif jenis == "tradisional":
            if data_t:
                self.main_layout_grid.addWidget(SectionHeader("tradisional", len(data_t)))
                self.main_layout_grid.addWidget(_buat_grid_section(data_t, "tradisional"))
            total  = len(data_t)
            sumber = "PIHPS Bandung — Pasar Tradisional"

        else:
            if data_m:
                self.main_layout_grid.addWidget(SectionHeader("modern", len(data_m)))
                self.main_layout_grid.addWidget(_buat_grid_section(data_m, "modern"))
            total  = len(data_m)
            sumber = "PIHPS Bandung — Pasar Modern"

        self.main_layout_grid.addStretch()
        self.lbl_info.setText(f"Menampilkan {total} komoditas · Sumber: {sumber}")