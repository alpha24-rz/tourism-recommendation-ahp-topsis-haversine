"""Template generator untuk Excel."""

import pandas as pd


def generate_excel_template(path):
    """Generate template Excel dengan kolom yang dibutuhkan.

    Args:
        path: Path untuk menyimpan file Excel.
    """
    columns = ['name', 'price', 'rating', 'rating_count', 'latitude', 'longitude']
    
    # Create sample data
    sample_data = {
        'name': ['Pantai Senggigi', 'Bukit Benten', 'Taman Nusantara'],
        'price': [50000, 30000, 25000],
        'rating': [4.5, 4.2, 4.0],
        'rating_count': [1200, 800, 600],
        'latitude': [-8.7, -8.65, -8.6],
        'longitude': [116.3, 116.25, 116.2]
    }
    
    df = pd.DataFrame(sample_data)
    df.to_excel(path, index=False, sheet_name='Wisata')
    
    print(f"Template saved to {path}")

