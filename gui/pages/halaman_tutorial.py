"""
gui/pages/halaman_tutorial.py — Panduan penggunaan aplikasi PokokNya.Bdg.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QByteArray
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer


# ── SVG Strings ────────────────────────────────────────────────────────────

_SVG_BERANDA = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
viewBox="0 0 24 24" fill="none" stroke="{warna}" stroke-width="2"
stroke-linecap="round" stroke-linejoin="round">
<path d="M3 9.5L12 3l9 6.5V20a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9.5z"/>
<path d="M9 21V12h6v9"/></svg>"""

_SVG_PENCARIAN = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
viewBox="0 0 24 24" fill="none" stroke="{warna}" stroke-width="2"
stroke-linecap="round" stroke-linejoin="round">
<circle cx="10" cy="10" r="6"/>
<line x1="14.5" y1="14.5" x2="21" y2="21"/>
<text x="7" y="13.5" font-size="7" fill="{warna}" stroke="none"
font-family="sans-serif" font-weight="bold">Rp</text></svg>"""

_SVG_PENGHITUNG = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
viewBox="0 0 24 24" fill="none" stroke="{warna}" stroke-width="2"
stroke-linecap="round" stroke-linejoin="round">
<path d="M6 2h12a1 1 0 0 1 1 1v3H5V3a1 1 0 0 1 1-1z"/>
<path d="M5 6h14l-1.5 14H6.5L5 6z"/>
<line x1="9" y1="11" x2="9" y2="16"/>
<line x1="12" y1="11" x2="12" y2="16"/>
<line x1="15" y1="11" x2="15" y2="16"/></svg>"""

_SVG_CART = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
viewBox="0 0 24 24" fill="none" stroke="{warna}" stroke-width="2"
stroke-linecap="round" stroke-linejoin="round">
<circle cx="8" cy="21" r="1"/>
<circle cx="19" cy="21" r="1"/>
<path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/>
</svg>"""

_SVG_FOLDER = """<svg xmlns="http://www.w3.org/2000/svg" fill="none"
viewBox="0 0 24 24" stroke-width="1.5" stroke="{warna}">
<path stroke-linecap="round" stroke-linejoin="round"
d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75
m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12
a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25
h-5.379a1.5 1.5 0 0 1-1.06-.44Z"/></svg>"""

_SVG_REFRESH = """<svg xmlns="http://www.w3.org/2000/svg" fill="none"
viewBox="0 0 24 24" stroke-width="1.5" stroke="{warna}">
<path stroke-linecap="round" stroke-linejoin="round"
d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0
3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1
13.803-3.7l3.181 3.182m0-4.991v4.99"/></svg>"""


# ── Helper: render SVG ke QPixmap ──────────────────────────────────────────

def _render_svg(svg_template: str, warna: str, ukuran: int = 22) -> QPixmap:
    svg_str = svg_template.replace("{warna}", warna)
    renderer = QSvgRenderer(QByteArray(svg_str.encode()))
    pixmap = QPixmap(ukuran, ukuran)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap


def _lbl_svg(svg_template: str, warna: str,
             bg: str, ukuran_kotak: int = 36,
             ukuran_ikon: int = 20) -> QLabel:
    """Buat QLabel berisi ikon SVG dengan background kotak berwarna."""
    lbl = QLabel()
    lbl.setFixedSize(ukuran_kotak, ukuran_kotak)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet(f"""
        background: {bg};
        border-radius: 8px;
        border: none;
    """)
    lbl.setPixmap(_render_svg(svg_template, warna, ukuran_ikon))
    return lbl


# ── Komponen UI ────────────────────────────────────────────────────────────

