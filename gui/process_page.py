"""
Process page untuk menjalankan TOPSIS calculation dan menampilkan hasil.
"""

import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
)

from core.database import load_wisata_db, load_user_location
from core.haversine import haversine_km
from core.topsis import topsis_rank


class ProcessPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._build()

    def _build(self):
        layout = QVBoxLayout()

        btn_calc = QPushButton('Hitung Jarak & Jalankan TOPSIS')
        btn_calc.clicked.connect(self.run_full_process)
        layout.addWidget(btn_calc)

        self.process_table = QTableWidget()
        layout.addWidget(self.process_table)

        self.setLayout(layout)

    def run_full_process(self):
        """Load data, calculate distance, and run TOPSIS."""
        df = load_wisata_db()

        if df.empty:
            QMessageBox.critical(
                self, 'Error',
                'Tidak ada data wisata. Upload atau muat dari DB dulu.'
            )
            return

        lat, lon, _ = load_user_location()

        if lat is None:
            QMessageBox.critical(
                self, 'Error',
                'Lokasi user belum disetel. Masukkan di tab Lokasi User.'
            )
            return

        # Calculate distance
        df['distance_km'] = df.apply(
            lambda r: haversine_km(
                lat, lon,
                float(r['latitude']), float(r['longitude'])
            ),
            axis=1
        )

        # Convert to numeric
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        df['rating_count'] = pd.to_numeric(df['rating_count'], errors='coerce')
        df['distance_km'] = pd.to_numeric(df['distance_km'], errors='coerce')

        # Get weights from weights_page
        wpage = self.parent.weights_page
        w = [
            wpage.spin_price.value(),
            wpage.spin_rating.value(),
            wpage.spin_count.value(),
            wpage.spin_dist.value()
        ]

        # Normalize weights
        w = pd.Series(w, dtype=float)
        if w.sum() == 0:
            nw = (w + 1) / (w.size + w.sum())
        else:
            nw = w / w.sum()

        # Run TOPSIS
        matrix = df[['price', 'rating', 'rating_count', 'distance_km']].copy()
        scores = topsis_rank(
            matrix, nw.values,
            ['cost', 'benefit', 'benefit', 'cost']
        )

        df['topsis_score'] = scores
        df['rank'] = df['topsis_score'].rank(ascending=False, method='min').astype(int)

        self.parent.latest_results = df.sort_values('rank')
        self._show_process_table(df)

        # Navigate to results tab (index 5)
        self.parent.pages.setCurrentIndex(5)

    def _show_process_table(self, df):
        """Display results in table."""
        cols = list(df.columns)
        self.process_table.setColumnCount(len(cols))
        self.process_table.setRowCount(len(df))
        self.process_table.setHorizontalHeaderLabels(cols)
        self.process_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for i, (_, row) in enumerate(df.iterrows()):
            for j, col in enumerate(cols):
                self.process_table.setItem(i, j, QTableWidgetItem(str(row[col])))
