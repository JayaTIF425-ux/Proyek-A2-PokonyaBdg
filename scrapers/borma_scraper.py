"""
scrapers/borma_scraper.py — Scraper supermarket Borma Dago via REST API.
Output: insert ke harga_supermarket di hargapangan.db

API: https://api.bormadago.com/api/search/search/
"""

import sys
import os
import requests
import time
import re
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

# Mapping kategori → list category ID (bisa lebih dari satu ID per kategori)
KATEGORI_IDS: dict[str, list[int]] = {
    "Telur Ayam":    [790, 789],
    "Daging Ayam":   [585],
    "Daging Sapi":   [586],
    "Beras":         [564],
    "Cabe":          [707],  # dipisah jadi Cabai Merah/Rawit pakai keyword
    "Bawang Merah":  [701],
    "Bawang Putih":  [702],
    "Minyak Goreng": [624],
    "Gula":          [95],
}

# Keyword untuk pisah kategori cabe dari ID 707
CABAI_KEYWORDS: dict[str, list[str]] = {
    "Cabai Merah": ["cabe merah", "cabai merah", "cabai keriting", "cabe keriting"],
    "Cabai Rawit": ["cabe rawit", "cabai rawit", "rawit"],
}

# Keyword untuk filter gula dari ID 95
GULA_KEYWORDS: list[str] = ["gula pasir", "gulaku", "gula putih"]

# Kata kunci yang menyebabkan produk di-skip (produk olahan/non-segar)
NEGATIF = {
    "mie", "indomie", "sarimi", "sedaap", "pop mie", "bihun", "soun", "supermi",
    "kwetiau", "nasi goreng", "tepung", "bubur", "kerupuk", "krupuk", "kripik",
    "migelas", "samyang", "noodle", "ramen",
    "racik", "sasa", "bumbu", "instan", "kaldu", "masako", "royco",
    "knorr", "ajinomoto", "saus", "saos", "kecap", "sambal", "terasi",
    "bubuk", "santan", "garam", "pasta", "curry", "margarin", "krim",
    "sup", "mayonais", "mayo", "kental", "bombay", "rasa", "barbeque",
    "nugget", "sosis", "bakso", "baso", "kornet", "corned", "ham",
    "smoked", "dendeng", "abon", "fiesta", "so good", "sunny gold",
    "champ", "kanzler", "lezza", "dimsum", "burger", "tuna", "mackarel",
    "teh", "tea", "kopi", "coffee", "susu", "milk", "chiki", "balls",
    "piattos", "snack", "keripik", "chips", "biskuit", "wafer", "coklat",
    "chocolate", "permen", "candy", "sirup", "syrup", "juice", "jus",
    "monde", "meriko", "beng-beng", "jelly", "sprite", "coca", "cola",
    "qtela", "potabee", "chitato", "crackers", "bisvit", "nutrisari",
    "ice", "pudding", "orange", "hemaviton", "kacang", "dua", "kelinci",
    "rokok", "filter", "sampo", "sabun", "deterjen", "odol", "tisu", "tissue",
    "spon", "softex", "bayclin", "promina", "felix", "kokona", "kertas", "paper",
    "tomato", "bayam", "hanasui", "pedigree", "me-o", "sheba", "cat", "face", "wash",
    "stick", "toothbrush", "kocokan", "centong", "lip", "bakar", "miyako", "cheese",
    "tempat", "coconut", "thinwall", "cetakan", "food", "container", "foodcontainer",
    "mozarella", "oil", "fisherman", "mashed", "potato", "puring", "soklin", "laut", "gim",
    "nagamas", "koffie", "yoghurt", "kapal", "taro", "bamboe", "spaghetti", "merica",
    "nissin", "kara", "oma", "gabus", "whiskas", "jahe", "indocafe", "jagung", "tomat",
    "arirang", "baby", "tolak", "singkong", "koffe", "soes", "sukses", "cocktail",
    "rapika", "strepsil", "japota", "cerelac", "grill", "ciptadent", "insto", "milo",
    "mangkok", "veritop", "seblak", "sozzis", "cedea", "kencur", "tini", "wini", "iyes",
    "herbadrink", "camilan", "paskali", "daiko", "kombinasi", "porstex", "garuda",
    "alamii", "pan", "colgate", "yogurt", "pronas", "asin", "puyuh", "teri", "desaku",
    "legging", "regulator", "caffe", "italian", "enzim", "setrika", "rak", "kanzler", "roasted",
    "spicy", "rolade", "canola", "sunflower", "virgin", "sasso classico"
}


