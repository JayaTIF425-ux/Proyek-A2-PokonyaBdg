import os
import json

_DATA_DIR   = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
_PREF_FILE  = os.path.join(_DATA_DIR, "theme_prefs.json")

_QSS_LIGHT = """
QWidget {
    background-color: #F8F6F2;
    color: #1A0A0E;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QFrame {
    background-color: #FFFFFF;
}
QLineEdit, QComboBox, QDateEdit, QTextEdit {
    background: #FAFAF8;
    border: 1.5px solid #E2D9CC;
    border-radius: 8px;
    padding: 6px 10px;
    color: #1A0A0E;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 2px solid #44101A;
    background: #FFFFFF;
}
QPushButton {
    background-color: #44101A;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 6px 14px;
    font-weight: 600;
}
QPushButton:hover { background-color: #6B1525; }
QPushButton:pressed { background-color: #3A0E16; }
QScrollArea, QScrollArea > QWidget > QWidget {
    background: transparent;
    border: none;
}
QTableWidget {
    background-color: #FFFFFF;
    color: #1A0A0E;
    gridline-color: #E2D9CC;
}
QHeaderView::section {
    background-color: #F4F0EA;
    color: #44101A;
    border: none;
    border-bottom: 1px solid #E2D9CC;
    padding: 6px 10px;
    font-weight: 600;
}
QLabel {
    background: transparent;
    color: #1A0A0E;
}
"""

_QSS_DARK = """
QWidget {
    background-color: #1A1A2E;
    color: #E8E0CC;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QFrame {
    background-color: #252535;
}
QLineEdit, QComboBox, QDateEdit, QTextEdit {
    background: #2E2E45;
    border: 1.5px solid #3A3A55;
    border-radius: 8px;
    padding: 6px 10px;
    color: #E8E0CC;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 2px solid #8B6F7A;
    background: #333350;
}
QPushButton {
    background-color: #44101A;
    color: #E8E0CC;
    border: none;
    border-radius: 8px;
    padding: 6px 14px;
    font-weight: 600;
}
QPushButton:hover { background-color: #6B1525; }
QPushButton:pressed { background-color: #3A0E16; }
QScrollArea, QScrollArea > QWidget > QWidget {
    background: transparent;
    border: none;
}
QTableWidget {
    background-color: #252535;
    color: #E8E0CC;
    gridline-color: #3A3A55;
}
QHeaderView::section {
    background-color: #1E1E30;
    color: #E8E0CC;
    border: none;
    border-bottom: 1px solid #3A3A55;
    padding: 6px 10px;
    font-weight: 600;
}
QLabel {
    background: transparent;
    color: #E8E0CC;
}
QScrollBar:vertical {
    background: #252535;
    width: 8px;
}
QScrollBar::handle:vertical {
    background: #44101A;
    border-radius: 4px;
    min-height: 20px;
}
"""


class ThemeManager:
    """Mengelola preferensi tema terang/gelap untuk aplikasi."""

    @staticmethod
    def _pastikan_folder():
        os.makedirs(_DATA_DIR, exist_ok=True)

    @staticmethod
    def get_theme() -> str:
        """Return 'light' atau 'dark'. Default: 'light'."""
        if not os.path.exists(_PREF_FILE):
            return "light"
        try:
            with open(_PREF_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("tema", "light")
        except Exception:
            return "light"

    @staticmethod
    def set_theme(tema: str) -> None:
        """Simpan preferensi tema. tema: 'light' atau 'dark'."""
        ThemeManager._pastikan_folder()
        with open(_PREF_FILE, "w", encoding="utf-8") as f:
            json.dump({"tema": tema}, f)

    @staticmethod
    def toggle() -> str:
        """Toggle antara light dan dark. Return tema baru."""
        tema_baru = "dark" if ThemeManager.get_theme() == "light" else "light"
        ThemeManager.set_theme(tema_baru)
        return tema_baru

    @staticmethod
    def get_stylesheet() -> str:
        """Return QSS stylesheet sesuai tema aktif."""
        return _QSS_DARK if ThemeManager.get_theme() == "dark" else _QSS_LIGHT

    @staticmethod
    def apply_to_app(app) -> None:
        """Terapkan stylesheet ke QApplication."""
        app.setStyleSheet(ThemeManager.get_stylesheet())