import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ast
import os
from datetime import datetime

def parse_nested_list(value_str):
    try:
        return ast.literal_eval(value_str)
    except:
        return None

def parse_dtw_data(dtw_str):
    try:
        return ast.literal_eval(dtw_str)
    except:
        return None

def create_output_directory(base_dir="dtw_analysis"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"{base_dir}_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def visualize_dtw_alignment(row_data, row_index, output_dir, figsize=(12, 16)):
    value_data = parse_nested_list(row_data['value'])
    dtw_distances = parse_dtw_data(row_data['dtw_distance_comparison'])
    dtw_indices = parse_dtw_data(row_data['dtw_comparison_index'])
    
    if not all([value_data, dtw_distances, dtw_indices]):
        print(f"Row {row_index + 1}: Data parsing failed, skipping...")
        return False
    
    try:
        ts0, ts1, ts2, ts3, ts4 = value_data
        target_series = [ts1, ts2, ts3, ts4]
        
        all_values = []
        all_values.extend(ts0)
        for ts in target_series:
            all_values.extend(ts)
        
        y_min = min(all_values)
        y_max = max(all_values)
        y_margin = (y_max - y_min) * 0.05
        y_range = (y_min - y_margin, y_max + y_margin)

        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['font.size'] = 10

        fig, axes = plt.subplots(4, 1, figsize=figsize)

        ts0_color = '#2E86AB'
        target_colors = ['#A23B72', '#F18F01', '#C73E1D', '#7209B7']
        highlight_color = '#FFE66D'
        
        for i, (target_ts, dtw_idx, distance) in enumerate(zip(target_series, dtw_indices, dtw_distances)):
            ax = axes[i]

            start_idx, end_idx = dtw_idx

            x_target = np.arange(len(target_ts))
            ax.plot(x_target, target_ts, color=target_colors[i], alpha=0.3, 
                    linewidth=1.5, label=f'TS{i+1}')

            segment_x = x_target[start_idx:end_idx+1]
            segment_y = target_ts[start_idx:end_idx+1]
            ax.plot(segment_x, segment_y, color=target_colors[i], 
                    linewidth=3, alpha=0.9, label=f'TS{i+1} Segment')

            ax.axvspan(start_idx, end_idx, alpha=0.15, color=highlight_color)

            ts0_x = np.arange(start_idx, start_idx + len(ts0))
            ts0_y = ts0
            
            ax.plot(ts0_x, ts0_y, color=ts0_color, 
                    linewidth=2.5, alpha=0.8, linestyle='--', 
                    marker='o', markersize=3, label='TS0')
            
            overlap_start = max(start_idx, ts0_x[0])
            overlap_end = min(end_idx, ts0_x[-1])
            
            if overlap_start <= overlap_end:
                for x_pos in range(int(overlap_start), int(overlap_end) + 1):
                    if x_pos in segment_x and x_pos in ts0_x:
                        target_y = target_ts[x_pos]
                        ts0_idx = x_pos - start_idx
                        if 0 <= ts0_idx < len(ts0):
                            ts0_value = ts0[ts0_idx]
                            ax.plot([x_pos, x_pos], [target_y, ts0_value], 
                                   color='gray', alpha=0.2, linewidth=0.8, linestyle=':')

            ax.set_ylim(y_range)
            ax.set_title(f'TS0 vs TS{i+1} (DTW: {distance:.3f})', fontsize=11, pad=10)

            if i == 3:
                ax.set_xlabel('Time Index', fontsize=10)
            ax.set_ylabel('Value', fontsize=10)

            ax.legend(fontsize=9, loc='upper right', framealpha=0.8)
            ax.grid(True, alpha=0.2)
            ax.tick_params(labelsize=9)
        
        fig.suptitle(f'Row {row_index+1} - DTW Alignment', fontsize=14, y=0.98)
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.95, hspace=0.3)
        
        filename = f"row_{row_index+1:02d}.png"
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return True
        
    except Exception as e:
        print(f"Row {row_index + 1} error: {str(e)}")
        plt.close()
        return False

def analyze_all_csv_rows(csv_file, output_dir=None, figsize=(12, 16)):
    try:
        print(f"Reading CSV: {csv_file}")
        df = pd.read_csv(csv_file)
        total_rows = len(df)
        print(f"Total rows: {total_rows}")
        
        if output_dir is None:
            output_dir = create_output_directory()
        else:
            os.makedirs(output_dir, exist_ok=True)
        
        print(f"Output: {output_dir}")
        
        success_count = 0
        
        for i in range(total_rows):
            print(f"Processing {i+1}/{total_rows}...", end=' ')
            
            row_data = df.iloc[i]
            success = visualize_dtw_alignment(row_data, i, output_dir, figsize)
            
            if success:
                success_count += 1
                print("✓")
            else:
                print("✗")

            if (i + 1) % 50 == 0:
                progress = (i + 1) / total_rows * 100
                print(f"Progress: {progress:.1f}% ({success_count}/{i+1})")
        
        print(f"\nCompleted: {success_count}/{total_rows} rows")
        print(f"Output: {output_dir}")
        
        return output_dir
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def analyze_specific_rows(csv_file, row_indices, output_dir=None, figsize=(12, 16)):
    try:
        print(f"Reading CSV: {csv_file}")
        df = pd.read_csv(csv_file)
        total_rows = len(df)

        indices = [i-1 if i > 0 else i for i in row_indices]
        valid_indices = [i for i in indices if 0 <= i < total_rows]
        
        if not valid_indices:
            print("No valid indices")
            return None
        
        print(f"Processing {len(valid_indices)} rows")

        if output_dir is None:
            output_dir = create_output_directory("dtw_specific")
        else:
            os.makedirs(output_dir, exist_ok=True)
        
        print(f"Output: {output_dir}")
        
        success_count = 0
        
        for idx, i in enumerate(valid_indices):
            print(f"Processing row {i+1} ({idx+1}/{len(valid_indices)})...", end=' ')
            
            row_data = df.iloc[i]
            success = visualize_dtw_alignment(row_data, i, output_dir, figsize)
            
            if success:
                success_count += 1
                print("✓")
            else:
                print("✗")
        
        print(f"\nCompleted: {success_count}/{len(valid_indices)} rows")
        print(f"Output: {output_dir}")
        
        return output_dir
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    csv_file_path = "your_data.csv"
    analyze_all_csv_rows(csv_file_path)