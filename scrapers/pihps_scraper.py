"""
scrapers/pihps_scraper.py — Ambil data harga dari API PIHPS (Bank Indonesia).
Output: langsung insert ke hargapangan.db (tabel harga_pangan)

Jalankan: python scrapers/pihps_scraper.py
"""

import sys
import os
import time
import requests
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import DBManager


# ── Konfigurasi ────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
}

# tempId untuk Kota Bandung — ubah jika PIHPS menggantinya
TEMP_ID = "57b2f394-0bb5-4d6d-b3e0-387ef8bc8738"

DAFTAR_KOMODITAS = [
    "Minyak Goreng Kemasan Bermerk 2",
    "Minyak Goreng Kemasan Bermerk 1",
    "Minyak Goreng Curah",
    "Gula Pasir Lokal",
    "Gula Pasir Kualitas Premium",
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

JEDA_ANTAR_REQUEST = 2   # detik, hindari rate limit


# ── Fungsi Inti ────────────────────────────────────────────────────────────

def build_url(nama_komoditas: str, ts: int) -> str:
    from urllib.parse import quote
    return (
        f"https://www.bi.go.id/hargapangan/WebSite/Home/GetChartData"
        f"?tempId={TEMP_ID}&comName={quote(nama_komoditas)}&_={ts}"
    )


def fetch_satu_komoditas(nama: str) -> list[dict]:
    """Ambil data satu komoditas dari PIHPS. Return list of {komoditas, harga, tanggal}."""
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

    # Normalkan struktur respons
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

    hasil = []
    for item in data_list:
        if not isinstance(item, dict):
            continue
        tgl_raw = item.get("date", "")
        hasil.append({
            "komoditas": item.get("name", nama),
            "harga":     float(item.get("nominal", 0) or 0),
            "tanggal":   tgl_raw.split("T")[0] if tgl_raw else "",
        })

    return hasil


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*55}")
    print("  PIHPS Scraper — Mulai")
    print(f"  Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}\n")

    db = DBManager()
    db.init_schema()

    total_records = 0
    for idx, nama in enumerate(DAFTAR_KOMODITAS, start=1):
        print(f"[{idx:2}/{len(DAFTAR_KOMODITAS)}] {nama}...", end=" ", flush=True)
        records = fetch_satu_komoditas(nama)

        if records:
            db.insert_harga_pihps(records)
            print(f"✓ {len(records)} titik data")
            total_records += len(records)
        else:
            print("0 data")

        if idx < len(DAFTAR_KOMODITAS):
            time.sleep(JEDA_ANTAR_REQUEST)

    print(f"\n{'='*55}")
    print(f"  Selesai! {total_records} baris tersimpan ke database.")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
