"""
TOPSIS (Technique for Order Preference by Similarity to Ideal Solution) implementation.
"""

import numpy as np


def topsis_rank(df, weights, criteria_types):
    """
    Calculate TOPSIS scores and ranking.
    
    Args:
        df: DataFrame with decision criteria columns.
        weights: Array of normalized weights.
        criteria_types: List of 'benefit' or 'cost' for each criteria.
        
    Returns:
        Array of TOPSIS scores.
    """
    X = df.values.astype(float)
    
    # Normalization
    denom = np.sqrt((X**2).sum(axis=0))
    denom[denom == 0] = 1e-12
    R = X / denom
    
    # Weighted normalization
    V = R * np.array(weights)
    
    # Define ideal best and worst solutions
    ideal_best = np.zeros(V.shape[1])
    ideal_worst = np.zeros(V.shape[1])
    
    for j, t in enumerate(criteria_types):
        if t == 'benefit':
            ideal_best[j] = V[:, j].max()
            ideal_worst[j] = V[:, j].min()
        else:
            ideal_best[j] = V[:, j].min()
            ideal_worst[j] = V[:, j].max()
    
    # Calculate distance to ideal solutions
    D_plus = np.sqrt(((V - ideal_best)**2).sum(axis=1))
    D_minus = np.sqrt(((V - ideal_worst)**2).sum(axis=1))
    
    # Calculate TOPSIS score
    score = D_minus / (D_plus + D_minus)
    
    return score
