"""
gui/components/price_chart.py — Komponen grafik tren harga.
Embed matplotlib ke PyQt6, data dari fetch_tren_harga_by_pasar() di DBManager.
Mendukung tampilan: Semua (dua garis), Tradisional, atau Modern saja.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from datetime import datetime

from database.db_manager import DBManager


# ── Worker Thread ──────────────────────────────────────────────────────────────

class TrenWorker(QThread):
    """Ambil data tren tradisional DAN modern di background."""
    selesai = pyqtSignal(list, list, str)   # (data_t, data_m, komoditas)

    def __init__(self, komoditas: str, jenis_pasar: str = "semua", hari: int = 30):
        super().__init__()
        self.komoditas   = komoditas
        self.jenis_pasar = jenis_pasar
        self.hari        = hari

    def run(self):
        try:
            db = DBManager()
            if self.jenis_pasar == "semua":
                data_t = list(db.fetch_tren_harga_by_pasar(
                    self.komoditas, "tradisional", self.hari))
                data_m = list(db.fetch_tren_harga_by_pasar(
                    self.komoditas, "modern", self.hari))
            elif self.jenis_pasar == "tradisional":
                data_t = list(db.fetch_tren_harga_by_pasar(
                    self.komoditas, "tradisional", self.hari))
                data_m = []
            else:  # modern
                data_t = []
                data_m = list(db.fetch_tren_harga_by_pasar(
                    self.komoditas, "modern", self.hari))
            self.selesai.emit(data_t, data_m, self.komoditas)
        except Exception as e:
            print(f"[TrenWorker] Error: {e}")
            self.selesai.emit([], [], self.komoditas)


# ── Canvas Matplotlib ──────────────────────────────────────────────────────────

class GrafikCanvas(FigureCanvas):
    """Canvas matplotlib yang di-embed di PyQt6."""

    # Warna pasar tradisional
    WARNA_TRADISIONAL      = "#8B5E00"   # coklat emas
    WARNA_TRADISIONAL_AREA = "#D4A017"
    WARNA_TITIK_T          = "#D4A017"

    # Warna pasar modern
    WARNA_MODERN           = "#1E3A8A"   # biru tua
    WARNA_MODERN_AREA      = "#3B82F6"
    WARNA_TITIK_M          = "#60A5FA"

    WARNA_GRID = "#f0ede8"
    WARNA_BG   = "#ffffff"

    def __init__(self, parent=None):
        self.fig = Figure(figsize=(5, 2.8), dpi=100)
        self.fig.patch.set_facecolor(self.WARNA_BG)
        self.ax  = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self._tampilkan_placeholder("Pilih komoditas untuk melihat tren harga")

    def _bersihkan(self):
        self.ax.clear()
        self.ax.set_facecolor(self.WARNA_BG)

    def _tampilkan_placeholder(self, pesan: str, warna: str = "#bbb"):
        self._bersihkan()
        self.ax.text(
            0.5, 0.5, pesan,
            ha="center", va="center",
            transform=self.ax.transAxes,
            fontsize=10, color=warna,
            wrap=True
        )
        self.ax.axis("off")
        self.fig.tight_layout()
        self.draw()

    def tampilkan_loading(self):
        self._tampilkan_placeholder("Memuat data...")

    @staticmethod
    def _parse_data(data: list):
        tanggal_list, harga_list = [], []
        for row in data:
            try:
                tgl = datetime.strptime(row["tanggal"], "%Y-%m-%d")
                tanggal_list.append(tgl)
                harga_list.append(float(row["harga"]))
            except (ValueError, KeyError, TypeError):
                continue
        return tanggal_list, harga_list

    def _plot_satu_garis(self, tanggal_list, harga_list,
                         warna_garis, warna_area, warna_titik,
                         label: str):
        """Gambar satu garis dengan area dan titik data."""
        self.ax.plot(
            tanggal_list, harga_list,
            color=warna_garis, linewidth=2,
            label=label, zorder=3
        )
        self.ax.fill_between(
            tanggal_list, harga_list,
            alpha=0.10, color=warna_area, zorder=2
        )
        self.ax.scatter(
            tanggal_list, harga_list,
            color=warna_titik, s=30, zorder=4,
            edgecolors=warna_garis, linewidths=0.8
        )
        # Anotasi titik terakhir
        self.ax.annotate(
            f"Rp {harga_list[-1]:,.0f}",
            xy=(tanggal_list[-1], harga_list[-1]),
            xytext=(8, 6), textcoords="offset points",
            fontsize=7, color=warna_garis, fontweight="bold",
            bbox=dict(
                boxstyle="round,pad=0.25",
                facecolor="#fff",
                edgecolor=warna_garis,
                linewidth=0.7,
                alpha=0.9
            )
        )

    def _format_sumbu(self, semua_tanggal):
        """Format sumbu X dan Y."""
        if len(semua_tanggal) <= 14:
            self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        else:
            self.ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        plt.setp(self.ax.get_xticklabels(), rotation=30, ha="right", fontsize=7)
        self.ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, _: f"Rp {x:,.0f}")
        )
        self.ax.tick_params(axis="y", labelsize=7)

    def plot(self, data_t: list, data_m: list, komoditas: str):
        """
        Render grafik tren harga.
        - data_t : tren pasar tradisional
        - data_m : tren pasar modern
        Bisa salah satu kosong (filter tunggal) atau keduanya ada (mode semua).
        """
        self._bersihkan()

        tgl_t, hrg_t = self._parse_data(data_t)
        tgl_m, hrg_m = self._parse_data(data_m)

        ada_t = len(tgl_t) >= 2
        ada_m = len(tgl_m) >= 2

        if not ada_t and not ada_m:
            self._tampilkan_placeholder(
                f"Belum ada data tren untuk\n'{komoditas}'\n\n"
                "Jalankan scraper PIHPS terlebih dahulu.",
                warna="#aaa"
            )
            return

        if ada_t:
            self._plot_satu_garis(
                tgl_t, hrg_t,
                self.WARNA_TRADISIONAL,
                self.WARNA_TRADISIONAL_AREA,
                self.WARNA_TITIK_T,
                label="Tradisional"
            )

        if ada_m:
            self._plot_satu_garis(
                tgl_m, hrg_m,
                self.WARNA_MODERN,
                self.WARNA_MODERN_AREA,
                self.WARNA_TITIK_M,
                label="Modern"
            )

        # Legend jika keduanya tampil
        if ada_t and ada_m:
            self.ax.legend(
                loc="upper left", fontsize=8,
                framealpha=0.85, edgecolor="#ccc"
            )

        # Judul perubahan (ambil dari data yang ada, prioritaskan tradisional)
        ref_hrg = hrg_t if ada_t else hrg_m
        if len(ref_hrg) >= 2:
            selisih = ref_hrg[-1] - ref_hrg[0]
            persen  = (selisih / ref_hrg[0] * 100) if ref_hrg[0] else 0
            tanda   = "↑" if selisih > 0 else "↓" if selisih < 0 else "→"
            warna_p = "#C0392B" if selisih > 0 else "#27AE60" if selisih < 0 else "#888"
            label_jenis = "(Tradisional)" if ada_t else "(Modern)"
            self.ax.set_title(
                f"{tanda} {abs(persen):.1f}%  (Rp {abs(selisih):,.0f}) {label_jenis}",
                fontsize=9, color=warna_p, pad=5, loc="right"
            )

        # Format sumbu
        semua_tgl = tgl_t + tgl_m
        self._format_sumbu(semua_tgl)

        # Rentang Y agar kedua garis terlihat
        semua_hrg = hrg_t + hrg_m
        margin = (max(semua_hrg) - min(semua_hrg)) * 0.3 or max(semua_hrg) * 0.05
        self.ax.set_ylim(
            bottom=min(semua_hrg) - margin,
            top=max(semua_hrg) + margin
        )

        # Grid & styling
        self.ax.grid(True, axis="y", color=self.WARNA_GRID,
                     linewidth=0.8, linestyle="--")
        for spine in ["top", "right"]:
            self.ax.spines[spine].set_visible(False)
        self.ax.spines["left"].set_color("#ddd")
        self.ax.spines["bottom"].set_color("#ddd")

        self.fig.tight_layout(pad=1.2)
        self.draw()


# ── Widget Utama ───────────────────────────────────────────────────────────────

class PriceChartWidget(QWidget):
    """
    Widget grafik tren harga lengkap dengan dropdown komoditas, periode,
    dan jenis pasar (Semua / Tradisional / Modern).

    Cara pakai di halaman_beranda.py:
        from gui.components.price_chart import PriceChartWidget
        self.chart = PriceChartWidget()
        layout.addWidget(self.chart)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._init_ui()
        self._muat_daftar_komoditas()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # ── Header: dropdown komoditas + periode + jenis pasar ──
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border: 1px solid #e0dbd5;
                border-radius: 8px;
            }
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(12, 8, 12, 8)

        lbl_judul = QLabel("Tren Harga")
        lbl_judul.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #6B1423; border: none;"
        )
        h_layout.addWidget(lbl_judul)
        h_layout.addStretch()

        # Dropdown komoditas
        lbl_k = QLabel("Komoditas:")
        lbl_k.setStyleSheet("font-size: 11px; color: #555; border: none;")
        self.combo_komoditas = QComboBox()
        self.combo_komoditas.setFixedWidth(210)
        self.combo_komoditas.setStyleSheet(self._style_combo())
        self.combo_komoditas.currentTextChanged.connect(self._on_komoditas_berubah)

        # Dropdown jenis pasar
        lbl_pasar = QLabel("Pasar:")
        lbl_pasar.setStyleSheet("font-size: 11px; color: #555; border: none;")
        self.combo_pasar = QComboBox()
        self.combo_pasar.addItems(["Semua", "Tradisional", "Modern"])
        self.combo_pasar.setFixedWidth(110)
        self.combo_pasar.setStyleSheet(self._style_combo())
        self.combo_pasar.currentIndexChanged.connect(self._on_filter_berubah)

        # Dropdown periode
        lbl_p = QLabel("Periode:")
        lbl_p.setStyleSheet("font-size: 11px; color: #555; border: none;")
        self.combo_hari = QComboBox()
        self.combo_hari.addItems(["7 hari", "14 hari", "30 hari", "60 hari", "90 hari"])
        self.combo_hari.setCurrentIndex(2)  # default 30 hari
        self.combo_hari.setFixedWidth(85)
        self.combo_hari.setStyleSheet(self._style_combo())
        self.combo_hari.currentIndexChanged.connect(self._on_filter_berubah)

        h_layout.addWidget(lbl_k)
        h_layout.addWidget(self.combo_komoditas)
        h_layout.addSpacing(10)
        h_layout.addWidget(lbl_pasar)
        h_layout.addWidget(self.combo_pasar)
        h_layout.addSpacing(10)
        h_layout.addWidget(lbl_p)
        h_layout.addWidget(self.combo_hari)

        layout.addWidget(header)

        # ── Area grafik ──
        self.frame_grafik = QFrame()
        self.frame_grafik.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border: 1px solid #e0dbd5;
                border-radius: 8px;
            }
        """)
        g_layout = QVBoxLayout(self.frame_grafik)
        g_layout.setContentsMargins(6, 6, 6, 4)

        self.canvas = GrafikCanvas(self)
        g_layout.addWidget(self.canvas)

        # Status kecil di bawah grafik
        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet(
            "color: #aaa; font-size: 10px; border: none; padding: 1px;"
        )
        g_layout.addWidget(self.lbl_status)

        layout.addWidget(self.frame_grafik)

    @staticmethod
    def _style_combo() -> str:
        return """
            QComboBox {
                padding: 3px 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 11px;
                background: #fff;
            }
            QComboBox:hover { border-color: #6B1423; }
            QComboBox::drop-down { border: none; }
        """

    # ── Logic ──────────────────────────────────────────────────────────

    def _muat_daftar_komoditas(self):
        """Isi dropdown dari database."""
        try:
            daftar = DBManager().daftar_komoditas()
            self.combo_komoditas.blockSignals(True)
            self.combo_komoditas.clear()
            if daftar:
                self.combo_komoditas.addItems(daftar)
                self.combo_komoditas.blockSignals(False)
                self._muat_grafik(daftar[0])
            else:
                self.combo_komoditas.addItem("Belum ada data")
                self.combo_komoditas.blockSignals(False)
                self.lbl_status.setText(
                    "Database kosong — jalankan scraper PIHPS dulu"
                )
        except Exception as e:
            self.lbl_status.setText(f"Gagal memuat komoditas: {e}")

    def _get_hari(self) -> int:
        return int(self.combo_hari.currentText().split()[0])

    def _get_jenis_pasar(self) -> str:
        mapping = {0: "semua", 1: "tradisional", 2: "modern"}
        return mapping.get(self.combo_pasar.currentIndex(), "semua")

    def _on_komoditas_berubah(self, nama: str):
        if nama and nama != "Belum ada data":
            self._muat_grafik(nama)

    def _on_filter_berubah(self):
        nama = self.combo_komoditas.currentText()
        if nama and nama != "Belum ada data":
            self._muat_grafik(nama)

    def _muat_grafik(self, komoditas: str):
        """Jalankan worker untuk ambil data lalu render grafik."""
        self.canvas.tampilkan_loading()
        self.lbl_status.setText("Memuat...")

        if self._worker and self._worker.isRunning():
            self._worker.quit()
            self._worker.wait()

        self._worker = TrenWorker(
            komoditas,
            jenis_pasar=self._get_jenis_pasar(),
            hari=self._get_hari()
        )
        self._worker.selesai.connect(self._on_data_siap)
        self._worker.start()

    def _on_data_siap(self, data_t: list, data_m: list, komoditas: str):
        self.canvas.plot(data_t, data_m, komoditas)
        total = len(data_t) + len(data_m)
        jenis = self._get_jenis_pasar()
        label_jenis = {
            "semua": "Tradisional & Modern",
            "tradisional": "Pasar Tradisional",
            "modern": "Pasar Modern"
        }.get(jenis, "")
        if total:
            self.lbl_status.setText(
                f"{total} titik data  ·  {komoditas}  ·  {label_jenis}  ·  Sumber: PIHPS Bandung"
            )
        else:
            self.lbl_status.setText(
                f"Tidak ada data untuk '{komoditas}' ({label_jenis})"
            )

    def refresh(self):
        """Panggil setelah scraper selesai untuk reload."""
        self._muat_daftar_komoditas()