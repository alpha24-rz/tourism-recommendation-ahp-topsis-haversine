# Project Structure Guide

## Directory Layout

```
System_pengambilan_keputusan/
│
├── app.py                          # Entry point - main application
├── requirements.txt                # Python dependencies
├── setup.cfg                       # Project configuration
├── .gitignore                      # Git ignore rules
│
├── README.md                       # Project documentation
├── TECHNICAL.md                    # Technical details
│
├── core/                           # Core business logic
│   ├── __init__.py
│   ├── ahp.py                      # AHP weight normalization
│   ├── database.py                 # SQLite database operations
│   ├── haversine.py                # Geographic distance calculation
│   └── topsis.py                   # TOPSIS ranking algorithm
│
├── gui/                            # PyQt5 GUI components
│   ├── __init__.py
│   ├── main_window.py              # Main window with tabs
│   ├── upload_page.py              # CSV/Excel data upload
│   ├── form_page.py                # Manual data entry form
│   ├── weights_page.py             # Weight preference setting
│   ├── process_page.py             # TOPSIS calculation & display
│   └── results_page.py             # Results ranking & export
│
└── env/                            # Python virtual environment (auto-created)
```

## Module Descriptions

### Core Modules

#### `core/database.py`
- **Purpose**: Database operations untuk wisata dan user location
- **Key Functions**:
  - `init_db()` - Initialize SQLite database
  - `save_wisata_rows(rows)` - Insert wisata data
  - `load_wisata_db()` - Load all wisata
  - `reset_wisata_table()` - Clear wisata data
  - `save_user_location(lat, lon)` - Save user coordinates
  - `load_user_location()` - Get user coordinates

#### `core/ahp.py`
- **Purpose**: Analytical Hierarchy Process weight normalization
- **Key Function**:
  - `normalize_weights(weights)` - Normalize weights to sum=1

#### `core/topsis.py`
- **Purpose**: TOPSIS multi-criteria decision making
- **Key Function**:
  - `topsis_rank(df, weights, criteria_types)` - Calculate TOPSIS scores

#### `core/haversine.py`
- **Purpose**: Geographic distance calculation
- **Key Function**:
  - `haversine_km(lat1, lon1, lat2, lon2)` - Calculate distance in kilometers

### GUI Modules

#### `gui/main_window.py`
- Main application window
- Contains 5 tabs untuk different functions
- Manages overall application state

#### `gui/upload_page.py`
- CSV/Excel file upload
- Data validation
- Display dalam table widget
- Save to database

#### `gui/form_page.py`
- Manual data entry form
- Input fields untuk 6 kriteria
- Form validation
- Direct save to database

#### `gui/weights_page.py`
- Weight preference setting (0-100)
- Automatic normalization display
- Bobot untuk 4 kriteria: price, rating, rating_count, distance

#### `gui/process_page.py`
- Koordinasi perhitungan distance dan TOPSIS
- Load data dari database
- Hitung jarak dengan haversine
- Run TOPSIS algorithm
- Display hasil dalam table

#### `gui/results_page.py`
- Display ranking results
- Export ke CSV
- Reset database option
- Show TOPSIS scores dan ranking

## Database Schema

### wisata table
```sql
CREATE TABLE wisata (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL,
    rating REAL,
    rating_count REAL,
    latitude REAL,
    longitude REAL,
    created_at TEXT
)
```

### user_location table
```sql
CREATE TABLE user_location (
    id INTEGER PRIMARY KEY,
    latitude REAL,
    longitude REAL,
    updated_at TEXT
)
```

## Data Flow

```
1. Data Input
   ↓
   ├── Upload CSV/Excel (UploadPage)
   └── Manual Form (FormPage)
   ↓
2. Data Storage (Database)
   ↓
3. Set Preferences (WeightsPage)
   ↓
4. Process (ProcessPage)
   ├── Load data
   ├── Calculate distance (Haversine)
   ├── Normalize weights (AHP)
   └── Run TOPSIS
   ↓
5. Results Display (ResultsPage)
   ├── Table view
   └── CSV export
```

## File Sizes

Core modules: ~80-100 lines each
GUI modules: ~90-150 lines each
Total code: ~1200 lines

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| PyQt5 | ≥5.15.0 | GUI framework |
| pandas | ≥1.3.0 | Data manipulation |
| numpy | ≥1.21.0 | Numerical computation |
| openpyxl | ≥3.6.0 | Excel support |

## Code Quality

- ✓ All syntax valid (Python 3.12)
- ✓ Proper imports dan organization
- ✓ Docstrings untuk semua functions
- ✓ Consistent naming conventions
- ✓ Error handling dengan try-except
- ✓ Clear separation of concerns
