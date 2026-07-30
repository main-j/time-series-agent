import random
from fastdtw import fastdtw
import numpy as np
import pandas as pd
import ast

class DTWAnalyzer:
    def __init__(self, patterns, max_overlap_ratio=0.0):
        self.patterns = patterns
        self.max_overlap_ratio = max_overlap_ratio
        self.data_type = self._detect_data_type()
    
    def _detect_data_type(self):
        has_hours = any('hours' in value for value in self.patterns.values())
        has_weeks = any('weeks' in value for value in self.patterns.values())
        
        if has_hours:
            return 'hourly'
        elif has_weeks:
            return 'weekly'
        else:
            return 'hourly'
    
    def _get_window_size(self, pattern_info):
        if 'hours' in pattern_info:
            return pattern_info['hours']
        elif 'weeks' in pattern_info:
            return pattern_info['weeks']
        else:
            return pattern_info.get('size', 24)
    
    def get_pattern_start(self, window_size, sequence_length):
        min_start = window_size
        max_start = sequence_length - 2*window_size
        if max_start < min_start:
            return None
        return random.randint(min_start, max_start)
    
    def calculate_dtw_distances(self, pattern, sequence, pattern_start, pattern_end, window_size):
        distances, indices = [], []
        pattern_array = np.array(pattern)
        
        max_overlap_length = int(window_size * self.max_overlap_ratio)
        
        for i in range(0, len(sequence) - window_size + 1):
            window_start = i
            window_end = i + window_size
            
            overlap_start = max(window_start, pattern_start)
            overlap_end = min(window_end, pattern_end)
            overlap_length = max(0, overlap_end - overlap_start)
            
            if overlap_length <= max_overlap_length:
                window_array = np.array(sequence[i:i + window_size])
                
                distance, path = fastdtw(pattern_array, window_array)
                
                distances.append(distance)
                indices.append(i)
        return distances, indices
    
    def _calculate_sliding_dtw_with_alignment(self, ts0, tsi):
        if len(ts0) == 0 or len(tsi) == 0:
            return float('inf'), [0, 0]
        
        window_size = len(ts0)
        
        if len(tsi) < window_size:
            distance, path = fastdtw(np.array(ts0), np.array(tsi))
            return distance, [0, len(tsi) - 1]
        
        ts0_array = np.array(ts0)
        
        distances = []
        start_indices = []
        
        for i in range(len(tsi) - window_size + 1):
            window = tsi[i:i + window_size]
            window_array = np.array(window)
            
            distance, path = fastdtw(ts0_array, window_array)
            
            distances.append(distance)
            start_indices.append(i)
        
        if not distances:
            return float('inf'), [0, 0]
        
        min_distance = min(distances)
        min_idx = distances.index(min_distance)
        best_start = start_indices[min_idx]
        best_end = best_start + window_size - 1
        
        return min_distance, [best_start, best_end]
    
    def process_csv_dtw_comparison(self, value_data):
        try:
            if isinstance(value_data, str):
                value_list = ast.literal_eval(value_data)
            else:
                value_list = value_data
            
            if not isinstance(value_list, list) or len(value_list) < 2:
                return [], []
            
            ts0 = value_list[0]
            if len(ts0) == 0:
                return [], []
            
            dtw_distances = []
            dtw_indices = []
            
            for i in range(1, min(5, len(value_list))):
                tsi = value_list[i]
                if len(tsi) == 0:
                    continue
                
                min_distance, index_range = self._calculate_sliding_dtw_with_alignment(ts0, tsi)
                dtw_distances.append(min_distance)
                dtw_indices.append(index_range)
            
            return dtw_distances, dtw_indices
        
        except Exception as e:
            print(f"Error processing row data: {e}")
            return [], []
        
    def process_csv_file(self, input_file, output_file):
        df = pd.read_csv(input_file)
        
        if 'value' not in df.columns:
            raise ValueError("'value' column not found in CSV file")
        
        total_rows = len(df)
        print(f"Starting to process CSV file, total {total_rows} rows of data...")

        dtw_distances_list = []
        dtw_indices_list = []
        
        for idx, row in df.iterrows():
            progress = (idx + 1) / total_rows * 100
            
            print(f"\rProcessing progress: {progress:.1f}% ({idx + 1}/{total_rows})", end='', flush=True)
            
            distances, indices = self.process_csv_dtw_comparison(row['value'])
            dtw_distances_list.append(distances)
            dtw_indices_list.append(indices)
        
        print()
        
        df['dtw_distance_comparison'] = dtw_distances_list
        df['dtw_comparison_index'] = dtw_indices_list
        
        df.to_csv(output_file, index=False)
        print(f"Processing completed! Results saved to: {output_file}")
        
        return df

    def get_top_segments(self, distances, indices, pattern_start):
        if len(distances) < 3:
            return [], []
        
        distance_pairs = list(zip(distances, indices))
        sorted_pairs = sorted(distance_pairs, key=lambda x: x[0])
        
        most_similar_dtw = sorted_pairs[:1]
        middle_index = len(sorted_pairs) // 2
        medium_similar = [sorted_pairs[middle_index]]
        least_similar = sorted_pairs[-1:]

        pattern_segment = (0.0, pattern_start)
        top_pairs = [pattern_segment] + most_similar_dtw + medium_similar + least_similar
        top_distances = [dist for dist, _ in top_pairs]
        top_indices = [idx for _, idx in top_pairs]
        
        return top_distances, top_indices
    
    def analyze_sequence(self, sequence, selected_pattern):
        pattern_info = self.patterns[selected_pattern]
        window_size = self._get_window_size(pattern_info)

        if len(sequence) < 3 * window_size:
            return None
        
        pattern_start = self.get_pattern_start(window_size, len(sequence))
        if pattern_start is None:
            return None
            
        pattern_end = pattern_start + window_size
        ts_pattern = sequence[pattern_start:pattern_end]
        
        distances, indices = self.calculate_dtw_distances(
            ts_pattern, sequence, pattern_start, pattern_end, window_size)
        
        if not distances:
            return None
        
        top_distances, top_indices = self.get_top_segments(distances, indices, pattern_start)
        
        if not top_distances:
            return None
        
        result = {
            'pattern_info': pattern_info,
            'pattern_start': pattern_start,
            'pattern_end': pattern_end,
            'ts_pattern': ts_pattern,
            'window_size': window_size,
            'top_distances': top_distances,
            'top_indices': top_indices,
            'data_type': self.data_type,
            'similarity_types': ['1st', '2nd', '3rd', '4th']
        }
        
        return result