"""
gui/widgets/scraper_dialog.py — Dialog loading saat scraping berlangsung.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QTextEdit, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont


class ScraperDialog(QDialog):
    """Dialog yang menampilkan progress scraping."""
    
    cancel_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Memuat Data Harga")
        self.setModal(True)
        self.setMinimumSize(500, 350)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self._is_cancelled = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Judul
        title = QLabel("Mengambil Data Harga Terbaru")
        title.setStyleSheet("color: #44101A; font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Mohon tunggu, sedang memuat data dari berbagai toko...")
        subtitle.setStyleSheet("color: #666; font-size: 12px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                background-color: #F5F5F5;
                height: 25px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #6B1525;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Label status
        self.status_label = QLabel("Memulai...")
        self.status_label.setStyleSheet("color: #44101A; font-size: 13px; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Log area
        log_label = QLabel("Log:")
        log_label.setStyleSheet("color: #666; font-size: 11px; font-weight: bold;")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #F9F9F9;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                color: #333;
            }
        """)
        layout.addWidget(self.log_text)
        
        # Tombol batal
        self.btn_cancel = QPushButton("Batal")
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 30px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
            }
        """)
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.clicked.connect(self._on_cancel)
        layout.addWidget(self.btn_cancel, alignment=Qt.AlignmentFlag.AlignCenter)
    
    def update_progress(self, message: str):
        """Update status dan tambahkan ke log."""
        self.status_label.setText(message)
        self.log_text.append(message)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def set_finished(self, success: bool, message: str):
        """Set dialog ke state selesai."""
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100 if success else 0)
        
        if self._is_cancelled:
            self.status_label.setText("Dibatalkan")
            self.log_text.append("\n" + "="*50)
            self.log_text.append("Scraping dibatalkan oleh user")
        else:
            self.status_label.setText("Selesai!" if success else "Gagal")
            self.log_text.append("\n" + "="*50)
            self.log_text.append(message)
        
        self.btn_cancel.setText("Tutup")
        self.btn_cancel.setEnabled(True)
        
        # Auto-close setelah 2 detik jika dibatalkan
        if self._is_cancelled:
            QTimer.singleShot(2000, self.accept)
    
    def _on_cancel(self):
        """Handle tombol batal/tutup."""
        if self.btn_cancel.text() == "Tutup":
            self.accept()
        else:
            self._is_cancelled = True
            self.btn_cancel.setEnabled(False)
            self.btn_cancel.setText("Membatalkan...")
            self.cancel_requested.emit()
            self.status_label.setText("Membatalkan...")
            self.log_text.append("\n[USER] Permintaan pembatalan dikirim...")