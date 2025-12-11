"""
Database management untuk wisata dan user location data.
"""

import sqlite3
from datetime import datetime
import os

import pandas as pd


DB_FILE = 'wisata_data.db'


def init_db(db_path=DB_FILE):
    """Initialize database tables if they don't exist."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Create wisata table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS wisata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL,
            rating REAL,
            rating_count REAL,
            latitude REAL,
            longitude REAL,
            created_at TEXT
        )
    ''')
    
    # Create user_location table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS user_location (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL,
            longitude REAL,
            updated_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()


def save_wisata_rows(rows, db_path=DB_FILE):
    """Save wisata rows to database."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    for r in rows:
        cur.execute('''
            INSERT INTO wisata (name, price, rating, rating_count, latitude, longitude, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            r['name'], 
            float(r['price']), 
            float(r['rating']), 
            float(r['rating_count']), 
            float(r['latitude']), 
            float(r['longitude']), 
            datetime.utcnow().isoformat()
        ))
    
    conn.commit()
    conn.close()


def load_wisata_db(db_path=DB_FILE):
    """Load all wisata from database."""
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query('SELECT * FROM wisata', conn)
    conn.close()
    return df


def reset_wisata_table(db_path=DB_FILE):
    """Reset wisata table (delete all data)."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('DELETE FROM wisata')
    conn.commit()
    conn.close()


def save_user_location(lat, lon, db_path=DB_FILE):
    """Save user location."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    
    try:
        cur.execute('DELETE FROM user_location')
        cur.execute(
            'INSERT INTO user_location (latitude, longitude, updated_at) VALUES (?, ?, ?)',
            (lat, lon, now)
        )
        conn.commit()
        
        # Verify the save
        cur.execute('SELECT COUNT(*) FROM user_location')
        count = cur.fetchone()[0]
        
        return count > 0
    finally:
        conn.close()


def load_user_location(db_path=DB_FILE):
    """Load latest user location."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT latitude, longitude, updated_at FROM user_location ORDER BY id DESC LIMIT 1')
    row = cur.fetchone()
    conn.close()
    
    if row:
        return float(row[0]), float(row[1]), row[2]
    return None, None, None