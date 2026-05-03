"""
scrapers/borma_scraper.py — Scraper supermarket Borma Dago via REST API.
Output: insert ke harga_supermarket di hargapangan.db

API: https://api.bormadago.com/api/search/search/
"""

import sys
import os
import requests
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import DBManager

# ── Konfigurasi ────────────────────────────────────────────────────────────

NAMA_TOKO = "Borma"
BASE_API  = "https://api.bormadago.com/api/search/search/"
HEADERS   = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer":    "https://www.bormadago.com",
    "Origin":     "https://www.bormadago.com",
    "Accept":     "application/json",
    "Accept-Language": "id",
}

KATEGORI_KEYWORDS: dict[str, list[str]] = {
    "Daging Ayam":   ["ayam", "chicken", "daging ayam"],
    "Daging Sapi":   ["sapi", "beef", "daging sapi", "has dalam", "has luar", "iga sapi"],
    "Beras":         ["beras", "rice"],
    "Minyak Goreng": ["minyak goreng", "cooking oil", "sunco", "bimoli", "filma", "sania"],
    "Cabai Merah":   ["cabe merah", "cabai merah", "cabai keriting", "cabe keriting"],
    "Cabai Rawit":   ["cabe rawit", "cabai rawit", "rawit"],
    "Telur Ayam":    ["telur ayam", "telur", "telor"],
    "Bawang Merah":  ["bawang merah", "shallot"],
    "Bawang Putih":  ["bawang putih", "garlic"],
    "Gula":          ["gula pasir", "gula merah", "gula aren", "gulaku"],
}

# Kata kunci yang menyebabkan produk di-skip (produk olahan/non-segar)
NEGATIF = {
    "mie", "indomie", "sarimi", "pop mie", "bihun", "soun", "noodle", "ramen",
    "nugget", "sosis", "bakso", "kornet", "ham", "smoked", "dendeng", "abon",
    "sambal", "kecap", "saos", "saus", "bumbu", "racik", "instan", "kaldu",
    "tepung", "kerupuk", "kripik", "snack", "chips", "biskuit", "wafer",
    "susu", "teh", "kopi", "sirup", "juice", "rokok", "sabun", "deterjen",
    "yoghurt", "mashed", "puyuh", "teri",
}


# ── Logika Kategorisasi ────────────────────────────────────────────────────

def deteksi_kategori(nama: str) -> str | None:
    n = nama.lower()
    if any(neg in n for neg in NEGATIF):
        return None
    for kat, keywords in KATEGORI_KEYWORDS.items():
        if any(kw.lower() in n for kw in keywords):
            return kat
    return None


# ── Scraper ────────────────────────────────────────────────────────────────

def scrape_semua_produk(url_awal: str, is_promo: bool = False) -> list[dict]:
    url   = url_awal
    hal   = 1
    hasil = []

    label = "Promo" if is_promo else "Reguler"
    print(f"\n  [{NAMA_TOKO}] Ambil produk {label}...")

    while url:
        print(f"    Halaman {hal}...", end=" ", flush=True)
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            data = resp.json()
        except Exception as e:
            print(f"✗ {e}")
            break

        for item in data.get("results", []):
            nama     = item.get("title", "")
            kategori = deteksi_kategori(nama)
            if not kategori:
                continue

            # Struktur harga: item["price_sell"]["price"]["amount"]
            # Harga dalam ribuan IDR, misal "29.90" = Rp 29.900
            harga = 0.0
            stok  = 0
            try:
                price_sell = item.get("price_sell") or {}
                amount_raw = price_sell.get("price", {}).get("amount", 0)
                harga = round(float(amount_raw or 0))
            except (TypeError, ValueError):
                harga = 0.0
            try:
                stok = int(
                    (item.get("inventory_generic") or {}).get("quantity_available", 0)
                    or 0
                )
            except (TypeError, ValueError):
                stok = 0

            hasil.append({
                "toko":         NAMA_TOKO,
                "kategori":     kategori,
                "nama_produk":  nama,
                "harga":        harga,
                "stok":         stok,
                "thumbnail_url": item.get("thumbnail_url", ""),
            })

        print(f"✓ ({len(hasil)} total terkumpul)")
        url = data.get("next")
        hal += 1

    return hasil


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*55}")
    print(f"  Borma Scraper — Mulai")
    print(f"  Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}")

    db = DBManager()
    db.init_schema()

    # Produk reguler + promo
    produk_reguler = scrape_semua_produk(BASE_API)
    produk_promo   = scrape_semua_produk(BASE_API + "?is_promo_active=true", is_promo=True)

    # Deduplikasi berdasarkan nama_produk
    semua = {p["nama_produk"]: p for p in produk_reguler + produk_promo}
    final = list(semua.values())

    if final:
        db.insert_harga_supermarket(final)

    print(f"\n{'='*55}")
    print(f"  Selesai! {len(final)} produk unik dari {NAMA_TOKO}.")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()