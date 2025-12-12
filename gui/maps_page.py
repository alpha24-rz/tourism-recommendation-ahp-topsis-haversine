"""Maps page untuk menentukan lokasi user dengan interactive map."""

import os
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, 
    QMessageBox, QHBoxLayout, QFrame, QGroupBox
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import pyqtSlot, QObject, QUrl, Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

from core.database import save_user_location, load_user_location, init_db


class Bridge(QObject):
    """Bridge untuk komunikasi antara JavaScript dan Python."""
    
    # Signal untuk mengirim data ke JavaScript
    updateMapSignal = pyqtSignal(float, float, str)
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.web_page_loaded = False
    
    @pyqtSlot(float, float)
    def updateLocation(self, lat, lng):
        """Update lokasi ketika user memilih di map."""
        self.parent.current_lat = lat
        self.parent.current_lng = lng
        
        # Update UI boxes
        self.parent.lat_box.setText(f"{lat:.6f}")
        self.parent.lng_box.setText(f"{lng:.6f}")
        
        # Emit signal untuk update status
        self.parent.location_selected.emit(True)
    
    @pyqtSlot()
    def onPageLoaded(self):
        """Dijalankan ketika halaman web selesai dimuat."""
        self.web_page_loaded = True
        print("Map page loaded successfully")
        
        # Coba muat lokasi terakhir jika ada
        lat, lng, _ = load_user_location()
        if lat is not None and lng is not None:
            # Kirim lokasi ke JavaScript
            self.updateMapSignal.emit(lat, lng, "last_location")
    
    @pyqtSlot(float, float, str)
    def setMarker(self, lat, lng, marker_type="user_click"):
        """Dipanggil dari JavaScript untuk menetapkan marker."""
        self.updateLocation(lat, lng)


