"""
Weights page untuk mengatur bobot preferensi menggunakan AHP.
"""

import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSpinBox, QPushButton, QMessageBox, QGridLayout
)


class WeightsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._build()

    def _build(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel(
            'Masukkan bobot preferensi (0-100). Sistem akan menormalisasi otomatis.'
        ))

        # Grid layout untuk spinbox
        grid = QGridLayout()

        self.spin_price = QSpinBox()
        self.spin_price.setRange(0, 100)
        self.spin_price.setValue(25)

        self.spin_rating = QSpinBox()
        self.spin_rating.setRange(0, 100)
        self.spin_rating.setValue(25)

        self.spin_count = QSpinBox()
        self.spin_count.setRange(0, 100)
        self.spin_count.setValue(25)

        self.spin_dist = QSpinBox()
        self.spin_dist.setRange(0, 100)
        self.spin_dist.setValue(25)

        grid.addWidget(QLabel('Harga'), 0, 0)
        grid.addWidget(self.spin_price, 0, 1)

        grid.addWidget(QLabel('Rating'), 1, 0)
        grid.addWidget(self.spin_rating, 1, 1)

        grid.addWidget(QLabel('Rating Count'), 2, 0)
        grid.addWidget(self.spin_count, 2, 1)

        grid.addWidget(QLabel('Jarak (km)'), 3, 0)
        grid.addWidget(self.spin_dist, 3, 1)

        layout.addLayout(grid)

        btn = QPushButton('Tampilkan Bobot Normalisasi')
        btn.clicked.connect(self.show_norm)
        layout.addWidget(btn)

        layout.addStretch()
        self.setLayout(layout)

    def show_norm(self):
        """Display normalized weights."""
        w = np.array([
            self.spin_price.value(),
            self.spin_rating.value(),
            self.spin_count.value(),
            self.spin_dist.value()
        ], dtype=float)

        s = w.sum()

        if s == 0:
            nw = [0.25, 0.25, 0.25, 0.25]
        else:
            nw = (w / s).round(4)

        message = (
            f'Harga: {nw[0]}\n'
            f'Rating: {nw[1]}\n'
            f'Rating Count: {nw[2]}\n'
            f'Jarak: {nw[3]}'
        )

        QMessageBox.information(self, 'Bobot Dinormalisasi', message)
