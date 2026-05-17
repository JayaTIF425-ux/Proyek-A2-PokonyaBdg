"""
database/auth_manager.py — Manajer autentikasi: login, register, role user/admin.
"""

import sqlite3
import hashlib
import os
from typing import Optional


class AuthManager:
    """Mengelola tabel users dan sesi login."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "data", "hargapangan.db")
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password menggunakan SHA-256."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    # ── Inisialisasi Skema ───────────────────────────────────────────────────

    def init_schema(self):
        """Buat tabel users jika belum ada, dan tambah akun default."""
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    username    TEXT    NOT NULL UNIQUE,
                    password    TEXT    NOT NULL,
                    role        TEXT    NOT NULL DEFAULT 'user',
                    dibuat_pada TEXT    DEFAULT (datetime('now'))
                );
            """)
        # Buat akun default jika tabel masih kosong
        self._seed_default_accounts()

    def _seed_default_accounts(self):
        """Tambahkan akun admin dan user default jika belum ada."""
        akun_default = [
            ("admin", "admin123", "admin"),
            ("user",  "user123",  "user"),
        ]
        with self._connect() as conn:
            for username, password, role in akun_default:
                existing = conn.execute(
                    "SELECT id FROM users WHERE username = ?", (username,)
                ).fetchone()
                if not existing:
                    conn.execute(
                        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                        (username, self._hash_password(password), role)
                    )

    # ── Login ────────────────────────────────────────────────────────────────

    def login(self, username: str, password: str) -> Optional[dict]:
        """
        Coba login. Return dict user jika berhasil, None jika gagal.
        Contoh return: {"id": 1, "username": "admin", "role": "admin"}
        """
        hashed = self._hash_password(password)
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, username, role FROM users WHERE username = ? AND password = ?",
                (username, hashed)
            ).fetchone()
        if row:
            return {"id": row["id"], "username": row["username"], "role": row["role"]}
        return None

    # ── Manajemen User (untuk admin) ─────────────────────────────────────────

    def daftar_users(self) -> list:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, username, role, dibuat_pada FROM users ORDER BY id"
            ).fetchall()
            return [dict(r) for r in rows]

    def tambah_user(self, username: str, password: str, role: str = "user") -> bool:
        """Tambah user baru. Return True jika berhasil, False jika username sudah ada."""
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    (username, self._hash_password(password), role)
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def hapus_user(self, user_id: int) -> bool:
        """Hapus user berdasarkan id. Tidak boleh menghapus diri sendiri."""
        with self._connect() as conn:
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return True

    def ubah_role(self, user_id: int, role_baru: str) -> bool:
        """Ubah role user berdasarkan id. Role valid: 'user' atau 'admin'."""
        if role_baru not in ("user", "admin"):
            return False
        with self._connect() as conn:
            conn.execute(
                "UPDATE users SET role = ? WHERE id = ?",
                (role_baru, user_id)
            )
        return True

    def ubah_password(self, user_id: int, password_baru: str):
        with self._connect() as conn:
            conn.execute(
                "UPDATE users SET password = ? WHERE id = ?",
                (self._hash_password(password_baru), user_id)
            )