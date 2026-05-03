"""
gui/components/calculator_card.py — Kartu produk untuk kalkulator belanja.
Mendukung harga multi-toko dan callback ke halaman penghitung.
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QToolTip
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor


class CalculatorCard(QFrame):
    """
    Kartu produk di panel kanan Penghitung Belanja.
    Menampilkan nama, harga minimum, dan kontrol qty (+/-).
    Menekan ikon info menampilkan harga dari semua toko.
    """

    def __init__(
        self,
        nama: str,
        harga: float,
        harga_per_toko: dict[str, float],
        callback_update,  # callable(nama, harga_per_toko, qty)
    ):
        super().__init__()
        self.nama          = nama
        self.harga         = harga
        self.harga_per_toko = harga_per_toko
        self.callback      = callback_update
        self.qty           = 0

        self.setFixedSize(200, 160)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
        """)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)

        # Header: nama + tombol info
        header_row = QHBoxLayout()
        title = QLabel(self.nama)
        title.setWordWrap(True)
        title.setStyleSheet(
            "font-weight: bold; color: #6B8E23; border: none; font-size: 12px;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_info = QPushButton("ℹ")
        btn_info.setFixedSize(20, 20)
        btn_info.setStyleSheet(
            "background: #e8f4fd; border-radius: 10px; font-size: 10px; border: none; color: #2980b9;"
        )
        btn_info.setCursor(QCursor(Qt.CursorShape.WhatsThisCursor))
        btn_info.clicked.connect(self._tampilkan_info_toko)

        header_row.addWidget(title)
        header_row.addStretch()
        header_row.addWidget(btn_info)

        # Harga minimum
        harga_min = min(self.harga_per_toko.values()) if self.harga_per_toko else self.harga
        price_lbl = QLabel(f"Rp {harga_min:,.0f}".replace(",", "."))
        price_lbl.setStyleSheet(
            "font-weight: bold; color: #333; border: none; font-size: 13px;"
        )
        price_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sub_lbl = QLabel("(harga terendah)")
        sub_lbl.setStyleSheet("font-size: 9px; color: #aaa; border: none;")
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Kontrol qty
        qty_row = QHBoxLayout()
        self.btn_min  = QPushButton("−")
        self.lbl_qty  = QLabel("0")
        self.btn_plus = QPushButton("+")

        for btn in (self.btn_min, self.btn_plus):
            btn.setFixedSize(28, 28)
            btn.setStyleSheet(
                "background-color: #f1f1f1; border-radius: 14px; "
                "font-weight: bold; font-size: 14px; border: 1px solid #ddd;"
            )

        self.lbl_qty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_qty.setStyleSheet("border: none; font-size: 14px; font-weight: bold;")
        self.lbl_qty.setFixedWidth(32)

        self.btn_min.clicked.connect(self._kurangi)
        self.btn_plus.clicked.connect(self._tambah)

        qty_row.addStretch()
        qty_row.addWidget(self.btn_min)
        qty_row.addWidget(self.lbl_qty)
        qty_row.addWidget(self.btn_plus)
        qty_row.addStretch()

        layout.addLayout(header_row)
        layout.addWidget(price_lbl)
        layout.addWidget(sub_lbl)
        layout.addStretch()
        layout.addLayout(qty_row)

    # ── Aksi ──────────────────────────────────────────────────────────────

    def _tambah(self):
        self.qty += 1
        self.lbl_qty.setText(str(self.qty))
        self.callback(self.nama, self.harga_per_toko, self.qty)

    def _kurangi(self):
        if self.qty > 0:
            self.qty -= 1
            self.lbl_qty.setText(str(self.qty))
            self.callback(self.nama, self.harga_per_toko, self.qty)

    def reset_qty(self):
        self.qty = 0
        self.lbl_qty.setText("0")

    def _tampilkan_info_toko(self):
        """Tampilkan tooltip berisi harga dari semua toko."""
        if not self.harga_per_toko:
            return
        baris = "\n".join(
            f"• {toko}: Rp {harga:,.0f}".replace(",", ".")
            for toko, harga in sorted(self.harga_per_toko.items(), key=lambda x: x[1])
        )
        QToolTip.showText(
            QCursor.pos(),
            f"Harga {self.nama} per toko:\n{baris}",
            self
        )
