"""Main window dengan sidebar navigation dan stacked pages."""

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import (
    QListWidget, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QMessageBox
)

from gui.upload_page import UploadPage
from gui.form_page import FormPage
from gui.maps_page import MapsPage
from gui.weights_page import WeightsPage
from gui.process_page import ProcessPage
from gui.results_page import ResultsPage
from core.database import init_db


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AHP → TOPSIS - Destinasi Wisata")
        self.resize(1200, 720)

        init_db()

        # ======================================================
        # MAIN ROOT LAYOUT
        # ======================================================
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ======================================================
        # TOPBAR / HEADER
        # ======================================================
        topbar = QWidget()
        topbar.setStyleSheet("""
            background-color: #111827;
            border: none;
        """)
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(12, 8, 12, 8)

        # Title
        title = QLabel("AHP → TOPSIS - Destinasi Wisata")
        title.setStyleSheet("""
            color: white;
            font-size: 20px;
            font-weight: bold;
        """)
        title.setAlignment(QtCore.Qt.AlignVCenter)

        topbar_layout.addWidget(title)

        # Spacer
        topbar_layout.addStretch()

        # Reload Button
        btn_reload = QPushButton("Reload Data")
        btn_reload.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btn_reload.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
        """)
        btn_reload.clicked.connect(self.reload_data)
        topbar_layout.addWidget(btn_reload)

        # Download Template Button
        btn_template = QPushButton("Download Template")
        btn_template.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btn_template.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        btn_template.clicked.connect(self.download_template)
        topbar_layout.addWidget(btn_template)

        root_layout.addWidget(topbar)

        # ======================================================
        # MAIN CONTENT AREA (SIDEBAR + PAGES)
        # ======================================================
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # --------------------------
        # SIDEBAR
        # --------------------------
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setSpacing(8)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #1F2937;
                color: white;
                padding: 10px;
                border: none;
                font-size: 16px;
            }
            QListWidget::item {
                padding: 12px;
                margin-top: 4px;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background-color: #3B82F6;
            }
            QListWidget::item:hover {
                background-color: #374151;
            }
        """)

        self.sidebar.addItem("Data Wisata")
        self.sidebar.addItem("Peta Lokasi")
        self.sidebar.addItem("Tambah Manual")
        self.sidebar.addItem("Bobot (AHP Simple)")
        self.sidebar.addItem("Proses & TOPSIS")
        self.sidebar.addItem("Hasil")

        content_layout.addWidget(self.sidebar)

        # --------------------------
        # PAGE STACK
        # --------------------------
        self.pages = QtWidgets.QStackedWidget()
        content_layout.addWidget(self.pages, stretch=1)

        # Register Pages
        self.upload_page = UploadPage(self)
        self.maps_page = MapsPage(self)
        self.form_page = FormPage(self)
        self.weights_page = WeightsPage(self)
        self.process_page = ProcessPage(self)
        self.results_page = ResultsPage(self)

        self.pages.addWidget(self.upload_page)   # index 0
        self.pages.addWidget(self.maps_page)     # index 1
        self.pages.addWidget(self.form_page)     # index 2
        self.pages.addWidget(self.weights_page)  # index 3
        self.pages.addWidget(self.process_page)  # index 4
        self.pages.addWidget(self.results_page)  # index 5

        # Bind Sidebar → Page Switch
        self.sidebar.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.sidebar.setCurrentRow(0)

        root_layout.addWidget(content)

        # Set final widget
        self.setCentralWidget(root)

    # ==========================================================
    # TOPBAR BUTTON HANDLERS
    # ==========================================================
    def reload_data(self):
        """Reload data dari database melalui UploadPage."""
        try:
            if hasattr(self.upload_page, 'refresh_from_db'):
                self.upload_page.refresh_from_db()
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Gagal reload data:\n{e}')

    def download_template(self):
        """Download template Excel menggunakan fungsi UploadPage."""
        try:
            if hasattr(self.upload_page, 'download_template'):
                self.upload_page.download_template()
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Gagal unduh template:\n{e}')
