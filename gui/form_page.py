"""
Form page untuk menambah data wisata secara manual.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)

from core.database import save_wisata_rows


class FormPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._build()

    def _build(self):
        layout = QVBoxLayout()

        # Input fields
        self.name = QLineEdit()
        self.name.setPlaceholderText('Nama')

        self.price = QLineEdit()
        self.price.setPlaceholderText('Harga (numeric)')

        self.rating = QLineEdit()
        self.rating.setPlaceholderText('Rating (numeric)')

        self.count = QLineEdit()
        self.count.setPlaceholderText('Rating Count (numeric)')

        self.lat = QLineEdit()
        self.lat.setPlaceholderText('Latitude (decimal)')

        self.lon = QLineEdit()
        self.lon.setPlaceholderText('Longitude (decimal)')

        # Add labels and fields
        layout.addWidget(QLabel('Nama'))
        layout.addWidget(self.name)

        layout.addWidget(QLabel('Harga'))
        layout.addWidget(self.price)

        layout.addWidget(QLabel('Rating'))
        layout.addWidget(self.rating)

        layout.addWidget(QLabel('Rating Count'))
        layout.addWidget(self.count)

        layout.addWidget(QLabel('Latitude'))
        layout.addWidget(self.lat)

        layout.addWidget(QLabel('Longitude'))
        layout.addWidget(self.lon)

        # Save button
        btn = QPushButton('Simpan ke DB')
        btn.clicked.connect(self.save)
        layout.addWidget(btn)

        layout.addStretch()
        self.setLayout(layout)

    def save(self):
        """Save form data to database."""
        try:
            row = {
                'name': self.name.text(),
                'price': float(self.price.text()),
                'rating': float(self.rating.text()),
                'rating_count': float(self.count.text()),
                'latitude': float(self.lat.text()),
                'longitude': float(self.lon.text())
            }
        except Exception:
            QMessageBox.critical(
                self, 'Error',
                'Validasi gagal. Pastikan semua field numerik diisi dengan benar.'
            )
            return

        save_wisata_rows([row])
        QMessageBox.information(self, 'Sukses', 'Tempat wisata disimpan ke database.')

        # Clear fields
        self.name.clear()
        self.price.clear()
        self.rating.clear()
        self.count.clear()
        self.lat.clear()
        self.lon.clear()
