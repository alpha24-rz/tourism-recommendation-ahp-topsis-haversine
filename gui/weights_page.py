"""
Weights page untuk mengatur bobot preferensi menggunakan AHP dengan interface yang user-friendly.
"""

import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSpinBox, QPushButton, QMessageBox, 
    QGridLayout, QGroupBox, QHBoxLayout, QComboBox, QSlider, QFormLayout,
    QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor


class CriteriaControl(QWidget):
    """Widget kontrol untuk satu kriteria dengan slider dan spinbox"""
    valueChanged = pyqtSignal(int)
    
    def __init__(self, label, description="", parent=None):
        super().__init__(parent)
        self.label = label
        self.description = description
        self._build()
        
    def _build(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 5, 0, 5)
        
        # Label kriteria
        self.lbl_title = QLabel(f"<b>{self.label}</b>")
        self.lbl_title.setStyleSheet("font-size: 11pt;")
        layout.addWidget(self.lbl_title)
        
        # Deskripsi
        if self.description:
            self.lbl_desc = QLabel(self.description)
            self.lbl_desc.setWordWrap(True)
            self.lbl_desc.setStyleSheet("color: #666; font-size: 9pt;")
            layout.addWidget(self.lbl_desc)
        
        # Kontainer untuk slider dan spinbox
        control_layout = QHBoxLayout()
        
        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(25)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.valueChanged.connect(self._on_slider_changed)
        control_layout.addWidget(self.slider)
        
        # SpinBox
        self.spinbox = QSpinBox()
        self.spinbox.setRange(0, 100)
        self.spinbox.setValue(25)
        self.spinbox.setFixedWidth(70)
        self.spinbox.valueChanged.connect(self._on_spinbox_changed)
        control_layout.addWidget(self.spinbox)
        
        layout.addLayout(control_layout)
        self.setLayout(layout)
        
    def _on_slider_changed(self, value):
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(value)
        self.spinbox.blockSignals(False)
        self.valueChanged.emit(value)
        
    def _on_spinbox_changed(self, value):
        self.slider.blockSignals(True)
        self.slider.setValue(value)
        self.slider.blockSignals(False)
        self.valueChanged.emit(value)
        
    def value(self):
        return self.slider.value()
        
    def setValue(self, value):
        self.slider.setValue(value)
        self.spinbox.setValue(value)


class PreferencePreset(QGroupBox):
    """Widget preset preferensi dengan visualisasi progress bar"""
    presetSelected = pyqtSignal(dict)
    
    def __init__(self, title, description, weights, parent=None):
        super().__init__(title, parent)
        self.weights = weights
        self.description = description
        self._build()
        
    def _build(self):
        layout = QVBoxLayout()
        
        # Deskripsi preset
        lbl_desc = QLabel(self.description)
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #555; font-size: 10pt; margin-bottom: 10px;")
        layout.addWidget(lbl_desc)
        
        # Visualisasi bobot
        for criteria, weight in self.weights.items():
            row_layout = QHBoxLayout()
            
            lbl_crit = QLabel(criteria)
            lbl_crit.setFixedWidth(100)
            
            # Progress bar sederhana
            progress_frame = QFrame()
            progress_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
            progress_frame.setFixedHeight(20)
            progress_frame.setFixedWidth(200)
            
            progress_inner = QFrame(progress_frame)
            progress_inner.setStyleSheet(f"background-color: #4CAF50; border-radius: 3px;")
            progress_inner.setFixedHeight(16)
            progress_inner.move(2, 2)
            progress_inner.resize(int(196 * weight / 100), 16)
            
            lbl_weight = QLabel(f"{weight}%")
            lbl_weight.setFixedWidth(40)
            
            row_layout.addWidget(lbl_crit)
            row_layout.addWidget(progress_frame)
            row_layout.addWidget(lbl_weight)
            row_layout.addStretch()
            
            layout.addLayout(row_layout)
        
        # Tombol pilih preset
        btn_select = QPushButton("Gunakan Preset Ini")
        btn_select.clicked.connect(self._on_select)
        btn_select.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        layout.addWidget(btn_select)
        
        self.setLayout(layout)
        
    def _on_select(self):
        self.presetSelected.emit(self.weights)


