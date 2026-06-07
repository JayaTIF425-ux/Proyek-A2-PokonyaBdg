"""
gui/components/product_card.py — Kartu komoditas dengan mini chart tren harga.

Fitur:
  - Header nama komoditas (warna berbeda: tradisional vs modern)
  - Mini chart SVG tren harga terpisah per jenis_pasar
  - Harga terkini + persentase perubahan
  - Tombol "Lihat Harga Berbagai Merk" → navigasi ke halaman pencarian
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath

from database.db_manager import DBManager


# ── Worker: ambil data tren di background ─────────────────────────────────────

class MiniChartWorker(QThread):
    selesai = pyqtSignal(list)

    def __init__(self, komoditas: str, jenis_pasar: str = "tradisional", hari: int = 999):
        super().__init__()
        self.komoditas   = komoditas
        self.jenis_pasar = jenis_pasar
        self.hari        = hari

    def run(self):
        try:
            # Gunakan query yang sudah difilter per jenis_pasar
            data = DBManager().fetch_tren_harga_by_pasar(
                self.komoditas, self.jenis_pasar, self.hari
            )
            self.selesai.emit(list(data))
        except Exception:
            self.selesai.emit([])


# ── Widget mini chart (pure PyQt6, tanpa matplotlib) ─────────────────────────

class MiniChartWidget(QFrame):
    """
    Grafik garis mini yang digambar langsung pakai QPainter.
    Mendukung warna garis berbeda berdasarkan jenis_pasar.
    """

    # Warna area fill untuk tiap jenis pasar
    WARNA_AREA = {
        "tradisional": QColor("#8B5E00"),   # coklat emas
        "modern":      QColor("#1E3A8A"),   # biru tua
    }

    def __init__(self, jenis_pasar: str = "tradisional", parent=None):
        super().__init__(parent)
        self.jenis_pasar   = jenis_pasar
        self._data_harga: list[float] = []
        self.setFixedHeight(72)
        self.setStyleSheet("background: transparent; border: none;")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_data(self, data: list):
        """Terima list of sqlite3.Row (tanggal, harga) lalu render ulang."""
        self._data_harga = []
        for row in data:
            try:
                self._data_harga.append(float(row["harga"]))
            except (KeyError, TypeError, ValueError):
                continue
        self.update()   # trigger paintEvent

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        pad_x, pad_y = 10, 8

        data = self._data_harga
        if len(data) < 2:
            pen = QPen(QColor("#ccc"), 1.5, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(pad_x, h // 2, w - pad_x, h // 2)
            painter.end()
            return

        min_h = min(data)
        max_h = max(data)
        rentang = max_h - min_h if max_h != min_h else 1

        def to_x(i):
            return pad_x + i * (w - 2 * pad_x) / (len(data) - 1)

        def to_y(val):
            return (h - pad_y) - (val - min_h) / rentang * (h - 2 * pad_y)

        points = [(to_x(i), to_y(v)) for i, v in enumerate(data)]

        # ── Area di bawah garis ──
        color_area = self.WARNA_AREA.get(self.jenis_pasar, QColor("#6B1423"))
        color_area_fill = QColor(color_area)
        color_area_fill.setAlpha(30)

        path_area = QPainterPath()
        path_area.moveTo(points[0][0], h - pad_y)
        for x, y in points:
            path_area.lineTo(x, y)
        path_area.lineTo(points[-1][0], h - pad_y)
        path_area.closeSubpath()
        painter.fillPath(path_area, QBrush(color_area_fill))

        # ── Warna garis: naik/turun ──
        naik = data[-1] >= data[0]
        warna_garis = QColor("#27AE60") if naik else QColor("#C0392B")

        pen = QPen(warna_garis, 2, Qt.PenStyle.SolidLine)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        path_line = QPainterPath()
        path_line.moveTo(*points[0])
        for x, y in points[1:]:
            path_line.lineTo(x, y)
        painter.drawPath(path_line)

        # ── Titik awal (kuning emas) ──
        painter.setBrush(QBrush(QColor("#D4A017")))
        painter.setPen(QPen(color_area, 1))
        painter.drawEllipse(int(points[0][0]) - 4, int(points[0][1]) - 4, 8, 8)

        # ── Titik akhir (warna naik/turun) ──
        painter.setBrush(QBrush(warna_garis))
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        painter.drawEllipse(int(points[-1][0]) - 4, int(points[-1][1]) - 4, 8, 8)

        painter.end()


# ── ProductCard utama ─────────────────────────────────────────────────────────

class ProductCard(QFrame):
    """
    Kartu komoditas lengkap dengan data terpisah per jenis_pasar.

    Parameter baru:
      jenis_pasar (str) — 'tradisional' atau 'modern'
        → menentukan warna header, warna area chart, dan query data tren.

    Signal:
      lihat_pencarian(str) — dipancarkan saat tombol diklik.
    """

    lihat_pencarian = pyqtSignal(str)

    # Tema warna per jenis pasar
    TEMA = {
        "tradisional": {
            "header_bg":  "#8B5E00",
            "hover_footer": "#FFF3CC",
        },
        "modern": {
            "header_bg":  "#1E3A8A",
            "hover_footer": "#DBEAFE",
        },
    }

    def __init__(
        self,
        nama: str,
        harga: float,
        toko: str,
        tanggal: str,
        jenis_pasar: str = "tradisional",
    ):
        super().__init__()
        self.nama        = nama
        self.harga       = harga
        self.toko        = toko
        self.tanggal     = tanggal
        self.jenis_pasar = jenis_pasar
        self._worker     = None

        self.setFixedSize(260, 220)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            QFrame:hover {
                border: 1.5px solid #6B8E23;
            }
        """)
        self._build_ui()
        self._muat_chart()

    # ── Build UI ───────────────────────────────────────────────────────────────

    def _build_ui(self):
        tema = self.TEMA.get(self.jenis_pasar, self.TEMA["tradisional"])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Header nama komoditas ──
        self.lbl_nama = QLabel(self.nama)
        self.lbl_nama.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_nama.setWordWrap(True)
        self.lbl_nama.setFixedHeight(36)
        self.lbl_nama.setStyleSheet(
            f"background-color: {tema['header_bg']}; color: white; "
            "font-weight: bold; font-size: 11px; padding: 4px 8px; "
            "border-top-left-radius: 7px; border-top-right-radius: 7px;"
        )
        layout.addWidget(self.lbl_nama)

        # ── Mini chart ──
        self.mini_chart = MiniChartWidget(jenis_pasar=self.jenis_pasar)
        layout.addWidget(self.mini_chart)

        # ── Baris harga + perubahan ──
        harga_row = QHBoxLayout()
        harga_row.setContentsMargins(10, 4, 10, 2)

        harga_fmt = f"Rp {self.harga:,.0f}".replace(",", ".")
        self.lbl_harga = QLabel(harga_fmt)
        self.lbl_harga.setStyleSheet(
            "font-size: 17px; font-weight: bold; color: #2c3e50; border: none;"
        )

        self.lbl_perubahan = QLabel("—")
        self.lbl_perubahan.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.lbl_perubahan.setStyleSheet("font-size: 10px; color: #aaa; border: none;")

        harga_row.addWidget(self.lbl_harga)
        harga_row.addStretch()
        harga_row.addWidget(self.lbl_perubahan)
        layout.addLayout(harga_row)

        # ── Satuan ──
        lbl_satuan = QLabel("PER Kg")
        lbl_satuan.setContentsMargins(10, 0, 0, 0)
        lbl_satuan.setStyleSheet("font-size: 9px; color: #aaa; border: none;")
        layout.addWidget(lbl_satuan)

        layout.addStretch()

        # ── Footer ──
        self.footer = QFrame()
        self.footer.setStyleSheet(f"""
            QFrame {{
                background: #f5f5f5;
                border: none;
                border-top: 1px solid #e0e0e0;
                border-bottom-left-radius: 7px;
                border-bottom-right-radius: 7px;
            }}
            QFrame:hover {{ background: {tema['hover_footer']}; }}
        """)
        self.footer.setFixedHeight(30)
        self.footer.setCursor(Qt.CursorShape.PointingHandCursor)

        footer_layout = QHBoxLayout(self.footer)
        footer_layout.setContentsMargins(10, 0, 8, 0)
        footer_layout.setSpacing(0)

        lbl_teks = QLabel("Lihat Harga Berbagai Merk")
        lbl_teks.setStyleSheet(
            "color: #6B8E23; font-size: 10px; font-weight: 500; "
            "border: none; background: transparent;"
        )
        lbl_arrow = QLabel("›")
        lbl_arrow.setStyleSheet(
            "color: #6B8E23; font-size: 16px; border: none; "
            "background: transparent; padding-right: 2px;"
        )

        footer_layout.addWidget(lbl_teks)
        footer_layout.addStretch()
        footer_layout.addWidget(lbl_arrow)
        layout.addWidget(self.footer)

    def mousePressEvent(self, event):
        if self.footer.geometry().contains(event.pos()):
            self.lihat_pencarian.emit(self.nama)
        super().mousePressEvent(event)

    # ── Load chart data ────────────────────────────────────────────────────────

    def _muat_chart(self):
        if self._worker and self._worker.isRunning():
            return
        # Kirim jenis_pasar ke worker agar query difilter dengan benar
        self._worker = MiniChartWorker(
            self.nama,
            jenis_pasar=self.jenis_pasar,
            hari=999
        )
        self._worker.selesai.connect(self._on_chart_data_siap)
        self._worker.start()

    @pyqtSlot(list)
    def _on_chart_data_siap(self, data: list):
        self.mini_chart.set_data(data)

        if len(data) >= 2:
            try:
                h_awal  = float(data[0]["harga"])
                h_akhir = float(data[-1]["harga"])
                if h_awal > 0:
                    persen  = (h_akhir - h_awal) / h_awal * 100
                    selisih = h_akhir - h_awal
                    tanda   = "↑" if persen > 0 else "↓" if persen < 0 else "→"
                    warna   = "#C0392B" if persen > 0 else "#27AE60" if persen < 0 else "#888"
                    teks    = f"{tanda} {abs(persen):.2f}% · Rp {abs(selisih):,.0f}".replace(",", ".")
                    self.lbl_perubahan.setText(teks)
                    self.lbl_perubahan.setStyleSheet(
                        f"font-size: 9px; color: {warna}; border: none;"
                    )
            except (TypeError, ValueError, KeyError):
                pass