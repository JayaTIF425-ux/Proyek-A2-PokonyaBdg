"""
database/db_manager.py — Manajer terpusat untuk seluruh operasi SQLite.

Skema Database:
  harga_pangan    : data dari API PIHPS (Bank Indonesia) — harga acuan nasional
  harga_supermarket : data hasil scraping toko (Yogya, Borma, dll.)
  ringkasan_harga : view agregasi untuk perbandingan cepat
"""

import sqlite3
import os
from typing import Optional
from datetime import datetime


class DBManager:
    """
    Singleton-style manager: buat satu instance, pakai di mana saja.
    Semua query dikumpulkan di sini agar tidak ada SQL tersebar di UI.
    """

    DEFAULT_DB = "hargapangan.db"

    def __init__(self, db_name: Optional[str] = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_file  = db_name or self.DEFAULT_DB
        self.db_path = os.path.join(base_dir, "data", db_file)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    # ── Koneksi ──────────────────────────────────────────────────────────

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # akses kolom by name
        return conn

    # ── Inisialisasi Skema ────────────────────────────────────────────────

    def init_schema(self):
        """Buat semua tabel jika belum ada. Aman dipanggil berkali-kali."""
        with self._connect() as conn:
            conn.executescript("""
                -- Harga acuan dari PIHPS (Bank Indonesia)
                CREATE TABLE IF NOT EXISTS harga_pangan (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    komoditas       TEXT    NOT NULL,
                    harga           REAL    NOT NULL DEFAULT 0,
                    tanggal         TEXT,
                    waktu_scraping  TEXT,
                    jenis_pasar     TEXT    DEFAULT 'tradisional'
                );

                -- Harga dari hasil scraping supermarket
                CREATE TABLE IF NOT EXISTS harga_supermarket (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    toko            TEXT    NOT NULL,
                    kategori        TEXT,
                    nama_produk     TEXT    NOT NULL,
                    harga           REAL    NOT NULL DEFAULT 0,
                    satuan          TEXT    DEFAULT 'kg',
                    stok            INTEGER DEFAULT 0,
                    thumbnail_url   TEXT,
                    tanggal_scraping TEXT
                );

                -- Komoditas master (untuk mapping nama antar sumber)
                CREATE TABLE IF NOT EXISTS komoditas (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama        TEXT    NOT NULL UNIQUE,
                    kategori    TEXT,
                    satuan      TEXT    DEFAULT 'kg',
                    deskripsi   TEXT
                );

                -- Indeks untuk mempercepat pencarian
                CREATE INDEX IF NOT EXISTS idx_hp_komoditas
                    ON harga_pangan(komoditas);
                CREATE INDEX IF NOT EXISTS idx_hs_nama
                    ON harga_supermarket(nama_produk);
                CREATE INDEX IF NOT EXISTS idx_hs_toko
                    ON harga_supermarket(toko);
                CREATE INDEX IF NOT EXISTS idx_hs_kategori
                    ON harga_supermarket(kategori);
            """)

    # ── Query: Beranda ────────────────────────────────────────────────────

    def fetch_ringkasan_harga(self) -> list[sqlite3.Row]:
        """
        Ambil harga rata-rata terbaru per komoditas dari semua sumber.
        Return: [(komoditas, harga_acuan, harga_min_toko, harga_max_toko, tanggal)]
        """
        sql = """
            SELECT
                hp.komoditas,
                ROUND(AVG(hp.harga), 0)  AS harga_acuan,
                (SELECT MIN(hs.harga) FROM harga_supermarket hs
                 WHERE LOWER(hs.nama_produk) LIKE '%' || LOWER(hp.komoditas) || '%')
                    AS harga_min_toko,
                (SELECT MAX(hs.harga) FROM harga_supermarket hs
                 WHERE LOWER(hs.nama_produk) LIKE '%' || LOWER(hp.komoditas) || '%')
                    AS harga_max_toko,
                MAX(hp.tanggal) AS tanggal_update
            FROM harga_pangan hp
            GROUP BY hp.komoditas
            ORDER BY hp.komoditas
        """
        with self._connect() as conn:
            return conn.execute(sql).fetchall()

    def fetch_semua_produk_pihps(self) -> list[sqlite3.Row]:
        """Ambil semua data PIHPS terbaru per komoditas."""
        sql = """
            SELECT komoditas, harga, 'PIHPS Bandung' AS toko, tanggal
            FROM harga_pangan
            WHERE (komoditas, tanggal) IN (
                SELECT komoditas, MAX(tanggal) FROM harga_pangan GROUP BY komoditas
            )
            ORDER BY komoditas
        """
        with self._connect() as conn:
            return conn.execute(sql).fetchall()
        
    def fetch_produk_pihps_by_pasar(self, jenis_pasar: str) -> list[sqlite3.Row]:
        """
        Ambil data PIHPS terbaru per komoditas berdasarkan jenis pasar.
        jenis_pasar: 'tradisional', 'modern', atau 'semua'
        """
        if jenis_pasar == "semua":
            sql = """
                SELECT komoditas, harga, jenis_pasar,
                       'PIHPS Bandung' AS toko, tanggal
                FROM harga_pangan
                WHERE (komoditas, tanggal) IN (
                    SELECT komoditas, MAX(tanggal)
                    FROM harga_pangan
                    GROUP BY komoditas
                )
                ORDER BY komoditas
            """
            with self._connect() as conn:
                return conn.execute(sql).fetchall()
        else:
            sql = """
                SELECT komoditas, harga, jenis_pasar,
                    'PIHPS Bandung' AS toko, tanggal
                FROM harga_pangan
                WHERE jenis_pasar = ?
                AND (komoditas, tanggal) IN (
                    SELECT komoditas, MAX(tanggal)
                    FROM harga_pangan
                    WHERE jenis_pasar = ?
                    GROUP BY komoditas
                )
                ORDER BY komoditas
            """
            with self._connect() as conn:
                return conn.execute(sql, (jenis_pasar, jenis_pasar)).fetchall()

    # ── Query: Pencarian ──────────────────────────────────────────────────

    def cari_produk(self, keyword: str) -> list[sqlite3.Row]:
        """
        Cari produk di seluruh sumber (PIHPS + supermarket).
        Return unified: (nama, harga, toko, tanggal)
        """
        kw = f"%{keyword}%"

        # Data dari PIHPS
        sql_pihps = """
            SELECT komoditas AS nama, harga, 'PIHPS Nasional' AS toko, tanggal
            FROM harga_pangan
            WHERE komoditas LIKE ?
            AND (komoditas, tanggal) IN (
                SELECT komoditas, MAX(tanggal) FROM harga_pangan
                WHERE komoditas LIKE ?
                GROUP BY komoditas
            )
        """

        # Data dari supermarket
        sql_toko = """
            SELECT nama_produk AS nama, harga, toko, tanggal_scraping AS tanggal
            FROM harga_supermarket
            WHERE nama_produk LIKE ?
            ORDER BY harga ASC
        """

        with self._connect() as conn:
            hasil_pihps = conn.execute(sql_pihps, (kw, kw)).fetchall()
            hasil_toko  = conn.execute(sql_toko,  (kw,)).fetchall()

        return hasil_pihps + hasil_toko

    # ── Query: Penghitung / Kalkulator ───────────────────────────────────

    def fetch_produk_untuk_kalkulator(self) -> list[sqlite3.Row]:
        """
        Ambil daftar produk beserta harga per toko.
        Digunakan di halaman Penghitung Belanja.
        Return: [(nama_produk, kategori, harga, toko)]
        """
        sql = """
            SELECT nama_produk, kategori, harga, toko, thumbnail_url
            FROM harga_supermarket
            ORDER BY kategori, nama_produk, harga
        """
        with self._connect() as conn:
            return conn.execute(sql).fetchall()

    def fetch_harga_per_toko(self, nama_produk: str) -> list[sqlite3.Row]:
        """
        Ambil semua harga untuk satu produk dari berbagai toko.
        Return: [(toko, harga, satuan)]
        """
        sql = """
            SELECT toko, harga, satuan
            FROM harga_supermarket
            WHERE nama_produk LIKE ?
            ORDER BY harga ASC
        """
        with self._connect() as conn:
            return conn.execute(sql, (f"%{nama_produk}%",)).fetchall()

    def perbandingan_harga(self, daftar_produk: list[str]) -> list[sqlite3.Row]:
        """
        Hitung estimasi total belanja per toko untuk daftar produk.
        Input: ['Beras', 'Telur Ayam', ...]
        Return: [(toko, total_estimasi, jumlah_item_tersedia)]
        """
        if not daftar_produk:
            return []

        placeholders = ",".join("?" * len(daftar_produk))
        sql = f"""
            SELECT
                toko,
                SUM(harga)          AS total_estimasi,
                COUNT(DISTINCT nama_produk) AS jumlah_item
            FROM harga_supermarket
            WHERE nama_produk IN ({placeholders})
            GROUP BY toko
            ORDER BY total_estimasi ASC
        """
        with self._connect() as conn:
            return conn.execute(sql, daftar_produk).fetchall()

    # ── Query: Tren Harga ─────────────────────────────────────────────────

    def fetch_tren_harga(self, komoditas: str, hari: int = 30) -> list[sqlite3.Row]:
        """
        Ambil data harga historis untuk grafik tren.
        Return: [(tanggal, harga)]
        """
        sql = """
            SELECT tanggal, ROUND(AVG(harga), 0) AS harga
            FROM harga_pangan
            WHERE komoditas LIKE ?
              AND tanggal >= date('now', ? || ' days')
            GROUP BY tanggal
            ORDER BY tanggal ASC
        """
        with self._connect() as conn:
            return conn.execute(sql, (f"%{komoditas}%", f"-{hari}")).fetchall()

    # ── Insert: Dari Scraper ──────────────────────────────────────────────

    def hapus_data_pihps(self):
        with self._connect() as conn:
            conn.execute("DELETE FROM harga_pangan")
    
    def hapus_data_toko(self, toko: str):
        with self._connect() as conn:
            conn.execute("DELETE FROM harga_supermarket WHERE toko = ?", (toko,))

    def insert_harga_pihps(self, records: list[dict]):
        """
        Insert batch data PIHPS.
        Tiap record: {komoditas, harga, tanggal, jenis_pasar}
        """
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rows = [
            (
                r["komoditas"],
                r["harga"],
                r.get("tanggal", ""),
                r.get("jenis_pasar", "tradisional"),  # ← TAMBAH INI
                waktu
            )
            for r in records
        ]
        with self._connect() as conn:
            conn.executemany(
                "INSERT INTO harga_pangan "
                "(komoditas, harga, tanggal, jenis_pasar, waktu_scraping) "
                "VALUES (?,?,?,?,?)",
                rows
            )

    def insert_harga_supermarket(self, records: list[dict]):
        if not records:
            return
    
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        toko = records[0]["toko"]  # ambil nama toko dari data pertama
    
        rows = [
            (
                r["toko"], r.get("kategori", ""), r["nama_produk"],
                r["harga"], r.get("satuan", "kg"), r.get("stok", 0),
                r.get("thumbnail_url", ""), waktu
            )
            for r in records
        ]
        with self._connect() as conn:
            # Hapus data lama dari toko ini dulu sebelum insert baru
            # conn.execute("DELETE FROM harga_supermarket WHERE toko = ?", (toko,))
            conn.executemany(
                "INSERT INTO harga_supermarket "
                "(toko, kategori, nama_produk, harga, satuan, stok, thumbnail_url, tanggal_scraping) "
                "VALUES (?,?,?,?,?,?,?,?)",
                rows
            )

    # ── Utilitas ──────────────────────────────────────────────────────────

    def daftar_toko(self) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT DISTINCT toko FROM harga_supermarket ORDER BY toko"
            ).fetchall()
            return [r["toko"] for r in rows]

    def daftar_komoditas(self) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT DISTINCT komoditas FROM harga_pangan ORDER BY komoditas"
            ).fetchall()
            return [r["komoditas"] for r in rows]

    def jumlah_data(self) -> dict:
        """Statistik ringkas jumlah data di DB."""
        with self._connect() as conn:
            n_pihps = conn.execute("SELECT COUNT(*) FROM harga_pangan").fetchone()[0]
            n_toko  = conn.execute("SELECT COUNT(*) FROM harga_supermarket").fetchone()[0]
            return {"pihps": n_pihps, "supermarket": n_toko}
