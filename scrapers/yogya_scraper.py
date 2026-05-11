# -*- coding: utf-8 -*-
"""
Scraper Yogya Online - fokus toko: YOGYA JUNCTION SUMBER SARI
"""

import os
import re
import sys
import time
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import DBManager  # noqa: E402

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


# -------------------- Config --------------------
NAMA_TOKO            = "Yogya"
BASE_SITE            = "https://supermarket.yogyaonline.co.id"
BASE_URL             = BASE_SITE + "/supermarket/{slug}/category"

TARGET_STORE_QUERY   = "sumber sari"
TARGET_STORE_KEYWORDS = ["JUNCTION", "SUMBER", "SARI"]
TARGET_STORE_VERIFY  = "SUMBER"

KATEGORI = [
    ("telur",         "fresh-telur"),
    ("daging_sapi",   "fresh-daging-dan-ayam-daging-sapi"),
    ("daging_ayam",   "fresh-daging-dan-ayam-ayam-bebek"),
    ("beras",         "makanan-bahan-masakan-beras"),
    ("sayur_sayuran", "fresh-buah-sayur-sayursayuran"),
    ("minyak_goreng", "makanan-bahan-masakan-cooking-oil"),
    ("gula",          "makanan-bahan-masakan-gula"),
]

KEYWORDS = {
    "telur":         ["telur ayam", "telur"],
    "daging_sapi":   ["sapi", "has dalam", "has luar", "sandung"],
    "daging_ayam":   ["ayam", "fillet", "paha", "dada", "sayap"],
    "beras":         ["beras"],
    "sayur_sayuran": ["bawang putih", "bawang merah", "cabe", "cabai"],
    "minyak_goreng": ["bimoli", "filma", "sania", "sunco", "tropical", "minyak goreng"],
    "gula":          ["gula"],
}

SCROLL_PAUSE              = 1.2
SCROLL_TIMEOUT            = 45   # maks scroll per kategori (detik)
MAX_PRODUK_PER_KATEGORI   = 40
PAGE_LOAD_TIMEOUT         = 30   # batas tunggu page load (detik)
PRODUK_WAIT_TIMEOUT       = 15   # batas tunggu elemen produk muncul (detik)

DEBUG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug_screenshots")

# CSS selector produk — digunakan di beberapa tempat
PRODUK_CSS = (
    ".col-sm-6.col-md-3.mb-3, "
    ".product-item, "
    "[class*='product-card'], "
    "[class*='item-product']"
)


# -------------------- Utils --------------------
def bersihkan_harga(teks: str) -> int:
    angka = re.sub(r"[^\d]", "", teks or "")
    return int(angka) if angka else 0

def cocok_keyword(nama_produk: str, kategori: str) -> bool:
    kws = KEYWORDS.get(kategori, [])
    if not kws:
        return True
    n = (nama_produk or "").lower()
    return any(k.lower() in n for k in kws)

def normalisasi_url_gambar(raw: str) -> str:
    if not raw:
        return ""
    return urljoin(BASE_SITE, raw.strip())


# -------------------- Driver --------------------
def build_driver(headless: bool = True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--lang=id-ID")
    opts.add_argument("--disable-notifications")
    opts.add_argument("--blink-settings=imagesEnabled=false")  # skip download gambar = lebih cepat

    # ⚡ KUNCI KECEPATAN: jangan tunggu semua resource, cukup DOM siap
    opts.page_load_strategy = "eager"

    opts.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.images": 2,  # blokir gambar di level Chrome
    })
    drv = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts,
    )
    drv.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    return drv


# -------------------- Debug --------------------
def simpan_screenshot(driver, nama: str):
    return
    os.makedirs(DEBUG_DIR, exist_ok=True)
    ts   = datetime.now().strftime("%H%M%S")
    path = os.path.join(DEBUG_DIR, f"{ts}_{nama}.png")
    try:
        driver.save_screenshot(path)
        print(f"  [DEBUG] Screenshot: {path}")
    except Exception as e:
        print(f"  [DEBUG] Gagal screenshot: {e}")

def dump_teks_halaman(driver, maks=20):
    try:
        lines = [l.strip() for l in
                 driver.find_element(By.TAG_NAME, "body").text.splitlines()
                 if l.strip()]
        print(f"  [DEBUG] Teks halaman ({len(lines)} baris):")
        for ln in lines[:maks]:
            print(f"    | {ln[:120]}")
    except Exception:
        pass


