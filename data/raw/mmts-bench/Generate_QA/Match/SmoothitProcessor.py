import pandas as pd
import numpy as np
import json
import ast

def moving_average_smooth(ts_data, window_size=3, decimal_places=None):
    if len(ts_data) < 2:
        return ts_data
    
    smoothed = []
    for i in range(len(ts_data)):
        start_idx = max(0, i - window_size // 2)
        end_idx = min(len(ts_data), i + window_size // 2 + 1)
        avg_value = np.mean(ts_data[start_idx:end_idx])
        
        if decimal_places is not None:
            avg_value = round(avg_value, decimal_places)
        
        smoothed.append(avg_value)
    
    return smoothed

def parse_value_column(value_str):
    try:
        if isinstance(value_str, str):
            try:
                return json.loads(value_str)
            except:
                return ast.literal_eval(value_str)
        else:
            return value_str
    except:
        print(f"Parsing failed: {value_str}")
        return None

def smooth_csv_data(input_file, output_file, window_size=3, decimal_places=2):
    df = pd.read_csv(input_file)
    print(f"Data loaded: {len(df)} rows")
    print(f"Smoothing parameters: window_size={window_size}, decimal_places={decimal_places}")
    
    processed_values = []
    
    for idx, value in enumerate(df['value']):
        if idx % 100 == 0:
            print(f"Processing progress: {idx}/{len(df)}")
        
        value_data = parse_value_column(value)
        
        if value_data is None or not isinstance(value_data, list):
            processed_values.append(value)
            continue
        
        smoothed_list = []
        for i, ts in enumerate(value_data):
            if i == 0:
                smoothed_list.append(ts)
            else:
                if isinstance(ts, list) and len(ts) > 0:
                    smoothed_ts = moving_average_smooth(ts, window_size, decimal_places)
                    smoothed_list.append(smoothed_ts)
                else:
                    smoothed_list.append(ts)
        
        processed_values.append(json.dumps(smoothed_list))
    
    df['value'] = processed_values
    
    df.to_csv(output_file, index=False)
    print(f"Processing completed! Saved to: {output_file}")