# ── Logika Kategorisasi Cabe ───────────────────────────────────────────────

def deteksi_cabai(nama: str) -> str | None:
    n = nama.lower()
    # Cek rawit dulu — lebih spesifik, hindari overlap "Cabai Rawit Merah"
    if any(kw in n for kw in CABAI_KEYWORDS["Cabai Rawit"]):
        return "Cabai Rawit"
    # Baru cek merah
    if any(kw in n for kw in CABAI_KEYWORDS["Cabai Merah"]):
        return "Cabai Merah"
    return None  # tidak cocok keyword manapun → skip


# ── Scraper ────────────────────────────────────────────────────────────────

def buat_session() -> requests.Session:
    """Buat session baru untuk simulasi refresh browser."""
    session = requests.Session()
    session.headers.update(HEADERS)
    try:
        session.get("https://www.bormadago.com", timeout=10)
    except Exception:
        pass  # tetap lanjut meski refresh gagal
    return session


def scrape_kategori(kategori: str, cat_id: int, is_promo: bool = False) -> list[dict]:
    url = f"{BASE_API}?is_offline_only=false&category={cat_id}"
    if is_promo:
        url += "&is_promo_active=true"

    hal   = 1
    hasil = []
    MAX_RETRY = 3
    TIMEOUT   = 20

    label = "Promo" if is_promo else "Reguler"
    print(f"\n  [{NAMA_TOKO}] Ambil produk {kategori} — {label}...")

    session = buat_session()  # fresh session tiap kategori

    while url:
        print(f"    Halaman {hal}...", end=" ", flush=True)

        berhasil = False
        data     = None

        for percobaan in range(1, MAX_RETRY + 1):
            try:
                resp = session.get(url, timeout=TIMEOUT)
                data = resp.json()
                berhasil = True
                break
            except requests.exceptions.Timeout:
                if percobaan < MAX_RETRY:
                    print(f"\n  ⚠ Timeout, retry ({percobaan}/{MAX_RETRY})...", end=" ", flush=True)
                    time.sleep(3)
                else:
                    print(f"\n  ✗ Gagal setelah {MAX_RETRY}x, skip halaman ini")
            except Exception as e:
                print(f"\n  ✗ Error: {e}, skip halaman ini")
                break

        if not berhasil:
            hal += 1
            url = re.sub(r'page=\d+', f'page={hal}', url) if "page=" in url \
                  else url + f"&page={hal}"
            continue

        results = data.get("results", [])
        if not results:
            print("✓ Semua halaman selesai")
            break

        for item in results:
            nama = item.get("title", "")
            if any(neg in nama.lower() for neg in NEGATIF):
                continue

            # ── Khusus Cabe: pisah jadi Cabai Merah / Cabai Rawit ──
            if kategori == "Cabe":
                kategori_final = deteksi_cabai(nama)
                if not kategori_final:
                    continue  # tidak cocok keyword manapun → skip
            # ── Khusus Gula: filter pakai keyword ──
            elif kategori == "Gula":
                if not any(kw in nama.lower() for kw in GULA_KEYWORDS):
                    continue  # bukan gula yang relevan → skip
                kategori_final = kategori
            else:
                kategori_final = kategori

            harga = 0.0
            stok  = 0
            try:
                price_sell = item.get("price_sell") or {}
                harga = round(float(price_sell.get("price", {}).get("amount", 0) or 0))
            except (TypeError, ValueError):
                harga = 0.0
            try:
                stok = int((item.get("inventory_generic") or {}).get("quantity_available", 0) or 0)
            except (TypeError, ValueError):
                stok = 0

            hasil.append({
                "toko":          NAMA_TOKO,
                "kategori":      kategori_final,
                "nama_produk":   nama,
                "harga":         harga,
                "stok":          stok,
                "thumbnail_url": item.get("thumbnail_url", ""),
            })

        print(f"✓ ({len(hasil)} total terkumpul)")
        url  = data.get("next")
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
    db.hapus_data_toko(NAMA_TOKO)

    semua: dict[tuple, dict] = {}  # key: (nama_produk, kategori) → deduplikasi

    for kategori, ids in KATEGORI_IDS.items():
        for cat_id in ids:
            for is_promo in [False, True]:
                produk = scrape_kategori(kategori, cat_id, is_promo)
                for p in produk:
                    semua[(p["nama_produk"], p["kategori"])] = p

    final = list(semua.values())

    if final:
        db.insert_harga_supermarket(final)

    print(f"\n{'='*55}")
    print(f"  Selesai! {len(final)} produk unik dari {NAMA_TOKO}.")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()