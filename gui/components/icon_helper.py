# gui/components/icon_helper.py

import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

KATEGORI_MAP = [
    # ── exact match kategori DB ──────────────────────────────
    ("cabai rawit hijau",   "cabe_rawit_hijau"),   # PIHPS
    ("cabai rawit merah",   "cabe_rawit_merah"),   # PIHPS
    ("cabai rawit",         "cabe_rawit_merah"),   # Supermarket → "Cabai Rawit"
    ("cabai merah besar",   "cabai_merah_besar"),  # PIHPS
    ("cabai merah",         "cabai_merah_besar"),  # Supermarket → "Cabai Merah"
    ("telur ayam",          "telur"),              # Supermarket → "Telur Ayam"
    ("telur ayam ras",      "telur"),              # PIHPS
    ("daging ayam",         "daging_ayam"),        # Supermarket & PIHPS
    ("daging sapi",         "daging_sapi"),        # Supermarket & PIHPS
    ("bawang merah",        "bawang_merah"),       # Supermarket & PIHPS
    ("bawang putih",        "bawang_putih"),       # Supermarket & PIHPS
    ("minyak goreng",       "minyak_goreng"),      # Supermarket → "Minyak Goreng"
    ("minyak",              "minyak_goreng"),
    ("gula pasir",          "gula_pasir"),         # PIHPS
    ("gula",                "gula_pasir"),         # Supermarket → "Gula"
    ("beras",               "beras"),              # Supermarket & PIHPS
    ("ketan",               "beras"),
]

NAMA_MAP = [
    ("beras induk ayam",    "beras"),
    ("bawang merah",        "bawang_merah"),
    ("bawang putih",        "bawang_putih"),
    ("keriting hijau",      "cabe_rawit_hijau"),
    ("keriting merah",      "cabai_merah_besar"),
    ("rawit hijau",         "cabe_rawit_hijau"),
    ("rawit merah",         "cabe_rawit_merah"),
    ("cabai rawit hijau",   "cabe_rawit_hijau"),
    ("cabai rawit merah",   "cabe_rawit_merah"),
    ("cabai rawit",         "cabe_rawit_merah"),
    ("cabai merah",         "cabai_merah_besar"),
    ("cabe rawit hijau",    "cabe_rawit_hijau"),
    ("cabe rawit merah",    "cabe_rawit_merah"),
    ("cabai",               "cabai_merah_besar"),
    ("telur ayam",          "telur"),
    ("telur",               "telur"),
    ("daging ayam",         "daging_ayam"),
    ("paha ayam",           "daging_ayam"),
    ("ayam",                "daging_ayam"),
    ("daging sapi",         "daging_sapi"),
    ("sapi",                "daging_sapi"),
    ("beras",               "beras"),
    ("ketan",               "beras"),
    ("minyak",              "minyak_goreng"),
    ("gula",                "gula_pasir"),
]

EMOJI_MAP = {
    "bawang merah": "🧅",
    "bawang putih": "🧄",
    "cabai":        "🌶️",
    "ayam":         "🍗",
    "sapi":         "🥩",
    "telur":        "🥚",
    "beras":        "🌾",
    "minyak":       "🫙",
    "gula":         "🍬",
}

# ✅ calculator_card.py ada di gui/components/ → naik 1x ke gui/ → masuk assets/images/fallback
ICONS_DIR = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),  # gui/components/
    "..",                                         # gui/
    "assets", "images", "fallback"               # gui/assets/images/fallback
))
ICON_EXT = ".jpg"


def get_icon_path(nama_produk: str, kategori: str = "") -> str | None:
    nama_lower = nama_produk.lower()

    # Jika kategori "cabai rawit" tanpa hijau/merah,
    # tentukan dari nama produk
    if kategori.lower() in ("cabai rawit",):
        if "hijau" in nama_lower:
            path = os.path.join(ICONS_DIR, "cabe_rawit_hijau" + ICON_EXT)
            if os.path.exists(path): return path
        else:
            path = os.path.join(ICONS_DIR, "cabe_rawit_merah" + ICON_EXT)
            if os.path.exists(path): return path

    # Lanjut normal
    if kategori:
        kategori_lower = kategori.lower()
        for keyword, filename in KATEGORI_MAP:
            if keyword in kategori_lower:
                path = os.path.join(ICONS_DIR, filename + ICON_EXT)
                if os.path.exists(path):
                    return path

    for keyword, filename in NAMA_MAP:
        if keyword in nama_lower:
            path = os.path.join(ICONS_DIR, filename + ICON_EXT)
            if os.path.exists(path):
                return path

    return None

def get_emoji(nama_produk: str) -> str:
    nama_lower = nama_produk.lower()
    return next(
        (e for k, e in EMOJI_MAP.items() if k in nama_lower),
        "🛒"
    )


def apply_icon_to_label(label, nama_produk: str, kategori: str = "", size: tuple = (70, 90)):
    icon_path = get_icon_path(nama_produk, kategori)  # ← nama_produk, bukan self.nama
    if icon_path:
        pixmap = QPixmap(icon_path).scaled(
            *size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        label.setPixmap(pixmap)
    else:
        label.setText(get_emoji(nama_produk))
        label.setStyleSheet(label.styleSheet() + "font-size: 28px;")