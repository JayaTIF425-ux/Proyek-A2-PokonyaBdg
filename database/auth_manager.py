"""
database/auth_manager.py — Autentikasi: login, register, Google OAuth, role user/admin.
"""

import sqlite3
import hashlib
import os
import secrets
from typing import Optional


class AuthManager:

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
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    # ── Inisialisasi Skema ───────────────────────────────────────────────────

    def init_schema(self):
        """Buat tabel users jika belum ada, dan tambah akun default."""
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    username     TEXT    NOT NULL UNIQUE,
                    password     TEXT,
                    role         TEXT    NOT NULL DEFAULT 'user',
                    display_name TEXT,
                    google_id    TEXT    UNIQUE,
                    email        TEXT,
                    dibuat_pada  TEXT    DEFAULT (datetime('now'))
                );
            """)
            # Migrasi: tambah kolom baru jika belum ada (untuk db lama)
            for kolom, tipe in [
                ("display_name", "TEXT"),
                ("google_id",    "TEXT"),
                ("email",        "TEXT"),
            ]:
                try:
                    conn.execute(f"ALTER TABLE users ADD COLUMN {kolom} {tipe}")
                except Exception:
                    pass  # Kolom sudah ada, lewati
        self._seed_default_accounts()

    # ── Login ────────────────────────────────────────────────────────────────

    def login(self, username: str, password: str) -> Optional[dict]:
        """Login dengan username. Kembalikan dict user termasuk display_name."""
        hashed = self._hash_password(password)
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, username, role, display_name, email FROM users "
                "WHERE username = ? AND password = ?",
                (username, hashed)
            ).fetchone()
        if row:
            data = dict(row)
            # Pastikan display_name selalu terisi (fallback ke username)
            if not data.get("display_name"):
                data["display_name"] = data["username"]
            return data
        return None

    def login_by_email(self, email: str, password: str) -> Optional[dict]:
        """Login dengan email langsung. Kembalikan dict user termasuk display_name."""
        hashed = self._hash_password(password)
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, username, role, display_name, email FROM users "
                "WHERE email = ? AND password = ?",
                (email, hashed)
            ).fetchone()
        if row:
            data = dict(row)
            if not data.get("display_name"):
                data["display_name"] = data["username"]
            return data
        return None

    # ── Registrasi User Baru ─────────────────────────────────────────────────

    def register(self, username: str, password: str,
                 email: str = "", display_name: str = "", role: str = "user") -> tuple[bool, str]:
        """
        Daftarkan user baru dengan role dinamis (default 'user').
        Return (True, "") jika berhasil, (False, pesan_error) jika gagal.
        """
        if len(password) < 6:
            return False, "Password minimal 6 karakter."
        if not username or len(username) < 3:
            return False, "Username minimal 3 karakter."

        # Validasi role hanya boleh 'user' atau 'admin'
        if role not in ("user", "admin"):
            role = "user"

        # display_name wajib diisi; fallback ke username jika kosong
        final_display = display_name.strip() if display_name.strip() else username

        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO users (username, password, role, email, display_name) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (username, self._hash_password(password), role,
                     email or None, final_display)
                )
            return True, ""
        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                return False, "Username sudah digunakan."
            if "email" in str(e):
                return False, "Email sudah terdaftar."
            return False, "Registrasi gagal."

    # ── Login / Register via Google ──────────────────────────────────────────

    def login_or_register_google(self, google_id: str, email: str,
                                display_name: str) -> dict:
        """
        Login dengan Google. Jika belum terdaftar, buat akun baru otomatis.
        Return dict user.
        """
        with self._connect() as conn:
            # Cek sudah ada belum
            row = conn.execute(
                "SELECT id, username, role, display_name FROM users WHERE google_id = ?",
                (google_id,)
            ).fetchone()
            if row:
                data = dict(row)
                if not data.get("display_name"):
                    data["display_name"] = display_name or data["username"]
                return data

            # Belum ada — buat akun baru
            base_username = email.split("@")[0].replace(".", "_")
            username = base_username
            counter = 1
            while conn.execute(
                "SELECT id FROM users WHERE username = ?", (username,)
            ).fetchone():
                username = f"{base_username}{counter}"
                counter += 1

            final_display = display_name.strip() if display_name.strip() else username

            conn.execute(
                "INSERT INTO users (username, google_id, email, role, display_name) "
                "VALUES (?, ?, ?, 'user', ?)",
                (username, google_id, email, final_display)
            )
            row = conn.execute(
                "SELECT id, username, role, display_name FROM users WHERE google_id = ?",
                (google_id,)
            ).fetchone()
            return dict(row)

    def cek_email_terdaftar(self, email: str) -> bool:
        with self._connect() as conn:
            return bool(conn.execute(
                "SELECT id FROM users WHERE email = ?", (email,)
            ).fetchone())

    # ── Manajemen User (untuk admin) ─────────────────────────────────────────

    def daftar_users(self) -> list:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, username, role, email, display_name, dibuat_pada "
                "FROM users ORDER BY id"
            ).fetchall()
            return [dict(r) for r in rows]

    def tambah_user(self, username: str, password: str, role: str = "user") -> bool:
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO users (username, password, role, display_name) VALUES (?, ?, ?, ?)",
                    (username, self._hash_password(password), role, username)
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def hapus_user(self, user_id: int) -> bool:
        with self._connect() as conn:
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return True

    def update_display_name(self, user_id: int, display_name: str) -> tuple[bool, str]:
        """Update hanya nama tampilan pengguna."""
        display_name = display_name.strip()
        if not display_name:
            return False, "Nama tampilan tidak boleh kosong."
        try:
            with self._connect() as conn:
                conn.execute(
                    "UPDATE users SET display_name=? WHERE id=?",
                    (display_name, user_id)
                )
            return True, ""
        except Exception as e:
            return False, str(e)

    def update_profil(self, user_id: int, display_name: str, username: str) -> tuple[bool, str]:
        """Update nama tampilan dan username."""
        display_name = display_name.strip()
        if not display_name:
            return False, "Nama tampilan tidak boleh kosong."
        if not username or len(username) < 3:
            return False, "Username minimal 3 karakter."
        try:
            with self._connect() as conn:
                conn.execute(
                    "UPDATE users SET display_name=?, username=? WHERE id=?",
                    (display_name, username, user_id)
                )
            return True, ""
        except sqlite3.IntegrityError:
            return False, "Username sudah digunakan."

    def ubah_password(self, user_id: int, password_lama: str, password_baru: str) -> tuple[bool, str]:
        """Ubah password dengan verifikasi password lama."""
        hashed_lama = self._hash_password(password_lama)
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id FROM users WHERE id = ? AND password = ?",
                (user_id, hashed_lama)
            ).fetchone()
            if not row:
                return False, "Password lama salah."
            if len(password_baru) < 6:
                return False, "Password baru minimal 6 karakter."
            conn.execute(
                "UPDATE users SET password=? WHERE id=?",
                (self._hash_password(password_baru), user_id)
            )
        return True, ""

    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Ambil data user terbaru berdasarkan ID."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, username, role, display_name, email FROM users WHERE id = ?",
                (user_id,)
            ).fetchone()
        if row:
            data = dict(row)
            if not data.get("display_name"):
                data["display_name"] = data["username"]
            return data
        return None

    def _seed_default_accounts(self):
        """Tambahkan akun admin dan user default jika belum ada."""
        akun_default = [
            ("admin", "admin123", "admin", "admin@gmail.com", "Admin"),
            ("user",  "user123",  "user",  "",                "User"),
        ]
        with self._connect() as conn:
            for username, password, role, email, display_name in akun_default:
                existing = conn.execute(
                    "SELECT id FROM users WHERE username = ?", (username,)
                ).fetchone()
                if not existing:
                    conn.execute(
                        "INSERT INTO users (username, password, role, display_name) VALUES (?, ?, ?, ?)",
                        (username, self._hash_password(password), role, display_name)
                    )

    def update_profil_email(self, user_id: int, display_name: str, email: str) -> bool:
        """Update nama tampilan dan email pengguna."""
        try:
            with self._connect() as conn:
                conn.execute(
                    "UPDATE users SET display_name = ?, email = ? WHERE id = ?",
                    (display_name, email, user_id)
                )
            return True
        except Exception:
            return False