# -------------------- Popup --------------------
def dismiss_popup(driver, timeout: float = 2):
    xp = (
        "//button["
        "  contains(translate(.,'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'TUTUP')"
        "  or contains(.,'×') or contains(.,'✕')]"
    )
    for _ in range(3):
        try:
            btn = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xp))
            )
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.4)
        except Exception:
            break
    driver.execute_script(
        "document.querySelectorAll("
        "  '.modal-backdrop,.overlay,[class*=\"overlay\"],[class*=\"backdrop\"]'"
        ").forEach(e=>e.remove());"
    )


# ====================== PILIH TOKO (SEKALI SAJA) ======================
# Dipanggil HANYA SATU KALI di main() sebelum loop kategori.
# Setelah toko dipilih, sesi browser (cookie) menyimpan toko aktif
# sepanjang driver hidup — tidak perlu ulang per-kategori.
# =====================================================================

def safe_get(driver, url: str):
    """driver.get() tapi tidak crash kalau page load timeout (eager strategy)."""
    try:
        driver.get(url)
    except TimeoutException:
        # eager strategy kadang lempar TimeoutException meski DOM sudah siap
        pass

def klik_dropdown_toko(driver) -> bool:
    """Klik elemen dropdown toko (📍 YOGYA JUNCTION... ▼) di pojok kanan atas."""
    clicked = driver.execute_script("""
        var els = Array.from(document.querySelectorAll('*'));
        var W   = window.innerWidth;
        var best = null, bestLen = 9999;
        for (var el of els) {
            if (!el.offsetParent) continue;
            var txt = (el.innerText || '').trim();
            var UP  = txt.toUpperCase();
            if (!UP.includes('JUNCTION')) continue;
            if (txt.length > 80 || txt.length < 3) continue;
            var r = el.getBoundingClientRect();
            if (r.top > 150 || r.left < W * 0.4) continue;
            if (txt.length < bestLen) { best = el; bestLen = txt.length; }
        }
        if (best) { best.click(); return best.innerText.trim(); }
        return null;
    """)
    if clicked:
        print(f"  [OK] Klik dropdown: '{clicked}'")
        time.sleep(1.8)
        return True

    # XPath fallback
    for xp in [
        "//*[contains(normalize-space(.),'JUNCTION') and string-length(normalize-space(.))<60"
        "    and not(self::script) and not(self::style)]",
        "//*[contains(@class,'store') or contains(@class,'location')][contains(.,'JUNCTION')]",
    ]:
        try:
            for el in driver.find_elements(By.XPATH, xp):
                if el.is_displayed():
                    driver.execute_script("arguments[0].click();", el)
                    time.sleep(1.8)
                    print(f"  [OK] Klik dropdown (XPath): '{el.text[:60]}'")
                    return True
        except Exception:
            continue
    return False

def dropdown_terbuka(driver) -> bool:
    for by, sel in [
        (By.XPATH, "//input[@type='text' or @type='search']"),
        (By.XPATH, "//*[@role='dialog']"),
        (By.XPATH, "//*[contains(@class,'modal') and (contains(.,'Pilih') or contains(.,'Toko'))]"),
    ]:
        try:
            if any(e.is_displayed() for e in driver.find_elements(by, sel)):
                return True
        except Exception:
            pass
    return False

def toko_aktif(driver) -> str:
    try:
        r = driver.execute_script("""
            var W = window.innerWidth;
            for (var el of document.querySelectorAll('*')) {
                if (!el.offsetParent) continue;
                var txt = (el.innerText||'').trim().toUpperCase();
                if (!txt.includes('JUNCTION') || txt.length > 80) continue;
                var r = el.getBoundingClientRect();
                if (r.top < 150 && r.left > W * 0.4) return txt;
            }
            return '';
        """)
        return (r or "").upper()
    except Exception:
        return ""

def toko_sudah_benar(driver) -> bool:
    aktif = toko_aktif(driver)
    if aktif:
        print(f"  [INFO] Toko aktif: '{aktif}'")
    return bool(aktif) and TARGET_STORE_VERIFY in aktif

