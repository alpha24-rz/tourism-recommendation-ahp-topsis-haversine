# Quick Start Guide

## Instalasi dan Menjalankan Aplikasi

### 1. Setup Environment

```bash
# Masuk ke folder project
cd System_pengambilan_keputusan

# Create virtual environment (jika belum ada)
python3 -m venv env

# Activate virtual environment
source env/bin/activate  # Linux/Mac
# atau
env\Scripts\activate  # Windows
```

### 2. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### 3. Run Application

```bash
python app.py
```

## Penggunaan Aplikasi

### Tab 1: Data Wisata
- **Upload CSV**: Upload file CSV dengan kolom: name, price, rating, rating_count, latitude, longitude
- **Upload Excel**: Upload file Excel (.xls/.xlsx) dengan format yang sama
- **Simpan ke DB**: Save data yang sudah di-load ke database
- **Muat dari DB**: Load data yang sudah ada di database

**Format CSV/Excel:**
```
name,price,rating,rating_count,latitude,longitude
Pantai Senggigi,50000,4.5,1200,-8.7,116.3
Bukit Benten,30000,4.2,800,-8.65,116.25
```

### Tab 2: Tambah Manual
- Input nama dan data wisata secara manual
- Semua field harus diisi
- Numeric fields harus berupa angka valid
- Click "Simpan ke DB" untuk menyimpan

### Tab 3: Bobot (AHP Simple)
- Set preferensi untuk 4 kriteria (0-100):
  - **Harga**: Lower is better (cost criteria)
  - **Rating**: Higher is better (benefit criteria)
  - **Rating Count**: Higher is better (benefit criteria)
  - **Jarak**: Lower is better (cost criteria)
- Default: 25 untuk setiap kriteria (equal weight)
- Click "Tampilkan Bobot Normalisasi" untuk lihat hasil normalisasi

### Tab 4: Proses & TOPSIS
- **Syarat sebelum proses:**
  1. Ada data wisata di database
  2. User location sudah di-set (di halaman ini)
  
- Click "Hitung Jarak & Jalankan TOPSIS" untuk:
  1. Calculate jarak antara user dan setiap wisata
  2. Run TOPSIS algorithm
  3. Generate ranking berdasarkan skor

- Hasil akan otomatis di-display di tab Results

### Tab 5: Hasil
- **Lihat Ranking**: Tabel menampilkan ranking wisata berdasarkan TOPSIS score
- **Export CSV**: Simpan hasil ke file CSV
- **Reset DB**: Hapus semua data wisata dari database (butuh konfirmasi)

## Kriteria & Scoring

### Kriteria Keputusan
| Kriteria | Tipe | Range | Deskripsi |
|----------|------|-------|-----------|
| Price | Cost | Rp | Harga tiket/masuk (semakin murah semakin baik) |
| Rating | Benefit | 1-5 | Rating dari user (semakin tinggi semakin baik) |
| Rating Count | Benefit | Integer | Jumlah rating (semakin banyak semakin baik) |
| Distance | Cost | km | Jarak dari user (semakin dekat semakin baik) |

### TOPSIS Score
- Range: 0 sampai 1
- Semakin tinggi = semakin baik
- Ranking: score tertinggi = rank 1

## Contoh Workflow

```
1. Siapkan file CSV dengan data wisata
   ↓
2. Tab "Data Wisata" → Upload CSV → Simpan ke DB
   ↓
3. Tab "Bobot" → Set preferensi bobot
   ↓
4. Tab "Proses" → Input lokasi user → Hitung Jarak & TOPSIS
   ↓
5. Tab "Hasil" → Lihat ranking → Export CSV (opsional)
```

## Tips & Tricks

1. **Bobot Optimal**: Gunakan bobot yang mencerminkan prioritas Anda
2. **Data Quality**: Pastikan data wisata lengkap dan valid
3. **Lokasi User**: Inputkan koordinat yang akurat untuk hasil jarak yang tepat
4. **Normalisasi**: Bobot otomatis dinormalisasi meskipun tidak sum=100
5. **Export**: Selalu export hasil sebelum reset database

## Troubleshooting

### Error: "Tidak ada data wisata"
- Pastikan sudah upload data atau load dari DB terlebih dahulu

### Error: "Lokasi user belum disetel"
- Inputkan latitude dan longitude user sebelum menjalankan TOPSIS

### Error: "Validasi gagal"
- Pastikan semua numeric fields berisi angka yang valid (bukan teks)

### Error: Module not found
- Pastikan virtual environment aktif
- Jalankan `pip install -r requirements.txt` untuk install dependencies

## File Database

- **Lokasi**: `wisata_data.db` (di folder project)
- **Tipe**: SQLite3
- **Auto-create**: Database otomatis dibuat saat pertama kali aplikasi dijalankan

## Keyboard Shortcuts

Tidak ada shortcut khusus. Gunakan mouse untuk navigasi.

## Support & Documentation

- **README.md**: Overview dan fitur project
- **STRUCTURE.md**: Arsitektur dan struktur code
- **TECHNICAL.md**: Dokumentasi teknis dan algoritma
- **PROJECT_STATUS.txt**: Status dan statistics project

---

**Version**: 1.0  
**Last Updated**: December 2025  
**Status**: Ready for Use ✓
