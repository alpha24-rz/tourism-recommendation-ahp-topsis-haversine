"""
Results page untuk menampilkan dan export hasil ranking wisata.
"""

import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QMessageBox, QHBoxLayout
)

from core.database import reset_wisata_table


class ResultsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._build()

    def _build(self):
        layout = QVBoxLayout()

        h = QHBoxLayout()

        btn_export = QPushButton('Export CSV')
        btn_export.clicked.connect(self.export_results_csv)

        btn_reset = QPushButton('Reset DB (Hapus semua data wisata)')
        btn_reset.clicked.connect(self.reset_db)

        h.addWidget(btn_export)
        h.addWidget(btn_reset)
        layout.addLayout(h)

        self.results_table = QTableWidget()
        layout.addWidget(self.results_table)

        self.setLayout(layout)

    def show_results(self):
        """Display results in table."""
        if getattr(self.parent, 'latest_results', None) is None:
            return

        df = self.parent.latest_results.copy()
        cols = [
            'name', 'price', 'rating', 'rating_count',
            'latitude', 'longitude', 'distance_km', 'topsis_score', 'rank'
        ]
        df = df[cols]

        self.results_table.setColumnCount(len(cols))
        self.results_table.setRowCount(len(df))
        self.results_table.setHorizontalHeaderLabels(cols)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for i, (_, row) in enumerate(df.iterrows()):
            for j, col in enumerate(cols):
                val = row[col]
                if isinstance(val, float):
                    item = QTableWidgetItem(f"{val:.4f}")
                else:
                    item = QTableWidgetItem(str(val))
                self.results_table.setItem(i, j, item)

    def export_results_csv(self):
        """Export results to CSV."""
        if getattr(self.parent, 'latest_results', None) is None:
            QMessageBox.information(self, 'Info', 'Belum ada hasil untuk diexport.')
            return

        path, _ = QFileDialog.getSaveFileName(self, 'Save CSV', filter='CSV Files (*.csv)')

        if not path:
            return

        df = self.parent.latest_results.copy()
        df.to_csv(path, index=False)
        QMessageBox.information(self, 'Sukses', f'Hasil diexport ke {path}')

    def reset_db(self):
        """Reset database with confirmation."""
        ok = QMessageBox.question(
            self, 'Konfirmasi',
            'Yakin ingin menghapus semua data wisata di database?'
        )

        if ok != QMessageBox.Yes:
            return

        reset_wisata_table()
        QMessageBox.information(self, 'Sukses', 'Semua data wisata terhapus.')
