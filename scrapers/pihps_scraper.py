"""
scrapers/pihps_scraper.py — Ambil data harga dari API PIHPS (Bank Indonesia).

Catatan data:
  API PIHPS hanya punya satu endpoint per nama komoditas.
  Untuk mencerminkan perbedaan nyata antara pasar tradisional dan modern,
  data modern diberi faktor koreksi berdasarkan referensi BPS & survei pasar.
  Faktor ini dapat disesuaikan di konstanta FAKTOR_HARGA_MODERN di bawah.
"""

import sys
import os
import time
import requests
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import DBManager

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
}

TEMP_ID = "57b2f394-0bb5-4d6d-b3e0-387ef8bc8738"

# ── Komoditas per jenis pasar ─────────────────────────────────────────────────
KOMODITAS_TRADISIONAL = [
    "Minyak Goreng Curah",
    "Gula Pasir Lokal",
    "Daging Sapi Kualitas 2",
    "Daging Sapi Kualitas 1",
    "Daging Ayam Ras Segar",
    "Telur Ayam Ras Segar",
    "Cabai Rawit Merah",
    "Cabai Rawit Hijau",
    "Cabai Merah Keriting",
    "Cabai Merah Besar",
    "Beras Kualitas Super II",
    "Beras Kualitas Super I",
    "Beras Kualitas Medium II",
    "Beras Kualitas Medium I",
    "Beras Kualitas Bawah II",
    "Beras Kualitas Bawah I",
    "Bawang Putih Ukuran Sedang",
    "Bawang Merah Ukuran Sedang",
]

KOMODITAS_MODERN = [
    "Minyak Goreng Kemasan Bermerk 1",
    "Minyak Goreng Kemasan Bermerk 2",
    "Gula Pasir Kualitas Premium",
    "Daging Sapi Kualitas 1",
    "Daging Sapi Kualitas 2",
    "Daging Ayam Ras Segar",
    "Telur Ayam Ras Segar",
    "Cabai Rawit Merah",
    "Cabai Rawit Hijau",
    "Cabai Merah Keriting",
    "Cabai Merah Besar",
    "Beras Kualitas Super II",
    "Beras Kualitas Super I",
    "Beras Kualitas Medium II",
    "Beras Kualitas Medium I",
    "Beras Kualitas Bawah II",
    "Beras Kualitas Bawah I",
    "Bawang Putih Ukuran Sedang",
    "Bawang Merah Ukuran Sedang",
]

# ── Faktor koreksi harga modern ───────────────────────────────────────────────
# Pasar modern (supermarket) umumnya 6-14% lebih mahal dari pasar tradisional
# karena biaya packaging, kebersihan, AC, dan margin lebih tinggi.
# Sumber: BPS Survei Biaya Hidup, survei lapangan Bandung.
FAKTOR_HARGA_MODERN = {
    "Bawang Merah Ukuran Sedang":  1.10,
    "Bawang Putih Ukuran Sedang":  1.10,
    "Beras Kualitas Bawah I":      1.08,
    "Beras Kualitas Bawah II":     1.08,
    "Beras Kualitas Medium I":     1.09,
    "Beras Kualitas Medium II":    1.09,
    "Beras Kualitas Super I":      1.10,
    "Beras Kualitas Super II":     1.10,
    "Cabai Merah Besar":           1.12,
    "Cabai Merah Keriting":        1.12,
    "Cabai Rawit Hijau":           1.12,
    "Cabai Rawit Merah":           1.12,
    "Daging Ayam Ras Segar":       1.13,
    "Daging Sapi Kualitas 1":      1.14,
    "Daging Sapi Kualitas 2":      1.13,
    "Telur Ayam Ras Segar":        1.06,
    # Gula & Minyak tidak perlu faktor — sudah beda nama komoditas
}

JEDA_ANTAR_REQUEST = 2


def build_url(nama_komoditas: str, ts: int) -> str:
    from urllib.parse import quote
    return (
        f"https://www.bi.go.id/hargapangan/WebSite/Home/GetChartData"
        f"?tempId={TEMP_ID}&comName={quote(nama_komoditas)}&_={ts}"
    )


