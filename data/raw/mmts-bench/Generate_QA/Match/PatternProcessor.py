import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Any
from datasets import load_from_disk
import ast

class TimeSeriesPatternProcessor:
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.scale_factor = 1.0
        self.decimal_places = 2
        self.input_df = None
        self.dataset = None
        self.hf_dataset = None
        self.results = []

    def _process_numerical_values(self, values: List[float]) -> List[float]:
        try:
            processed_values = []
            for value in values:
                scaled_value = value * self.scale_factor
                rounded_value = round(scaled_value, self.decimal_places)
                processed_values.append(rounded_value)
            return processed_values
        except Exception as e:
            if self.verbose:
                print(f"Numerical processing error: {e}")
            return values
    
    def save_filtered_input(self, output_path: str, filtered_ts_ids: set) -> bool:
        if self.input_df is None:
            return False
        
        try:
            filtered_input_df = self.input_df[self.input_df['ts_id'].isin(filtered_ts_ids)]
            filtered_input_df.to_csv(output_path, index=False)
            
            if self.verbose:
                original_count = len(self.input_df)
                filtered_count = len(filtered_input_df)
                print(f"Filtered input file saved to: {output_path}, original rows: {original_count}, filtered rows: {filtered_count}")
            return True
        except Exception as e:
            if self.verbose:
                print(f"Failed to save filtered input file: {e}")
            return False

    def _filter_by_dtw_threshold(self, df: pd.DataFrame, filter_rules: Optional[List[Dict[str, Any]]]) -> tuple:
        
        if not filter_rules:
            return df, set(df['ts_id'].unique())
        
        segment_type_mapping = {
            '1st Similar': 0,
            '2nd Similar': 1,
            '3rd Similar': 2,
            '4th Similar': 3
        }
        
        valid_ts_ids = []
        
        for idx, row in df.iterrows():
            ts_id = row['ts_id']
            
            try:
                dtw_distances = ast.literal_eval(row['dtw_distance'])
                
                if not isinstance(dtw_distances, list):
                    if self.verbose:
                        print(f"ts_id={ts_id} dTW_distance format incorrect, skipping")
                    continue
                    
            except (ValueError, SyntaxError) as e:
                if self.verbose:
                    print(f"ts_id={ts_id} dTW_distance parsing failed: {e}")
                continue
            
            meets_all_rules = True
            
            for rule in filter_rules:
                segment_type = rule['segment_type']
                condition = rule['condition']
                threshold = rule['threshold']
                
                if segment_type not in segment_type_mapping:
                    if self.verbose:
                        print(f"Unknown segment type: {segment_type}")
                    continue
                
                list_index = segment_type_mapping[segment_type]
                
                if list_index >= len(dtw_distances):
                    if self.verbose:
                        print(f"ts_id={ts_id} dTW_distance list length insufficient, cannot get index {list_index}")
                    meets_all_rules = False
                    break
                
                dtw_value = dtw_distances[list_index]
                
                rule_passed = False
                if condition == 'less_than':
                    rule_passed = dtw_value < threshold
                elif condition == 'less_equal':
                    rule_passed = dtw_value <= threshold
                elif condition == 'greater_than':
                    rule_passed = dtw_value > threshold
                elif condition == 'greater_equal':
                    rule_passed = dtw_value >= threshold
                elif condition == 'between':
                    if isinstance(threshold, list) and len(threshold) == 2:
                        min_val, max_val = threshold
                        rule_passed = min_val <= dtw_value <= max_val
                    else:
                        if self.verbose:
                            print(f"Between condition threshold format error: {threshold}")
                        meets_all_rules = False
                        break
                elif condition == 'equal':
                    rule_passed = abs(dtw_value - threshold) < 1e-6
                else:
                    if self.verbose:
                        print(f"Unknown condition type: {condition}")
                    meets_all_rules = False
                    break
                
                if not rule_passed:
                    meets_all_rules = False
                    break
            
            if meets_all_rules:
                valid_ts_ids.append(ts_id)
        
        filtered_df = df[df['ts_id'].isin(valid_ts_ids)]
        
        if self.verbose:
            original_count = df['ts_id'].nunique()
            filtered_count = filtered_df['ts_id'].nunique()
            print(f"DTW filtering: {original_count} -> {filtered_count} ts_ids")
            print(f"Filtered out {original_count - filtered_count} ts_ids")
        
        return filtered_df, set(valid_ts_ids)
    
    def _extract_data_segment(self, ts_id: int, start_idx: int, end_idx: int) -> Optional[List]:
        try:
            if not self._validate_indices(ts_id, start_idx, end_idx):
                return None
            
            data_segment = self.dataset.iloc[ts_id, start_idx:end_idx+1].values.tolist()
            
            processed_segment = self._process_numerical_values(data_segment)
            
            return processed_segment
            
        except Exception:
            return None
    
    def load_input_csv(self, csv_path: str) -> bool:
        try:
            self.input_df = pd.read_csv(csv_path)
            if self.verbose:
                print(f"CSV file loaded successfully, data shape: {self.input_df.shape}")
            return True
        except Exception as e:
            if self.verbose:
                print(f"Failed to load CSV file: {e}")
            return False
    
    def load_dataset(self, dataset_path: str, data_column: str = 'data') -> bool:
        try:
            self.hf_dataset = load_from_disk(dataset_path)
            self.dataset = self._convert_hf_to_dataframe(data_column)
            
            if self.verbose:
                print(f"Dataset loaded successfully, shape: {self.dataset.shape}")
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"Failed to load dataset: {e}")
            return False
    
    def _convert_hf_to_dataframe(self, data_column: str = 'data') -> Optional[pd.DataFrame]:
        try:
            column_candidates = [data_column, 'timeseries', 'values', 'data']
            
            for column in column_candidates:
                if column in self.hf_dataset.column_names:
                    return pd.DataFrame(self.hf_dataset[column])
            
            for column in self.hf_dataset.column_names:
                sample_data = self.hf_dataset[column][0]
                if isinstance(sample_data, (list, np.ndarray)):
                    return pd.DataFrame(self.hf_dataset[column])
            
            raise ValueError(f"No suitable data column found. Available columns: {self.hf_dataset.column_names}")
                
        except Exception as e:
            if self.verbose:
                print(f"Failed to convert dataset: {e}")
            return None
    
    def validate_data(self) -> bool:
        if self.input_df is None or self.dataset is None:
            return False
        
        required_columns = [
            'ts_id', 'pattern_name', 'pattern_index', 
            'option_index', 'dtw_distance'
        ]
        
        missing_columns = [col for col in required_columns if col not in self.input_df.columns]
        if missing_columns:
            if self.verbose:
                print(f"Missing required columns: {missing_columns}")
            return False
            
        return True
    
    def process_data(self, output_config: Optional[Dict[str, Any]] = None, dtw_threshold: Optional[List[Dict[str, Any]]] = None) -> tuple:
        if not self.validate_data():
            return False, set()
        
        filtered_df, valid_ts_ids = self._filter_by_dtw_threshold(self.input_df, dtw_threshold)
        self.ts_id_column = filtered_df['ts_id'].tolist()
        
        default_config = {
            'qa_type': 'pattern_similarity',
            'local_overall': 'local',
            'task_type': 'time_series_analysis',
            'question_template': 'Find similar patterns for time series {}',
            'option': '',
            'answer': '',
            'domain': '',
            'freq': '',
            'is_univariate': True
        }
        
        if output_config:
            default_config.update(output_config)
        
        default_config['task_type'] = str(default_config['task_type'])
        default_config['question_template'] = str(default_config['question_template'])
        default_config['option'] = str(default_config['option'])
        default_config['answer'] = str(default_config['answer'])
        
        self.results = []
        
        num_counter = 1
        
        for idx, row in filtered_df.iterrows():
            try:
                ts_id = row['ts_id']
                result_row = self._process_single_group(ts_id, row, default_config, num_counter)
                if result_row:
                    self.results.append(result_row)
                    num_counter += 1
            except Exception as e:
                if self.verbose:
                    print(f"Error processing ts_id={ts_id}: {e}")
                continue
        
        return len(self.results) > 0, valid_ts_ids
    
    def _process_single_group(self, ts_id: int, row: pd.Series, config: Dict[str, Any], num: int) -> Optional[Dict[str, Any]]:
        
        try:
            pattern_name = str(row['pattern_name'])
            pattern_index = ast.literal_eval(row['pattern_index'])
            option_index = ast.literal_eval(row['option_index'])
            dtw_distances = ast.literal_eval(row['dtw_distance'])
            
            if (not isinstance(pattern_index, list) or len(pattern_index) != 2 or
                not isinstance(option_index, list) or not isinstance(dtw_distances, list) or
                len(option_index) != len(dtw_distances)):
                return None
            
            pattern_start, pattern_end = int(pattern_index[0]), int(pattern_index[1])
            if not self._validate_indices(ts_id, pattern_start, pattern_end):
                return None
            
            ts0_data = self._extract_data_segment(ts_id, pattern_start, pattern_end)
            if ts0_data is None:
                return None
            
            ts_segments = [ts0_data]
            
            for seg_idx in option_index:
                if isinstance(seg_idx, list) and len(seg_idx) == 2:
                    seg_start, seg_end = int(seg_idx[0]), int(seg_idx[1])
                    if self._validate_indices(ts_id, seg_start, seg_end):
                        seg_data = self._extract_data_segment(ts_id, seg_start, seg_end)
                        if seg_data is not None:
                            ts_segments.append(seg_data)
            
            if len(ts_segments) <= 1:
                return None
            
            return {
                'num': num,
                'ts_id': ts_id,
                'qa_type': config['qa_type'],
                'local_overall': config['local_overall'],
                'task_type': str(config['task_type']),
                'question': str(config['question_template'].format(ts_id)),
                'option': str(config['option']),
                'answer': str(config['answer']),
                'domain': config['domain'],
                'freq': config['freq'],
                'is_univariate': config['is_univariate'],
                'value': str(ts_segments),
                'pattern_name': pattern_name,
                'pattern_index': pattern_index,
                'option_index': option_index,
                'dtw_distance': dtw_distances
            }
            
        except Exception as e:
            if self.verbose:
                print(f"Failed to process ts_id={ts_id}: {e}")
            return None
    
    
    def _validate_indices(self, ts_id: int, start_idx: int, end_idx: int) -> bool:
        if (ts_id >= len(self.dataset) or 
            end_idx >= self.dataset.shape[1] or 
            start_idx < 0 or 
            end_idx < start_idx):
            return False
        return True
    
    def save_results(self, output_path: str) -> bool:
        if not self.results:
            return False
        
        try:
            output_df = pd.DataFrame(self.results)
            output_df.to_csv(output_path, index=False)
            if self.verbose:
                print(f"Results saved to: {output_path}, total {len(self.results)} records")
            return True
        except Exception as e:
            if self.verbose:
                print(f"Failed to save file: {e}")
            return False
    
    def get_results(self) -> List[Dict[str, Any]]:
        return self.results
    
    def get_results_dataframe(self) -> Optional[pd.DataFrame]:
        if not self.results:
            return None
        return pd.DataFrame(self.results)
    
    def process_and_save(self, input_csv_path: str, dataset_path: str, output_csv_path: str,
                    data_column: str = 'target', output_config: Optional[Dict[str, Any]] = None,
                    scale_factor: float = 1.0, decimal_places: int = 2, 
                    dtw_threshold: Optional[List[Dict[str, Any]]] = None) -> bool:
        try:
            self.scale_factor = scale_factor
            self.decimal_places = decimal_places
            
            if self.verbose:
                print(f"Numerical processing parameters: scale_factor={self.scale_factor}, decimal_places={self.decimal_places}")
                if dtw_threshold is not None:
                    print(f"DTW filter rules count: {len(dtw_threshold)}")
            
            if not self.load_input_csv(input_csv_path):
                return False
            
            if not self.load_dataset(dataset_path, data_column):
                return False
            
            success, valid_ts_ids = self.process_data(output_config, dtw_threshold)
            if not success:
                return False
            
            if not self.save_results(output_csv_path):
                return False
            
            if self.verbose:
                print(f"Processing completed! Output file: {output_csv_path}")
                print(f"Successfully processed {len(self.results)} records")
                print(f"Valid ts_id count: {len(valid_ts_ids)}")
            
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"Processing failed: {e}")
            return False