def pilih_toko_target(driver) -> bool:
    """
    Pilih toko target. Dipanggil SEKALI sebelum loop kategori.
    Return True jika berhasil (atau sudah terset).
    """
    safe_get(driver, BASE_SITE)
    time.sleep(2.5)
    dismiss_popup(driver)
    simpan_screenshot(driver, "01_halaman_awal")

    if toko_sudah_benar(driver):
        print("  [OK] Toko sudah sesuai, tidak perlu ganti.")
        return True

    if not klik_dropdown_toko(driver):
        simpan_screenshot(driver, "err_klik_dropdown")
        dump_teks_halaman(driver)
        return False

    simpan_screenshot(driver, "02_setelah_klik")

    for _ in range(12):
        if dropdown_terbuka(driver):
            break
        time.sleep(0.5)
    else:
        print("  [!] Panel pilih toko tidak terbuka.")
        simpan_screenshot(driver, "err_panel")
        dump_teks_halaman(driver)
        return False

    simpan_screenshot(driver, "03_panel_terbuka")

    # Isi input search
    inp = None
    for by, sel in [
        (By.XPATH, "//input[@type='search']"),
        (By.XPATH, "//input[contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
                   "'abcdefghijklmnopqrstuvwxyz'),'cari')]"),
        (By.CSS_SELECTOR, "[role='dialog'] input"),
        (By.CSS_SELECTOR, ".modal input"),
        (By.XPATH, "//input[@type='text']"),
    ]:
        try:
            for e in driver.find_elements(by, sel):
                if e.is_displayed() and e.is_enabled():
                    inp = e; break
            if inp:
                break
        except Exception:
            continue

    if inp:
        print(f"  [OK] Input search: placeholder='{inp.get_attribute('placeholder')}'")
        inp.click(); time.sleep(0.2)
        inp.send_keys(Keys.CONTROL + "a"); inp.send_keys(Keys.DELETE); inp.clear()
        inp.send_keys(TARGET_STORE_QUERY)
        time.sleep(3.0)
        simpan_screenshot(driver, "04_hasil_search")
    else:
        print("  [!] Input search tidak ditemukan, lanjut tanpa filter...")

    # Temukan baris toko
    baris = _cari_baris_toko(driver)
    if baris is None:
        print("  [!] Baris toko tidak ditemukan.")
        _debug_daftar_toko(driver)
        simpan_screenshot(driver, "err_toko_tidak_ada")
        return False

    return _klik_tombol_pilih(driver, baris)

def _cari_baris_toko(driver):
    time.sleep(1.0)
    kw_cond = " and ".join(
        f"contains(translate(.,'{k.lower()}','{k.upper()}'),'{k}')"
        for k in TARGET_STORE_KEYWORDS
    )
    for xp in [
        f"//*[self::li or self::div or self::tr][{kw_cond}]",
        f"//*[{kw_cond}][not(self::script)][not(self::style)]",
    ]:
        try:
            for el in WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((By.XPATH, xp))):
                txt = (el.text or "").upper()
                if all(k in txt for k in TARGET_STORE_KEYWORDS) and el.is_displayed():
                    print(f"  [OK] Baris toko: '{txt[:80]}'")
                    return el
        except Exception:
            continue

    idx = driver.execute_script("""
        var kws = arguments[0];
        var els = document.querySelectorAll('*');
        for (var i=0;i<els.length;i++){
            var txt=(els[i].innerText||'').toUpperCase();
            if(txt.length>300) continue;
            if(kws.every(k=>txt.includes(k)) && els[i].offsetParent) return i;
        }
        return -1;
    """, TARGET_STORE_KEYWORDS)
    if idx >= 0:
        try:
            el = driver.find_elements(By.XPATH, "//*")[idx]
            print(f"  [OK] Baris toko (JS): '{el.text[:80]}'")
            return el
        except Exception:
            pass
    return None

def _klik_tombol_pilih(driver, baris_el) -> bool:
    for xp in [
        ".//button[contains(translate(.,'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'PILIH')]",
        ".//button", ".//a", ".//span",
    ]:
        try:
            for btn in baris_el.find_elements(By.XPATH, xp):
                if not (btn.is_displayed() and btn.is_enabled()): continue
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                time.sleep(0.3)
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(2.5)
                dismiss_popup(driver)
                if toko_sudah_benar(driver):
                    simpan_screenshot(driver, "05_toko_dipilih")
                    print("  [OK] Toko berhasil dipilih!")
                    return True
        except Exception:
            continue
    # fallback: klik baris langsung
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", baris_el)
        time.sleep(0.2)
        driver.execute_script("arguments[0].click();", baris_el)
        time.sleep(2.5)
        dismiss_popup(driver)
        simpan_screenshot(driver, "05_klik_baris")
        print("  [OK] Klik baris langsung.")
        return True
    except Exception as e:
        print(f"  [!] Gagal klik baris: {e}")
        return False

def _debug_daftar_toko(driver, maks=20):
    print(f"  [DEBUG] Elemen berisi 'JUNCTION'/'SUMBER' (maks {maks}):")
    try:
        els = driver.find_elements(By.XPATH,
            "//*[not(self::script) and not(self::style)"
            "    and (contains(translate(.,'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'JUNCTION')"
            "     or  contains(translate(.,'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'SUMBER'))]")
        seen, count = set(), 0
        for el in els:
            txt = " ".join((el.text or "").split())
            if not txt or txt in seen or not el.is_displayed(): continue
            seen.add(txt)
            print(f"    <{el.tag_name} class='{(el.get_attribute('class') or '')[:40]}'> {txt[:100]}")
            count += 1
            if count >= maks: break
        if count == 0:
            print("    (kosong)")
            dump_teks_halaman(driver, 30)
    except Exception as e:
        print(f"  [DEBUG] Error: {e}")


