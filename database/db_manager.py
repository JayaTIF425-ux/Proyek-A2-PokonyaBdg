"""
database/db_manager.py — Manajer terpusat untuk seluruh operasi SQLite.
"""

import sqlite3
import os
from typing import Optional
from datetime import datetime


class DBManager:
    DEFAULT_DB = "hargapangan.db"

    def __init__(self, db_name: Optional[str] = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_file  = db_name or self.DEFAULT_DB
        self.db_path = os.path.join(base_dir, "data", db_file)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self):
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS harga_pangan (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    komoditas       TEXT    NOT NULL,
                    harga           REAL    NOT NULL DEFAULT 0,
                    tanggal         TEXT,
                    waktu_scraping  TEXT,
                    jenis_pasar     TEXT    DEFAULT 'tradisional'
                );
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
                CREATE TABLE IF NOT EXISTS komoditas (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama        TEXT    NOT NULL UNIQUE,
                    kategori    TEXT,
                    satuan      TEXT    DEFAULT 'kg',
                    deskripsi   TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_hp_komoditas ON harga_pangan(komoditas);
                CREATE INDEX IF NOT EXISTS idx_hs_nama ON harga_supermarket(nama_produk);
                CREATE INDEX IF NOT EXISTS idx_hs_toko ON harga_supermarket(toko);
                CREATE INDEX IF NOT EXISTS idx_hs_kategori ON harga_supermarket(kategori);
            """)

    # ── Query: Beranda ──────────────────────────────────────────────────

    def fetch_ringkasan_harga(self) -> list[sqlite3.Row]:
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

    # ── Query: Pencarian ────────────────────────────────────────────────

    def cari_produk(self, keyword: str) -> list[sqlite3.Row]:
        kw = f"%{keyword}%"
        sql_pihps = """
            SELECT komoditas AS nama, harga, 'PIHPS Nasional' AS toko,
                tanggal, '' AS thumbnail_url
            FROM harga_pangan
            WHERE komoditas LIKE ?
            AND (komoditas, tanggal) IN (
                SELECT komoditas, MAX(tanggal) FROM harga_pangan
                WHERE komoditas LIKE ?
                GROUP BY komoditas
            )
        """
        sql_toko = """
            SELECT nama_produk AS nama, harga, toko,
                tanggal_scraping AS tanggal, thumbnail_url
            FROM harga_supermarket
            WHERE nama_produk LIKE ?
            ORDER BY harga ASC
        """
        with self._connect() as conn:
            hasil_pihps = conn.execute(sql_pihps, (kw, kw)).fetchall()
            hasil_toko  = conn.execute(sql_toko,  (kw,)).fetchall()
        return hasil_pihps + hasil_toko

    # ── Query: Kalkulator ───────────────────────────────────────────────

    def fetch_produk_untuk_kalkulator(self) -> list[sqlite3.Row]:
        sql = """
            SELECT nama_produk, kategori, harga, toko, thumbnail_url
            FROM harga_supermarket
            ORDER BY kategori, nama_produk, harga
        """
        with self._connect() as conn:
            return conn.execute(sql).fetchall()

    def fetch_harga_per_toko(self, nama_produk: str) -> list[sqlite3.Row]:
        sql = """
            SELECT toko, harga, satuan
            FROM harga_supermarket
            WHERE nama_produk LIKE ?
            ORDER BY harga ASC
        """
        with self._connect() as conn:
            return conn.execute(sql, (f"%{nama_produk}%",)).fetchall()

    def perbandingan_harga(self, daftar_produk: list[str]) -> list[sqlite3.Row]:
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

    # ── Query: Tren Harga ───────────────────────────────────────────────

    def fetch_tren_harga(self, komoditas: str, hari: int = 999) -> list[sqlite3.Row]:
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

    # ── Insert: Dari Scraper ────────────────────────────────────────────

    def hapus_data_pihps(self):
        with self._connect() as conn:
            conn.execute("DELETE FROM harga_pangan")

    def hapus_data_toko(self, toko: str):
        with self._connect() as conn:
            conn.execute("DELETE FROM harga_supermarket WHERE toko = ?", (toko,))

    def insert_harga_pihps(self, records: list[dict]):
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rows = [
            (
                r["komoditas"],
                r["harga"],
                r.get("tanggal", ""),
                r.get("jenis_pasar", "tradisional"),
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
        rows = [
            (
                r["toko"], r.get("kategori", ""), r["nama_produk"],
                r["harga"], r.get("satuan", "kg"), r.get("stok", 0),
                r.get("thumbnail_url", ""), waktu
            )
            for r in records
        ]
        with self._connect() as conn:
            conn.executemany(
                "INSERT INTO harga_supermarket "
                "(toko, kategori, nama_produk, harga, satuan, stok, thumbnail_url, tanggal_scraping) "
                "VALUES (?,?,?,?,?,?,?,?)",
                rows
            )

    # ── CRUD Manual ─────────────────────────────────────────────────────

    def tambah_produk(self, nama: str, harga: float, toko: str,
                      tanggal: str, kategori: str = "", satuan: str = "kg") -> int:
        """INSERT satu baris ke harga_supermarket. Return id baris baru."""
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = """
            INSERT INTO harga_supermarket
                (toko, kategori, nama_produk, harga, satuan, stok, thumbnail_url, tanggal_scraping)
            VALUES (?, ?, ?, ?, ?, 0, '', ?)
        """
        with self._connect() as conn:
            cur = conn.execute(sql, (toko, kategori, nama, float(harga), satuan, tanggal or waktu[:10]))
            return cur.lastrowid

    def update_produk(self, id_produk: int, nama: str, harga: float,
                      toko: str, tanggal: str, kategori: str = "", satuan: str = "kg"):
        """UPDATE baris di harga_supermarket berdasarkan id."""
        sql = """
            UPDATE harga_supermarket
            SET nama_produk = ?, harga = ?, toko = ?, tanggal_scraping = ?,
                kategori = ?, satuan = ?
            WHERE id = ?
        """
        with self._connect() as conn:
            conn.execute(sql, (nama, float(harga), toko, tanggal, kategori, satuan, id_produk))

    def hapus_produk(self, id_produk: int):
        """DELETE satu baris dari harga_supermarket berdasarkan id."""
        with self._connect() as conn:
            conn.execute("DELETE FROM harga_supermarket WHERE id = ?", (id_produk,))

    def cari_produk_dengan_id(self, keyword: str) -> list[sqlite3.Row]:
        """Cari produk dan kembalikan id-nya (untuk keperluan Edit/Hapus)."""
        kw = f"%{keyword}%"
        sql_toko = """
            SELECT id, nama_produk AS nama, harga, toko,
                   tanggal_scraping AS tanggal, thumbnail_url,
                   'supermarket' AS sumber
            FROM harga_supermarket
            WHERE nama_produk LIKE ?
            ORDER BY harga ASC
        """
        sql_pihps = """
            SELECT id, komoditas AS nama, harga,
                   'PIHPS Nasional' AS toko,
                   tanggal, '' AS thumbnail_url,
                   'pihps' AS sumber
            FROM harga_pangan
            WHERE komoditas LIKE ?
              AND (komoditas, tanggal) IN (
                  SELECT komoditas, MAX(tanggal) FROM harga_pangan
                  WHERE komoditas LIKE ?
                  GROUP BY komoditas
              )
        """
        with self._connect() as conn:
            hasil_toko  = conn.execute(sql_toko, (kw,)).fetchall()
            hasil_pihps = conn.execute(sql_pihps, (kw, kw)).fetchall()
        return hasil_toko + hasil_pihps

    def fetch_semua_produk_supermarket(self, limit: int = 200) -> list[sqlite3.Row]:
        """Ambil semua produk supermarket."""
        sql = """
            SELECT id, nama_produk AS nama, harga, toko,
                   tanggal_scraping AS tanggal, thumbnail_url, kategori, satuan
            FROM harga_supermarket
            ORDER BY toko, nama_produk
            LIMIT ?
        """
        with self._connect() as conn:
            return conn.execute(sql, (limit,)).fetchall()

    def statistik_harga(self) -> dict:
        """Statistik ringkas untuk dashboard."""
        with self._connect() as conn:
            total    = conn.execute("SELECT COUNT(*) FROM harga_supermarket").fetchone()[0]
            avg      = conn.execute("SELECT ROUND(AVG(harga),0) FROM harga_supermarket").fetchone()[0]
            termahal = conn.execute(
                "SELECT nama_produk, harga, toko FROM harga_supermarket ORDER BY harga DESC LIMIT 1"
            ).fetchone()
            termurah = conn.execute(
                "SELECT nama_produk, harga, toko FROM harga_supermarket WHERE harga > 0 ORDER BY harga ASC LIMIT 1"
            ).fetchone()
            jml_toko = conn.execute("SELECT COUNT(DISTINCT toko) FROM harga_supermarket").fetchone()[0]
            return {
                "total": total,
                "avg": avg or 0,
                "termahal": dict(termahal) if termahal else {},
                "termurah": dict(termurah) if termurah else {},
                "jml_toko": jml_toko,
            }

    def ekspor_csv(self, path: str):
        """Ekspor seluruh data harga_supermarket ke file CSV."""
        import csv
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, toko, kategori, nama_produk, harga, satuan, tanggal_scraping "
                "FROM harga_supermarket ORDER BY toko, nama_produk"
            ).fetchall()
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Toko", "Kategori", "Nama Produk", "Harga", "Satuan", "Tanggal"])
            for r in rows:
                writer.writerow(list(r))

    # ── Utilitas ────────────────────────────────────────────────────────

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
        with self._connect() as conn:
            n_pihps = conn.execute("SELECT COUNT(*) FROM harga_pangan").fetchone()[0]
            n_toko  = conn.execute("SELECT COUNT(*) FROM harga_supermarket").fetchone()[0]
            return {"pihps": n_pihps, "supermarket": n_toko}