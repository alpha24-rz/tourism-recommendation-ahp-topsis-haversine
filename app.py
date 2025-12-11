"""
AHP-TOPSIS Sistem Pengambilan Keputusan Destinasi Wisata
Main entry point untuk aplikasi.
"""

import sys
from PyQt5.QtWidgets import QApplication

from gui.main_window import MainWindow


def main():
    """Initialize and run the application."""
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()

    # Show results page when results tab is selected
    def on_tab_change(idx):
        try:
            # Index 5 adalah halaman "Hasil"
            if idx == 5:
                win.results_page.show_results()
        except Exception:
            pass

    win.sidebar.currentRowChanged.connect(on_tab_change)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
