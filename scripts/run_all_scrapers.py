"""
scripts/run_all_scrapers.py — Jalankan semua scraper secara berurutan.

Penggunaan:
  python scripts/run_all_scrapers.py
  python scripts/run_all_scrapers.py --hanya pihps
  python scripts/run_all_scrapers.py --hanya yogya borma
"""

import sys
import os
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def jalankan_pihps():
    print("\n" + "━"*55)
    print("  ▶  PIHPS Scraper")
    print("━"*55)
    from scrapers.pihps_scraper import main
    main()


def jalankan_yogya():
    print("\n" + "━"*55)
    print("  ▶  Yogya Scraper")
    print("━"*55)
    from scrapers.yogya_scraper import main
    main()


def jalankan_borma():
    print("\n" + "━"*55)
    print("  ▶  Borma Scraper")
    print("━"*55)
    from scrapers.borma_scraper import main
    main()


SCRAPERS = {
    "pihps": jalankan_pihps,
    "yogya": jalankan_yogya,
    "borma": jalankan_borma,
}


def main():
    parser = argparse.ArgumentParser(description="Jalankan scraper PokokNya.Bdg")
    parser.add_argument(
        "--hanya", nargs="+", choices=list(SCRAPERS.keys()),
        help="Pilih scraper tertentu (default: semua)"
    )
    args = parser.parse_args()

    target = args.hanya or list(SCRAPERS.keys())

    print(f"\n{'═'*55}")
    print("  PokokNya.Bdg — Mulai Scraping")
    print(f"  Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Target: {', '.join(target)}")
    print(f"{'═'*55}")

    sukses = []
    gagal  = []
    for nama in target:
        try:
            SCRAPERS[nama]()
            sukses.append(nama)
        except Exception as e:
            print(f"\n  ✗ {nama} gagal: {e}")
            gagal.append(nama)

    print(f"\n{'═'*55}")
    print(f"  Selesai! Sukses: {sukses}  |  Gagal: {gagal}")
    print(f"{'═'*55}\n")

    # Sukses kalau minimal 1 scraper berhasil
    sys.exit(0 if sukses else 1)

if __name__ == "__main__":
    main()
