import os
import random
import pandas as pd
import matplotlib.pyplot as plt
import ast
import csv
from datetime import datetime

class DataUtils:
    
    def __init__(self, results_dir):
        self.results_dir = results_dir
        
        self.segment_info = [
            "1st Similar",        
            "2nd Similar",         
            "3rd Similar",         
            "4th Similar"          
        ]
        
        self.images_dir = self._create_images_dir()
    
    def _create_images_dir(self):
        images_path = os.path.join(self.results_dir, 'images')
        if not os.path.exists(images_path):
            os.makedirs(images_path)
            print(f"Created image output directory: {images_path}")
        return images_path
    
    def get_segment_bounds(self, idx, window_size, sequence_length):
        start_time = idx
        end_time = idx + window_size - 1
        
        if start_time < 0 or end_time >= sequence_length:
            print(f"Warning: Boundary exceeds sequence range! idx={idx}, window_size={window_size}, sequence_length={sequence_length}")
            print(f"Calculated boundaries: start_time={start_time}, end_time={end_time}")
            print("Setting both start_time and end_time to 0")
            return 0, 0
        
        return start_time, end_time
    
    def collect_data(self, temp_data, row_index, sequence, analysis_result):
        pattern_info = analysis_result['pattern_info']
        pattern_start = analysis_result['pattern_start']
        pattern_end = analysis_result['pattern_end']
        top_distances = analysis_result['top_distances']
        top_indices = analysis_result['top_indices']
        window_size = analysis_result['window_size']
        
        option_index = []
        dtw_distance = []
        
        for i, (dist, idx) in enumerate(zip(top_distances, top_indices)):
            start_time, end_time = self.get_segment_bounds(idx, window_size, len(sequence))
            option_index.append([start_time, end_time])
            dtw_distance.append(round(dist, 2))
        
        temp_data[row_index] = {
            'pattern_name': pattern_info['name'],
            'pattern_index': [pattern_start, pattern_end - 1],
            'option_index': option_index,
            'dtw_distance': dtw_distance
        }

    def write_merged_csv_data(self, csv_path, temp_data):
        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ts_id', 'pattern_name', 'pattern_index', 'option_index', 'dtw_distance'])
            
            for ts_id in sorted(temp_data.keys()):
                data = temp_data[ts_id]
                writer.writerow([
                    ts_id,
                    data['pattern_name'],
                    data['pattern_index'],
                    data['option_index'],
                    data['dtw_distance']
                ])
    
    def create_csv_file(self):
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
            print(f"Created results directory: {self.results_dir}")
        
        current_date = datetime.now()
        formatted_date = current_date.strftime('%Y%m%d')
        csv_path = os.path.join(self.results_dir, f'analysis_results_{formatted_date}.csv')
        return csv_path
    
    def select_random_samples(self, total_size, sample_size):
        if sample_size < total_size:
            return random.sample(range(total_size), sample_size)
        else:
            return list(range(total_size))
    
    def plot_row_timeseries(self, csv_file_path, row_index=0, output_path=None, figsize=(12, 8), show_plot=True):
        df = pd.read_csv(csv_file_path)
        
        if row_index >= len(df):
            print(f"Row index {row_index} exceeds data range")
            return False
        
        try:
            value_str = str(df.iloc[row_index]['value'])
            if value_str == 'nan' or value_str == '':
                print(f"Row {row_index} value column is empty")
                return False
                
            value_data = ast.literal_eval(value_str)
            
            if not isinstance(value_data, list):
                print(f"Row {row_index} value data format is incorrect")
                return False
            
            if len(value_data) > 0 and isinstance(value_data[0], list):
                timeseries_list = value_data
            else:
                timeseries_list = [value_data]
            
            num_series = len(timeseries_list)
            
            fig, axes = plt.subplots(num_series, 1, figsize=figsize, squeeze=False)
            
            row_info = df.iloc[row_index]
            fig.suptitle(f"Row {row_info.get('num', row_index)} - {row_info.get('qa_type', 'Unknown')}", 
                         fontsize=16, fontweight='bold')
            
            for i, ts_data in enumerate(timeseries_list):
                ax = axes[i, 0]
                
                if len(ts_data) == 0:
                    ax.set_title(f'ts{i} (No Data)')
                    continue
                
                x_data = list(range(len(ts_data)))
                
                ax.plot(x_data, ts_data, 
                       marker='o', 
                       markersize=4,
                       linewidth=2,
                       alpha=0.8)
                
                ax.grid(True, alpha=0.3)
                ax.set_title(f'ts{i}', fontsize=12)
                ax.set_ylabel('Value')
                
                if i == num_series - 1:
                    ax.set_xlabel('Time Index')
            
            plt.tight_layout()
            
            if output_path is None:
                output_path = os.path.join(self.images_dir, f'row_{row_index+1}.png')
            
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            
            if show_plot:
                plt.show()
            
            return True
            
        except Exception as e:
            print(f"Error plotting row {row_index}: {str(e)}")
            return False
        
        finally:
            if 'fig' in locals():
                plt.close(fig)
    
    def plot_all_rows_separately(self, csv_file_path, custom_output_dir=None, figsize=(12, 8)):
        df = pd.read_csv(csv_file_path)
        
        output_dir = custom_output_dir if custom_output_dir else self.images_dir
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")
        
        success_count = 0
        total_count = len(df)
        
        print(f"Starting to process {total_count} rows of data...")
        
        for idx in range(total_count):
            try:
                value_str = str(df.iloc[idx]['value'])
                if value_str == 'nan' or value_str == '':
                    continue
                
                output_path = os.path.join(output_dir, f"row_{idx+1}.png")
                
                if self.plot_row_timeseries(csv_file_path, row_index=idx, 
                                      output_path=output_path, figsize=figsize, 
                                      show_plot=False):
                    success_count += 1
                
            except Exception as e:
                print(f"Error processing row {idx}: {str(e)}")
                continue
        
        print(f"Processing complete! Successfully generated {success_count}/{total_count} images")
    
    def plot_specific_rows(self, csv_file_path, row_indices, custom_output_dir=None, figsize=(12, 8)):
        output_dir = custom_output_dir if custom_output_dir else self.images_dir
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")
        
        success_count = 0
        
        print(f"Starting to process specified {len(row_indices)} rows of data...")
        
        for idx in row_indices:
            try:
                output_path = os.path.join(output_dir, f"row_{idx+1}.png")
                
                if self.plot_row_timeseries(csv_file_path, row_index=idx, 
                                          output_path=output_path, figsize=figsize):
                    success_count += 1
                
            except Exception as e:
                print(f"Error processing row {idx}: {str(e)}")
                continue
        
        print(f"Processing complete! Successfully generated {success_count}/{len(row_indices)} images")
        print(f"Image save directory: {output_dir}")