# ====================== SCRAPE KATEGORI ======================

def parse_produk(html: str, kategori: str) -> list[dict]:
    soup  = BeautifulSoup(html, "html.parser")
    cards = (soup.select(".col-sm-6.col-md-3.mb-3")
             or soup.select(".product-item")
             or soup.select("[class*='product-card']")
             or soup.select("[class*='item-product']"))
    hasil = []
    for el in cards:
        try:
            nama_el  = (el.select_one(".three-line")
                        or el.select_one("[class*='product-name']")
                        or el.select_one("h5,h4,h3"))
            harga_el = (el.select_one(".product-price")
                        or el.select_one("[class*='price']")
                        or el.select_one("[class*='harga']"))
            if not nama_el or not harga_el: continue
            nama  = nama_el.get_text(strip=True)
            harga = bersihkan_harga(harga_el.get_text(strip=True))
            if harga <= 0 or not cocok_keyword(nama, kategori): continue
            img = ""
            img_el = el.select_one("img")
            if img_el:
                img = (img_el.get("data-src") or img_el.get("data-lazy-src")
                       or img_el.get("src") or "")
                img = normalisasi_url_gambar(img)
            hasil.append({
                "toko": NAMA_TOKO, "kategori": kategori,
                "nama_produk": nama, "harga": harga, "thumbnail_url": img,
            })
        except Exception:
            continue
    return hasil[:MAX_PRODUK_PER_KATEGORI]

def scroll_sampai_selesai(driver):
    """Scroll ke bawah sampai tidak ada konten baru atau timeout."""
    t0 = time.time()
    last_h = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE)
        new_h = driver.execute_script("return document.body.scrollHeight")
        if new_h == last_h:
            break
        last_h = new_h
        if time.time() - t0 > SCROLL_TIMEOUT:
            print("  [!] Scroll timeout, lanjut parsing...")
            break

def scrape_kategori(driver, nama_kategori: str, slug: str) -> list[dict]:
    url = BASE_URL.format(slug=slug)
    print(f"\n  [{NAMA_TOKO}] {nama_kategori.upper()} -> {url}")

    # Navigasi (eager strategy: tidak block di page load)
    safe_get(driver, url)
    dismiss_popup(driver)

    # Tunggu elemen produk muncul (lebih singkat, lanjut kalau muncul)
    try:
        WebDriverWait(driver, PRODUK_WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, PRODUK_CSS))
        )
    except TimeoutException:
        # Kalau tetap timeout, coba lanjut — mungkin selector beda
        print(f"  [!] Produk belum muncul dalam {PRODUK_WAIT_TIMEOUT}s, coba parse...")

    scroll_sampai_selesai(driver)
    hasil = parse_produk(driver.page_source, nama_kategori)
    print(f"  + ditemukan {len(hasil)} produk valid")
    return hasil


# -------------------- Main --------------------
def main():
    print("\n" + "=" * 60)
    print("  Yogya Scraper -- Mulai")
    print(f"  Waktu  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Target : {' '.join(TARGET_STORE_KEYWORDS)}")
    print(f"  Debug  : {DEBUG_DIR}")
    print("=" * 60)

    db = DBManager()
    db.init_schema()
    db.hapus_data_toko(NAMA_TOKO)

    driver = build_driver(headless=True)
    semua  = []

    try:
        # ── Pilih toko: HANYA SEKALI ──
        print("\n  Memilih toko...")
        ok = False
        for attempt in range(1, 4):
            if pilih_toko_target(driver):
                ok = True
                break
            print(f"  [!] Attempt {attempt}/3 gagal, coba lagi...")
            time.sleep(2.0)

        if not ok:
            print(f"\n  [X] Gagal set toko. Cek: {DEBUG_DIR}")
            return

        # ── Scrape tiap kategori ──
        for nama_kat, slug_kat in KATEGORI:
            hasil = scrape_kategori(driver, nama_kat, slug_kat)
            if not hasil:
                # Satu retry saja
                print(f"  [!] Retry {nama_kat}...")
                time.sleep(1.5)
                hasil = scrape_kategori(driver, nama_kat, slug_kat)

            if not hasil:
                print(f"  [!] Tidak ada hasil: {nama_kat}")
                continue

            db.insert_harga_supermarket(hasil)
            semua.extend(hasil)
            print(f"  + {len(hasil)} produk disimpan")
            time.sleep(0.5)

    finally:
        driver.quit()

    print("\n" + "=" * 60)
    print(f"  Selesai! Total {len(semua)} produk dari {NAMA_TOKO}.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()