"""
Upload page untuk upload data wisata dari CSV atau Excel.
"""

import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QLabel
)

from core.database import save_wisata_rows, load_wisata_db
from utils.template_generator import generate_excel_template



REQUIRED_COLS = [
    'name', 'price', 'rating', 'rating_count', 'latitude', 'longitude'
]


class UploadPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.df_data = pd.DataFrame(columns=REQUIRED_COLS)
        self._build()

    # ==========================================================
    # UI BUILDER
    # ==========================================================
    def _build(self):
        layout = QVBoxLayout()
        h = QHBoxLayout()

        # Buttons
        btn_load_csv = QPushButton('Upload CSV')
        btn_load_csv.clicked.connect(self.load_csv)

        btn_load_excel = QPushButton('Upload Excel')
        btn_load_excel.clicked.connect(self.load_excel)

        btn_save_db = QPushButton('Simpan ke DB')
        btn_save_db.clicked.connect(self.save_to_db)

        btn_refresh = QPushButton('Muat dari DB')
        btn_refresh.clicked.connect(self.refresh_from_db)

        h.addWidget(btn_load_csv)
        h.addWidget(btn_load_excel)
        h.addWidget(btn_save_db)
        h.addWidget(btn_refresh)
        layout.addLayout(h)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(len(REQUIRED_COLS))
        self.table.setHorizontalHeaderLabels(REQUIRED_COLS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        note = QLabel(
            'Format kolom wajib: name, price, rating, rating_count, latitude, longitude'
        )
        layout.addWidget(note)

        self.setLayout(layout)

    # ==========================================================
    # FILE LOADERS
    # ==========================================================
    def load_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Open CSV', filter='CSV Files (*.csv)'
        )
        if not path:
            return

        try:
            df = pd.read_csv(path)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Gagal membaca CSV:\n{e}')
            return

        self._ingest_df(df)

    def load_excel(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Open Excel', filter='Excel Files (*.xls *.xlsx)'
        )
        if not path:
            return

        try:
            df = pd.read_excel(path)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Gagal membaca Excel:\n{e}')
            return

        self._ingest_df(df)

    # ==========================================================
    # INGEST & VALIDATION
    # ==========================================================
    def _ingest_df(self, df):
        """Validasi kolom dan tampilkan ke tabel."""
        missing = set(REQUIRED_COLS) - set(df.columns)
        if missing:
            QMessageBox.critical(
                self, 'Error',
                f'Kolom wajib yang hilang: {", ".join(missing)}'
            )
            return

        # Ambil hanya kolom yang dibutuhkan
        df = df[REQUIRED_COLS].copy()

        # Penanganan NaN
        df = df.fillna('')

        self.df_data = df
        self._refresh_table_from_df()

        QMessageBox.information(
            self, 'Sukses',
            f'Data berhasil dimuat: {len(self.df_data)} baris'
        )

    # ==========================================================
    # RENDER TABLE
    # ==========================================================
    def _refresh_table_from_df(self):
        self.table.setRowCount(len(self.df_data))

        for i, (_, row) in enumerate(self.df_data.iterrows()):
            for j, col in enumerate(REQUIRED_COLS):
                self.table.setItem(i, j, QTableWidgetItem(str(row[col])))

    # ==========================================================
    # DATABASE OPERATIONS
    # ==========================================================
    def save_to_db(self):
        if self.df_data.empty:
            QMessageBox.warning(self, 'Warning', 'Tidak ada data untuk disimpan.')
            return

        try:
            rows = self.df_data.to_dict('records')
            save_wisata_rows(rows)
            QMessageBox.information(
                self, 'Sukses',
                f'{len(rows)} data wisata berhasil disimpan ke database.'
            )
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Gagal menyimpan ke DB:\n{e}')

    def refresh_from_db(self):
        """Load data dari database (manual)."""
        try:
            df = load_wisata_db()

            if df.empty:
                QMessageBox.information(self, 'Info', 'Database kosong.')
                return

            df = df[REQUIRED_COLS].copy()
            df = df.fillna('')

            self.df_data = df
            self._refresh_table_from_df()

            QMessageBox.information(
                self, 'Sukses',
                f'Data dimuat dari DB: {len(self.df_data)} baris'
            )
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Gagal membaca DB:\n{e}')

    # ==========================================================
    # EXTRA — DIPANGGIL DARI TOPBAR
    # ==========================================================
    def load_data(self):
        """Alias reload untuk dipanggil dari tombol topbar."""
        self.refresh_from_db()

    def download_template(self):
        """Generate template Excel untuk user."""

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan Template",
            "template_wisata.xlsx",
            "Excel File (*.xlsx)"
        )

        if not save_path:
            return

        try:
            # Panggil generator template
            generate_excel_template(save_path)

            QMessageBox.information(
                self,
                "Sukses",
                "Template berhasil dibuat dan disimpan."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Gagal membuat template:\n{e}"
            )