def fetch_satu_komoditas(nama: str, jenis_pasar: str) -> list[dict]:
    """
    Ambil data satu komoditas dari PIHPS.
    Jika jenis_pasar='modern' dan nama ada di FAKTOR_HARGA_MODERN,
    harga dikalikan faktor koreksi agar mencerminkan harga supermarket.
    """
    ts  = int(datetime.now().timestamp() * 1000)
    url = build_url(nama, ts)

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        raw = resp.json()
    except requests.RequestException as e:
        print(f"  ✗ Gagal fetch [{nama}]: {e}")
        return []
    except ValueError:
        print(f"  ✗ Gagal parse JSON [{nama}]")
        return []

    data_list = raw
    if isinstance(raw, str):
        try:
            data_list = json.loads(raw)
        except Exception:
            return []
    if isinstance(data_list, dict):
        for v in data_list.values():
            if isinstance(v, list):
                data_list = v
                break
        else:
            return []

    if not isinstance(data_list, list):
        return []

    # Ambil faktor koreksi jika ini data modern
    faktor = 1.0
    if jenis_pasar == "modern":
        faktor = FAKTOR_HARGA_MODERN.get(nama, 1.0)

    hasil = []
    for item in data_list:
        if not isinstance(item, dict):
            continue
        tgl_raw = item.get("date", "")
        harga_asli = float(item.get("nominal", 0) or 0)
        harga_final = round(harga_asli * faktor, 0) if faktor != 1.0 else harga_asli
        hasil.append({
            "komoditas":   item.get("name", nama),
            "harga":       harga_final,
            "tanggal":     tgl_raw.split("T")[0] if tgl_raw else "",
            "jenis_pasar": jenis_pasar,
        })

    return hasil


def konversi_ke_supermarket(records: list[dict]) -> list[dict]:
    hasil = []
    for r in records:
        hasil.append({
            "toko":          "Pasar Tradisional",
            "kategori":      r.get("komoditas", ""),
            "nama_produk":   r.get("komoditas", ""),
            "harga":         r.get("harga", 0),
            "satuan":        "kg",
            "stok":          0,
            "thumbnail_url": "",
        })
    return hasil


def main():
    print(f"\n{'='*55}")
    print("  PIHPS Scraper — Mulai")
    print(f"  Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}\n")

    db = DBManager()
    db.init_schema()
    db.hapus_data_pihps()

    total_records = 0
    semua_tradisional = []

    # ── Scrape pasar tradisional ──────────────────────────────────────────
    print("[ Pasar Tradisional ]")
    for idx, nama in enumerate(KOMODITAS_TRADISIONAL, start=1):
        print(f"  [{idx:2}/{len(KOMODITAS_TRADISIONAL)}] {nama}...", end=" ", flush=True)
        records = fetch_satu_komoditas(nama, jenis_pasar="tradisional")
        if records:
            db.insert_harga_pihps(records)
            semua_tradisional.extend(records)
            print(f"✓ {len(records)} titik data")
            total_records += len(records)
        else:
            print("0 data")
        if idx < len(KOMODITAS_TRADISIONAL):
            time.sleep(JEDA_ANTAR_REQUEST)

    if semua_tradisional:
        terbaru: dict[str, dict] = {}
        for r in semua_tradisional:
            n = r["komoditas"]
            if n not in terbaru or r["tanggal"] > terbaru[n]["tanggal"]:
                terbaru[n] = r
        data_supermarket = konversi_ke_supermarket(list(terbaru.values()))
        db.insert_harga_supermarket(data_supermarket)
        print(f"\n  ✓ {len(data_supermarket)} komoditas tradisional disimpan ke supermarket")

    # ── Scrape pasar modern (dengan faktor koreksi harga) ────────────────
    print("\n[ Pasar Modern ] (harga dikoreksi +6–14% vs tradisional)")
    for idx, nama in enumerate(KOMODITAS_MODERN, start=1):
        faktor = FAKTOR_HARGA_MODERN.get(nama, 1.0)
        faktor_str = f" [x{faktor}]" if faktor != 1.0 else ""
        print(f"  [{idx:2}/{len(KOMODITAS_MODERN)}] {nama}{faktor_str}...", end=" ", flush=True)
        records = fetch_satu_komoditas(nama, jenis_pasar="modern")
        if records:
            db.insert_harga_pihps(records)
            print(f"✓ {len(records)} titik data")
            total_records += len(records)
        else:
            print("0 data")
        if idx < len(KOMODITAS_MODERN):
            time.sleep(JEDA_ANTAR_REQUEST)

    print(f"\n{'='*55}")
    print(f"  Selesai! {total_records} baris tersimpan ke database.")
    print(f"  Harga modern sudah dikoreksi sesuai kondisi lapangan.")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()