def _buat_kartu(svg_template: str, warna_ikon: str, warna_bg: str,
                judul: str, deskripsi: str, poin: list[str]) -> QFrame:
    kartu = QFrame()
    kartu.setStyleSheet("""
        QFrame {
            background: white;
            border: 1px solid #e8e8e8;
            border-radius: 10px;
        }
    """)
    layout = QVBoxLayout(kartu)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(8)

    # Header
    header = QHBoxLayout()
    header.setSpacing(10)
    header.addWidget(_lbl_svg(svg_template, warna_ikon, warna_bg))

    lbl_judul = QLabel(judul)
    lbl_judul.setStyleSheet(
        "font-size: 14px; font-weight: bold; color: #2c3e50; border: none;"
    )
    header.addWidget(lbl_judul)
    header.addStretch()
    layout.addLayout(header)

    # Deskripsi
    lbl_desk = QLabel(deskripsi)
    lbl_desk.setWordWrap(True)
    lbl_desk.setStyleSheet(
        "font-size: 12px; color: #555; border: none;"
    )
    layout.addWidget(lbl_desk)

    # Poin
    for item in poin:
        lbl_p = QLabel(f"  •  {item}")
        lbl_p.setWordWrap(True)
        lbl_p.setStyleSheet("font-size: 12px; color: #666; border: none;")
        layout.addWidget(lbl_p)

    layout.addStretch()
    return kartu


def _buat_section_header(svg_template: str, judul: str) -> QHBoxLayout:
    row = QHBoxLayout()
    row.setSpacing(8)
    row.setContentsMargins(0, 8, 0, 0)

    lbl_ikon = QLabel()
    lbl_ikon.setFixedSize(22, 22)
    lbl_ikon.setPixmap(_render_svg(svg_template, "#2c3e50", 20))
    lbl_ikon.setStyleSheet("border: none; background: transparent;")

    lbl_j = QLabel(judul)
    lbl_j.setStyleSheet(
        "font-size: 14px; font-weight: bold; color: #2c3e50; border: none;"
    )
    row.addWidget(lbl_ikon)
    row.addWidget(lbl_j)
    row.addStretch()
    return row


def _buat_kotak_kecil(judul: str, isi: str) -> QFrame:
    frame = QFrame()
    frame.setStyleSheet("""
        QFrame {
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #e8e8e8;
        }
    """)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(12, 10, 12, 10)
    layout.setSpacing(4)

    lbl_j = QLabel(judul)
    lbl_j.setStyleSheet(
        "font-size: 13px; font-weight: bold; color: #2c3e50; border: none;"
    )
    lbl_i = QLabel(isi)
    lbl_i.setWordWrap(True)
    lbl_i.setStyleSheet(
        "font-size: 12px; color: #666; border: none;"
    )
    layout.addWidget(lbl_j)
    layout.addWidget(lbl_i)
    return frame


def _buat_sumber(svg_template: str, warna_ikon: str, warna_bg: str,
                 nama: str, keterangan: str) -> QFrame:
    frame = QFrame()
    frame.setStyleSheet("border: none; background: transparent;")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(8, 8, 8, 8)
    layout.setSpacing(6)
    layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    lbl_ikon = _lbl_svg(svg_template, warna_ikon, warna_bg,
                         ukuran_kotak=40, ukuran_ikon=20)
    lbl_ikon.setStyleSheet(
        f"background: {warna_bg}; border-radius: 20px; border: none;"
    )

    lbl_nama = QLabel(nama)
    lbl_nama.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl_nama.setStyleSheet(
        "font-size: 13px; font-weight: bold; color: #2c3e50; border: none;"
    )

    lbl_ket = QLabel(keterangan)
    lbl_ket.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl_ket.setWordWrap(True)
    lbl_ket.setStyleSheet("font-size: 11px; color: #888; border: none;")

    layout.addWidget(lbl_ikon, alignment=Qt.AlignmentFlag.AlignHCenter)
    layout.addWidget(lbl_nama)
    layout.addWidget(lbl_ket)
    return frame


# ── Halaman Utama ──────────────────────────────────────────────────────────

