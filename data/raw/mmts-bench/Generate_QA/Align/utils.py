import os
import pandas as pd
import matplotlib.pyplot as plt
import ast
import numpy as np
from pathlib import Path

class ImagePlotter:
    
    def __init__(self, output_dir="generated_images"):
        self.output_dir = output_dir
        self._create_output_dir()
    
    def _create_output_dir(self):
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def plot_first_sublist(self, csv_file_path):
        df = pd.read_csv(csv_file_path)
        
        plt.rcParams['figure.figsize'] = (8, 6)
        plt.rcParams['figure.dpi'] = 100
        
        success_count = 0
        
        for index, row in df.iterrows():
            try:
                num = row['num']
                
                value_str = row['value']
                
                if isinstance(value_str, str):
                    try:
                        nested_list = ast.literal_eval(value_str)
                    except (ValueError, SyntaxError):
                        print(f"Skip row {index}, unable to parse value: {value_str}")
                        continue
                else:
                    nested_list = value_str
                
                if isinstance(nested_list, list) and len(nested_list) > 0:
                    first_sublist = nested_list[0]
                    
                    if isinstance(first_sublist, list):
                        plt.figure(figsize=(8, 6))
                        
                        plt.plot(first_sublist, linewidth=2, color='blue')
                        plt.title(f'Data Visualization', fontsize=14)
                        plt.xlabel('Index', fontsize=12)
                        plt.ylabel('Value', fontsize=12)
                        plt.grid(True, alpha=0.3)
                        
                        mean_val = np.mean(first_sublist)
                        max_val = np.max(first_sublist)
                        min_val = np.min(first_sublist)
                        
                        plt.text(0.02, 0.98, f'Mean: {mean_val:.2f}\nMax: {max_val:.2f}\nMin: {min_val:.2f}', 
                                transform=plt.gca().transAxes, verticalalignment='top',
                                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
                        
                        plt.tight_layout()
                        
                        output_path = os.path.join(self.output_dir, f"{num}.jpg")
                        plt.savefig(output_path, format='jpg', bbox_inches='tight', dpi=100)
                        plt.close()
                        
                        success_count += 1
                        print(f"Image saved: {output_path}")
                        
                    else:
                        print(f"Skip row {index}, first element is not a list")
                else:
                    print(f"Skip row {index}, value is not a valid nested list")
                    
            except Exception as e:
                print(f"Error processing row {index}: {e}")
                continue
        
        print(f"First sublist plotting completed! Successfully generated {success_count} images")
    
    def plot_all_sublists(self, csv_file_path, row_index=0, output_filename=None):
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
            
            fig, axes = plt.subplots(num_series, 1, figsize=(8, 6 * num_series), squeeze=False)
            
            row_info = df.iloc[row_index]
            fig.suptitle(f"Row {row_info.get('num', row_index)}", 
                        fontsize=16, fontweight='bold')
            
            for i, ts_data in enumerate(timeseries_list):
                ax = axes[i, 0]
                
                if len(ts_data) == 0:
                    ax.set_title(f'TS {i+1} (No Data)')
                    continue
                
                ax.plot(ts_data, linewidth=2, color='blue')
                ax.set_title(f'TS {i+1}', fontsize=12)
                ax.set_xlabel('Index', fontsize=12)
                ax.set_ylabel('Value', fontsize=12)
                ax.grid(True, alpha=0.3)
                
                mean_val = np.mean(ts_data)
                max_val = np.max(ts_data)
                min_val = np.min(ts_data)
                
                ax.text(0.02, 0.98, f'Mean: {mean_val:.2f}\nMax: {max_val:.2f}\nMin: {min_val:.2f}', 
                        transform=ax.transAxes, verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            plt.tight_layout()
            
            if output_filename is None:
                num_value = row_info.get('num', row_index)
                output_filename = f'{num_value}.jpg'
            
            output_path = os.path.join(self.output_dir, output_filename)
            plt.savefig(output_path, dpi=100, bbox_inches='tight')
            plt.close(fig)
            
            print(f"All sublists image saved: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error plotting row {row_index}: {str(e)}")
            return False
    
    def plot_multiple_rows_all_sublists(self, csv_file_path, row_indices=None):
        df = pd.read_csv(csv_file_path)
        
        if row_indices is None:
            row_indices = list(range(len(df)))
        
        success_count = 0
        
        print(f"Starting to process all sublists for {len(row_indices)} rows...")
        
        for idx in row_indices:
            try:
                if self.plot_all_sublists(csv_file_path, row_index=idx):
                    success_count += 1
                
            except Exception as e:
                print(f"Error processing row {idx}: {str(e)}")
                continue
        
        print(f"All sublists plotting completed! Successfully generated {success_count}/{len(row_indices)} images")

if __name__ == "__main__":
    plotter = ImagePlotter(output_dir="generated_images")
    
    csv_file = "your_data.csv"
    
    print("=== Starting first sublist plotting ===")
    plotter.plot_first_sublist(csv_file)
    
    print("\n=== Starting all sublists plotting for specified row ===")
    plotter.plot_all_sublists(csv_file, row_index=0)
    
    print("\n=== Starting all sublists plotting for multiple rows ===")
    plotter.plot_multiple_rows_all_sublists(csv_file, row_indices=[0, 1, 2])