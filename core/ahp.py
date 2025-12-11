"""
Analytical Hierarchy Process (AHP) - Weight normalization.
"""

import numpy as np


def normalize_weights(weights):
    """
    Normalize weights so they sum to 1.
    
    Args:
        weights: List or array of weights.
        
    Returns:
        Normalized weights array.
    """
    w = np.array(weights, dtype=float)
    s = w.sum()
    
    if s == 0:
        return np.ones_like(w) / len(w)
    
    return w / s
