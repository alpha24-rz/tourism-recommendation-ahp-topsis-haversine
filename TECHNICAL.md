# Dokumentasi Teknis

## Arsitektur Aplikasi

### Layering

```
┌─────────────────────────────────────┐
│   GUI Layer (PyQt5)                 │
│   ├── MainWindow                    │
│   ├── UploadPage, FormPage          │
│   ├── WeightsPage, ProcessPage      │
│   └── ResultsPage                   │
└────────────┬────────────────────────┘
             │
┌────────────┴────────────────────────┐
│   Core Logic Layer                  │
│   ├── database (CRUD operations)    │
│   ├── ahp (weight normalization)    │
│   ├── topsis (ranking algorithm)    │
│   └── haversine (distance calc)     │
└────────────┬────────────────────────┘
             │
┌────────────┴────────────────────────┐
│   Data Layer (SQLite)               │
│   ├── wisata table                  │
│   └── user_location table           │
└─────────────────────────────────────┘
```

## Alur Aplikasi

### 1. Upload & Input Data
- User upload CSV/Excel atau input manual
- Data di-validate dan disimpan ke database

### 2. Tentukan Bobot Preferensi
- User masukkan bobot untuk 4 kriteria (0-100)
- Sistem otomatis normalisasi (sum = 1)

### 3. Proses TOPSIS
1. Load data wisata dari database
2. Hitung jarak menggunakan Haversine formula
3. Convert semua nilai ke numeric
4. Jalankan TOPSIS dengan:
   - Normalisasi vektor
   - Weighted normalization
   - Calculate ideal best/worst solutions
   - Calculate distances dan scores
5. Rank berdasarkan skor

### 4. Export Hasil
- Tampilkan tabel hasil ranking
- Export ke CSV jika diperlukan

## Implementasi TOPSIS

```python
Input: 
  - Decision matrix (m x n)
  - Weights vector (n)
  - Criteria types (benefit/cost)

Process:
  1. Vector Normalization: R = X / sqrt(sum(X²))
  2. Weighted Normalization: V = R * W
  3. Ideal Solution: Ideal_best, Ideal_worst
  4. Distance: D+ = sqrt(sum((V - Ideal_best)²))
              D- = sqrt(sum((V - Ideal_worst)²))
  5. Score: S = D- / (D+ + D-)
  
Output: 
  - TOPSIS score (0-1) per alternatif
  - Ranking based on score (descending)
```

## Database Operations

### Create
```python
save_wisata_rows([{
    'name': 'Pantai Senggigi',
    'price': 50000,
    'rating': 4.5,
    'rating_count': 1200,
    'latitude': -8.7,
    'longitude': 116.3
}])
```

### Read
```python
df = load_wisata_db()  # Get all wisata
lat, lon = load_user_location()  # Get user location
```

### Delete
```python
reset_wisata_table()  # Clear all wisata
```

## File Handling

### CSV Upload
- Columns required: name, price, rating, rating_count, latitude, longitude
- Data type conversion otomatis (numeric fields)
- Validation dilakukan sebelum insert

### Excel Upload
- Supported: .xls, .xlsx
- Sama dengan CSV handling

### CSV Export
- Export hasil ranking dengan kolom: 
  name, price, rating, rating_count, latitude, longitude, distance_km, topsis_score, rank
- Tanpa index column

## Error Handling

| Error | Handling |
|-------|----------|
| Empty file | Message dialog + return |
| Invalid numeric | Try-except + validation message |
| Missing location | Check before TOPSIS + message |
| Empty database | Message dialog |
| Database error | Sqlite3 exception handling |

## Performance Considerations

1. **Data Loading**: 
   - Load semua wisata saat proses
   - Gunakan pandas untuk operasi bulk

2. **Calculation**:
   - Gunakan numpy untuk matrix operations
   - Vectorized operations lebih cepat dari loop

3. **UI Responsiveness**:
   - Long operations bisa pakai threading jika data besar
   - Current implementation ok untuk dataset kecil-medium

## Testing Strategy

### Unit Tests (belum implemented)
```
test_core/
  ├── test_ahp.py
  ├── test_topsis.py
  ├── test_haversine.py
  └── test_database.py
```

### Manual Testing Checklist
- [ ] Upload CSV dengan data valid
- [ ] Upload CSV dengan format invalid
- [ ] Add manual data dengan input valid/invalid
- [ ] Ubah bobot dan lihat normalisasi
- [ ] Jalankan TOPSIS tanpa location
- [ ] Jalankan TOPSIS dengan data lengkap
- [ ] Export ke CSV
- [ ] Reset database

## Peningkatan Masa Depan

1. **Features**:
   - Add user location picker (map)
   - Multiple TOPSIS results compare
   - Save bobot preferences
   - Edit/delete wisata

2. **Technical**:
   - Add unit tests & CI/CD
   - Threading untuk long operations
   - Logging system
   - Config file management
   - Database migration tools

3. **UI/UX**:
   - Progress bar untuk long operations
   - Better error messages
   - Input validation feedback
   - Dark theme option
