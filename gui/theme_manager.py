# gui/theme_manager.py
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import QObject, pyqtSignal

TEMA = {
    "light": {
        "sidebar":    "#44101A",
        "sidebar_aktif": "#6B1525",
        "aksen":      "#F1C40F",
        "bg":         "#F8F6F2",
        "card":       "#FFFFFF",
        "teks_utama": "#1A0A0E",
        "teks_redup": "#6B5B61",
        "border":     "#E2D9CC",
        "error":      "#C0392B",
        "success":    "#27AE60",
    },
    "dark": {
        "sidebar":    "#1A0A0E",
        "sidebar_aktif": "#3D1020",
        "aksen":      "#F1C40F",
        "bg":         "#121212",
        "card":       "#1E1E1E",
        "teks_utama": "#F0ECE8",
        "teks_redup": "#9A8A90",
        "border":     "#3A2A2E",
        "error":      "#E74C3C",
        "success":    "#2ECC71",
    },
}

class ThemeManager(QObject):
    tema_berubah = pyqtSignal(str)   # emit "light" atau "dark"

    def __init__(self, app: QApplication):
        super().__init__()
        self._app = app
        # Deteksi otomatis dari OS
        hints = app.styleHints()
        hints.colorSchemeChanged.connect(self._on_system_changed)
        self._mode = self._deteksi_mode()

    def _deteksi_mode(self) -> str:
        from PyQt6.QtCore import Qt
        scheme = self._app.styleHints().colorScheme()
        return "dark" if scheme == Qt.ColorScheme.Dark else "light"

    def _on_system_changed(self):
        self._mode = self._deteksi_mode()
        self.tema_berubah.emit(self._mode)

    def warna(self, kunci: str) -> str:
        return TEMA[self._mode].get(kunci, "#000000")

    def mode(self) -> str:
        return self._mode