class MapsPage(QWidget):
    """Page untuk memilih lokasi user menggunakan map."""
    
    # Signal untuk memberitahu bahwa lokasi telah dipilih
    location_selected = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_lat = None
        self.current_lng = None
        self.bridge = None
        self.btn_save = None
        self.status_label = None
        self.lat_box = None
        self.lng_box = None
        self.web = None
        
        # Initialize database
        init_db()
        
        # Build UI and setup web channel BEFORE loading the HTML to avoid
        # race where the page's QWebChannel JS executes before Python side is ready.
        self._build()
    
    def _build(self):
        """Build UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # ==================
        # Title
        # ==================
        title_label = QLabel("Pilih Lokasi Anda")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        layout.addWidget(title_label)
        
        # ==================
        # Instructions
        # ==================
        instruction_label = QLabel(
            "Klik pada peta untuk memilih lokasi atau seret marker ke posisi yang diinginkan."
        )
        instruction_label.setWordWrap(True)
        instruction_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")
        layout.addWidget(instruction_label)
        
        # ==================
        # Map Frame
        # ==================
        map_group = QGroupBox("Peta Interaktif")
        map_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #3498db;
            }
        """)
        
        map_layout = QVBoxLayout()
        map_layout.setContentsMargins(5, 15, 5, 5)
        
        self.web = QWebEngineView()
        self.web.setMinimumHeight(400)

        # Allow local file (file:///) content to access remote resources
        # (Leaflet CSS/JS/CDN) so the page loaded from disk can fetch https:// assets.
        # This prevents CORS errors like: "Access to script at 'https://...' from origin 'file://' has been blocked".
        try:
            self.web.page().settings().setAttribute(
                QWebEngineSettings.LocalContentCanAccessRemoteUrls, True
            )
            self.web.page().settings().setAttribute(
                QWebEngineSettings.LocalContentCanAccessFileUrls, True
            )
        except Exception:
            # Older PyQt versions might not expose these attributes; ignore safely.
            pass

        # Setup web channel BEFORE loading the page to ensure
        # the JavaScript QWebChannel has the transport available
        # when `qrc:///qtwebchannel/qwebchannel.js` executes.
        self._setup_web_channel()

        # Resolve asset path relative to project root (module location)
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        html_path = os.path.join(base_dir, 'assets', 'maps.html')

        if os.path.exists(html_path):
            self.web.load(QUrl.fromLocalFile(html_path))
        else:
            # Fallback: simple HTML jika file tidak ada
            print(f"File maps.html tidak ditemukan di: {html_path}")
            self.web.setHtml(self._get_fallback_html())
        
        map_layout.addWidget(self.web)
        map_group.setLayout(map_layout)
        layout.addWidget(map_group, stretch=1)
        
        # ==================
        # Coordinate Display
        # ==================
        coord_group = QGroupBox("Koordinat")
        coord_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #27ae60;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #27ae60;
            }
        """)
        
        coord_layout = QVBoxLayout()
        coord_layout.setSpacing(5)
        
        # Latitude
        lat_layout = QHBoxLayout()
        lat_label = QLabel('Latitude:')
        lat_label.setFixedWidth(80)
        self.lat_box = QLineEdit()
        self.lat_box.setReadOnly(False)  # Biarkan bisa diedit manual
        self.lat_box.setPlaceholderText('Masukkan latitude...')
        self.lat_box.textChanged.connect(self._on_coordinate_changed)
        lat_layout.addWidget(lat_label)
        lat_layout.addWidget(self.lat_box)
        coord_layout.addLayout(lat_layout)
        
        # Longitude
        lng_layout = QHBoxLayout()
        lng_label = QLabel('Longitude:')
        lng_label.setFixedWidth(80)
        self.lng_box = QLineEdit()
        self.lng_box.setReadOnly(False)  # Biarkan bisa diedit manual
        self.lng_box.setPlaceholderText('Masukkan longitude...')
        self.lng_box.textChanged.connect(self._on_coordinate_changed)
        lng_layout.addWidget(lng_label)
        lng_layout.addWidget(self.lng_box)
        coord_layout.addLayout(lng_layout)
        
        # Update Button untuk koordinat manual
        update_btn = QPushButton('Update Peta dari Koordinat')
        update_btn.clicked.connect(self._update_map_from_coordinates)
        update_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        coord_layout.addWidget(update_btn)
        
        coord_group.setLayout(coord_layout)
        layout.addWidget(coord_group)
        
        # ==================
        # Action Buttons
        # ==================
        button_group = QFrame()
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Save Button
        btn_save = QPushButton(' Simpan Lokasi')
        btn_save.clicked.connect(self.save_location)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        btn_save.setEnabled(False)
        self.btn_save = btn_save
        
        # Reset Button
        btn_reset = QPushButton(' Reset')
        btn_reset.clicked.connect(self.reset_location)
        btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        # Current Location Button
        btn_current = QPushButton(' Lokasi Saya')
        btn_current.clicked.connect(self._get_current_location)
        btn_current.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        button_layout.addWidget(btn_save)
        button_layout.addWidget(btn_reset)
        button_layout.addWidget(btn_current)
        button_layout.addStretch()
        
        button_group.setLayout(button_layout)
        layout.addWidget(button_group)
        
        # Status Label
        self.status_label = QLabel("Belum ada lokasi yang dipilih")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-style: italic;
                padding: 5px;
                border-top: 1px solid #ecf0f1;
                margin-top: 10px;
            }
        """)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # Connect signal
        self.location_selected.connect(self._on_location_selected)
    
    def _setup_web_channel(self):
        """Setup web channel untuk komunikasi dengan JavaScript."""
        self.bridge = Bridge(self)
        channel = QWebChannel(self.web.page())
        self.web.page().setWebChannel(channel)
        channel.registerObject("pyObj", self.bridge)
        
        # Connect bridge signal
        self.bridge.updateMapSignal.connect(self._send_to_js)
        
        # Connect page load finished signal
        self.web.page().loadFinished.connect(self.bridge.onPageLoaded)
    
    def _send_to_js(self, lat, lng, action_type):
        """Kirim data ke JavaScript."""
        if self.bridge and self.bridge.web_page_loaded:
            js_code = f"""
                if (typeof setUserLocation === 'function') {{
                    setUserLocation({lat}, {lng}, "{action_type}");
                }}
            """
            self.web.page().runJavaScript(js_code)
    
    def _on_coordinate_changed(self):
        """Handle ketika koordinat diubah manual."""
        try:
            lat_text = self.lat_box.text().strip()
            lng_text = self.lng_box.text().strip()
            
            if lat_text and lng_text:
                lat = float(lat_text)
                lng = float(lng_text)
                
                # Validasi range
                if -90 <= lat <= 90 and -180 <= lng <= 180:
                    self.current_lat = lat
                    self.current_lng = lng
                    self.location_selected.emit(True)
                else:
                    self.location_selected.emit(False)
            else:
                self.location_selected.emit(False)
        except ValueError:
            self.location_selected.emit(False)
    
    def _update_map_from_coordinates(self):
        """Update peta berdasarkan koordinat manual."""
        try:
            lat = float(self.lat_box.text())
            lng = float(self.lng_box.text())
            
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                self._send_to_js(lat, lng, "manual_input")
                self.status_label.setText(f"Peta diperbarui ke: {lat:.6f}, {lng:.6f}")
                self.status_label.setStyleSheet("color: #27ae60;")
            else:
                QMessageBox.warning(self, 'Koordinat Tidak Valid', 
                                  'Latitude harus antara -90 sampai 90\nLongitude harus antara -180 sampai 180')
        except ValueError:
            QMessageBox.warning(self, 'Format Tidak Valid', 
                              'Masukkan angka yang valid untuk koordinat')
    
    def _get_current_location(self):
        """Coba dapatkan lokasi saat ini menggunakan browser geolocation."""
        js_code = """
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        let lat = position.coords.latitude;
                        let lng = position.coords.longitude;
                        if (window.pyObj) {
                            window.pyObj.setMarker(lat, lng, "current_location");
                        }
                    },
                    function(error) {
                        alert("Tidak dapat mendapatkan lokasi: " + error.message);
                    }
                );
            } else {
                alert("Browser tidak mendukung geolocation");
            }
        """
        self.web.page().runJavaScript(js_code)
    
    def _on_location_selected(self, selected):
        """Handle ketika lokasi dipilih."""
        self.btn_save.setEnabled(selected)
        if selected and self.current_lat is not None and self.current_lng is not None:
            self.status_label.setText(f"Lokasi dipilih: {self.current_lat:.6f}, {self.current_lng:.6f}")
            self.status_label.setStyleSheet("color: #27ae60;")
        else:
            self.status_label.setText("Belum ada lokasi yang dipilih")
            self.status_label.setStyleSheet("color: #7f8c8d;")
    
    def _get_fallback_html(self):
        """Return fallback HTML untuk map."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Peta Lokasi</title>
            <style>
                body { 
                    font-family: 'Arial', sans-serif; 
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }
                .fallback-container {
                    background: white;
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    text-align: center;
                    max-width: 500px;
                }
                .warning-icon {
                    font-size: 64px;
                    color: #f39c12;
                    margin-bottom: 20px;
                }
                h2 {
                    color: #2c3e50;
                    margin-bottom: 15px;
                }
                p {
                    color: #7f8c8d;
                    line-height: 1.6;
                    margin-bottom: 10px;
                }
                .coordinates-input {
                    margin: 20px 0;
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 8px;
                }
                input {
                    width: 45%;
                    padding: 10px;
                    margin: 5px;
                    border: 2px solid #ddd;
                    border-radius: 4px;
                    font-size: 14px;
                }
                button {
                    background: #3498db;
                    color: white;
                    border: none;
                    padding: 12px 25px;
                    border-radius: 6px;
                    font-size: 14px;
                    cursor: pointer;
                    margin-top: 10px;
                }
                button:hover {
                    background: #2980b9;
                }
            </style>
        </head>
        <body>
            <div class="fallback-container">
                <div class="warning-icon">⚠️</div>
                <h2>Peta Tidak Tersedia</h2>
                <p>File <strong>assets/maps.html</strong> tidak ditemukan.</p>
                <p>Silakan buat file tersebut atau gunakan form input manual di bawah:</p>
                
                <div class="coordinates-input">
                    <p><strong>Masukkan Koordinat Manual:</strong></p>
                    <input type="text" id="latInput" placeholder="Latitude (-90 to 90)">
                    <input type="text" id="lngInput" placeholder="Longitude (-180 to 180)">
                    <br>
                    <button onclick="submitManualCoords()">Gunakan Koordinat Ini</button>
                </div>
                
                <p><small>Pastikan Anda telah membuat file maps.html di folder assets</small></p>
            </div>
            
            <script>
                function submitManualCoords() {
                    let lat = document.getElementById('latInput').value;
                    let lng = document.getElementById('lngInput').value;
                    
                    if (lat && lng && window.pyObj) {
                        window.pyObj.setMarker(parseFloat(lat), parseFloat(lng), "manual_fallback");
                        alert('Koordinat diterima: ' + lat + ', ' + lng);
                    } else {
                        alert('Masukkan koordinat yang valid');
                    }
                }
            </script>
        </body>
        </html>
        """
    
    def save_location(self):
        """Save location ke database."""
        if self.current_lat is None or self.current_lng is None:
            QMessageBox.warning(self, 'Perhatian', 'Silakan pilih lokasi terlebih dahulu.')
            return
        
        try:
            # Konfirmasi sebelum simpan
            reply = QMessageBox.question(
                self, 'Konfirmasi',
                f'Simpan lokasi ini?\n\nLatitude: {self.current_lat:.6f}\nLongitude: {self.current_lng:.6f}',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                save_user_location(self.current_lat, self.current_lng)
                
                # Show success message
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle('Sukses')
                msg.setText('Lokasi berhasil disimpan!')
                msg.setInformativeText(
                    f'Koordinat yang disimpan:\n'
                    f'• Latitude: {self.current_lat:.6f}\n'
                    f'• Longitude: {self.current_lng:.6f}'
                )
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                
                # Update status
                self.status_label.setText("Lokasi berhasil disimpan ke database")
                self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
                
        except Exception as e:
            QMessageBox.critical(
                self, 'Error',
                f'Gagal menyimpan lokasi:\n{str(e)}'
            )
    
    def reset_location(self):
        """Reset lokasi yang dipilih."""
        reply = QMessageBox.question(
            self, 'Konfirmasi Reset',
            'Reset lokasi yang dipilih?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.current_lat = None
            self.current_lng = None
            self.lat_box.clear()
            self.lng_box.clear()
            self.location_selected.emit(False)
            
            # Reset map melalui JavaScript
            if self.bridge and self.bridge.web_page_loaded:
                self.web.page().runJavaScript("if (typeof resetLocation === 'function') { resetLocation(); }")
            
            self.status_label.setText("Lokasi telah direset")
            self.status_label.setStyleSheet("color: #e74c3c;")
    
    def load_last_location(self):
        """Load lokasi terakhir dari database."""
        lat, lng, _ = load_user_location()
        if lat is not None and lng is not None:
            self.current_lat = lat
            self.current_lng = lng
            self.lat_box.setText(f"{lat:.6f}")
            self.lng_box.setText(f"{lng:.6f}")
            self.location_selected.emit(True)
            
            # Update map
            self._send_to_js(lat, lng, "loaded_from_db")