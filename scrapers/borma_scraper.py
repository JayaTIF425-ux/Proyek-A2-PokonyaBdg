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
    "legging", "regulator", "caffe", "italian", "enzim", "setrika", "rak", "kanzler", "roasted"
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
    MAX_RETRY = 3
    TIMEOUT   = 20

    label = "Promo" if is_promo else "Reguler"
    print(f"\n  [{NAMA_TOKO}] Ambil produk {label}...")

    while url:
        print(f"    Halaman {hal}...", end=" ", flush=True)

        # ── retry loop ──
        berhasil = False
        data     = None

        for percobaan in range(1, MAX_RETRY + 1):
            try:
                resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
                data = resp.json()
                berhasil = True
                break
            except requests.exceptions.Timeout:
                if percobaan < MAX_RETRY:
                    print(f"\n  ⚠ Timeout, retry ({percobaan}/{MAX_RETRY})...",
                          end=" ", flush=True)
                    time.sleep(3)
                else:
                    print(f"\n  ✗ Gagal setelah {MAX_RETRY}x, skip halaman ini")
            except Exception as e:
                print(f"\n  ✗ Error: {e}, skip halaman ini")
                break

        if not berhasil:
            hal += 1
            if "page=" in url:
                url = re.sub(r'page=\d+', f'page={hal}', url)
            else:
                sep = "&" if "?" in url else "?"
                url = f"{url}{sep}page={hal}"
            continue

        results = data.get("results", [])
        if not results:
            print("✓ Semua halaman selesai")
            break

        for item in results:
            nama     = item.get("title", "")
            kategori = deteksi_kategori(nama)
            if not kategori:
                continue

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
                    (item.get("inventory_generic") or {})
                    .get("quantity_available", 0) or 0
                )
            except (TypeError, ValueError):
                stok = 0

            hasil.append({
                "toko":          NAMA_TOKO,
                "kategori":      kategori,
                "nama_produk":   nama,
                "harga":         harga,
                "stok":          stok,
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
    db.hapus_data_toko(NAMA_TOKO)

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