"""
Results page untuk menampilkan dan export hasil ranking wisata dengan UI yang lebih informatif.
"""

import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QMessageBox, QHBoxLayout, QLabel, QFrame, QGroupBox, QProgressBar,
    QGridLayout, QTabWidget, QTextEdit, QScrollArea, QSizePolicy, QSplitter,
    QToolButton, QMenu, QStyle
)
from PyQt5.QtWidgets import QLineEdit, QComboBox
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QBrush, QIcon, QPixmap
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import seaborn as sns
from datetime import datetime


class ScoreVisualization(QWidget):
    """Widget untuk visualisasi skor TOPSIS"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvas(self.figure)
        self._build()
        
    def _build(self):
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
    def plot_scores(self, df):
        """Plot bar chart untuk skor TOPSIS"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Sort by rank
        df_sorted = df.sort_values('rank')
        
        # Ambil top 15 untuk visualisasi yang lebih baik
        df_plot = df_sorted.head(15)
        
        colors = plt.cm.YlOrRd(np.linspace(0.4, 0.9, len(df_plot)))
        
        bars = ax.barh(range(len(df_plot)), df_plot['topsis_score'], color=colors)
        
        # Tambah nilai di ujung bar
        for i, (bar, score) in enumerate(zip(bars, df_plot['topsis_score'])):
            width = bar.get_width()
            ax.text(width + 0.01, bar.get_y() + bar.get_height()/2,
                   f'{score:.3f}', ha='left', va='center', fontsize=9)
        
        ax.set_yticks(range(len(df_plot)))
        ax.set_yticklabels(df_plot['name'], fontsize=9)
        ax.invert_yaxis()  # Rank tertinggi di atas
        ax.set_xlabel('TOPSIS Score', fontsize=10, fontweight='bold')
        ax.set_title('Top 15 Rekomendasi Wisata', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        
        self.figure.tight_layout()
        self.canvas.draw()


class ResultsPage(QWidget):
    """Halaman hasil ranking dengan visualisasi yang kaya"""
    
    resultsUpdated = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.df_results = None
        self._build()
        
    def _build(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        # Header
        header = QLabel("📊 Hasil Rekomendasi Wisata")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("""
            color: #2c3e50;
            padding: 15px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                      stop:0 #3498db, stop:1 #2ecc71);
            color: white;
            border-radius: 8px;
        """)
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # Stats Panel
        self.stats_panel = self._create_stats_panel()
        main_layout.addWidget(self.stats_panel)
        
        # Tab Widget untuk berbagai view
        self.tab_widget = QTabWidget()
        
        # Tab 1: Tabel Detail
        self.tab_table = QWidget()
        self._build_table_tab()
        self.tab_widget.addTab(self.tab_table, "📋 Tabel Detail")
        
        # Tab 2: Visualisasi
        self.tab_viz = QWidget()
        self._build_viz_tab()
        self.tab_widget.addTab(self.tab_viz, "📈 Visualisasi")
        
        # Tab 3: Ringkasan
        self.tab_summary = QWidget()
        self._build_summary_tab()
        self.tab_widget.addTab(self.tab_summary, "📝 Ringkasan")
        
        main_layout.addWidget(self.tab_widget)
        
        # Action Buttons
        action_panel = self._create_action_panel()
        main_layout.addWidget(action_panel)
        
        self.setLayout(main_layout)
        
    def _create_stats_panel(self):
        """Membuat panel statistik"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        panel.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
            }
            QLabel {
                font-size: 11pt;
            }
        """)
        
        layout = QGridLayout()
        
        # Stat 1: Jumlah Data
        self.stat_count = QLabel("Jumlah Wisata: 0")
        self.stat_count.setStyleSheet("color: #3498db; font-weight: bold;")
        layout.addWidget(self.stat_count, 0, 0)
        
        # Stat 2: Range Harga
        self.stat_price = QLabel("Range Harga: -")
        self.stat_price.setStyleSheet("color: #e74c3c; font-weight: bold;")
        layout.addWidget(self.stat_price, 0, 1)
        
        # Stat 3: Range Rating
        self.stat_rating = QLabel("Range Rating: -")
        self.stat_rating.setStyleSheet("color: #f39c12; font-weight: bold;")
        layout.addWidget(self.stat_rating, 0, 2)
        
        # Stat 4: Rekomendasi Terbaik
        self.stat_best = QLabel("Rekomendasi Terbaik: -")
        self.stat_best.setStyleSheet("color: #2ecc71; font-weight: bold;")
        layout.addWidget(self.stat_best, 0, 3)
        
        panel.setLayout(layout)
        return panel
        
    def _build_table_tab(self):
        """Membangun tab tabel"""
        layout = QVBoxLayout()
        
        # Filter bar
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Cari nama wisata...")
        self.filter_input.textChanged.connect(self.filter_table)
        filter_layout.addWidget(self.filter_input)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Semua", "Top 10", "Top 20", "Rating > 4", "Harga < 100k"])
        self.filter_combo.currentTextChanged.connect(self.filter_table)
        filter_layout.addWidget(self.filter_combo)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Tabel
        self.results_table = QTableWidget()
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f9f9f9;
                gridline-color: #ddd;
                font-size: 10pt;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
        """)
        
        # Enable sorting
        self.results_table.setSortingEnabled(True)
        
        layout.addWidget(self.results_table)
        self.tab_table.setLayout(layout)
        
    def _build_viz_tab(self):
        """Membangun tab visualisasi"""
        layout = QVBoxLayout()
        
        # Visualisasi skor
        self.viz_widget = ScoreVisualization()
        layout.addWidget(self.viz_widget)
        
        # Kontrol visualisasi
        viz_controls = QHBoxLayout()
        viz_controls.addWidget(QLabel("Tampilkan:"))
        
        self.viz_count = QComboBox()
        self.viz_count.addItems(["Top 10", "Top 15", "Top 20", "Semua"])
        self.viz_count.currentTextChanged.connect(self.update_visualization)
        viz_controls.addWidget(self.viz_count)
        
        viz_controls.addStretch()
        layout.addLayout(viz_controls)
        
        self.tab_viz.setLayout(layout)
        
    def _build_summary_tab(self):
        """Membangun tab ringkasan"""
        layout = QVBoxLayout()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        summary_widget = QWidget()
        summary_layout = QVBoxLayout()
        
        # Ringkasan analisis
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: none;
                font-size: 11pt;
                padding: 15px;
            }
        """)
        
        # Breakdown kriteria
        self.criteria_breakdown = QTextEdit()
        self.criteria_breakdown.setReadOnly(True)
        self.criteria_breakdown.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ddd;
                font-size: 10pt;
                padding: 15px;
            }
        """)
        
        summary_layout.addWidget(QLabel("<h3>Ringkasan Analisis</h3>"))
        summary_layout.addWidget(self.summary_text)
        summary_layout.addWidget(QLabel("<h3>Breakdown Kriteria</h3>"))
        summary_layout.addWidget(self.criteria_breakdown)
        
        summary_widget.setLayout(summary_layout)
        scroll.setWidget(summary_widget)
        layout.addWidget(scroll)
        
        self.tab_summary.setLayout(layout)
        
    def _create_action_panel(self):
        """Membuat panel tombol aksi"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        panel.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout()
        
        # Tombol Export dengan menu
        export_menu = QMenu()
        export_csv_action = export_menu.addAction("📄 Export ke CSV")
        export_excel_action = export_menu.addAction("📊 Export ke Excel")
        export_json_action = export_menu.addAction("📋 Export ke JSON")
        
        export_csv_action.triggered.connect(lambda: self.export_results('csv'))
        export_excel_action.triggered.connect(lambda: self.export_results('excel'))
        export_json_action.triggered.connect(lambda: self.export_results('json'))
        
        btn_export = QToolButton()
        btn_export.setText("💾 Export Data")
        btn_export.setPopupMode(QToolButton.MenuButtonPopup)
        btn_export.setMenu(export_menu)
        btn_export.setStyleSheet("""
            QToolButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11pt;
            }
            QToolButton:hover {
                background-color: #2980b9;
            }
            QToolButton::menu-indicator {
                image: none;
            }
        """)
        
        # Tombol Print
        btn_print = QPushButton("🖨️ Cetak Ringkasan")
        btn_print.clicked.connect(self.print_summary)
        btn_print.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        
        # Tombol Reset dengan konfirmasi
        btn_reset = QPushButton("🗑️ Reset Database")
        btn_reset.clicked.connect(self.confirm_reset_db)
        btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        layout.addWidget(btn_export)
        layout.addWidget(btn_print)
        layout.addStretch()
        layout.addWidget(btn_reset)

        # Button to delete the DB file entirely (destructive)
        btn_delete_db = QPushButton("🧹 Hapus File DB")
        btn_delete_db.setToolTip("Hapus file database (menghapus semua data) dan buat ulang database kosong")
        btn_delete_db.setStyleSheet("""
            QPushButton {
                background-color: #d35400;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_delete_db.clicked.connect(self.confirm_delete_db)
        layout.addWidget(btn_delete_db)
        
        panel.setLayout(layout)
        return panel
        
    def show_results(self):
        """Display results in table and update all views."""
        if getattr(self.parent, 'latest_results', None) is None:
            return
            
        self.df_results = self.parent.latest_results.copy()
        
        # Format kolom numerik untuk tampilan yang lebih baik
        self._format_numeric_columns()
        
        # Update stats panel
        self._update_stats_panel()
        
        # Update table
        self._update_table()
        
        # Update visualization
        self.update_visualization()
        
        # Update summary
        self._update_summary()
        
        # Emit signal
        self.resultsUpdated.emit()
        
    def _format_numeric_columns(self):
        """Format kolom numerik untuk menghindari trailing zeros"""
        if self.df_results is None:
            return
            
        # Format kolom harga ke integer (jika tanpa desimal)
        if 'price' in self.df_results.columns:
            # Cek apakah semua harga adalah integer
            if self.df_results['price'].dropna().apply(lambda x: float(x).is_integer()).all():
                self.df_results['price'] = self.df_results['price'].astype(int)
            else:
                self.df_results['price'] = self.df_results['price'].round(2)
                
        # Format rating
        if 'rating' in self.df_results.columns:
            self.df_results['rating'] = self.df_results['rating'].round(2)
            
        # Format rating_count ke integer
        if 'rating_count' in self.df_results.columns:
            self.df_results['rating_count'] = self.df_results['rating_count'].astype(int)
            
        # Format distance_km
        if 'distance_km' in self.df_results.columns:
            self.df_results['distance_km'] = self.df_results['distance_km'].round(2)
            
        # Format topsis_score
        if 'topsis_score' in self.df_results.columns:
            self.df_results['topsis_score'] = self.df_results['topsis_score'].round(4)
            
        # Format koordinat
        if 'latitude' in self.df_results.columns:
            self.df_results['latitude'] = self.df_results['latitude'].round(6)
        if 'longitude' in self.df_results.columns:
            self.df_results['longitude'] = self.df_results['longitude'].round(6)
            
    def _update_stats_panel(self):
        """Update panel statistik"""
        if self.df_results is None or self.df_results.empty:
            return
            
        # Jumlah data
        self.stat_count.setText(f"Jumlah Wisata: {len(self.df_results)}")
        
        # Range harga
        if 'price' in self.df_results.columns:
            min_price = self.df_results['price'].min()
            max_price = self.df_results['price'].max()
            self.stat_price.setText(f"Range Harga: Rp{min_price:,} - Rp{max_price:,}")
            
        # Range rating
        if 'rating' in self.df_results.columns:
            min_rating = self.df_results['rating'].min()
            max_rating = self.df_results['rating'].max()
            self.stat_rating.setText(f"Range Rating: {min_rating:.1f} - {max_rating:.1f}")
            
        # Rekomendasi terbaik
        if 'name' in self.df_results.columns and 'rank' in self.df_results.columns:
            best = self.df_results[self.df_results['rank'] == 1]
            if not best.empty:
                best_name = best.iloc[0]['name']
                if len(best_name) > 30:
                    best_name = best_name[:27] + "..."
                self.stat_best.setText(f"Rekomendasi Terbaik: {best_name}")
                
    def _update_table(self):
        """Update tabel hasil"""
        if self.df_results is None:
            return
            
        df = self.df_results.copy()
        
        # Pilih kolom untuk ditampilkan dengan nama yang lebih user-friendly
        display_cols = {
            'rank': 'Rank',
            'name': 'Nama Wisata',
            'price': 'Harga (Rp)',
            'rating': 'Rating',
            'rating_count': 'Jumlah Ulasan',
            'distance_km': 'Jarak (km)',
            'topsis_score': 'Skor TOPSIS'
        }
        
        # Filter kolom yang ada
        available_cols = {k: v for k, v in display_cols.items() if k in df.columns}
        
        # Tambah kolom latitude/longitude jika diperlukan
        if 'latitude' in df.columns and 'longitude' in df.columns:
            available_cols['latitude'] = 'Latitude'
            available_cols['longitude'] = 'Longitude'
        
        # Setup tabel
        self.results_table.setColumnCount(len(available_cols))
        self.results_table.setRowCount(len(df))
        self.results_table.setHorizontalHeaderLabels(list(available_cols.values()))
        # Save mapping for filtered display
        self.display_cols = available_cols
        
        # Isi data
        for i, (_, row) in enumerate(df.iterrows()):
            for j, (col_key, col_name) in enumerate(available_cols.items()):
                val = row[col_key]
                
                # Format khusus untuk tipe data tertentu
                if col_key == 'price' and isinstance(val, (int, float)):
                    display_val = f"Rp{val:,}"
                elif col_key == 'rating_count' and isinstance(val, (int, float)):
                    display_val = f"{val:,}"
                elif col_key in ['distance_km', 'topsis_score', 'rating'] and isinstance(val, float):
                    if col_key == 'distance_km':
                        display_val = f"{val:.2f} km"
                    elif col_key == 'topsis_score':
                        display_val = f"{val:.4f}"
                    else:
                        display_val = f"{val:.2f}"
                else:
                    display_val = str(val)
                    
                item = QTableWidgetItem(display_val)
                
                # Warna berdasarkan rank
                if col_key == 'rank':
                    if val == 1:
                        item.setBackground(QColor(255, 255, 204))  # Kuning muda
                        item.setForeground(QBrush(QColor(0, 0, 0)))
                    elif val <= 3:
                        item.setBackground(QColor(204, 255, 204))  # Hijau muda
                    elif val <= 10:
                        item.setBackground(QColor(224, 224, 255))  # Biru muda
                        
                self.results_table.setItem(i, j, item)
        
        # Atur resize mode
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Nama wisata lebih lebar
        
        # Sort by rank secara default
        self.results_table.sortItems(0, Qt.AscendingOrder)
        
    def filter_table(self):
        """Filter tabel berdasarkan input"""
        if self.df_results is None:
            return
            
        search_text = self.filter_input.text().lower()
        filter_type = self.filter_combo.currentText()
        
        df = self.df_results.copy()
        
        # Filter berdasarkan teks pencarian
        if search_text:
            df = df[df['name'].str.lower().str.contains(search_text)]
            
        # Filter berdasarkan tipe
        if filter_type == "Top 10":
            df = df.head(10)
        elif filter_type == "Top 20":
            df = df.head(20)
        elif filter_type == "Rating > 4":
            df = df[df['rating'] > 4]
        elif filter_type == "Harga < 100k":
            df = df[df['price'] < 100000]
            
        # Update tabel dengan data yang difilter
        self._display_filtered_table(df)
        
    def _display_filtered_table(self, df):
        """Tampilkan tabel dengan data yang sudah difilter"""
        self.results_table.setRowCount(len(df))
        
        for i, (_, row) in enumerate(df.iterrows()):
            for j in range(self.results_table.columnCount()):
                col_key = list(self.display_cols.keys())[j]
                val = row[col_key]
                
                # Format yang sama seperti sebelumnya
                if col_key == 'price' and isinstance(val, (int, float)):
                    display_val = f"Rp{val:,}"
                elif col_key == 'rating_count' and isinstance(val, (int, float)):
                    display_val = f"{val:,}"
                elif col_key in ['distance_km', 'topsis_score', 'rating'] and isinstance(val, float):
                    if col_key == 'distance_km':
                        display_val = f"{val:.2f} km"
                    elif col_key == 'topsis_score':
                        display_val = f"{val:.4f}"
                    else:
                        display_val = f"{val:.2f}"
                else:
                    display_val = str(val)
                    
                item = QTableWidgetItem(display_val)
                self.results_table.setItem(i, j, item)
                
    def update_visualization(self):
        """Update visualisasi"""
        if self.df_results is None or self.viz_widget is None:
            return
            
        df = self.df_results.copy()
        
        # Filter berdasarkan pilihan
        viz_type = self.viz_count.currentText()
        if viz_type == "Top 10":
            df = df.head(10)
        elif viz_type == "Top 15":
            df = df.head(15)
        elif viz_type == "Top 20":
            df = df.head(20)
        # Untuk "Semua" tidak perlu filter
            
        self.viz_widget.plot_scores(df)
        
    def _update_summary(self):
        """Update ringkasan analisis"""
        if self.df_results is None:
            return
            
        # Buat ringkasan analisis
        summary = self._generate_summary()
        self.summary_text.setHtml(summary)
        
        # Buat breakdown kriteria
        breakdown = self._generate_criteria_breakdown()
        self.criteria_breakdown.setHtml(breakdown)
        
    def _generate_summary(self):
        """Generate HTML summary"""
        df = self.df_results
        
        total_wisata = len(df)
        avg_price = df['price'].mean()
        avg_rating = df['rating'].mean()
        avg_distance = df['distance_km'].mean() if 'distance_km' in df.columns else 0
        
        best = df[df['rank'] == 1].iloc[0] if not df[df['rank'] == 1].empty else None
        
        html = f"""
        <div style='font-family: Arial;'>
            <h3 style='color: #2c3e50;'>Ringkasan Analisis TOPSIS</h3>
            <p><b>Total Wisata Dianalisis:</b> {total_wisata}</p>
            <p><b>Rata-rata Harga:</b> Rp{avg_price:,.0f}</p>
            <p><b>Rata-rata Rating:</b> {avg_rating:.2f}</p>
            <p><b>Rata-rata Jarak:</b> {avg_distance:.2f} km</p>
        """
        
        if best is not None:
            html += f"""
            <hr>
            <h4 style='color: #27ae60;'>🏆 Rekomendasi Terbaik</h4>
            <p><b>Nama:</b> {best['name']}</p>
            <p><b>Skor TOPSIS:</b> {best['topsis_score']:.4f}</p>
            <p><b>Harga:</b> Rp{best['price']:,}</p>
            <p><b>Rating:</b> {best['rating']:.2f}</p>
            <p><b>Jarak:</b> {best.get('distance_km', 0):.2f} km</p>
            """
            
        html += "</div>"
        return html
        
    def _generate_criteria_breakdown(self):
        """Generate HTML untuk breakdown kriteria"""
        # Ambil bobot dari parent jika ada
        weights = getattr(self.parent, 'weights', None)
        
        if weights is None:
            weights = [0.25, 0.25, 0.25, 0.25]  # Default
        
        criteria = ['Harga', 'Rating', 'Jumlah Ulasan', 'Jarak']
        
        html = """
        <div style='font-family: Arial;'>
            <table border='1' style='border-collapse: collapse; width: 100%;'>
                <tr style='background-color: #2c3e50; color: white;'>
                    <th style='padding: 8px;'>Kriteria</th>
                    <th style='padding: 8px;'>Bobot</th>
                    <th style='padding: 8px;'>Persentase</th>
                </tr>
        """
        
        for i, (crit, w) in enumerate(zip(criteria, weights)):
            percentage = w * 100
            color = "#e74c3c" if crit == "Harga" else (
                    "#2ecc71" if crit == "Rating" else (
                    "#3498db" if crit == "Jumlah Ulasan" else "#f39c12"))
            
            html += f"""
                <tr>
                    <td style='padding: 8px;'><b>{crit}</b></td>
                    <td style='padding: 8px;'>{w:.4f}</td>
                    <td style='padding: 8px;'>
                        <div style='background-color: {color}; width: {percentage}%; 
                             height: 20px; border-radius: 3px;'></div>
                        {percentage:.1f}%
                    </td>
                </tr>
            """
            
        html += "</table></div>"
        return html
        
    def export_results(self, format_type='csv'):
        """Export results to different formats."""
        if self.df_results is None:
            QMessageBox.information(self, 'Info', 'Belum ada hasil untuk diexport.')
            return
            
        # Pilih filter berdasarkan format
        filters = {
            'csv': 'CSV Files (*.csv)',
            'excel': 'Excel Files (*.xlsx)',
            'json': 'JSON Files (*.json)'
        }
        
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            f'Save as {format_type.upper()}',
            filter=filters.get(format_type, 'All Files (*.*)')
        )
        
        if not filename:
            return
            
        try:
            if format_type == 'csv':
                self.df_results.to_csv(filename, index=False)
            elif format_type == 'excel':
                self.df_results.to_excel(filename, index=False, engine='openpyxl')
            elif format_type == 'json':
                self.df_results.to_json(filename, orient='records', indent=2)
                
            QMessageBox.information(
                self, 
                'Sukses', 
                f'Data berhasil diexport ke: {filename}'
            )
        except Exception as e:
            QMessageBox.critical(
                self, 
                'Error', 
                f'Gagal mengexport data: {str(e)}'
            )
            
    def print_summary(self):
        """Print atau save summary sebagai PDF/HTML"""
        if self.df_results is None:
            return
            
        # Buat dialog untuk memilih format
        from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
        
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec_() == QPrintDialog.Accepted:
            # Cetak ringkasan
            # Implementasi printing bisa ditambahkan di sini
            QMessageBox.information(self, "Info", "Fitur printing dalam pengembangan.")
            
    def confirm_reset_db(self):
        """Konfirmasi reset database"""
        reply = QMessageBox.question(
            self, 'Konfirmasi Reset Database',
            '<b>⚠️ PERINGATAN: </b>Anda akan menghapus SEMUA data wisata dari database.<br><br>'
            'Apakah Anda yakin ingin melanjutkan?<br><br>'
            '<i>Data yang dihapus tidak dapat dikembalikan.</i>',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.reset_db()

    def confirm_delete_db(self):
        """Ask confirmation before deleting the DB file."""
        reply = QMessageBox.question(
            self, 'Konfirmasi Hapus Database',
            '<b>⚠️ PERINGATAN: </b>Anda akan <u>menghapus file database</u> secara permanen.'
            '<br><br>Semua data wisata akan hilang dan tidak dapat dikembalikan.'
            '<br><br>Apakah Anda yakin ingin melanjutkan?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.delete_db_file()

    def delete_db_file(self):
        """Delete the database file and recreate an empty DB schema."""
        try:
            from core.database import delete_database_file, init_db

            deleted = delete_database_file()
            # Recreate empty DB so app continues to work
            init_db()

            if deleted:
                # Clear UI similar to reset
                self.df_results = None
                self.results_table.clear()
                self.results_table.setRowCount(0)
                self.results_table.setColumnCount(0)

                self.stat_count.setText("Jumlah Wisata: 0")
                self.stat_price.setText("Range Harga: -")
                self.stat_rating.setText("Range Rating: -")
                self.stat_best.setText("Rekomendasi Terbaik: -")

                self.summary_text.clear()
                self.criteria_breakdown.clear()

                QMessageBox.information(self, 'Sukses', 'File database dihapus dan database kosong dibuat ulang.')
            else:
                QMessageBox.information(self, 'Info', 'File database tidak ditemukan atau gagal dihapus.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Gagal menghapus database: {e}')
            
    def reset_db(self):
        """Reset database dengan feedback visual"""
        try:
            from core.database import reset_wisata_table
            reset_wisata_table()
            
            # Clear semua tampilan
            self.df_results = None
            self.results_table.clear()
            self.results_table.setRowCount(0)
            self.results_table.setColumnCount(0)
            
            # Update stats panel
            self.stat_count.setText("Jumlah Wisata: 0")
            self.stat_price.setText("Range Harga: -")
            self.stat_rating.setText("Range Rating: -")
            self.stat_best.setText("Rekomendasi Terbaik: -")
            
            # Clear summary
            self.summary_text.clear()
            self.criteria_breakdown.clear()
            
            # Show success message
            QMessageBox.information(
                self, 
                'Sukses', 
                '✅ Database berhasil direset. Semua data wisata telah dihapus.'
            )
        except Exception as e:
            QMessageBox.critical(
                self, 
                'Error', 
                f'Gagal mereset database: {str(e)}'
            )