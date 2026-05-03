"""
scripts/bersihkan_data.py — Bersihkan database dari data tidak valid.

Yang dibersihkan:
  1. Harga = 0
  2. Harga tidak wajar (> Rp 10.000.000)
  3. Data duplikat — simpan hanya data terbaru per produk per toko

Jalankan: python scripts/bersihkan_data.py
"""

import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "hargapangan.db"
)

BATAS_HARGA_WAJAR = 10_000_000


def bersihkan():
    if not os.path.exists(DB_PATH):
        print(f"✗ Database tidak ditemukan: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)

    print("\n" + "="*50)
    print("  Analisis Database")
    print("="*50)

    nol = conn.execute(
        "SELECT COUNT(*) FROM harga_supermarket WHERE harga = 0"
    ).fetchone()[0]

    ganjil = conn.execute(
        f"SELECT COUNT(*) FROM harga_supermarket WHERE harga > {BATAS_HARGA_WAJAR}"
    ).fetchone()[0]

    duplikat = conn.execute("""
        SELECT COUNT(*) FROM harga_supermarket
        WHERE id NOT IN (
            SELECT MAX(id) FROM harga_supermarket
            GROUP BY nama_produk, toko
        )
    """).fetchone()[0]

    total_masalah = nol + ganjil + duplikat

    print(f"  Harga Rp 0          : {nol} baris")
    print(f"  Harga > Rp 10 juta  : {ganjil} baris")
    print(f"  Duplikat produk     : {duplikat} baris")
    print(f"  Total akan dihapus  : {total_masalah} baris")

    if total_masalah == 0:
        print("\n✓ Database sudah bersih!")
        conn.close()
        return

    print()

    if ganjil > 0:
        contoh = conn.execute(
            f"SELECT nama_produk, harga, toko FROM harga_supermarket "
            f"WHERE harga > {BATAS_HARGA_WAJAR} LIMIT 5"
        ).fetchall()
        print("  Contoh harga tidak wajar:")
        for nama, harga, toko in contoh:
            print(f"    - {nama[:40]} | Rp {int(harga):,}".replace(",", ".") + f" | {toko}")
        print()

    konfirmasi = input("Lanjutkan pembersihan? (y/n): ").strip().lower()
    if konfirmasi != "y":
        print("Dibatalkan.")
        conn.close()
        return

    print("\nMembersihkan...")

    d1 = conn.execute("DELETE FROM harga_supermarket WHERE harga = 0").rowcount
    print(f"  ✓ Hapus {d1} baris harga Rp 0")

    d2 = conn.execute(
        f"DELETE FROM harga_supermarket WHERE harga > {BATAS_HARGA_WAJAR}"
    ).rowcount
    print(f"  ✓ Hapus {d2} baris harga tidak wajar")

    d3 = conn.execute("""
        DELETE FROM harga_supermarket
        WHERE id NOT IN (
            SELECT MAX(id) FROM harga_supermarket
            GROUP BY nama_produk, toko
        )
    """).rowcount
    print(f"  ✓ Hapus {d3} baris duplikat")

    conn.commit()

    sisa = conn.execute("SELECT COUNT(*) FROM harga_supermarket").fetchone()[0]
    conn.close()

    print(f"\n✓ Selesai! Sisa data valid: {sisa} baris")
    print("  Silakan klik Refresh di aplikasi.\n")


if __name__ == "__main__":
    bersihkan()