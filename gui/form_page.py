"""
Form page untuk menambah data wisata secara manual dengan UI yang user-friendly.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox,
    QGroupBox, QHBoxLayout, QGridLayout, QFrame, QDoubleSpinBox, QSpinBox,
    QFormLayout
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QDoubleValidator, QIntValidator, QPixmap, QIcon
import re


class ValidationLabel(QLabel):
    """Label khusus untuk menampilkan status validasi"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVisible(False)
        self.setWordWrap(True)
        
    def show_error(self, message):
        self.setText(f"❌ {message}")
        self.setStyleSheet("color: #e74c3c; font-size: 9pt; padding: 5px; background-color: #ffe6e6; border-radius: 4px;")
        self.setVisible(True)
        
    def show_success(self, message):
        self.setText(f"✓ {message}")
        self.setStyleSheet("color: #27ae60; font-size: 9pt; padding: 5px; background-color: #e8f7ef; border-radius: 4px;")
        self.setVisible(True)
        
    def hide_message(self):
        self.setVisible(False)


class FormField(QWidget):
    """Widget field input dengan validasi real-time"""
    validationChanged = pyqtSignal(bool)
    
    def __init__(self, label, input_widget, validation_type="text", parent=None):
        super().__init__(parent)
        self.label = label
        self.input_widget = input_widget
        self.validation_type = validation_type
        self.validator_label = ValidationLabel()
        self._build()
        
    def _build(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 5)
        
        # Label field
        lbl = QLabel(f"<b>{self.label}</b>")
        lbl.setStyleSheet("font-size: 10pt; color: #2c3e50;")
        layout.addWidget(lbl)
        
        # Input widget
        layout.addWidget(self.input_widget)
        
        # Validator label
        layout.addWidget(self.validator_label)
        
        # Setup validasi real-time jika applicable
        if hasattr(self.input_widget, 'textChanged'):
            self.input_widget.textChanged.connect(self.validate)
        elif hasattr(self.input_widget, 'valueChanged'):
            self.input_widget.valueChanged.connect(self.validate)
        
        self.setLayout(layout)
        
    def validate(self):
        """Validasi input"""
        is_valid = True
        message = ""
        
        if self.validation_type == "text":
            value = self.input_widget.text() if hasattr(self.input_widget, 'text') else ""
            if not value.strip():
                is_valid = False
                message = "Harus diisi"
            else:
                is_valid = True
                message = "Valid"
                
        elif self.validation_type == "numeric":
            value = self.input_widget.text() if hasattr(self.input_widget, 'text') else ""
            try:
                float(value)
                is_valid = True
                message = "Format angka valid"
            except:
                is_valid = False
                message = "Harus angka"
                
        elif self.validation_type == "latlong":
            value = self.input_widget.text() if hasattr(self.input_widget, 'text') else ""
            try:
                val = float(value)
                if -90 <= val <= 90:
                    is_valid = True
                    message = "Koordinat valid"
                else:
                    is_valid = False
                    message = "Harus antara -90 dan 90"
            except:
                is_valid = False
                message = "Format angka tidak valid"
                
        elif self.validation_type == "longitude":
            value = self.input_widget.text() if hasattr(self.input_widget, 'text') else ""
            try:
                val = float(value)
                if -180 <= val <= 180:
                    is_valid = True
                    message = "Koordinat valid"
                else:
                    is_valid = False
                    message = "Harus antara -180 dan 180"
            except:
                is_valid = False
                message = "Format angka tidak valid"
        
        # Update tampilan
        if not is_valid and message:
            self.validator_label.show_error(message)
        elif is_valid and message:
            self.validator_label.show_success(message)
        else:
            self.validator_label.hide_message()
            
        self.validationChanged.emit(is_valid)
        return is_valid
        
    def value(self):
        """Get value dari input widget"""
        if hasattr(self.input_widget, 'text'):
            return self.input_widget.text()
        elif hasattr(self.input_widget, 'value'):
            return self.input_widget.value()
        return None
        
    def setValue(self, value):
        """Set value ke input widget"""
        if hasattr(self.input_widget, 'setText'):
            self.input_widget.setText(str(value))
        elif hasattr(self.input_widget, 'setValue'):
            self.input_widget.setValue(float(value))


