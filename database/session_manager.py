import os
import json
import base64


_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
_SESSION_FILE = os.path.join(_DATA_DIR, "session.json")


class SessionManager:
    """Menyimpan, memuat, dan menghapus sesi login user ke file JSON lokal."""

    @staticmethod
    def _pastikan_folder():
        os.makedirs(_DATA_DIR, exist_ok=True)

    @staticmethod
    def simpan_sesi(user_dict: dict) -> None:
        """
        Simpan data sesi user ke data/session.json.
        user_dict berisi: id, username, role, display_name (opsional).
        """
        SessionManager._pastikan_folder()
        data_sesi = {
            "id":           user_dict.get("id", 0),
            "username":     user_dict.get("username", ""),
            "role":         user_dict.get("role", "user"),
            "display_name": user_dict.get("display_name", ""),
        }
        # Enkripsi ringan dengan base64 agar tidak terbaca langsung
        raw = json.dumps(data_sesi, ensure_ascii=False)
        encoded = base64.b64encode(raw.encode("utf-8")).decode("utf-8")
        with open(_SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump({"sesi": encoded}, f)

    @staticmethod
    def muat_sesi() -> dict | None:
        """
        Muat data sesi dari file. Return dict user jika valid, None jika tidak ada.
        """
        if not os.path.exists(_SESSION_FILE):
            return None
        try:
            with open(_SESSION_FILE, "r", encoding="utf-8") as f:
                wrapper = json.load(f)
            encoded = wrapper.get("sesi", "")
            raw = base64.b64decode(encoded.encode("utf-8")).decode("utf-8")
            data = json.loads(raw)
            # Validasi minimal: harus ada username dan role
            if data.get("username") and data.get("role"):
                return data
        except Exception:
            pass
        return None

    @staticmethod
    def hapus_sesi() -> None:
        """Hapus file sesi (dipakai saat logout)."""
        if os.path.exists(_SESSION_FILE):
            try:
                os.remove(_SESSION_FILE)
            except Exception:
                pass