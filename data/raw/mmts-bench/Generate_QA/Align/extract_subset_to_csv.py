import os
import random
import pandas as pd
from datasets import load_from_disk
import numpy as np
from tqdm import tqdm
import time

def generate_time_series_dataset(x, y, output_csv_path):
    datasets = []
    print("Starting to load datasets...")
    for i, path in enumerate(dataset_paths):
        try:
            print(f"Loading {dataset_configs[i]['name']}...")
            start_time = time.time()
            ds = load_from_disk(path)
            load_time = time.time() - start_time
            datasets.append(ds)
            print(f"Successfully loaded {dataset_configs[i]['name']}, time: {load_time:.2f}s, data size: {len(ds)}")
        except Exception as e:
            print(f"Failed to load dataset {path}: {e}")
            return
    
    if len(datasets) != 3:
        print("Need 3 datasets to continue")
        return
    
    print("\nPre-checking dataset validity...")
    max_window = max(y)
    for i, dataset in enumerate(datasets):
        valid_count = 0
        sample_size = min(100, len(dataset))
        
        for j in range(sample_size):
            if is_valid_sample(dataset[j], i, max_window):
                valid_count += 1
        
        valid_ratio = valid_count / sample_size
        print(f"{dataset_configs[i]['name']}: sampling validity rate {valid_ratio:.2%} ({valid_count}/{sample_size})")
        
        if valid_ratio < 0.1:
            print(f"Warning: {dataset_configs[i]['name']} may have insufficient valid data")
    
    results = []
    
    samples_per_window = x // len(y)
    remaining_samples = x % len(y)
    
    samples_per_main_dataset = x // 3
    main_dataset_allocation = [samples_per_main_dataset] * 3
    for i in range(x % 3):
        main_dataset_allocation[i] += 1
    
    main_dataset_sequence = []
    for i in range(3):
        main_dataset_sequence.extend([i] * main_dataset_allocation[i])
    random.shuffle(main_dataset_sequence)
    
    window_sequence = []
    for i, window_length in enumerate(y):
        count = samples_per_window + (1 if i < remaining_samples else 0)
        window_sequence.extend([window_length] * count)
    random.shuffle(window_sequence)
    
    print(f"\nStarting to generate {x} data samples...")
    
    max_attempts_per_sample = 50
    failed_attempts = 0
    
    pbar = tqdm(range(x), desc="Generating data")
    
    for idx in pbar:
        attempts = 0
        success = False
        
        while attempts < max_attempts_per_sample and not success:
            try:
                attempts += 1
                
                window_length = window_sequence[idx]
                main_dataset_idx = main_dataset_sequence[idx]
                
                main_dataset = datasets[main_dataset_idx]
                main_dataset_name = dataset_configs[main_dataset_idx]['name']
                
                other_dataset_indices = [i for i in range(3) if i != main_dataset_idx]
                
                main_valid_rows = find_random_valid_rows(main_dataset, main_dataset_idx, window_length, 2, max_search=20)
                if len(main_valid_rows) < 2:
                    continue
                
                other_valid_rows = []
                for other_idx in other_dataset_indices:
                    other_dataset = datasets[other_idx]
                    valid_rows = find_random_valid_rows(other_dataset, other_idx, window_length, 1, max_search=10)
                    if len(valid_rows) < 1:
                        break
                    other_valid_rows.append((other_idx, valid_rows[0]))
                
                if len(other_valid_rows) < 2:
                    continue
                
                ts_data = []
                option_indices = []
                selected_info = []
                
                extraction_success = True
                for i in range(2):
                    row_idx = main_valid_rows[i]
                    ts_segment, start_pos, selected_index = extract_data_from_dataset(
                        main_dataset, main_dataset_idx, row_idx, window_length
                    )
                    
                    if ts_segment is None:
                        extraction_success = False
                        break
                    
                    ts_data.append(ts_segment)
                    option_indices.append([start_pos, start_pos + window_length - 1])
                    selected_info.append(f"dataset_{main_dataset_idx}_index_{selected_index}")
                
                if not extraction_success:
                    continue
                
                for other_dataset_idx, row_idx in other_valid_rows:
                    other_dataset = datasets[other_dataset_idx]
                    ts_segment, start_pos, selected_index = extract_data_from_dataset(
                        other_dataset, other_dataset_idx, row_idx, window_length
                    )
                    
                    if ts_segment is None:
                        extraction_success = False
                        break
                    
                    ts_data.append(ts_segment)
                    option_indices.append([start_pos, start_pos + window_length - 1])
                    selected_info.append(f"dataset_{other_dataset_idx}_index_{selected_index}")
                
                if not extraction_success or len(ts_data) < 4:
                    continue
                
                main_freq = main_dataset[main_valid_rows[0]]['freq']
                
                record = {
                    'num': idx + 1,
                    'ts_id': main_valid_rows[0],
                    'qa_type': 'a multiple choice question',
                    'local_overall': 'overall',
                    'task_type': 'caption',
                    'question': '',
                    'option': 'A) ts1.\nB) ts2.\nC) ts3.\nD) ts4.',
                    'answer': 'A',
                    'domain': main_dataset_name,
                    'freq': main_freq,
                    'is_univariate': True,
                    'value': ts_data,
                    'option_index': option_indices
                }
                
                results.append(record)
                success = True
                
                pbar.set_description(f"Generating data (success: {len(results)})")
                
            except Exception as e:
                print(f"\nError generating data sample {idx + 1}: {e}")
                continue
        
        if not success:
            failed_attempts += 1
            print(f"\nFailed to generate data sample {idx + 1}, attempted {max_attempts_per_sample} times")
            
        if failed_attempts > x * 0.5:
            print(f"\nToo many failures ({failed_attempts}), terminating early")
            break
    
    pbar.close()
    
    if results:
        df = pd.DataFrame(results)
        df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
        print(f"\nSuccessfully generated {len(results)} data samples, saved to {output_csv_path}")
        
        print("\nStatistics:")
        print("Main dataset distribution:")
        print(df['domain'].value_counts())
        print("\nWindow length distribution:")
        window_lengths = [len(val[0]) for val in df['value']]
        window_df = pd.DataFrame({'window_length': window_lengths})
        print(window_df['window_length'].value_counts().sort_index())
    else:
        print("No data samples were successfully generated")

