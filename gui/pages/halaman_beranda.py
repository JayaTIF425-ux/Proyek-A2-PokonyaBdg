from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QGridLayout, QFrame, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from database.db_manager import DBManager
from gui.components.product_card import ProductCard
from gui.widgets.loading_widget import LoadingWidget
from gui.widgets.refresh_widget import RefreshWidget


class DataWorker(QThread):
    selesai = pyqtSignal(list)

    def __init__(self, jenis_pasar: str = "semua"):
        super().__init__()
        self.jenis_pasar = jenis_pasar

    def run(self):
        data = DBManager().fetch_produk_pihps_by_pasar(self.jenis_pasar)
        self.selesai.emit(list(data))


# ── Widget Statistik Ringkasan Beranda ────────────────────────────────────────

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
        self.setMinimumHeight(80)
        self.setMaximumHeight(100)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(0)

        self.lbl_produk    = self._buat_stat("📦 Produk Terpantau", "–")
        layout.addWidget(self._separator())
        self.lbl_terendah  = self._buat_stat("💰 Harga Terendah", "–")
        layout.addWidget(self._separator())
        self.lbl_diperbarui = self._buat_stat("🕐 Terakhir Diperbarui", "–")

        self.perbarui()

    def _buat_stat(self, label: str, nilai: str) -> QLabel:
        """Buat satu kartu stat dan tambahkan ke layout. Return label nilai."""
        container = QFrame()
        container.setStyleSheet("border: none; background: transparent;")
        v = QVBoxLayout(container)
        v.setContentsMargins(16, 0, 16, 0)
        v.setSpacing(2)
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_label = QLabel(label)
        lbl_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_label.setStyleSheet(
            "font-size: 11px; color: #8B7B6B; border: none; background: transparent;"
        )

        lbl_nilai = QLabel(nilai)
        lbl_nilai.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_nilai.setStyleSheet(
            "font-size: 15px; font-weight: bold; color: #5C1A28; "
            "border: none; background: transparent;"
        )

        v.addWidget(lbl_label)
        v.addWidget(lbl_nilai)
        self.layout().addWidget(container)
        return lbl_nilai

    def _separator(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("color: #E2D9CC; background: #E2D9CC; max-width: 1px;")
        return sep

    def perbarui(self, data: list | None = None):
        """Perbarui angka-angka statistik. Jika data=None, ambil langsung dari DB."""
        try:
            db = DBManager()
            stat = db.statistik_harga()

            total = stat.get("total", 0)
            self.lbl_produk.setText(str(total) if total else "–")

            if data:
                harga_list = []
                for row in data:
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
        self.grid = QGridLayout(self.grid_container)
        self.grid.setSpacing(12)
        self.scroll.setWidget(self.grid_container)

        layout.addWidget(self.loading)
        layout.addWidget(self.scroll)

        self.lbl_info = QLabel("")
        self.lbl_info.setStyleSheet("color: #888; font-size: 11px; padding: 4px;")
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_info)

    def _get_jenis_pasar(self) -> str:
        """Konversi pilihan dropdown ke nilai yang dikirim ke DB."""
        idx = self.combo_pasar.currentIndex()
        mapping = {
            0: "semua",
            1: "tradisional",
            2: "modern",
        }
        return mapping.get(idx, "semua")

    def _on_filter_pasar_berubah(self):
        """Dipanggil setiap dropdown berubah — reload data sesuai filter."""
        self._muat_data()

    def _muat_data(self):
        self.loading.show()
        self.scroll.hide()

        self.worker = DataWorker(jenis_pasar=self._get_jenis_pasar())
        self.worker.selesai.connect(self._tampilkan_data)
        self.worker.start()

    def _tampilkan_data(self, data: list):
        self.loading.hide()
        self.scroll.show()

        # Bersihkan grid lama
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)

        # Perbarui statistik ringkasan dengan data terbaru
        self.stat_beranda.perbarui(data)

        if not data:
            lbl = QLabel("Belum ada data. Jalankan scraper terlebih dahulu.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: #999; font-size: 14px; padding: 40px;")
            self.grid.addWidget(lbl, 0, 0)
            return

        jenis = self._get_jenis_pasar()
        sumber = {
            "semua":       "PIHPS Bandung — Pasar Tradisional & Modern",
            "tradisional": "PIHPS Bandung — Pasar Tradisional",
            "modern":      "PIHPS Bandung — Pasar Modern",
        }.get(jenis, "PIHPS Bandung")

        KOLOM = 3
        for i, row in enumerate(data):
            card = ProductCard(
                nama=row["komoditas"] if hasattr(row, "keys") else row[0],
                harga=row["harga"]    if hasattr(row, "keys") else row[1],
                toko=row["toko"]      if hasattr(row, "keys") else row[3],
                tanggal=row["tanggal"] if hasattr(row, "keys") else row[4],
            )
            card.lihat_pencarian.connect(self.navigasi_pencarian)
            self.grid.addWidget(card, i // KOLOM, i % KOLOM)

        self.lbl_info.setText(
            f"Menampilkan {len(data)} komoditas · Sumber: {sumber}"
        )