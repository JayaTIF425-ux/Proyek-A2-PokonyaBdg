import os
import json

_DATA_DIR  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
_PREF_FILE = os.path.join(_DATA_DIR, "theme_prefs.json")


# ─────────────────────────────────────────────────────────────────────────────
# Palet warna per tema — dipakai di QSS dan komponen custom (sidebar, dll.)
# ─────────────────────────────────────────────────────────────────────────────

PALET = {
    "light": {
        # Latar
        "bg":           "#F8F6F2",
        "bg_card":      "#FFFFFF",
        "bg_input":     "#FAFAF8",
        "bg_header":    "#F4F0EA",
        "bg_sidebar":   "#44101A",
        "bg_sidebar_active": "#6B1525",

        # Teks
        "text":         "#1A0A0E",
        "text_mid":     "#6B5B61",
        "text_light":   "#A89BA0",
        "text_sidebar": "#FFFFFF",
        "text_accent":  "#F1C40F",

        # Border
        "border":       "#E2D9CC",
        "border_focus": "#44101A",
        "divider":      "#E2D9CC",

        # Aksen & Status
        "accent":       "#5C1A28",
        "accent_hover": "#7A2236",
        "success":      "#27AE60",
        "error":        "#C0392B",
        "warning":      "#F39C12",

        # Komponen khas
        "stat_bg":      "#FDF8F5",
        "stat_value":   "#5C1A28",
        "stat_label":   "#8B7B6B",
        "green_accent": "#6B8E23",
        "green_hover":  "#5a7a1c",
        "scroll_bar":   "#E2D9CC",
        "scroll_handle":"#44101A",
    },
    "dark": {
        # Latar
        "bg":           "#12121E",
        "bg_card":      "#1E1E30",
        "bg_input":     "#252540",
        "bg_header":    "#1A1A2E",
        "bg_sidebar":   "#0D0D1A",
        "bg_sidebar_active": "#2A1020",

        # Teks
        "text":         "#E8E0CC",
        "text_mid":     "#A89BA0",
        "text_light":   "#6B5B61",
        "text_sidebar": "#E8E0CC",
        "text_accent":  "#F1C40F",

        # Border
        "border":       "#2E2E50",
        "border_focus": "#8B6F7A",
        "divider":      "#2E2E50",

        # Aksen & Status
        "accent":       "#7A2236",
        "accent_hover": "#9A2A44",
        "success":      "#2ECC71",
        "error":        "#E74C3C",
        "warning":      "#F39C12",

        # Komponen khas
        "stat_bg":      "#1E1E30",
        "stat_value":   "#F1C40F",
        "stat_label":   "#A89BA0",
        "green_accent": "#4E6B1A",
        "green_hover":  "#3d5914",
        "scroll_bar":   "#252540",
        "scroll_handle":"#7A2236",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# QSS Stylesheet lengkap per tema
# ─────────────────────────────────────────────────────────────────────────────

def _buat_qss(tema: str) -> str:
    p = PALET[tema]
    return f"""
/* ── Global ────────────────────────────────────────────────────────────── */
QWidget {{
    background-color: {p['bg']};
    color: {p['text']};
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}}

/* ── Frame / Card ───────────────────────────────────────────────────────── */
QFrame {{
    background-color: {p['bg_card']};
    border: none;
}}

/* ── Input ──────────────────────────────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background: {p['bg_input']};
    border: 1.5px solid {p['border']};
    border-radius: 8px;
    padding: 6px 10px;
    color: {p['text']};
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 2px solid {p['border_focus']};
    background: {p['bg_card']};
}}
QLineEdit::placeholder, QTextEdit::placeholder {{
    color: {p['text_light']};
}}

/* ── ComboBox ───────────────────────────────────────────────────────────── */
QComboBox {{
    background: {p['bg_input']};
    border: 1.5px solid {p['border']};
    border-radius: 8px;
    padding: 5px 10px;
    color: {p['text']};
}}
QComboBox:focus {{
    border: 2px solid {p['border_focus']};
}}
QComboBox QAbstractItemView {{
    background: {p['bg_card']};
    color: {p['text']};
    selection-background-color: {p['accent']};
    selection-color: #FFFFFF;
    border: 1px solid {p['border']};
    border-radius: 4px;
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

/* ── Button ─────────────────────────────────────────────────────────────── */
QPushButton {{
    background-color: {p['accent']};
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 6px 14px;
    font-weight: 600;
}}
QPushButton:hover {{ background-color: {p['accent_hover']}; }}
QPushButton:pressed {{ background-color: {p['accent']}; }}
QPushButton:disabled {{
    background-color: {p['border']};
    color: {p['text_light']};
}}

/* ── Label ──────────────────────────────────────────────────────────────── */
QLabel {{
    background: transparent;
    color: {p['text']};
    border: none;
}}

/* ── ScrollArea ─────────────────────────────────────────────────────────── */
QScrollArea, QScrollArea > QWidget > QWidget {{
    background: transparent;
    border: none;
}}

/* ── ScrollBar ──────────────────────────────────────────────────────────── */
QScrollBar:vertical {{
    background: {p['scroll_bar']};
    width: 8px;
    border-radius: 4px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {p['scroll_handle']};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: {p['scroll_bar']};
    height: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {p['scroll_handle']};
    border-radius: 4px;
    min-width: 24px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ── Table ──────────────────────────────────────────────────────────────── */
QTableWidget {{
    background-color: {p['bg_card']};
    color: {p['text']};
    gridline-color: {p['border']};
    border: none;
    border-radius: 8px;
}}
QHeaderView::section {{
    background-color: {p['bg_header']};
    color: {p['text_mid']};
    border: none;
    border-bottom: 1px solid {p['border']};
    padding: 8px 10px;
    font-weight: 600;
    font-size: 12px;
}}
QTableWidget::item {{
    padding: 10px;
    color: {p['text']};
    border-bottom: 1px solid {p['border']};
}}
QTableWidget::item:selected {{
    background-color: {p['accent']};
    color: #FFFFFF;
}}

/* ── DateEdit ───────────────────────────────────────────────────────────── */
QDateEdit {{
    background: {p['bg_input']};
    border: 1.5px solid {p['border']};
    border-radius: 8px;
    padding: 5px 10px;
    color: {p['text']};
}}
QDateEdit:focus {{ border: 2px solid {p['border_focus']}; }}

/* ── ToolTip ────────────────────────────────────────────────────────────── */
QToolTip {{
    background-color: {p['bg_card']};
    color: {p['text']};
    border: 1px solid {p['border']};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}}

/* ── GroupBox ───────────────────────────────────────────────────────────── */
QGroupBox {{
    border: 1.5px solid {p['border']};
    border-radius: 10px;
    margin-top: 12px;
    padding-top: 8px;
    color: {p['text']};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    color: {p['accent_hover']};
    font-weight: 600;
}}

/* ── Tab Widget ─────────────────────────────────────────────────────────── */
QTabWidget::pane {{
    border: 1px solid {p['border']};
    border-radius: 8px;
    background: {p['bg_card']};
}}
QTabBar::tab {{
    background: {p['bg_header']};
    color: {p['text_mid']};
    padding: 8px 16px;
    border: 1px solid {p['border']};
    border-bottom: none;
    border-radius: 6px 6px 0 0;
}}
QTabBar::tab:selected {{
    background: {p['bg_card']};
    color: {p['accent']};
    font-weight: 600;
}}

/* ── CheckBox ───────────────────────────────────────────────────────────── */
QCheckBox {{
    color: {p['text']};
    spacing: 6px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 2px solid {p['border']};
    border-radius: 4px;
    background: {p['bg_input']};
}}
QCheckBox::indicator:checked {{
    background: {p['accent']};
    border-color: {p['accent']};
}}

/* ── Splitter ───────────────────────────────────────────────────────────── */
QSplitter::handle {{
    background: {p['border']};
    width: 1px;
    height: 1px;
}}

/* ── MessageBox ─────────────────────────────────────────────────────────── */
QMessageBox {{
    background-color: {p['bg_card']};
    color: {p['text']};
}}
"""


_QSS_LIGHT = _buat_qss("light")
_QSS_DARK  = _buat_qss("dark")


# ─────────────────────────────────────────────────────────────────────────────
# ThemeManager — API publik
# ─────────────────────────────────────────────────────────────────────────────

class ThemeManager:
    """
    Mengelola preferensi tema terang/gelap untuk aplikasi.

    Penggunaan:
        tema = ThemeManager.get_theme()          # 'light' atau 'dark'
        ThemeManager.set_theme('dark')
        tema_baru = ThemeManager.toggle()
        ThemeManager.apply_to_app(QApplication.instance())
        palet = ThemeManager.get_palette()       # dict warna tema aktif
    """

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
        if tema not in ("light", "dark"):
            tema = "light"
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
    def get_palette() -> dict:
        """
        [BARU] Return dict palet warna sesuai tema aktif.
        Dipakai komponen custom untuk mengambil warna tanpa hard-code hex.
        """
        return PALET[ThemeManager.get_theme()]

    @staticmethod
    def apply_to_app(app) -> None:
        """Terapkan stylesheet ke QApplication secara global."""
        app.setStyleSheet(ThemeManager.get_stylesheet())

    @staticmethod
    def apply_to_widget(widget) -> None:
        """
        [BARU] Terapkan stylesheet ke satu widget saja (tidak global).
        Berguna untuk dialog/popup yang butuh tema konsisten.
        """
        widget.setStyleSheet(ThemeManager.get_stylesheet())