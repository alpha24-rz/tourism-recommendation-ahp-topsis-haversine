# AHP-TOPSIS Sistem Pengambilan Keputusan Destinasi Wisata

Aplikasi PyQt5 untuk membantu pengambilan keputusan pemilihan destinasi wisata menggunakan metode AHP (Analytical Hierarchy Process) dan TOPSIS (Technique for Order Preference by Similarity to Ideal Solution).

## Fitur

- **Upload Data**: Upload data wisata dari CSV/Excel
- **Tambah Manual**: Tambah data wisata secara manual melalui form
- **Bobot AHP**: Tentukan preferensi bobot untuk setiap kriteria
- **TOPSIS Ranking**: Hitung jarak dan ranking wisata berdasarkan kriteria
- **Export Hasil**: Export hasil ranking ke CSV
- **Reset Database**: Hapus semua data dan mulai dari awal

## Struktur Proyek

```
System_pengambilan_keputusan/
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── ahp.py              # AHP weight normalization
│   │   ├── database.py         # Database management
│   │   ├── haversine.py        # Distance calculation
│   │   └── topsis.py           # TOPSIS ranking
│   └── gui/
│       ├── __init__.py
│       ├── main_window.py      # Main window dengan tabs
│       ├── upload_page.py      # Upload data page
│       ├── form_page.py        # Manual form entry
│       ├── weights_page.py     # Weight preferences
│       ├── process_page.py     # TOPSIS calculation
│       └── results_page.py     # Results display
├── app.py                      # Entry point
├── requirements.txt            # Dependencies
└── wisata_data.db             # SQLite database (generated)
```

## Instalasi

### 1. Buat Virtual Environment

```bash
python3 -m venv env
source env/bin/activate  # Linux/Mac
# atau
env\Scripts\activate  # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## Penggunaan

### Menjalankan Aplikasi

```bash
python app.py
```

### Tab Utama

1. **Data Wisata**: Upload CSV/Excel dengan kolom: name, price, rating, rating_count, latitude, longitude
2. **Tambah Manual**: Input data wisata secara manual
3. **Bobot (AHP)**: Tentukan preferensi bobot (0-100) untuk setiap kriteria
4. **Proses & TOPSIS**: Jalankan perhitungan jarak dan TOPSIS ranking
5. **Hasil**: Lihat hasil ranking dan export ke CSV

## Dependencies

- PyQt5 (GUI framework)
- pandas (Data manipulation)
- numpy (Numerical computation)
- openpyxl (Excel support)

## Catatan Teknis

### Database Schema

**wisata table:**
- id (INTEGER PRIMARY KEY)
- name (TEXT)
- price (REAL)
- rating (REAL)
- rating_count (REAL)
- latitude (REAL)
- longitude (REAL)
- created_at (TEXT)

**user_location table:**
- id (INTEGER PRIMARY KEY)
- latitude (REAL)
- longitude (REAL)
- updated_at (TEXT)

### Algoritma

- **AHP**: Normalisasi bobot sehingga total = 1
- **Haversine**: Menghitung jarak geografis antar koordinat
- **TOPSIS**: Multi-criteria decision making dengan normalisasi vektor

## License

Bebas digunakan untuk keperluan akademis dan personal.
