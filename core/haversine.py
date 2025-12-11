"""
Haversine formula untuk menghitung jarak antara dua koordinat geografis.
"""

import math


def haversine_km(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two geographic coordinates using Haversine formula.
    
    Args:
        lat1, lon1: First coordinate (latitude, longitude) in degrees.
        lat2, lon2: Second coordinate (latitude, longitude) in degrees.
        
    Returns:
        Distance in kilometers.
    """
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = (math.sin(dlat / 2)**2 + 
         math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return 6371.0 * c
