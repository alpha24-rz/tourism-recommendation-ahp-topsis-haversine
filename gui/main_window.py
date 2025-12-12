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
        self.setWindowTitle("AHP 1 TOPSIS - Destinasi Wisata")

        # Determine a responsive default window size based on the primary
        # screen available geometry so the app looks good on common PC/laptop
        # resolutions (desktop and laptop). Use a percentage of available
        # screen area but cap to reasonable maximums.
        try:
            screen = QtWidgets.QApplication.primaryScreen()
            if screen is not None:
                geom = screen.availableGeometry()
                sw, sh = geom.width(), geom.height()
            else:
                sw, sh = 1366, 768
        except Exception:
            sw, sh = 1366, 768

        # Choose window size: up to 90% of screen width, 85% height, capped
        win_w = int(min(1366, max(900, sw * 0.9)))
        win_h = int(min(900, max(650, sh * 0.75)))
        self.resize(win_w, win_h)
        self.setMinimumSize(800, 600)

        # Compute sidebar width proportionally (keeps usable layout on narrow screens)
        # Range: 180-280px based on screen width percentage
        self._sidebar_width = int(max(180, min(280, sw * 0.15)))

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
        topbar_layout.setContentsMargins(8, 8, 8, 8)

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
        # apply responsive sidebar width computed from screen geometry
        self.sidebar.setFixedWidth(self._sidebar_width)
        self.sidebar.setSpacing(2)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #1F2937;
                color: white;
                padding: 10px;
                border: none;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 10px;
                margin: 2px 0;
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
        # ensure pages have a reasonable minimum width on narrow screens
        self.pages.setMinimumWidth(int(max(480, win_w - self._sidebar_width - 80)))
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