class WeightsPage(QWidget):
    """Halaman pengaturan bobot AHP yang user-friendly"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.criteria_controls = {}
        self._build()
        
    def _build(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        
        # Header
        header = QLabel("Atur Bobot Preferensi")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(header)
        
        desc = QLabel("""
        Atur seberapa penting setiap kriteria dalam rekomendasi tempat makan.
        Total bobot akan dinormalisasi otomatis menjadi 100%.
        """)
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #7f8c8d; font-size: 11pt; margin-bottom: 20px;")
        main_layout.addWidget(desc)
        
        # Bagian 1: Preset Preferensi
        preset_group = QGroupBox("Pilihan Cepat (Preset)")
        preset_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #3498db;
            }
        """)
        
        preset_layout = QHBoxLayout()
        
        # Preset 1: Harga Murah
        preset1 = PreferencePreset(
            "💰 Harga Terjangkau",
            "Prioritaskan tempat dengan harga murah",
            {"Harga": 60, "Rating": 20, "Jumlah Ulasan": 10, "Jarak": 10}
        )
        preset1.presetSelected.connect(self.apply_preset)
        
        # Preset 2: Rating Tinggi
        preset2 = PreferencePreset(
            "⭐ Rating Terbaik",
            "Prioritaskan tempat dengan rating tinggi",
            {"Harga": 20, "Rating": 60, "Jumlah Ulasan": 15, "Jarak": 5}
        )
        preset2.presetSelected.connect(self.apply_preset)
        
        # Preset 3: Jarak Dekat
        preset3 = PreferencePreset(
            "📍 Jarak Terdekat",
            "Prioritaskan tempat yang dekat",
            {"Harga": 15, "Rating": 15, "Jumlah Ulasan": 10, "Jarak": 60}
        )
        preset3.presetSelected.connect(self.apply_preset)
        
        preset_layout.addWidget(preset1)
        preset_layout.addWidget(preset2)
        preset_layout.addWidget(preset3)
        preset_group.setLayout(preset_layout)
        main_layout.addWidget(preset_group)
        
        # Bagian 2: Kontrol Manual
        manual_group = QGroupBox("Atur Manual")
        manual_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2ecc71;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #27ae60;
            }
        """)
        
        manual_layout = QGridLayout()
        manual_layout.setVerticalSpacing(15)
        manual_layout.setHorizontalSpacing(20)
        
        # Kriteria Harga
        price_group = QGroupBox("Kriteria Harga")
        price_layout = QVBoxLayout()
        
        price_pref = QComboBox()
        price_pref.addItems(["Netral", "Murah", "Sangat Murah", "Mahal", "Sangat Mahal"])
        price_pref.currentTextChanged.connect(self._on_price_pref_changed)
        price_layout.addWidget(price_pref)
        
        price_control = CriteriaControl(
            "Bobot Harga", 
            "Semakin tinggi nilai, semakin penting faktor harga"
        )
        price_control.valueChanged.connect(self.update_total)
        price_layout.addWidget(price_control)
        price_group.setLayout(price_layout)
        
        # Kriteria Rating
        rating_group = QGroupBox("Kriteria Rating")
        rating_layout = QVBoxLayout()
        
        rating_pref = QComboBox()
        rating_pref.addItems(["Netral", "Rendah", "Sedang", "Tinggi", "Sangat Tinggi"])
        rating_pref.currentTextChanged.connect(self._on_rating_pref_changed)
        rating_layout.addWidget(rating_pref)
        
        rating_control = CriteriaControl(
            "Bobot Rating", 
            "Semakin tinggi nilai, semakin penting faktor rating"
        )
        rating_control.valueChanged.connect(self.update_total)
        rating_layout.addWidget(rating_control)
        rating_group.setLayout(rating_layout)
        
        # Kriteria Jumlah Ulasan
        count_group = QGroupBox("Kriteria Jumlah Ulasan")
        count_layout = QVBoxLayout()
        
        count_pref = QComboBox()
        count_pref.addItems(["Netral", "Sedikit", "Sedang", "Banyak", "Sangat Banyak"])
        count_pref.currentTextChanged.connect(self._on_count_pref_changed)
        count_layout.addWidget(count_pref)
        
        count_control = CriteriaControl(
            "Bobot Jumlah Ulasan", 
            "Semakin tinggi nilai, semakin penting faktor jumlah ulasan"
        )
        count_control.valueChanged.connect(self.update_total)
        count_layout.addWidget(count_control)
        count_group.setLayout(count_layout)
        
        # Kriteria Jarak
        distance_group = QGroupBox("Kriteria Jarak")
        distance_layout = QVBoxLayout()
        
        distance_pref = QComboBox()
        distance_pref.addItems(["Netral", "Sangat Dekat", "Dekat", "Jauh", "Sangat Jauh"])
        distance_pref.currentTextChanged.connect(self._on_distance_pref_changed)
        distance_layout.addWidget(distance_pref)
        
        distance_control = CriteriaControl(
            "Bobot Jarak", 
            "Semakin tinggi nilai, semakin penting faktor jarak (dekat lebih baik)"
        )
        distance_control.valueChanged.connect(self.update_total)
        distance_layout.addWidget(distance_control)
        distance_group.setLayout(distance_layout)
        
        manual_layout.addWidget(price_group, 0, 0)
        manual_layout.addWidget(rating_group, 0, 1)
        manual_layout.addWidget(count_group, 1, 0)
        manual_layout.addWidget(distance_group, 1, 1)
        
        manual_group.setLayout(manual_layout)
        main_layout.addWidget(manual_group)
        
        # Simpan kontrol untuk referensi
        self.price_control = price_control
        self.rating_control = rating_control
        self.count_control = count_control
        self.distance_control = distance_control
        
        self.price_pref = price_pref
        self.rating_pref = rating_pref
        self.count_pref = count_pref
        self.distance_pref = distance_pref
        
        # Bagian 3: Total dan Aksi
        footer_layout = QHBoxLayout()
        
        # Panel total
        total_panel = QFrame()
        total_panel.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        total_panel.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        total_layout = QVBoxLayout()
        self.lbl_total = QLabel("Total Bobot: 100 / 100")
        self.lbl_total.setFont(QFont("Arial", 12, QFont.Bold))
        self.lbl_total.setStyleSheet("color: #27ae60;")
        
        self.lbl_warning = QLabel("")
        self.lbl_warning.setStyleSheet("color: #e74c3c; font-size: 10pt;")
        
        total_layout.addWidget(self.lbl_total)
        total_layout.addWidget(self.lbl_warning)
        total_panel.setLayout(total_layout)
        
        footer_layout.addWidget(total_panel)
        footer_layout.addStretch()
        
        # Tombol aksi
        btn_layout = QVBoxLayout()
        
        btn_normalize = QPushButton("🔄 Normalisasi Otomatis")
        btn_normalize.setToolTip("Atur ulang total bobot menjadi 100%")
        btn_normalize.clicked.connect(self.normalize_weights)
        btn_normalize.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        btn_show = QPushButton("📊 Tampilkan Bobot Normalisasi")
        btn_show.clicked.connect(self.show_normalized_weights)
        btn_show.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        
        btn_layout.addWidget(btn_normalize)
        btn_layout.addWidget(btn_show)
        footer_layout.addLayout(btn_layout)
        
        main_layout.addLayout(footer_layout)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        self.update_total()
        
    def _on_price_pref_changed(self, text):
        """Atur bobot berdasarkan preferensi harga"""
        weights = {
            "Netral": 25,
            "Murah": 40,
            "Sangat Murah": 60,
            "Mahal": 15,
            "Sangat Mahal": 10
        }
        if text in weights:
            self.price_control.setValue(weights[text])
            self.normalize_weights()
            
    def _on_rating_pref_changed(self, text):
        """Atur bobot berdasarkan preferensi rating"""
        weights = {
            "Netral": 25,
            "Rendah": 10,
            "Sedang": 20,
            "Tinggi": 40,
            "Sangat Tinggi": 60
        }
        if text in weights:
            self.rating_control.setValue(weights[text])
            self.normalize_weights()
            
    def _on_count_pref_changed(self, text):
        """Atur bobot berdasarkan preferensi jumlah ulasan"""
        weights = {
            "Netral": 25,
            "Sedikit": 15,
            "Sedang": 25,
            "Banyak": 35,
            "Sangat Banyak": 45
        }
        if text in weights:
            self.count_control.setValue(weights[text])
            self.normalize_weights()
            
    def _on_distance_pref_changed(self, text):
        """Atur bobot berdasarkan preferensi jarak"""
        weights = {
            "Netral": 25,
            "Sangat Dekat": 60,
            "Dekat": 40,
            "Jauh": 15,
            "Sangat Jauh": 10
        }
        if text in weights:
            self.distance_control.setValue(weights[text])
            self.normalize_weights()
            
    def apply_preset(self, weights):
        """Terapkan preset yang dipilih"""
        self.price_control.setValue(weights.get("Harga", 25))
        self.rating_control.setValue(weights.get("Rating", 25))
        self.count_control.setValue(weights.get("Jumlah Ulasan", 25))
        self.distance_control.setValue(weights.get("Jarak", 25))
        
        # Reset combobox ke netral
        self.price_pref.setCurrentText("Netral")
        self.rating_pref.setCurrentText("Netral")
        self.count_pref.setCurrentText("Netral")
        self.distance_pref.setCurrentText("Netral")
        
        self.update_total()
        
    def update_total(self):
        """Update tampilan total bobot"""
        total = (
            self.price_control.value() + 
            self.rating_control.value() + 
            self.count_control.value() + 
            self.distance_control.value()
        )
        
        self.lbl_total.setText(f"Total Bobot: {total} / 100")
        
        if total > 100:
            self.lbl_total.setStyleSheet("color: #e74c3c; font-weight: bold;")
            self.lbl_warning.setText("⚠️ Total melebihi 100%! Gunakan tombol normalisasi.")
        elif total < 100:
            self.lbl_total.setStyleSheet("color: #f39c12; font-weight: bold;")
            self.lbl_warning.setText(f"⚠️ Kurang {100-total}% untuk mencapai 100%")
        else:
            self.lbl_total.setStyleSheet("color: #27ae60; font-weight: bold;")
            self.lbl_warning.setText("✓ Total bobot sudah tepat 100%")
            
    def normalize_weights(self):
        """Normalisasi bobot menjadi total 100%"""
        values = [
            self.price_control.value(),
            self.rating_control.value(),
            self.count_control.value(),
            self.distance_control.value()
        ]
        
        total = sum(values)
        
        if total == 0:
            normalized = [25, 25, 25, 25]
        else:
            normalized = [int(v * 100 / total) for v in values]
            
            # Distribusikan sisa pembulatan
            remainder = 100 - sum(normalized)
            for i in range(abs(remainder)):
                idx = i % 4
                if remainder > 0:
                    normalized[idx] += 1
                else:
                    normalized[idx] -= 1
        
        self.price_control.setValue(normalized[0])
        self.rating_control.setValue(normalized[1])
        self.count_control.setValue(normalized[2])
        self.distance_control.setValue(normalized[3])
        
        self.update_total()
        
    def show_normalized_weights(self):
        """Tampilkan bobot yang sudah dinormalisasi"""
        values = np.array([
            self.price_control.value(),
            self.rating_control.value(),
            self.count_control.value(),
            self.distance_control.value()
        ], dtype=float)
        
        total = values.sum()
        
        if total == 0:
            nw = [0.25, 0.25, 0.25, 0.25]
        else:
            nw = (values / total).round(4)
        
        # Tampilkan dalam format yang lebih informatif
        message = (
            "<h3>Bobot Normalisasi (AHP)</h3>"
            "<table border='1' cellpadding='5' style='border-collapse: collapse; margin: 10px;'>"
            "<tr style='background-color: #3498db; color: white;'>"
            "<th>Kriteria</th><th>Bobot Awal</th><th>Bobot Normalisasi</th><th>Persentase</th>"
            "</tr>"
            f"<tr><td>Harga</td><td>{int(values[0])}</td><td>{nw[0]:.4f}</td><td>{nw[0]*100:.2f}%</td></tr>"
            f"<tr><td>Rating</td><td>{int(values[1])}</td><td>{nw[1]:.4f}</td><td>{nw[1]*100:.2f}%</td></tr>"
            f"<tr><td>Jumlah Ulasan</td><td>{int(values[2])}</td><td>{nw[2]:.4f}</td><td>{nw[2]*100:.2f}%</td></tr>"
            f"<tr><td>Jarak</td><td>{int(values[3])}</td><td>{nw[3]:.4f}</td><td>{nw[3]*100:.2f}%</td></tr>"
            f"<tr style='font-weight: bold; background-color: #f8f9fa;'>"
            f"<td>Total</td><td>{int(total)}</td><td>1.0000</td><td>100.00%</td>"
            "</tr>"
            "</table>"
            "<p>Bobot normalisasi akan digunakan dalam perhitungan AHP.</p>"
        )
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Bobot Normalisasi")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.exec_()
        
    def get_normalized_weights(self):
        """Dapatkan bobot normalisasi untuk perhitungan AHP"""
        values = np.array([
            self.price_control.value(),
            self.rating_control.value(),
            self.count_control.value(),
            self.distance_control.value()
        ], dtype=float)
        
        total = values.sum()
        
        if total == 0:
            return np.array([0.25, 0.25, 0.25, 0.25])
        
        return values / total