class FormPage(QWidget):
    """Halaman form input data wisata dengan UI modern"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.fields = []
        self._build()
        
    def _build(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        
        # Header dengan ikon
        header = QLabel("➕ Tambah Data Wisata Baru")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("""
            color: #2c3e50; 
            margin-bottom: 10px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 8px;
            border-left: 5px solid #3498db;
        """)
        main_layout.addWidget(header)
        
        desc = QLabel("""
        Isi form berikut untuk menambahkan data tempat wisata baru ke dalam sistem.
        Semua field wajib diisi dengan data yang valid.
        """)
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #7f8c8d; font-size: 11pt; margin-bottom: 20px;")
        main_layout.addWidget(desc)
        
        # Form dalam grup
        form_group = QGroupBox("📋 Form Data Wisata")
        form_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-size: 12pt;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #3498db;
            }
        """)
        
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(20)
        
        # Nama Wisata
        name_input = QLineEdit()
        name_input.setPlaceholderText("Contoh: Pantai Kuta, Candi Borobudur")
        name_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: #f0f8ff;
            }
        """)
        name_field = FormField("Nama Tempat Wisata", name_input, "text")
        self.fields.append(name_field)
        form_layout.addWidget(name_field, 0, 0, 1, 2)
        
        # Harga dan Rating dalam satu baris
        price_layout = QHBoxLayout()
        
        # Harga
        price_input = QLineEdit()
        price_input.setPlaceholderText("Contoh: 50000")
        price_input.setValidator(QIntValidator(0, 1000000000))
        price_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: #f0f8ff;
            }
        """)
        price_field = FormField("Harga Tiket (Rp)", price_input, "numeric")
        price_layout.addWidget(price_field)
        
        # Rating
        rating_input = QLineEdit()
        rating_input.setPlaceholderText("Contoh: 4.5")
        rating_input.setValidator(QDoubleValidator(0.0, 5.0, 1))
        rating_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: #f0f8ff;
            }
        """)
        rating_field = FormField("Rating (0-5)", rating_input, "numeric")
        price_layout.addWidget(rating_field)
        
        form_layout.addLayout(price_layout, 1, 0, 1, 2)
        
        # Rating Count
        count_input = QLineEdit()
        count_input.setPlaceholderText("Contoh: 1000")
        count_input.setValidator(QIntValidator(0, 1000000000))
        count_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: #f0f8ff;
            }
        """)
        count_field = FormField("Jumlah Ulasan", count_input, "numeric")
        form_layout.addWidget(count_field, 2, 0, 1, 2)
        
        # Koordinat dalam grup khusus
        coord_group = QGroupBox("📍 Koordinat Lokasi")
        coord_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2ecc71;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-size: 10pt;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #27ae60;
            }
        """)
        
        coord_layout = QGridLayout()
        
        # Latitude
        lat_input = QLineEdit()
        lat_input.setPlaceholderText("Contoh: -6.2088 (Jakarta)")
        lat_input.setValidator(QDoubleValidator(-90.0, 90.0, 6))
        lat_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border-color: #2ecc71;
                background-color: #f0f8ff;
            }
        """)
        lat_field = FormField("Latitude", lat_input, "latlong")
        coord_layout.addWidget(lat_field, 0, 0)
        
        # Longitude
        lon_input = QLineEdit()
        lon_input.setPlaceholderText("Contoh: 106.8456 (Jakarta)")
        lon_input.setValidator(QDoubleValidator(-180.0, 180.0, 6))
        lon_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border-color: #2ecc71;
                background-color: #f0f8ff;
            }
        """)
        lon_field = FormField("Longitude", lon_input, "longitude")
        coord_layout.addWidget(lon_field, 0, 1)
        
        # Info koordinat
        info_label = QLabel("💡 Tips: Gunakan Google Maps untuk mendapatkan koordinat")
        info_label.setStyleSheet("""
            color: #7f8c8d;
            font-size: 9pt;
            font-style: italic;
            padding: 5px;
            background-color: #f8f9fa;
            border-radius: 4px;
        """)
        info_label.setWordWrap(True)
        coord_layout.addWidget(info_label, 1, 0, 1, 2)
        
        coord_group.setLayout(coord_layout)
        form_layout.addWidget(coord_group, 3, 0, 1, 2)
        
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        
        # Status validasi
        self.validation_panel = QFrame()
        self.validation_panel.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.validation_panel.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        self.validation_panel.setVisible(False)
        
        validation_layout = QVBoxLayout()
        self.validation_label = QLabel()
        self.validation_label.setWordWrap(True)
        validation_layout.addWidget(self.validation_label)
        self.validation_panel.setLayout(validation_layout)
        
        main_layout.addWidget(self.validation_panel)
        
        # Tombol aksi
        button_layout = QHBoxLayout()
        
        # Tombol Clear
        btn_clear = QPushButton("🗑️ Bersihkan Form")
        btn_clear.setToolTip("Kosongkan semua field")
        btn_clear.clicked.connect(self.clear_form)
        btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        # Tombol Simpan
        btn_save = QPushButton("💾 Simpan ke Database")
        btn_save.setToolTip("Simpan data ke database")
        btn_save.clicked.connect(self.save)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        
        button_layout.addWidget(btn_clear)
        button_layout.addStretch()
        button_layout.addWidget(btn_save)
        
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        
        # Simpan reference
        self.name_field = name_field
        self.price_field = price_field
        self.rating_field = rating_field
        self.count_field = count_field
        self.lat_field = lat_field
        self.lon_field = lon_field
        self.save_button = btn_save
        
        # Koneksi validasi
        for field in self.fields:
            field.validationChanged.connect(self.update_validation_status)
            
        self.setLayout(main_layout)
        
    def update_validation_status(self):
        """Update status validasi keseluruhan form"""
        all_valid = True
        error_fields = []
        
        for field in self.fields:
            if not field.validate():
                all_valid = False
                error_fields.append(field.label.text().replace('<b>', '').replace('</b>', ''))
        
        if all_valid:
            self.validation_panel.setVisible(True)
            self.validation_label.setText("✓ Semua data valid. Data siap disimpan.")
            self.validation_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            self.save_button.setEnabled(True)
        else:
            self.validation_panel.setVisible(True)
            self.validation_label.setText(f"⚠️ Ada {len(error_fields)} field yang perlu diperbaiki: {', '.join(error_fields)}")
            self.validation_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            self.save_button.setEnabled(False)
            
    def clear_form(self):
        """Clear semua field form"""
        for field in self.fields:
            field.setValue("")
        self.validation_panel.setVisible(False)
        self.save_button.setEnabled(True)
        
        # Fokus ke field pertama
        self.name_field.input_widget.setFocus()
        
    def save(self):
        """Save form data to database."""
        try:
            # Validasi akhir sebelum save
            all_valid = True
            for field in self.fields:
                if not field.validate():
                    all_valid = False
                    break
                    
            if not all_valid:
                QMessageBox.warning(
                    self, 'Validasi Gagal',
                    'Masih ada field yang belum valid. Periksa kembali data Anda.'
                )
                return
            
            # Ambil data
            row = {
                'name': self.name_field.value(),
                'price': float(self.price_field.value()),
                'rating': float(self.rwating_field.value()),
                'rating_count': float(self.count_field.value()),
                'latitude': float(self.lat_field.value()),
                'longitude': float(self.lon_field.value())
            }
            
            # Validasi tambahan untuk koordinat
            if not (-90 <= row['latitude'] <= 90):
                raise ValueError("Latitude harus antara -90 dan 90")
            if not (-180 <= row['longitude'] <= 180):
                raise ValueError("Longitude harus antara -180 dan 180")
            if row['rating'] < 0 or row['rating'] > 5:
                raise ValueError("Rating harus antara 0 dan 5")
            if row['price'] < 0:
                raise ValueError("Harga tidak boleh negatif")
            if row['rating_count'] < 0:
                raise ValueError("Jumlah ulasan tidak boleh negatif")
                
        except ValueError as e:
            QMessageBox.critical(
                self, 'Error Validasi',
                f'Data tidak valid: {str(e)}'
            )
            return
        except Exception as e:
            QMessageBox.critical(
                self, 'Error',
                f'Terjadi kesalahan: {str(e)}'
            )
            return
        
        # Simpan ke database
        try:
            from core.database import save_wisata_rows
            save_wisata_rows([row])
            
            # Tampilkan notifikasi sukses
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Sukses")
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setText("✅ Data berhasil disimpan ke database!")
            msg_box.setInformativeText(f"Data <b>{row['name']}</b> telah ditambahkan.")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
            
            # Clear form setelah sukses
            self.clear_form()
            
        except Exception as e:
            QMessageBox.critical(
                self, 'Error Database',
                f'Gagal menyimpan ke database: {str(e)}'
            )
            
    def show_sample_data(self):
        """Tampilkan contoh data untuk testing"""
        sample_data = {
            'name': "Pantai Kuta Bali",
            'price': "50000",
            'rating': "4.5",
            'rating_count': "12500",
            'latitude': "-8.7222",
            'longitude': "115.1707"
        }
        
        self.name_field.setValue(sample_data['name'])
        self.price_field.setValue(sample_data['price'])
        self.rating_field.setValue(sample_data['rating'])
        self.count_field.setValue(sample_data['rating_count'])
        self.lat_field.setValue(sample_data['latitude'])
        self.lon_field.setValue(sample_data['longitude'])
        
        # Fokus ke field terakhir
        self.lon_field.input_widget.setFocus()