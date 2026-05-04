"""
gui/components/product_card.py — Kartu tampilan produk standar.
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt


class ProductCard(QFrame):
    """
    Kartu untuk menampilkan satu komoditas:
      - Header berwarna dengan nama produk
      - Harga besar
      - Info toko + tanggal
    """

    def __init__(self, nama: str, harga: float, toko: str, tanggal: str):
        super().__init__()
        self.nama    = nama
        self.harga   = harga
        self.toko    = toko
        self.tanggal = tanggal

        self.setFixedSize(230, 190)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            QFrame:hover {
                border: 1px solid #6B8E23;
                background-color: #fefefe;
            }
        """)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(4)

        # Header
        header = QLabel(self.nama)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setWordWrap(True)
        header.setStyleSheet(
            "background-color: #6B8E23; color: white; font-weight: bold; "
            "padding: 10px; border-top-left-radius: 7px; border-top-right-radius: 7px;"
        )

        # Harga
        harga_fmt = f"Rp {self.harga:,.0f}".replace(",", ".")
        price_lbl = QLabel(harga_fmt)
        price_lbl.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #2c3e50; "
            "border: none; padding: 8px 12px 4px 12px;"
        )

        # Info toko & tanggal
        info_lbl = QLabel(f"📍 {self.toko}\n📅 {self.tanggal or '-'}")
        info_lbl.setStyleSheet(
            "font-size: 10px; color: #7f8c8d; border: none; padding: 0 12px;"
        )

        layout.addWidget(header)
        layout.addWidget(price_lbl)
        layout.addWidget(info_lbl)
        layout.addStretch()
