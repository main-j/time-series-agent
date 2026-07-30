# FinditProcessor.py
import pandas as pd
import ast
import numpy as np
from datasets import load_from_disk

def extend_option_index_and_update_value(csv_file_path, dataset_path, output_file_path=None, 
                                       scale_factor=1.0, decimal_places=None, 
                                       add_noise=False, noise_level=0.1, noise_type='gaussian'):
    ds = load_from_disk(dataset_path)
    df = pd.read_csv(csv_file_path)
    
    def safe_eval(x):
        try:
            return ast.literal_eval(x)
        except:
            return x
    
    df['value'] = df['value'].apply(safe_eval)
    df['pattern_index'] = df['pattern_index'].apply(safe_eval)
    df['option_index'] = df['option_index'].apply(safe_eval)
    
    def add_noise_to_values(values, add_noise, noise_level, noise_type):
        if not add_noise or len(values) == 0:
            return values
        
        try:
            values_array = np.array(values)
            
            if noise_type == 'gaussian':
                data_std = np.std(values_array)
                if data_std == 0:
                    data_mean = np.mean(values_array)
                    noise_std = noise_level * abs(data_mean) if data_mean != 0 else noise_level
                else:
                    noise_std = noise_level * data_std
                noise = np.random.normal(0, noise_std, len(values_array))
                
            elif noise_type == 'uniform':
                data_range = np.max(values_array) - np.min(values_array)
                if data_range == 0:
                    data_mean = np.mean(values_array)
                    noise_range = noise_level * abs(data_mean) if data_mean != 0 else noise_level
                else:
                    noise_range = noise_level * data_range
                noise = np.random.uniform(-noise_range/2, noise_range/2, len(values_array))
                
            else:
                data_std = np.std(values_array)
                noise_std = noise_level * data_std if data_std > 0 else noise_level
                noise = np.random.normal(0, noise_std, len(values_array))
            
            noisy_values = values_array + noise
            return noisy_values.tolist()
            
        except Exception as e:
            print(f"Error Adding Noise: {e}")
            return values
    
    def apply_scale_factor(values, scale_factor):
        if scale_factor == 1.0:
            return values
        try:
            return [val * scale_factor for val in values]
        except:
            return values

    def apply_decimal_places(values, decimal_places):
        if decimal_places is None:
            return values
        try:
            return [round(val, decimal_places) for val in values]
        except:
            return values
    
    def extend_indices_and_update_value(row_data):
        ts_id = row_data['ts_id']
        pattern_index = row_data['pattern_index']
        option_index = row_data['option_index']
        current_value = row_data['value']
        
        try:
            ts_id = int(ts_id)
        except (ValueError, TypeError):
            return row_data['value'], row_data['option_index']
        
        if (not isinstance(pattern_index, list) or 
            not isinstance(option_index, list) or 
            not isinstance(current_value, list)):
            return row_data['value'], row_data['option_index']
        
        if ts_id >= len(ds) or ts_id < 0:
            return row_data['value'], row_data['option_index']
        
        try:
            sequence = ds[ts_id]['target']
            sequence_length = len(sequence)
        except:
            return row_data['value'], row_data['option_index']
        
        new_value = [current_value[0]]
        new_option_index = []
        
        for i, option_sublist in enumerate(option_index):
            if not isinstance(option_sublist, list) or len(option_sublist) < 2:
                new_option_index.append(option_sublist)
                if i + 1 < len(current_value):
                    new_value.append(current_value[i + 1])
                else:
                    new_value.append([])
                continue
            
            start_idx, end_idx = option_sublist[0], option_sublist[1]
            window_length = end_idx - start_idx + 1
            
            extended_start = max(0, start_idx - window_length)
            extended_end = min(sequence_length - 1, end_idx + window_length)
            
            new_option_index.append([extended_start, extended_end])
            
            try:
                if i + 1 < len(current_value):
                    original_values = current_value[i + 1]
                    if not isinstance(original_values, list):
                        original_values = []
                else:
                    original_values = []
                
                left_extension_start = extended_start
                left_extension_end = start_idx - 1
                right_extension_start = end_idx + 1
                right_extension_end = extended_end

                left_extension_values = []
                if left_extension_start <= left_extension_end:
                    left_data = sequence[left_extension_start:left_extension_end + 1]
                    if hasattr(left_data, 'tolist'):
                        left_data = left_data.tolist()
                    elif not isinstance(left_data, list):
                        left_data = list(left_data)
                    
                    left_data = apply_scale_factor(left_data, scale_factor)
                    left_data = add_noise_to_values(left_data, add_noise, noise_level, noise_type)
                    left_extension_values = apply_decimal_places(left_data, decimal_places)
                
                right_extension_values = []
                if right_extension_start <= right_extension_end:
                    right_data = sequence[right_extension_start:right_extension_end + 1]
                    if hasattr(right_data, 'tolist'):
                        right_data = right_data.tolist()
                    elif not isinstance(right_data, list):
                        right_data = list(right_data)
                    
                    right_data = apply_scale_factor(right_data, scale_factor)
                    right_data = add_noise_to_values(right_data, add_noise, noise_level, noise_type)
                    right_extension_values = apply_decimal_places(right_data, decimal_places)
                
                combined_values = left_extension_values + original_values + right_extension_values
                
                new_value.append(combined_values)
                
            except Exception as e:
                print(f"Error Processing Row {idx}: {e}")
                if i + 1 < len(current_value):
                    new_value.append(current_value[i + 1])
                else:
                    new_value.append([])
                new_option_index[-1] = option_sublist
        
        return new_value, new_option_index
    
    results = []
    for idx, row in df.iterrows():
        result = extend_indices_and_update_value(row)
        results.append(result)
    
    df['value'] = [result[0] for result in results]
    df['option_index'] = [result[1] for result in results]
    
    if output_file_path:
        df_to_save = df.copy()
        df_to_save['value'] = df_to_save['value'].apply(str)
        df_to_save['pattern_index'] = df_to_save['pattern_index'].apply(str)
        df_to_save['option_index'] = df_to_save['option_index'].apply(str)
        df_to_save.to_csv(output_file_path, index=False)
    
    return df

if __name__ == "__main__":
    # without noise
    df1 = extend_option_index_and_update_value(
        csv_file_path="input.csv",
        dataset_path="dataset_path",
        output_file_path="output_no_noise.csv"
    )
    
    # with gaussian noise
    df2 = extend_option_index_and_update_value(
        csv_file_path="input.csv",
        dataset_path="dataset_path",
        output_file_path="output_with_gaussian_noise.csv",
        add_noise=True,
        noise_level=0.1,
        noise_type='gaussian'
    )
    
    # with uniform noise
    df3 = extend_option_index_and_update_value(
        csv_file_path="input.csv",
        dataset_path="dataset_path",
        output_file_path="output_with_uniform_noise.csv",
        add_noise=True,
        noise_level=0.05,
        noise_type='uniform'
    )