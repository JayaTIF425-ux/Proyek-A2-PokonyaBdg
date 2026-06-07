import os
import json

_DATA_DIR  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
_PREF_FILE = os.path.join(_DATA_DIR, "theme_prefs.json")

# ── Light Mode ────────────────────────────────────────────────────────────────
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
QScrollBar:vertical {
    background: #F0EDE8;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #C0B0A8;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background: #44101A; }
"""

# ── Dark Mode ─────────────────────────────────────────────────────────────────
# Hierarki warna:
#   Halaman (bg)  : #16213E  (navy gelap)
#   Card/Panel    : #1E2A45  (navy sedikit lebih terang)
#   Card elevated : #253354  (untuk hover/focus)
#   Border        : #2E4070  (biru navy redup)
#   Teks utama    : #E8EAF0  (putih kebiruan)
#   Teks sekunder : #A8B4CC  (abu biru)
#   Aksen sidebar : tetap #44101A maroon
_QSS_DARK = """
QWidget {
    background-color: #16213E;
    color: #E8EAF0;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QMainWindow, QDialog {
    background-color: #16213E;
}
QFrame {
    background-color: #1E2A45;
    color: #E8EAF0;
}
QScrollArea {
    background: transparent;
    border: none;
}
QScrollArea > QWidget > QWidget {
    background: transparent;
}
QLineEdit, QComboBox, QDateEdit, QTextEdit {
    background: #1A2540;
    border: 1.5px solid #2E4070;
    border-radius: 8px;
    padding: 6px 10px;
    color: #E8EAF0;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 2px solid #8B9B3A;
    background: #1E2A45;
}
QLineEdit::placeholder { color: #6B7A99; }
QPushButton {
    background-color: #44101A;
    color: #E8EAF0;
    border: none;
    border-radius: 8px;
    padding: 6px 14px;
    font-weight: 600;
}
QPushButton:hover { background-color: #6B1525; }
QPushButton:pressed { background-color: #3A0E16; }
QPushButton:disabled { background-color: #2E3A55; color: #6B7A99; }
QTableWidget {
    background-color: #1E2A45;
    color: #E8EAF0;
    gridline-color: #2E4070;
    border: none;
}
QTableWidget::item {
    color: #E8EAF0;
    border-bottom: 1px solid #2E4070;
}
QTableWidget::item:selected {
    background-color: #2E4070;
    color: #E8EAF0;
}
QHeaderView::section {
    background-color: #162035;
    color: #A8B4CC;
    border: none;
    border-bottom: 1px solid #2E4070;
    padding: 6px 10px;
    font-weight: 600;
}
QLabel {
    background: transparent;
    color: #E8EAF0;
}
QScrollBar:vertical {
    background: #1E2A45;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #2E4070;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background: #8B9B3A; }
QScrollBar:horizontal {
    background: #1E2A45;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #2E4070;
    border-radius: 4px;
}
QComboBox QAbstractItemView {
    background-color: #1E2A45;
    color: #E8EAF0;
    border: 1px solid #2E4070;
    selection-background-color: #2E4070;
    selection-color: #E8EAF0;
}
QTabWidget::pane {
    background-color: #1E2A45;
    border: 1px solid #2E4070;
}
QTabBar::tab {
    background: #162035;
    color: #A8B4CC;
    padding: 8px 16px;
    border: none;
}
QTabBar::tab:selected {
    background: #1E2A45;
    color: #E8EAF0;
    border-bottom: 2px solid #8B9B3A;
}
QTabBar::tab:hover { background: #1E2A45; color: #E8EAF0; }
QProgressBar {
    background: #1A2540;
    border: 1px solid #2E4070;
    border-radius: 6px;
    color: #E8EAF0;
}
QProgressBar::chunk {
    background-color: #8B9B3A;
    border-radius: 6px;
}
QMessageBox { background-color: #1E2A45; color: #E8EAF0; }
QMessageBox QLabel { color: #E8EAF0; }
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
    def is_dark() -> bool:
        return ThemeManager.get_theme() == "dark"

    @staticmethod
    def get_stylesheet() -> str:
        """Return QSS stylesheet sesuai tema aktif."""
        return _QSS_DARK if ThemeManager.get_theme() == "dark" else _QSS_LIGHT

    @staticmethod
    def ikon_stroke() -> str:
        """Warna stroke SVG yang cocok dengan tema aktif."""
        return "#E8EAF0" if ThemeManager.get_theme() == "dark" else "#5C1A28"

    @staticmethod
    def ikon_stroke_muted() -> str:
        """Warna stroke redup/sekunder sesuai tema."""
        return "#A8B4CC" if ThemeManager.get_theme() == "dark" else "#A89BA0"

    @staticmethod
    def apply_to_app(app) -> None:
        """Terapkan stylesheet ke QApplication."""
        app.setStyleSheet(ThemeManager.get_stylesheet())