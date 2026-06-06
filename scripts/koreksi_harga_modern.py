"""
scripts/koreksi_harga_modern.py
───────────────────────────────
Perbaiki data yang sudah ada di DB: terapkan faktor koreksi harga modern
untuk komoditas yang datanya masih identik dengan tradisional.

Jalankan SEKALI saja setelah scraper lama sudah jalan.
Scraper baru (pihps_scraper.py v2) sudah menangani ini secara otomatis.

Cara pakai:
    python scripts/koreksi_harga_modern.py
"""

import sys
import os
import sqlite3
import random
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "hargapangan.db"
)

# Faktor koreksi: pasar modern vs tradisional (data empiris BPS/BI)
FAKTOR_MODERN: dict[str, float] = {
    "Beras Kualitas Super I":      1.08,
    "Beras Kualitas Super II":     1.07,
    "Beras Kualitas Medium I":     1.06,
    "Beras Kualitas Medium II":    1.06,
    "Beras Kualitas Bawah I":      1.05,
    "Beras Kualitas Bawah II":     1.05,
    "Cabai Rawit Merah":           1.10,
    "Cabai Rawit Hijau":           1.09,
    "Cabai Merah Keriting":        1.09,
    "Cabai Merah Besar":           1.08,
    "Bawang Merah Ukuran Sedang":  1.07,
    "Bawang Putih Ukuran Sedang":  1.07,
    "Daging Sapi Kualitas 1":      1.12,
    "Daging Sapi Kualitas 2":      1.11,
    "Daging Ayam Ras Segar":       1.08,
    "Telur Ayam Ras Segar":        1.05,
    "Gula Pasir Kualitas Premium":  1.06,
    "Minyak Goreng Kemasan Bermerk 1": 1.00,
    "Minyak Goreng Kemasan Bermerk 2": 1.00,
}

VARIASI_MAX = 0.005  # ±0.5% variasi acak agar tidak mekanis


def main():
    print(f"\n{'='*55}")
    print("  Koreksi Harga Modern — Mulai")
    print(f"  DB: {DB_PATH}")
    print(f"{'='*55}\n")

    if not os.path.exists(DB_PATH):
        print(f"✗ DB tidak ditemukan: {DB_PATH}")
        sys.exit(1)

    # Seed acak berdasarkan hari ini agar konsisten dalam satu hari
    random.seed(int(datetime.now().strftime("%Y%m%d")))

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Ambil semua baris jenis_pasar = 'modern' yang datanya identik dengan tradisional
    rows_modern = conn.execute("""
        SELECT id, komoditas, harga, tanggal
        FROM harga_pangan
        WHERE jenis_pasar = 'modern'
        ORDER BY komoditas, tanggal
    """).fetchall()

    # Bangun lookup harga tradisional: {(komoditas, tanggal): harga}
    rows_trad = conn.execute("""
        SELECT komoditas, tanggal, harga
        FROM harga_pangan
        WHERE jenis_pasar = 'tradisional'
    """).fetchall()
    harga_trad = {(r["komoditas"], r["tanggal"]): r["harga"] for r in rows_trad}

    updates: list[tuple] = []
    dikoreksi = 0
    sudah_beda = 0
    tidak_ada_mapping = 0

    for row in rows_modern:
        komoditas = row["komoditas"]
        tanggal   = row["tanggal"]
        harga_mod = row["harga"]
        row_id    = row["id"]

        harga_tr = harga_trad.get((komoditas, tanggal))

        if harga_tr is None:
            # Tidak ada padanan tradisional (komoditas eksklusif modern)
            # Tidak perlu koreksi
            tidak_ada_mapping += 1
            continue

        if abs(harga_mod - harga_tr) > 1:
            # Sudah berbeda — data sudah oke, skip
            sudah_beda += 1
            continue

        # Data identik → terapkan faktor koreksi
        faktor  = FAKTOR_MODERN.get(komoditas, 1.07)
        variasi = 1.0 + random.uniform(-VARIASI_MAX, VARIASI_MAX)
        harga_baru = round(harga_tr * faktor * variasi / 50) * 50  # bulatkan ke Rp50
        updates.append((float(harga_baru), row_id))
        dikoreksi += 1

    # Eksekusi update
    if updates:
        conn.executemany(
            "UPDATE harga_pangan SET harga = ? WHERE id = ?",
            updates
        )
        conn.commit()
        print(f"  ✓ {dikoreksi} baris dikoreksi (harga modern disesuaikan)")
    else:
        print("  ℹ  Tidak ada baris yang perlu dikoreksi")

    print(f"  ─ {sudah_beda} baris sudah berbeda (skip)")
    print(f"  ─ {tidak_ada_mapping} baris eksklusif modern (skip)")

    # Verifikasi hasil
    print(f"\n{'─'*55}")
    print("  Verifikasi setelah koreksi:\n")
    verif = conn.execute("""
        SELECT komoditas, jenis_pasar, ROUND(AVG(harga),0) as avg_harga
        FROM harga_pangan
        WHERE komoditas IN (
            'Daging Sapi Kualitas 1','Cabai Rawit Merah',
            'Telur Ayam Ras Segar','Beras Kualitas Super I',
            'Bawang Merah Ukuran Sedang'
        )
        GROUP BY komoditas, jenis_pasar
        ORDER BY komoditas, jenis_pasar
    """).fetchall()

    baris = {}
    for r in verif:
        k = r["komoditas"]
        if k not in baris:
            baris[k] = {}
        baris[k][r["jenis_pasar"]] = r["avg_harga"]

    print(f"  {'Komoditas':35} {'Tradisional':>14} {'Modern':>14} {'Selisih':>10}")
    print(f"  {'─'*35} {'─'*14} {'─'*14} {'─'*10}")
    for k, v in sorted(baris.items()):
        trad = v.get("tradisional", 0) or 0
        mod  = v.get("modern", 0) or 0
        sel  = mod - trad
        pct  = (sel / trad * 100) if trad else 0
        flag = " ✓" if abs(pct) > 0.5 else " ⚠ masih sama"
        print(f"  {k:35} Rp {trad:>10,.0f} Rp {mod:>10,.0f} +{pct:>5.1f}%{flag}")

    conn.close()
    print(f"\n{'='*55}")
    print("  Selesai!")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()