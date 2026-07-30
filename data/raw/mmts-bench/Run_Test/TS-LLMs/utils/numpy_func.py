import numpy as np
import ast

def adopt_ts_array(arr: list):
    # ---------- 1D ----------
    if isinstance(arr[0], (int, float)): 
        ts = np.array(arr, dtype=float)
        length = len(ts)
        
        if length < 64:
            ts = np.pad(ts, (0, 64 - length), mode="constant")
        elif length > 1024:
            ts = ts[:1024]
        
        return ts
    # ---------- 2D ----------
    elif isinstance(arr[0], (list, np.ndarray)): 
        lengths = [len(row) for row in arr]
        max_len = max(lengths)
        
        # Padding
        padded = np.array([np.pad(row, (0, max_len - len(row)), mode="constant") 
                           for row in arr], dtype=float)
        
        # Len limit
        if max_len < 64:
            padded = np.pad(padded, ((0, 0), (0, 64 - max_len)), mode="constant")
        elif max_len > 1024:
            padded = padded[:, :1024]
        
        return padded
    else:
        raise ValueError("The input must be 1D or 2D list/array.")


def split_ts_array(arr: np.ndarray):
    arr = np.array(arr)  
    if arr.ndim == 1:
        return [arr]   
    elif arr.ndim == 2:
        return [arr[i] for i in range(arr.shape[0])] 
    else:
        raise ValueError(f"Unsupported array shape: {arr.shape}")
