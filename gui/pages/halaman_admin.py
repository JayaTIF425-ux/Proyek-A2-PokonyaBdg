"""
gui/pages/halaman_admin.py — Halaman manajemen data (hanya untuk admin).
Admin bisa: tambah, edit, hapus produk supermarket + kelola akun user.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QMessageBox, QDialog, QFormLayout, QComboBox,
    QTabWidget, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from database.db_manager import DBManager
from database.auth_manager import AuthManager


# ══════════════════════════════════════════════════════════════════════════════
# Dialog: Tambah / Edit Produk
# ══════════════════════════════════════════════════════════════════════════════

class DialogProduk(QDialog):
    """Dialog form untuk tambah atau edit produk supermarket."""

    def __init__(self, parent=None, data: dict = None):
        super().__init__(parent)
        self.setWindowTitle("Tambah Produk" if data is None else "Edit Produk")
        self.setFixedSize(400, 340)
        self.data = data  # None = mode tambah; dict = mode edit

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)

        self.input_nama     = QLineEdit()
        self.input_harga    = QLineEdit()
        self.input_toko     = QLineEdit()
        self.input_kategori = QLineEdit()
        self.input_satuan   = QComboBox()
        self.input_satuan.addItems(["kg", "gram", "liter", "ml", "pcs", "ikat", "butir"])
        self.input_tanggal  = QLineEdit()
        self.input_tanggal.setPlaceholderText("YYYY-MM-DD")

        for widget in [self.input_nama, self.input_harga,
                       self.input_toko, self.input_kategori, self.input_tanggal]:
            widget.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #ccc; border-radius: 6px;
                    padding: 6px 10px; font-size: 13px;
                }
                QLineEdit:focus { border: 1.5px solid #44101A; }
            """)

        form.addRow("Nama Produk *", self.input_nama)
        form.addRow("Harga (Rp) *",  self.input_harga)
        form.addRow("Toko *",        self.input_toko)
        form.addRow("Kategori",      self.input_kategori)
        form.addRow("Satuan",        self.input_satuan)
        form.addRow("Tanggal",       self.input_tanggal)
        layout.addLayout(form)

        # Prefill jika mode edit
        if data:
            self.input_nama.setText(data.get("nama", ""))
            self.input_harga.setText(str(data.get("harga", "")))
            self.input_toko.setText(data.get("toko", ""))
            self.input_kategori.setText(data.get("kategori", ""))
            self.input_tanggal.setText(data.get("tanggal", ""))
            idx = self.input_satuan.findText(data.get("satuan", "kg"))
            if idx >= 0:
                self.input_satuan.setCurrentIndex(idx)

        btn_row = QHBoxLayout()
        btn_simpan = QPushButton("Simpan")
        btn_batal  = QPushButton("Batal")
        btn_simpan.setFixedHeight(36)
        btn_batal.setFixedHeight(36)
        btn_simpan.setStyleSheet("""
            QPushButton { background: #44101A; color: white; border-radius: 6px;
                          font-weight: bold; border: none; }
            QPushButton:hover { background: #6B1525; }
        """)
        btn_batal.setStyleSheet("""
            QPushButton { background: #eee; color: #333; border-radius: 6px; border: none; }
            QPushButton:hover { background: #ddd; }
        """)
        btn_simpan.clicked.connect(self._simpan)
        btn_batal.clicked.connect(self.reject)
        btn_row.addWidget(btn_batal)
        btn_row.addWidget(btn_simpan)
        layout.addLayout(btn_row)

    def _simpan(self):
        nama  = self.input_nama.text().strip()
        harga = self.input_harga.text().strip()
        toko  = self.input_toko.text().strip()
        if not nama or not harga or not toko:
            QMessageBox.warning(self, "Peringatan", "Nama, Harga, dan Toko wajib diisi.")
            return
        try:
            float(harga)
        except ValueError:
            QMessageBox.warning(self, "Peringatan", "Harga harus berupa angka.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "nama":     self.input_nama.text().strip(),
            "harga":    float(self.input_harga.text().strip()),
            "toko":     self.input_toko.text().strip(),
            "kategori": self.input_kategori.text().strip(),
            "satuan":   self.input_satuan.currentText(),
            "tanggal":  self.input_tanggal.text().strip(),
        }

# ══════════════════════════════════════════════════════════════════════════════
# Dialog: Tambah User
# ══════════════════════════════════════════════════════════════════════════════