class HalamanTutorial(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 16)
        layout.setSpacing(0)

        # Judul
        lbl_judul = QLabel("Tutorial Aplikasi")
        lbl_judul.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #2c3e50;"
        )
        lbl_sub = QLabel("Panduan lengkap menggunakan aplikasi mobile PokokNya.Bdg")
        lbl_sub.setStyleSheet(
            "font-size: 13px; color: #888; margin-bottom: 12px; border: none;"
        )
        layout.addWidget(lbl_judul)
        layout.addWidget(lbl_sub)

        # Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")

        konten = QWidget()
        konten.setStyleSheet("background: transparent;")
        k = QVBoxLayout(konten)
        k.setContentsMargins(0, 0, 8, 16)
        k.setSpacing(14)

        # ── 3 kartu fitur ──────────────────────────────────────────────────
        grid = QHBoxLayout()
        grid.setSpacing(12)

        grid.addWidget(_buat_kartu(
            svg_template=_SVG_BERANDA,
            warna_ikon="#3B6D11",
            warna_bg="#EAF3DE",
            judul="Beranda",
            deskripsi=(
                "Halaman utama menampilkan harga rata-rata seluruh komoditas "
                "bahan pokok berdasarkan data PIHPS Bandung untuk pasar tradisional "
                "dan modern secara real-time."
            ),
            poin=[
                "Filter Pasar Tradisional / Modern / Semua",
                "Klik 'Lihat Harga Berbagai Merk' untuk cari di supermarket dan pasar tradisional",
            ],
        ))

        grid.addWidget(_buat_kartu(
            svg_template=_SVG_PENCARIAN,
            warna_ikon="#185FA5",
            warna_bg="#E6F1FB",
            judul="Pencarian",
            deskripsi=(
                "Cari harga komoditas dari semua sumber (PIHPS Nasional, "
                "Borma, dan Yogya) dalam satu tampilan."
            ),
            poin=[
                "Ketik nama bahan (misal: beras, telur, ayam)",
                "Hasil diurutkan dari harga termurah",
                "Klik 'Lihat Semua' untuk tampilkan semua produk",
            ],
        ))

        grid.addWidget(_buat_kartu(
            svg_template=_SVG_PENGHITUNG,
            warna_ikon="#854F0B",
            warna_bg="#FAEEDA",
            judul="Penghitung Belanja",
            deskripsi=(
                "Estimasi total belanja sebelum pergi ke pasar tradisional atau supermarket."
            ),
            poin=[
                "Pilih produk dari panel kanan",
                "Atur jumlah dengan tombol + dan −",
                "Total belanja otomatis terupdate di panel kiri",
                "Reset keranjang untuk mulai ulang",
            ],
        ))

        k.addLayout(grid)

        # ── Section: Memperbarui Data ──────────────────────────────────────
        k.addLayout(_buat_section_header(_SVG_REFRESH, "Memperbarui Data"))

        frame_update = QFrame()
        frame_update.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e8e8e8;
                border-radius: 10px;
            }
        """)
        update_layout = QHBoxLayout(frame_update)
        update_layout.setContentsMargins(16, 16, 16, 16)
        update_layout.setSpacing(12)
        update_layout.addWidget(_buat_kotak_kecil(
            "Refresh",
            "Muat ulang tampilan dari data yang sudah ada di database. "
        ))
        update_layout.addWidget(_buat_kotak_kecil(
            "Update Data",
            "Jalankan scraper untuk ambil data terbaru dari PIHPS, Borma, "
            "dan Yogya. Butuh 2–5 menit dan memerlukan koneksi internet."
        ))
        k.addWidget(frame_update)

        # ── Section: Sumber Data ───────────────────────────────────────────
        k.addLayout(_buat_section_header(_SVG_FOLDER, "Sumber Data"))

        frame_sumber = QFrame()
        frame_sumber.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e8e8e8;
                border-radius: 10px;
            }
        """)
        sumber_layout = QHBoxLayout(frame_sumber)
        sumber_layout.setContentsMargins(16, 16, 16, 16)
        sumber_layout.setSpacing(0)

        for nama, ket, warna_ikon, warna_bg in [
            ("PIHPS",  "Pasar Tradisional & Modern\nBank Indonesia", "#3B6D11", "#EAF3DE"),
            ("Borma",  "Supermarket Bandung",           "#185FA5", "#E6F1FB"),
            ("Yogya",  "Supermarket Bandung",       "#854F0B", "#FAEEDA"),
        ]:
            sumber_layout.addWidget(_buat_sumber(
                svg_template=_SVG_CART,
                warna_ikon=warna_ikon,
                warna_bg=warna_bg,
                nama=nama,
                keterangan=ket,
            ))

        k.addWidget(frame_sumber)
        k.addStretch()

        scroll.setWidget(konten)
        layout.addWidget(scroll)