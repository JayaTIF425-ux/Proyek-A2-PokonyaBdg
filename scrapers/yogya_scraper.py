"""
scrapers/yogya_scraper.py — Scraper supermarket Yogya Online.
Strategi:
  - Kategori biasa        : requests + BeautifulSoup
  - Kategori infinite scroll: Selenium (sayur, dll.)

Output: insert ke harga_supermarket di hargapangan.db

Dependensi: pip install requests beautifulsoup4 selenium
"""

import sys
import os
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import DBManager

# ── Konfigurasi ────────────────────────────────────────────────────────────

NAMA_TOKO = "Yogya"
BASE_URL  = "https://supermarket.yogyaonline.co.id/supermarket/{slug}/category"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "id-ID,id;q=0.9",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "Referer": "https://supermarket.yogyaonline.co.id/",
}

# (nama_internal, slug_url, perlu_selenium)
KATEGORI = [
    ("telur",         "fresh-telur",                       False),
    ("daging_sapi",   "fresh-daging-dan-ayam-daging-sapi", False),
    ("daging_ayam",   "fresh-daging-dan-ayam-ayam-bebek",  False),
    ("beras",         "makanan-bahan-masakan-beras",        False),
    ("sayur_sayuran", "fresh-buah-sayur-sayursayuran",      True),
    ("minyak_goreng", "makanan-bahan-masakan-cooking-oil",  False),
    ("gula",          "makanan-bahan-masakan-gula",         False),
]

KEYWORDS: dict[str, list[str]] = {
    "telur":         ["telur ayam"],
    "daging_sapi":   ["sapi", "has dalam", "has luar", "sandung"],
    "daging_ayam":   ["ayam", "fillet", "paha", "dada", "sayap"],
    "beras":         ["beras"],
    "sayur_sayuran": ["bawang putih", "bawang merah", "cabe", "cabai"],
    "minyak_goreng": ["bimoli", "filma", "sania", "sunco", "tropical", "minyak goreng"],
    "gula":          ["gula"],
}

MAX_PRODUK   = 20
SCROLL_PAUSE = 2
SCROLL_TIMEOUT = 120


# ── Utilitas ───────────────────────────────────────────────────────────────

def bersihkan_harga(teks: str) -> int:
    angka = re.sub(r"[^\d]", "", teks)
    return int(angka) if angka else 0


def cocok_keyword(nama: str, kategori: str) -> bool:
    keywords = KEYWORDS.get(kategori)
    if not keywords:
        return True
    n = nama.lower()
    return any(kw.lower() in n for kw in keywords)


def proses_elemen(elemen, nama_kategori: str) -> list[dict]:
    hasil = []
    for el in elemen:
        try:
            nama_el  = el.select_one(".three-line")
            harga_el = el.select_one(".product-price")
            if not nama_el or not harga_el:
                continue
            nama  = nama_el.get_text(strip=True)
            harga = bersihkan_harga(harga_el.get_text(strip=True))
            if not cocok_keyword(nama, nama_kategori) or harga == 0:
                continue
            hasil.append({"toko": NAMA_TOKO, "kategori": nama_kategori, "nama_produk": nama, "harga": harga})
        except Exception as e:
            print(f"  [!] Parse error: {e}")
    return hasil


# ── Scraper A: requests ───────────────────────────────────────────────────

def scrape_requests(session: requests.Session, nama: str, slug: str) -> list[dict]:
    url = BASE_URL.format(slug=slug)
    print(f"\n  [{NAMA_TOKO}] {nama.upper()} (requests)  →  {url}")
    try:
        resp = session.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  ✗ Gagal: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    elemen = soup.select(".col-sm-6.col-md-3.mb-3") or soup.select(".product-item")
    print(f"  {len(elemen)} elemen ditemukan")
    return proses_elemen(elemen[:MAX_PRODUK], nama)


# ── Scraper B: Selenium ───────────────────────────────────────────────────

def scrape_selenium(nama: str, slug: str) -> list[dict]:
    """Gunakan Selenium untuk halaman infinite scroll."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError:
        print("  ✗ Selenium belum terinstall. Jalankan: pip install selenium")
        return []

    url = BASE_URL.format(slug=slug)
    print(f"\n  [{NAMA_TOKO}] {nama.upper()} (Selenium)  →  {url}")

    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_experimental_option(
        "prefs", {"profile.managed_default_content_settings.images": 2}
    )

    driver = webdriver.Chrome(options=opts)
    elemen = []
    try:
        driver.get(url)
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".col-sm-6.col-md-3.mb-3"))
            )
        except Exception:
            print("  [!] Timeout tunggu halaman. Skip.")
            return []

        # Scroll sampai habis
        last_h = driver.execute_script("return document.body.scrollHeight")
        t0 = time.time()
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE)
            new_h = driver.execute_script("return document.body.scrollHeight")
            if new_h == last_h or time.time() - t0 > SCROLL_TIMEOUT:
                break
            last_h = new_h

        soup   = BeautifulSoup(driver.page_source, "html.parser")
        elemen = soup.select(".col-sm-6.col-md-3.mb-3")
        print(f"  {len(elemen)} elemen ditemukan setelah scroll")
    finally:
        driver.quit()

    return proses_elemen(elemen, nama)


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*55}")
    print(f"  Yogya Scraper — Mulai")
    print(f"  Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}")

    db = DBManager()
    db.init_schema()
    db.hapus_data_toko(NAMA_TOKO)

    session = requests.Session()
    semua   = []

    for nama_kat, slug_kat, pakai_selenium in KATEGORI:
        hasil = scrape_selenium(nama_kat, slug_kat) if pakai_selenium \
                else scrape_requests(session, nama_kat, slug_kat)
        semua.extend(hasil)
        if hasil:
            db.insert_harga_supermarket(hasil)
            print(f"  ✓ {len(hasil)} produk disimpan")
        time.sleep(1)

    print(f"\n{'='*55}")
    print(f"  Selesai! Total {len(semua)} produk dari {NAMA_TOKO}.")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