class DialogTambahUser(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tambah Akun")
        self.setFixedSize(340, 240)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)

        self.input_username = QLineEdit()
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.combo_role = QComboBox()
        self.combo_role.addItems(["user", "admin"])

        _style = """
            QLineEdit { border: 1px solid #ccc; border-radius: 6px;
                        padding: 6px 10px; font-size: 13px; }
            QLineEdit:focus { border: 1.5px solid #44101A; }
        """
        self.input_username.setStyleSheet(_style)
        self.input_password.setStyleSheet(_style)

        form.addRow("Username *", self.input_username)
        form.addRow("Password *", self.input_password)
        form.addRow("Role",       self.combo_role)
        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_simpan = QPushButton("Tambah")
        btn_batal  = QPushButton("Batal")
        btn_simpan.setFixedHeight(36)
        btn_batal.setFixedHeight(36)
        btn_simpan.setStyleSheet("""
            QPushButton { background: #44101A; color: white; border-radius: 6px;
                          font-weight: bold; border: none; }
            QPushButton:hover { background: #6B1525; }
        """)
        btn_batal.setStyleSheet("""
            QPushButton { background: #eee; color: #333; border-radius: 6px; border: none; }
        """)
        btn_simpan.clicked.connect(self._simpan)
        btn_batal.clicked.connect(self.reject)
        btn_row.addWidget(btn_batal)
        btn_row.addWidget(btn_simpan)
        layout.addLayout(btn_row)

    def _simpan(self):
        if not self.input_username.text().strip() or not self.input_password.text():
            QMessageBox.warning(self, "Peringatan", "Username dan password wajib diisi.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "username": self.input_username.text().strip(),
            "password": self.input_password.text(),
            "role":     self.combo_role.currentText(),
        }


# ══════════════════════════════════════════════════════════════════════════════
# Halaman Admin Utama
# ══════════════════════════════════════════════════════════════════════════════