def is_valid_sample(sample, dataset_idx, window_length):
    target_data = sample['target']
    
    if dataset_idx == 0:
        return len(target_data) >= window_length
    else:
        if dataset_idx == 1:
            available_indices = list(range(10, 17))
        else:
            available_indices = [0, 1]
        
        for idx in available_indices:
            if idx < len(target_data) and len(target_data[idx]) >= window_length:
                return True
        return False

def find_random_valid_rows(dataset, dataset_idx, window_length, needed_count, max_search=50):
    valid_rows = []
    searched_indices = set()
    dataset_size = len(dataset)
    
    attempts = 0
    while len(valid_rows) < needed_count and attempts < max_search:
        attempts += 1
        row_idx = random.randint(0, dataset_size - 1)
        
        if row_idx in searched_indices:
            continue
        
        searched_indices.add(row_idx)
        
        try:
            if is_valid_sample(dataset[row_idx], dataset_idx, window_length):
                valid_rows.append(row_idx)
        except Exception as e:
            continue
    
    return valid_rows

def extract_data_from_dataset(dataset, dataset_idx, row_idx, window_length):
    try:
        config = dataset_configs[dataset_idx]
        target_data = dataset[row_idx]['target']
        
        if config['type'] == 'single':
            if len(target_data) < window_length:
                return None, None, None
            start_pos = random.randint(0, len(target_data) - window_length)
            ts_segment = target_data[start_pos:start_pos + window_length]
            selected_index = None
            
        else:
            available_indices = config['indices']
            valid_indices = []
            for idx in available_indices:
                if idx < len(target_data) and len(target_data[idx]) >= window_length:
                    valid_indices.append(idx)
            
            if not valid_indices:
                return None, None, None
            
            selected_index = random.choice(valid_indices)
            selected_data = target_data[selected_index]
            start_pos = random.randint(0, len(selected_data) - window_length)
            ts_segment = selected_data[start_pos:start_pos + window_length]
        
        scale_factor = config.get('scale_factor', 1.0)
        decimal_places = config.get('decimal_places', 2)
        
        ts_segment = [round(float(val) * scale_factor, decimal_places) for val in ts_segment]
        
        return ts_segment, start_pos, selected_index
    
    except Exception as e:
        return None, None, None

dataset_paths = [
    '/nas/datasets/AAA_TS_Benchmark/lotsa_data/traffic_hourly',
    '/nas/datasets/AAA_TS_Benchmark/lotsa_data/era5_2018',
    '/nas/datasets/AAA_TS_Benchmark/lotsa_data/alibaba_cluster_trace_2018'
]

dataset_configs = [
    {
        'name': 'traffic_hourly', 
        'type': 'single', 
        'indices': None,
        'scale_factor': 100,
        'decimal_places': 2
    },
    {
        'name': 'era5_2018', 
        'type': 'multi', 
        'indices': list(range(10, 17)),
        'scale_factor': 1.0,
        'decimal_places': 2
    },
    {
        'name': 'alibaba', 
        'type': 'multi', 
        'indices': [0, 1],
        'scale_factor': 1.0,
        'decimal_places': 2
    }
]

if __name__ == "__main__":
    data_amount = 10
    window_lengths = [24, 48, 72, 168]
    output_path = "time_series_dataset_test.csv"
    
    generate_time_series_dataset(data_amount, window_lengths, output_path)