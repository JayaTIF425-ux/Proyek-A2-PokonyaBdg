from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QToolTip, QLineEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QCursor, QPixmap, QImage, QIntValidator
import os
import requests


class ImageLoaderThread(QThread):
    image_loaded = pyqtSignal(QPixmap)
    image_failed = pyqtSignal()

    def __init__(self, sumber: str):
        super().__init__()
        self.sumber = sumber

    def run(self):
        try:
            pixmap = QPixmap()
            if os.path.isfile(self.sumber):
                pixmap.load(self.sumber)
            elif self.sumber.startswith("http"):
                r = requests.get(self.sumber, timeout=6)
                r.raise_for_status()
                image = QImage()
                image.loadFromData(r.content)
                pixmap = QPixmap.fromImage(image)
            else:
                self.image_failed.emit()
                return

            if not pixmap.isNull():
                self.image_loaded.emit(pixmap)
            else:
                self.image_failed.emit()
        except Exception:
            self.image_failed.emit()


class CalculatorCard(QFrame):
    """
    Kartu produk di panel kanan Penghitung Belanja.
    Qty bisa diubah via tombol +/− atau diketik langsung.
    """

    def __init__(
        self,
        nama: str,
        harga: float,
        harga_per_toko: dict[str, float],
        callback_update,
        gambar_url: str = "",
    ):
        super().__init__()
        self.nama = nama
        self.harga = harga
        self.harga_per_toko = harga_per_toko
        self.callback = callback_update
        self.qty = 0
        self.gambar_url = gambar_url if isinstance(gambar_url, str) and gambar_url.strip() else ""

        self.setFixedSize(230, 300)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 15px;
            }
        """)
        self._build_ui()

        if self.gambar_url:
            self._muat_gambar()
        else:
            self._tampilkan_placeholder()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 14)
        layout.setSpacing(2)

        self.lbl_gambar = QLabel()
        self.lbl_gambar.setFixedSize(130, 130)
        self.lbl_gambar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_gambar.setStyleSheet("border: none;")

        gambar_row = QHBoxLayout()
        gambar_row.addStretch()
        gambar_row.addWidget(self.lbl_gambar)
        gambar_row.addStretch()

        info_row = QHBoxLayout()
        info_row.setContentsMargins(0, 6, 8, 0)
        btn_info = QPushButton("ℹ")
        btn_info.setFixedSize(20, 20)
        btn_info.setStyleSheet(
            "background: #e8f4fd; border-radius: 10px; font-size: 10px; border: none; color: #2980b9;"
        )
        btn_info.setCursor(QCursor(Qt.CursorShape.WhatsThisCursor))
        btn_info.clicked.connect(self._tampilkan_info_toko)
        info_row.addStretch()
        info_row.addWidget(btn_info)

        title = QLabel(self.nama)
        title.setWordWrap(True)
        title.setStyleSheet(
            "font-weight: bold; color: #67823A; border: none; font-size: 12px; padding: 0 8px;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        toko_tunggal = list(self.harga_per_toko.keys())[0] if len(self.harga_per_toko) == 1 else ""
        if toko_tunggal:
            sub_toko = QLabel(toko_tunggal)
            sub_toko.setStyleSheet("font-size: 10px; color: #888; border: none;")
            sub_toko.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            sub_toko = None

        harga_min = min(self.harga_per_toko.values()) if self.harga_per_toko else self.harga
        price_lbl = QLabel(f"Rp {harga_min:,.0f}".replace(",", "."))
        price_lbl.setStyleSheet(
            "font-weight: bold; color: #67823A; border: none; font-size: 13px;"
        )
        price_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sub_lbl = QLabel("(harga terendah)") if len(self.harga_per_toko) > 1 else QLabel("")
        sub_lbl.setStyleSheet("font-size: 9px; color: #aaa; border: none;")
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ── Qty row: tombol − | input | tombol + ──────────────────────────
        qty_row = QHBoxLayout()
        self.btn_min  = QPushButton("−")
        self.btn_plus = QPushButton("+")

        # ▼ PERUBAHAN: QLabel → QLineEdit agar bisa diketik langsung
        self.input_qty = QLineEdit("0")
        self.input_qty.setFixedWidth(44)
        self.input_qty.setFixedHeight(30)
        self.input_qty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_qty.setValidator(QIntValidator(0, 9999, self))
        self.input_qty.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                color: #333;
                background: white;
                padding: 0;
            }
            QLineEdit:focus {
                border: 1.5px solid #67823A;
            }
        """)
        self.input_qty.editingFinished.connect(self._set_qty_dari_input)

        for btn in (self.btn_min, self.btn_plus):
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(
                "background-color: #67823A; border-radius: 15px; "
                "font-weight: bold; font-size: 14px; border: none; color: white;"
            )

        self.btn_min.clicked.connect(self._kurangi)
        self.btn_plus.clicked.connect(self._tambah)

        qty_row.addStretch()
        qty_row.addWidget(self.btn_min)
        qty_row.addWidget(self.input_qty)
        qty_row.addWidget(self.btn_plus)
        qty_row.addStretch()

        layout.addLayout(info_row)
        layout.addLayout(gambar_row)
        layout.addWidget(title)
        if sub_toko:
            layout.addWidget(sub_toko)
        layout.addWidget(price_lbl)
        layout.addWidget(sub_lbl)
        layout.addStretch()
        layout.addLayout(qty_row)

    def _muat_gambar(self):
        self._thread = ImageLoaderThread(self.gambar_url)
        self._thread.image_loaded.connect(self._tampilkan_gambar)
        self._thread.image_failed.connect(self._tampilkan_placeholder)
        self._thread.start()

    def _tampilkan_placeholder(self):
        self.lbl_gambar.setPixmap(QPixmap())
        self.lbl_gambar.setStyleSheet(
            "border: 2px dashed #ccc; border-radius: 10px;"
            "background-color: #f5f5f5; color: #aaa; font-size: 11px;"
        )
        self.lbl_gambar.setText("No Image")

    def _tampilkan_gambar(self, pixmap: QPixmap):
        scaled = pixmap.scaled(
            118, 118,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.lbl_gambar.setStyleSheet("border: none;")
        self.lbl_gambar.setText("")
        self.lbl_gambar.setPixmap(scaled)

    def _tambah(self):
        self.qty += 1
        self.input_qty.setText(str(self.qty))
        self.callback(self.nama, self.harga_per_toko, self.qty)

    def _kurangi(self):
        if self.qty > 0:
            self.qty -= 1
            self.input_qty.setText(str(self.qty))
            self.callback(self.nama, self.harga_per_toko, self.qty)

    # ▼ BARU: sinkronisasi ketika user selesai mengetik di input_qty
    def _set_qty_dari_input(self):
        teks = self.input_qty.text().strip()
        try:
            nilai = int(teks)
            if nilai < 0:
                nilai = 0
        except ValueError:
            nilai = self.qty  # kembalikan ke nilai sebelumnya jika tidak valid
        self.qty = nilai
        self.input_qty.setText(str(self.qty))
        self.callback(self.nama, self.harga_per_toko, self.qty)

    def reset_qty(self):
        self.qty = 0
        self.input_qty.setText("0")

    def _tampilkan_info_toko(self):
        if not self.harga_per_toko:
            return
        baris = "\n".join(
            f"• {toko}: Rp {harga:,.0f}".replace(",", ".")
            for toko, harga in sorted(self.harga_per_toko.items(), key=lambda x: x[1])
        )
        QToolTip.showText(QCursor.pos(), f"Harga {self.nama} per toko:\n{baris}", self)