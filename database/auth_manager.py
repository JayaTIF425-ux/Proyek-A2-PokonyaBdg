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
        hashed = self._hash_password(password)
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, username, role, display_name FROM users "
                "WHERE username = ? AND password = ?",
                (username, hashed)
            ).fetchone()
        if row:
            return dict(row)
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

        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO users (username, password, role, email, display_name) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (username, self._hash_password(password), role,
                     email or None, display_name or username)
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
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, username, role, display_name FROM users WHERE google_id = ?",
                (google_id,)
            ).fetchone()
            if row:
                return dict(row)

            base_username = email.split("@")[0].replace(".", "_")
            username = base_username
            counter = 1
            while conn.execute(
                "SELECT id FROM users WHERE username = ?", (username,)
            ).fetchone():
                username = f"{base_username}{counter}"
                counter += 1

            conn.execute(
                "INSERT INTO users (username, google_id, email, role, display_name) "
                "VALUES (?, ?, ?, 'user', ?)",
                (username, google_id, email, display_name)
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
                    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    (username, self._hash_password(password), role)
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def hapus_user(self, user_id: int) -> bool:
        with self._connect() as conn:
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return True

    # ── [BARU] Update Profil Lengkap ─────────────────────────────────────────

    def update_profil_lengkap(
        self,
        user_id: int,
        display_name: str,
        new_password: Optional[str] = None,
    ) -> tuple[bool, str]:
        """
        [BARU] Update display_name dan (opsional) password sekaligus.

        Ini adalah method utama yang dipanggil oleh _DialogEditProfil.
        Password di-update TANPA memerlukan verifikasi password lama,
        karena user sudah terautentikasi melalui sesi login.

        Args:
            user_id      : ID user di database.
            display_name : Nama tampilan baru.
            new_password : Password baru. Jika None / kosong, password tidak diubah.

        Returns:
            (True, "") jika berhasil, (False, pesan_error) jika gagal.
        """
        if not display_name or not display_name.strip():
            return False, "Nama tampilan tidak boleh kosong."

        if new_password is not None and new_password.strip():
            if len(new_password) < 6:
                return False, "Password minimal 6 karakter."

        try:
            with self._connect() as conn:
                # Selalu update display_name
                conn.execute(
                    "UPDATE users SET display_name = ? WHERE id = ?",
                    (display_name.strip(), user_id)
                )
                # [FIX] Jika ada password baru, langsung update tanpa verifikasi lama
                if new_password and new_password.strip():
                    conn.execute(
                        "UPDATE users SET password = ? WHERE id = ?",
                        (self._hash_password(new_password), user_id)
                    )
            return True, ""
        except Exception as e:
            return False, f"Gagal menyimpan: {str(e)}"

    # ── Update Profil (username + display_name) ──────────────────────────────

    def update_profil(self, user_id: int, display_name: str, username: str) -> tuple[bool, str]:
        """Update nama tampilan dan username."""
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

    # ── [FIX] Ubah Password ──────────────────────────────────────────────────

    def ubah_password(
        self,
        user_id: int,
        password_lama: str,
        password_baru: str,
        force_update: bool = False,
    ) -> tuple[bool, str]:
        """
        Ubah password.

        Args:
            force_update: Jika True, skip verifikasi password lama.
                          Dipakai oleh panel Edit Profil (user sudah login).
        """
        if len(password_baru) < 6:
            return False, "Password baru minimal 6 karakter."

        with self._connect() as conn:
            if not force_update:
                # Verifikasi password lama (untuk fitur ganti password dengan konfirmasi)
                hashed_lama = self._hash_password(password_lama)
                row = conn.execute(
                    "SELECT id FROM users WHERE id = ? AND password = ?",
                    (user_id, hashed_lama)
                ).fetchone()
                if not row:
                    return False, "Password lama salah."

            conn.execute(
                "UPDATE users SET password=? WHERE id=?",
                (self._hash_password(password_baru), user_id)
            )
        return True, ""

    # ── [BARU] Set Password Langsung ────────────────────────────────────────

    def set_password(self, user_id: int, password_baru: str) -> tuple[bool, str]:
        """
        [BARU] Set password langsung tanpa verifikasi password lama.
        Alias dari ubah_password(..., force_update=True).
        """
        return self.ubah_password(
            user_id=user_id,
            password_lama="",
            password_baru=password_baru,
            force_update=True,
        )

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
                        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                        (username, self._hash_password(password), role)
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