class HalamanAdmin(QWidget):
    """
    Halaman khusus admin:
    - Tab 1: Manajemen produk (tambah, edit, hapus)
    - Tab 2: Manajemen akun user
    """

    def __init__(self, current_user: dict):
        super().__init__()
        self.db   = DBManager()
        self.auth = AuthManager()
        self.current_user = current_user

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # ── Header ─────────────────────────────────────────────────────────
        header = QHBoxLayout()
        lbl = QLabel("⚙️  Panel Admin")
        lbl.setStyleSheet(
            "color: #44101A; font-size: 22px; font-weight: bold;"
        )
        lbl_user = QLabel(f"Login sebagai: <b>{current_user['username']}</b> (admin)")
        lbl_user.setStyleSheet("color: #666; font-size: 13px;")
        lbl_user.setTextFormat(Qt.TextFormat.RichText)
        header.addWidget(lbl)
        header.addStretch()
        header.addWidget(lbl_user)
        layout.addLayout(header)

        # ── Tabs ─────────────────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #ddd; border-radius: 8px; }
            QTabBar::tab { padding: 10px 20px; font-size: 13px; }
            QTabBar::tab:selected { background: #44101A; color: white;
                                    border-radius: 6px; }
        """)
        self.tab_produk = self._buat_tab_produk()
        self.tab_user   = self._buat_tab_user()
        self.tabs.addTab(self.tab_produk, "📦  Manajemen Produk")
        self.tabs.addTab(self.tab_user,   "👥  Manajemen Akun")
        layout.addWidget(self.tabs)

        # Muat data awal
        self._muat_produk()
        self._muat_users()

    # ── Tab: Produk ──────────────────────────────────────────────────────────

    def _buat_tab_produk(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Toolbar
        toolbar = QHBoxLayout()
        self.input_cari_produk = QLineEdit()
        self.input_cari_produk.setPlaceholderText("🔍 Cari produk...")
        self.input_cari_produk.setFixedHeight(36)
        self.input_cari_produk.setStyleSheet("""
            QLineEdit { border: 1px solid #ccc; border-radius: 8px;
                        padding: 6px 12px; font-size: 13px; }
        """)
        self.input_cari_produk.textChanged.connect(self._filter_produk)

        btn_tambah = QPushButton("＋ Tambah Produk")
        btn_tambah.setFixedHeight(36)
        btn_tambah.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_tambah.setStyleSheet("""
            QPushButton { background: #44101A; color: white; border-radius: 8px;
                          font-size: 13px; font-weight: bold; padding: 0 16px; border: none; }
            QPushButton:hover { background: #6B1525; }
        """)
        btn_tambah.clicked.connect(self._tambah_produk)

        toolbar.addWidget(self.input_cari_produk, 1)
        toolbar.addWidget(btn_tambah)
        layout.addLayout(toolbar)

        # Tabel produk
        self.tabel_produk = QTableWidget()
        self.tabel_produk.setColumnCount(7)
        self.tabel_produk.setHorizontalHeaderLabels(
            ["ID", "Nama Produk", "Harga", "Toko", "Kategori", "Satuan", "Tanggal"]
        )
        self.tabel_produk.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabel_produk.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.tabel_produk.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.tabel_produk.setAlternatingRowColors(True)
        self.tabel_produk.setStyleSheet("""
            QTableWidget { border: 1px solid #ddd; border-radius: 6px; font-size: 13px; }
            QHeaderView::section { background: #44101A; color: white; padding: 8px; }
            QTableWidget::item:selected { background: #F1C40F; color: black; }
        """)
        layout.addWidget(self.tabel_produk)

        # Tombol Edit & Hapus
        btn_row = QHBoxLayout()
        btn_edit = QPushButton("✏️  Edit Terpilih")
        btn_hapus = QPushButton("🗑️  Hapus Terpilih")
        for btn in [btn_edit, btn_hapus]:
            btn.setFixedHeight(36)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setStyleSheet("""
            QPushButton { background: #2980b9; color: white; border-radius: 8px;
                          font-size: 13px; padding: 0 16px; border: none; }
            QPushButton:hover { background: #3498db; }
        """)
        btn_hapus.setStyleSheet("""
            QPushButton { background: #c0392b; color: white; border-radius: 8px;
                          font-size: 13px; padding: 0 16px; border: none; }
            QPushButton:hover { background: #e74c3c; }
        """)
        btn_edit.clicked.connect(self._edit_produk)
        btn_hapus.clicked.connect(self._hapus_produk)
        btn_row.addStretch()
        btn_row.addWidget(btn_edit)
        btn_row.addWidget(btn_hapus)
        layout.addLayout(btn_row)

        return widget

    def _muat_produk(self):
        rows = self.db.fetch_semua_produk_supermarket(limit=500)
        self._isi_tabel_produk(rows)

    def _isi_tabel_produk(self, rows):
        self.tabel_produk.setRowCount(len(rows))
        for i, r in enumerate(rows):
            r = dict(r)
            self.tabel_produk.setItem(i, 0, QTableWidgetItem(str(r["id"])))
            self.tabel_produk.setItem(i, 1, QTableWidgetItem(r["nama"] or ""))
            self.tabel_produk.setItem(i, 2, QTableWidgetItem(
                f"Rp {int(r['harga']):,}".replace(",", ".")
            ))
            self.tabel_produk.setItem(i, 3, QTableWidgetItem(r["toko"] or ""))
            self.tabel_produk.setItem(i, 4, QTableWidgetItem(r.get("kategori", "") or ""))
            self.tabel_produk.setItem(i, 5, QTableWidgetItem(r.get("satuan", "") or ""))
            self.tabel_produk.setItem(i, 6, QTableWidgetItem(r["tanggal"] or ""))

    def _filter_produk(self, keyword: str):
        kw = keyword.lower()
        for i in range(self.tabel_produk.rowCount()):
            nama = self.tabel_produk.item(i, 1)
            toko = self.tabel_produk.item(i, 3)
            cocok = (kw in (nama.text().lower() if nama else "")) or \
                    (kw in (toko.text().lower() if toko else ""))
            self.tabel_produk.setRowHidden(i, not cocok)

    def _tambah_produk(self):
        dialog = DialogProduk(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            d = dialog.get_data()
            self.db.tambah_produk(
                nama=d["nama"], harga=d["harga"], toko=d["toko"],
                tanggal=d["tanggal"], kategori=d["kategori"], satuan=d["satuan"]
            )
            self._muat_produk()
            QMessageBox.information(self, "Berhasil", "Produk berhasil ditambahkan.")

    def _edit_produk(self):
        row = self.tabel_produk.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Peringatan", "Pilih produk yang ingin diedit.")
            return
        id_item = self.tabel_produk.item(row, 0)
        if not id_item:
            return
        id_produk = int(id_item.text())
        data = {
            "nama":     self.tabel_produk.item(row, 1).text(),
            "harga":    self.tabel_produk.item(row, 2).text().replace("Rp ", "").replace(".", ""),
            "toko":     self.tabel_produk.item(row, 3).text(),
            "kategori": self.tabel_produk.item(row, 4).text(),
            "satuan":   self.tabel_produk.item(row, 5).text(),
            "tanggal":  self.tabel_produk.item(row, 6).text(),
        }
        dialog = DialogProduk(self, data=data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            d = dialog.get_data()
            self.db.update_produk(
                id_produk=id_produk, nama=d["nama"], harga=d["harga"],
                toko=d["toko"], tanggal=d["tanggal"],
                kategori=d["kategori"], satuan=d["satuan"]
            )
            self._muat_produk()
            QMessageBox.information(self, "Berhasil", "Produk berhasil diperbarui.")

    def _hapus_produk(self):
        row = self.tabel_produk.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Peringatan", "Pilih produk yang ingin dihapus.")
            return
        id_item  = self.tabel_produk.item(row, 0)
        nama_item = self.tabel_produk.item(row, 1)
        if not id_item:
            return
        konfirmasi = QMessageBox.question(
            self, "Konfirmasi Hapus",
            f"Yakin ingin menghapus produk:\n{nama_item.text() if nama_item else ''}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if konfirmasi == QMessageBox.StandardButton.Yes:
            self.db.hapus_produk(int(id_item.text()))
            self._muat_produk()
            QMessageBox.information(self, "Berhasil", "Produk berhasil dihapus.")

     # ── Tab: User ────────────────────────────────────────────────────────────
 
    def _buat_tab_user(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
 
        # Toolbar
        toolbar = QHBoxLayout()
        lbl = QLabel("Daftar Akun Terdaftar")
        lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #44101A;")
        btn_tambah_user = QPushButton("＋ Tambah Akun")
        btn_tambah_user.setFixedHeight(36)
        btn_tambah_user.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_tambah_user.setStyleSheet("""
            QPushButton { background: #44101A; color: white; border-radius: 8px;
                          font-size: 13px; font-weight: bold; padding: 0 16px; border: none; }
            QPushButton:hover { background: #6B1525; }
        """)
        btn_tambah_user.clicked.connect(self._tambah_user)
        toolbar.addWidget(lbl)
        toolbar.addStretch()
        toolbar.addWidget(btn_tambah_user)
        layout.addLayout(toolbar)
 
        # Tabel user
        self.tabel_user = QTableWidget()
        self.tabel_user.setColumnCount(4)
        self.tabel_user.setHorizontalHeaderLabels(["ID", "Username", "Role", "Dibuat Pada"])
        self.tabel_user.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabel_user.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabel_user.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabel_user.setAlternatingRowColors(True)
        self.tabel_user.setStyleSheet("""
            QTableWidget { border: 1px solid #ddd; border-radius: 6px; font-size: 13px; }
            QHeaderView::section { background: #44101A; color: white; padding: 8px; }
            QTableWidget::item:selected { background: #F1C40F; color: black; }
        """)
        layout.addWidget(self.tabel_user)
 
        btn_row = QHBoxLayout()
        btn_hapus_user = QPushButton("🗑️  Hapus Akun Terpilih")
        btn_hapus_user.setFixedHeight(36)
        btn_hapus_user.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_hapus_user.setStyleSheet("""
            QPushButton { background: #c0392b; color: white; border-radius: 8px;
                          font-size: 13px; padding: 0 16px; border: none; }
            QPushButton:hover { background: #e74c3c; }
        """)
        btn_hapus_user.clicked.connect(self._hapus_user)
        btn_row.addStretch()
        btn_row.addWidget(btn_hapus_user)
        layout.addLayout(btn_row)
 
        return widget
 
    def _muat_users(self):
        users = self.auth.daftar_users()
        self.tabel_user.setRowCount(len(users))
        for i, u in enumerate(users):
            self.tabel_user.setItem(i, 0, QTableWidgetItem(str(u["id"])))
            self.tabel_user.setItem(i, 1, QTableWidgetItem(u["username"]))
            item_role = QTableWidgetItem(u["role"])
            item_role.setForeground(
                QColor("#c0392b") if u["role"] == "admin" else QColor("#2980b9")
            )
            self.tabel_user.setItem(i, 2, item_role)
            self.tabel_user.setItem(i, 3, QTableWidgetItem(u.get("dibuat_pada", "")))
 
    def _tambah_user(self):
        dialog = DialogTambahUser(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            d = dialog.get_data()
            berhasil = self.auth.tambah_user(d["username"], d["password"], d["role"])
            if berhasil:
                self._muat_users()
                QMessageBox.information(self, "Berhasil", "Akun berhasil ditambahkan.")
            else:
                QMessageBox.warning(self, "Gagal", "Username sudah digunakan.")
 
    def _hapus_user(self):
        row = self.tabel_user.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Peringatan", "Pilih akun yang ingin dihapus.")
            return
        id_item   = self.tabel_user.item(row, 0)
        nama_item = self.tabel_user.item(row, 1)
        if not id_item:
            return
        user_id = int(id_item.text())
        if user_id == self.current_user["id"]:
            QMessageBox.warning(self, "Tidak Bisa", "Tidak dapat menghapus akun sendiri.")
            return
        konfirmasi = QMessageBox.question(
            self, "Konfirmasi Hapus",
            f"Yakin ingin menghapus akun: {nama_item.text() if nama_item else ''}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if konfirmasi == QMessageBox.StandardButton.Yes:
            self.auth.hapus_user(user_id)
            self._muat_users()
            QMessageBox.information(self, "Berhasil", "Akun berhasil dihapus.")