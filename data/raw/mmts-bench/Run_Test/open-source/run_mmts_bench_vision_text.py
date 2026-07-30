import pandas as pd
import openai
import json
import time
import os
from tqdm import tqdm
import logging
from typing import Optional, List, Dict, Any, Set, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from datetime import datetime
import numpy as np
import ast
import matplotlib.pyplot as plt
import base64
import io

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('csv_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CSVOpenAIProcessor:
    def __init__(self, 
                 csv_path: str,
                 base_url: str = "http://127.0.0.1:18001/v1",
                 api_key: str = "any-key",
                 model: str = "qwen2.5-vl-7b-instruct",
                 real_model_name: Optional[str] = None,
                 output_dir: Optional[str] = None,
                 max_workers: int = 5,
                 save_interval: int = 10,
                 max_retries: int = 3,
                 retry_delay: float = 0.2,
                 n_evaluations: int = 5,
                 temperature: float = 1.0,
                 max_tokens: int = 4096,
                 use_precomputed_base64: bool = True,
                 api_timeout: float = 45.0):
        """
        Initialize CSV processor
        
        Args:
            csv_path: Path to CSV file
            base_url: OpenAI API base URL
            api_key: API key
            model: Model name (used for naming files and columns)
            real_model_name: Actual model name to call (if None, uses model)
            output_dir: Output directory path (if None, auto-created)
            max_workers: Maximum concurrent threads
            save_interval: Save interval (saves after processing N tasks)
            max_retries: Maximum retry attempts per request
            retry_delay: Delay between requests
            n_evaluations: Number of evaluations per question
            use_precomputed_base64: Whether to use precomputed base64 data
            api_timeout: API timeout in seconds
        """
        self.csv_path = csv_path
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.real_model_name = real_model_name if real_model_name is not None else model
        self.max_workers = max_workers
        self.save_interval = save_interval
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.n_evaluations = n_evaluations
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.use_precomputed_base64 = use_precomputed_base64
        self.api_timeout = api_timeout
        
        self.client = openai.OpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=api_timeout
        )
        
        base_name = os.path.splitext(os.path.basename(csv_path))[0]
        model_clean = model.replace('-', '_')
        
        if output_dir is None:
            csv_dir = os.path.dirname(csv_path)
            rollout_dir = os.path.join(csv_dir, "rollout", model_clean)
        else:
            rollout_dir = output_dir
        
        os.makedirs(rollout_dir, exist_ok=True)
        
        self.output_file = os.path.join(rollout_dir, f"{base_name}_{model_clean}_processed.csv")
        self.checkpoint_file = os.path.join(rollout_dir, f"{base_name}_{model_clean}_checkpoint.json")
        self.progress_file = os.path.join(rollout_dir, f"{base_name}_{model_clean}_progress.csv")
        
        csv_dir = os.path.dirname(csv_path)
        self.precomputed_csv_path = os.path.join(csv_dir, f"{base_name}_with_base64.csv")
        
        self.response_column = f"{model_clean}_response"
        self.response_details_column = f"{model_clean}_response_details"
        self.response_avg_column = f"{model_clean}_response_avg"
        
        self.lock = threading.Lock()
        self.completed_tasks_map: Dict[int, Dict[str, Any]] = {}
        self.original_df: Optional[pd.DataFrame] = None
        
    def _safe_init_dataframe_columns(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Safely initialize new columns in DataFrame"""
        for col in columns:
            if col not in df.columns:
                if col.endswith('_details') or col == self.response_column:
                    df[col] = pd.Series([[] for _ in range(len(df))], dtype=object, index=df.index)
                elif col.endswith('_avg'):
                    df[col] = 0.0
                else:
                    df[col] = ''
            else:
                if col.endswith('_details') or col == self.response_column:
                    df[col] = df[col].astype('object')
                    for i in df.index:
                        if not isinstance(df.at[i, col], list):
                            df.at[i, col] = []
        return df

    def load_data(self) -> pd.DataFrame:
        """Load CSV data, preferring precomputed base64 data"""
        try:
            if self.use_precomputed_base64 and os.path.exists(self.precomputed_csv_path):
                logger.info(f"Loading precomputed CSV with base64 data: {self.precomputed_csv_path}")
                df = pd.read_csv(self.precomputed_csv_path)
                
                if 'image_base64' in df.columns:
                    logger.info(f"Successfully loaded precomputed CSV file with {len(df)} rows and base64 data")
                else:
                    logger.warning("Precomputed CSV exists but lacks 'image_base64' column, fallback to original CSV")
                    df = pd.read_csv(self.csv_path)
            else:
                logger.info(f"Loading original CSV file: {self.csv_path}")
                df = pd.read_csv(self.csv_path)
            
            required_columns = ['question', 'value', 'option']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                logger.error(f"Missing required columns: {missing_columns}")
                logger.info(f"Available columns: {list(df.columns)}")
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            self.original_df = df.copy()
            
            new_columns = [self.response_column, self.response_details_column, self.response_avg_column]
            df = self._safe_init_dataframe_columns(df, new_columns)
            
            return df
        except Exception as e:
            logger.error(f"Failed to load CSV file: {e}")
            raise
    
    def load_checkpoint_state(self) -> Set[int]:
        """
        Load checkpoint state, return set of completed tasks
        
        Returns:
            Set of completed task row indices
        """
        if not os.path.exists(self.checkpoint_file):
            return set()
        
        try:
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            
            completed_tasks = set()
            self.completed_tasks_map = {}
            
            for row_idx_str, task_result in checkpoint_data.items():
                try:
                    row_idx = int(row_idx_str)
                    completed_tasks.add(row_idx)
                    self.completed_tasks_map[row_idx] = task_result
                except ValueError:
                    logger.warning(f"Skipping invalid checkpoint task key: {row_idx_str}")
                    continue
            
            logger.info(f"Loaded {len(completed_tasks)} completed tasks from checkpoint")
            return completed_tasks
            
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}, starting from scratch")
            return set()
    
    def save_checkpoint_state(self, completed_tasks: Dict[int, Dict[str, Any]]):
        """
        Save checkpoint state (saves both JSON and CSV formats)
        
        Args:
            completed_tasks: Dictionary of completed tasks
        """
        try:
            checkpoint_data = {}
            for row_idx, task_result in completed_tasks.items():
                checkpoint_data[str(row_idx)] = task_result
            
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
            
            if self.original_df is not None and len(completed_tasks) > 0:
                progress_df = self.original_df.copy()
                
                new_columns = [self.response_column, self.response_details_column, self.response_avg_column]
                progress_df = self._safe_init_dataframe_columns(progress_df, new_columns)
                
                self.update_dataframe_with_results(progress_df, completed_tasks)
                progress_df = self._add_progress_columns(progress_df, completed_tasks)
                
                progress_df.to_csv(self.progress_file, index=False, encoding='utf-8')
                
                total_rows = len(progress_df)
                completed_rows = len(completed_tasks)
                progress_percent = (completed_rows / total_rows * 100) if total_rows > 0 else 0
                
                logger.info(f"Checkpoint saved: JSON + CSV format")
                logger.info(f"  - Contains {len(completed_tasks)} completed tasks")
                logger.info(f"  - Overall progress: {completed_rows}/{total_rows} ({progress_percent:.1f}%)")
                logger.info(f"  - Progress file: {self.progress_file}")
            else:
                logger.info(f"Checkpoint saved: JSON format only ({len(completed_tasks)} tasks)")
            
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")

    def _add_progress_columns(self, df: pd.DataFrame, completed_tasks: Dict[int, Dict[str, Any]]) -> pd.DataFrame:
        """
        Add progress statistics columns to DataFrame
        
        Args:
            df: Target DataFrame
            completed_tasks: Dictionary of completed tasks
            
        Returns:
            DataFrame with progress columns added
        """
        completion_status = []
        success_status = []
        evaluation_counts = []
        success_rates = []
        
        for idx in range(len(df)):
            if idx in completed_tasks:
                task_result = completed_tasks[idx]
                success_count = task_result.get('success_count', 0)
                total_evaluations = task_result.get('total_evaluations', self.n_evaluations)
                
                completion_status.append('Completed')
                if success_count > 0:
                    success_status.append('Success')
                    success_rate = success_count / total_evaluations if total_evaluations > 0 else 0.0
                    success_rates.append(round(success_rate, 3))
                else:
                    success_status.append('Failed')
                    success_rates.append(0.0)
                
                evaluation_counts.append(f"{success_count}/{total_evaluations}")
            else:
                completion_status.append('Pending')
                success_status.append('Pending')
                evaluation_counts.append(f"0/{self.n_evaluations}")
                success_rates.append(0.0)
        
        df['completion_status'] = completion_status
        df['success_status'] = success_status
        df['evaluation_counts'] = evaluation_counts
        df['success_rates'] = success_rates
        
        return df

    def get_image_base64(self, row_idx: int, value: str) -> str:
        """
        Get base64 encoding of image, preferring precomputed data
        
        Args:
            row_idx: Row index
            value: Time series data
            
        Returns:
            Base64 encoded image data
        """
        try:
            if 'image_base64' in self.original_df.columns:
                precomputed_base64 = self.original_df.iloc[row_idx]['image_base64']
                if pd.notna(precomputed_base64) and precomputed_base64 != '':
                    logger.debug(f"Using precomputed base64 for row {row_idx}")
                    return precomputed_base64
            
            logger.warning(f"No precomputed base64 for row {row_idx}, generating on-the-fly")
            return self.create_time_series_image_base64(value)
            
        except Exception as e:
            logger.error(f"Failed to get base64 for row {row_idx}: {e}")
            return self.create_time_series_image_base64(value)

    def create_time_series_image_base64(self, value: str) -> str:
        """
        Create time series image and return base64 encoding (fallback method)
        
        Args:
            value: Time series data string
            
        Returns:
            Base64 encoded image data
        """
        try:
            value_list = ast.literal_eval(value)
            
            plt.figure(figsize=(8, 6), dpi=72)
            
            if len(value_list) > 8:
                plt.plot(range(len(value_list)), value_list, 'b-', linewidth=1.5)
                plt.title('Time Series', fontsize=12)
                plt.xlabel('Time Index', fontsize=10)
                plt.ylabel('Value', fontsize=10)
                plt.grid(True, alpha=0.3)
            else:
                num_channels = len(value_list)
                rows = num_channels
                cols = 1
                
                for i, channel_data in enumerate(value_list):
                    plt.subplot(rows, cols, i + 1)
                    plt.plot(range(len(channel_data)), channel_data, 'b-', linewidth=1.5)
                    plt.title(f'Time Series {i+1}', fontsize=10)
                    plt.xlabel('Time Index', fontsize=8)
                    plt.ylabel('Value', fontsize=8)
                    plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0.1)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return image_base64
            
        except Exception as e:
            logger.error(f"Failed to create time series image: {e}")
            plt.close()
            return ""

    def create_prompt(self, question: str, value: str, option: str, row_idx: int) -> str:
        """Create prompt using precomputed base64 data"""

        system_prompt = """You are an expert AI assistant specialized in answering multiple-choice questions with high accuracy and consistency. Your task is to analyze questions carefully and provide clear, well-reasoned answers.

IMPORTANT INSTRUCTIONS:
1. You must select your answer from the given options only
2. Your final answer must be a single letter (A, B, C, D, etc.)
3. If the question seems ambiguous, choose the most reasonable interpretation
4. Do not make up information not provided in the question

RESPONSE FORMAT:
You must structure your final answer exactly as follows:

<final_answer>
[State your chosen option as a single letter: A, B, C, or D]
</final_answer>

Remember: Your final answer should contain ONLY the letter of your chosen option, nothing else."""

        value_list = ast.literal_eval(value)
        given_values = []
        if len(value_list) > 10:
            given_values.append(f"Given Time Series: {value_list}")
        else:
            for i, val in enumerate(value_list):
                given_values.append(f"Given Time Series {i+1}: {val}")
        given_values_str = "\n".join(given_values)
        
        image_base64 = self.get_image_base64(row_idx, value)

        user_prompt = f"""Please answer the following multiple-choice question based on the given information:

Question: {question}

{given_values_str}

The time series data is shown in the image below.

Available Options: {option}

Please analyze this question carefully, consider the given time series data shown in the image and all available options, then provide your answer following the exact format specified in the system instructions."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]

        return messages
    
    def call_api_multiple_times(self, prompt: str, row_idx: int) -> Dict[str, Any]:
        """
        Make multiple API calls for a single question
        
        Args:
            prompt: Prompt text
            row_idx: Row index
            
        Returns:
            Dictionary containing multiple evaluation results
        """
        responses = []
        final_answers = []
        extracted_options = []
        
        for eval_idx in range(self.n_evaluations):
            for attempt in range(self.max_retries):
                try:
                    logger.info(f"Processing row {row_idx + 1}, evaluation {eval_idx + 1}/{self.n_evaluations}, attempt {attempt + 1}/{self.max_retries}")
                    
                    if 'gpt-5' in self.real_model_name:
                        response = self.client.chat.completions.create(
                            model=self.real_model_name,
                            messages=prompt,
                            max_completion_tokens=self.max_tokens,
                            temperature=self.temperature
                        )
                    else:
                        response = self.client.chat.completions.create(
                            model=self.real_model_name,
                            messages=prompt,
                            max_tokens=self.max_tokens,
                            temperature=self.temperature
                        )
                    
                    response_content = response.choices[0].message.content
                    final_answer = self.extract_final_answer(response_content)
                    extracted_option = self.extract_option_from_response(response_content)
                    
                    responses.append(response_content)
                    final_answers.append(final_answer)
                    extracted_options.append(extracted_option)
                    
                    time.sleep(self.retry_delay)
                    break
                    
                except openai.APITimeoutError:
                    error_msg = "API request timeout"
                    logger.warning(f"Row {row_idx + 1}, evaluation {eval_idx + 1}, attempt {attempt + 1}: {error_msg}")
                    
                except openai.APIError as e:
                    error_msg = f"API error: {str(e)}"
                    logger.warning(f"Row {row_idx + 1}, evaluation {eval_idx + 1}, attempt {attempt + 1}: {error_msg}")
                    
                except Exception as e:
                    error_msg = f"Unexpected error: {str(e)}"
                    logger.error(f"Row {row_idx + 1}, evaluation {eval_idx + 1}, attempt {attempt + 1}: {error_msg}")
                
                if attempt < self.max_retries:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.info(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
            
            if len(responses) <= eval_idx:
                responses.append(f"API call failed: {error_msg}")
                final_answers.append("")
                extracted_options.append("")
        
        success_count = sum(1 for response in responses if not response.startswith("API call failed"))
        
        valid_answers = [ans for ans in final_answers if ans and not ans == ""]
        valid_options = [opt for opt in extracted_options if opt and not opt == ""]
        
        if valid_answers:
            from collections import Counter
            answer_counts = Counter(valid_answers)
            best_answer = answer_counts.most_common(1)[0][0]
        else:
            best_answer = ""
        
        if valid_options:
            from collections import Counter
            option_counts = Counter(valid_options)
            best_option = option_counts.most_common(1)[0][0]
        else:
            best_option = ""
        
        return {
            'row_idx': row_idx,
            'success': success_count > 0,
            'responses': responses,
            'final_answers': final_answers,
            'extracted_options': extracted_options,
            'best_answer': best_answer,
            'best_option': best_option,
            'success_count': success_count,
            'total_evaluations': self.n_evaluations,
            'error': None if success_count > 0 else "All evaluations failed"
        }
    
    def extract_final_answer(self, response: str) -> str:
        """Extract final answer from response"""
        try:
            import re
            match = re.search(r'<final_answer>(.*?)</final_answer>', response, re.DOTALL)
            if match:
                return match.group(1).strip()
            else:
                return response.strip()
        except Exception as e:
            logger.warning(f"Failed to extract final answer: {e}")
            return response.strip() if response else ""
    
    def extract_option_from_response(self, response: str) -> str:
        """Extract option answer from response"""
        try:
            final_answer = self.extract_final_answer(response)
            
            import re
            
            option_pattern1 = r'\b([A-Z])\b'
            matches1 = re.findall(option_pattern1, final_answer)
            if matches1:
                return matches1[0]
            
            option_pattern2 = r'(?:answer is|choose|option)\s*([A-Z])'
            matches2 = re.findall(option_pattern2, final_answer, re.IGNORECASE)
            if matches2:
                return matches2[0]
            
            option_pattern3 = r'[\(\[]([A-Z])[\)\]]'
            matches3 = re.findall(option_pattern3, final_answer)
            if matches3:
                return matches3[0]
            
            option_pattern4 = r'\b([A-Z])\b'
            matches4 = re.findall(option_pattern4, response)
            if matches4:
                return matches4[-1]
            
            return ""
            
        except Exception as e:
            logger.warning(f"Failed to extract option from response: {e}")
            return ""
    
    def create_remaining_tasks(self, df: pd.DataFrame, completed_tasks: Set[int]) -> List[Dict[str, Any]]:
        """
        Create remaining tasks to process
        
        Args:
            df: Data DataFrame
            completed_tasks: Set of completed tasks
        
        Returns:
            List of remaining tasks
        """
        tasks = []
        for row_idx in range(len(df)):
            if row_idx not in completed_tasks:
                row = df.iloc[row_idx]
                prompt = self.create_prompt(
                    str(row['question']), 
                    str(row['value']), 
                    str(row['option']),
                    row_idx
                )
                
                task_info = {
                    'row_idx': row_idx,
                    'prompt': prompt,
                    'question': str(row['question']),
                    'value': str(row['value']),
                    'option': str(row['option'])
                }
                tasks.append(task_info)
        
        return tasks
    
    def process_single_task(self, task_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single task (including multiple evaluations)
        
        Args:
            task_info: Dictionary containing task information
        
        Returns:
            Processing result dictionary
        """
        row_idx = task_info['row_idx']
        prompt = task_info['prompt']
        
        try:
            result = self.call_api_multiple_times(prompt, row_idx)
            return result
        except Exception as e:
            logger.error(f"Failed to process row {row_idx + 1}: {str(e)}")
            return {
                'row_idx': row_idx,
                'success': False,
                'responses': [f"Task execution failed: {str(e)}"] * self.n_evaluations,
                'final_answers': [""] * self.n_evaluations,
                'extracted_options': [""] * self.n_evaluations,
                'best_option': "",
                'success_count': 0,
                'total_evaluations': self.n_evaluations,
                'error': str(e)
            }
    
    def update_dataframe_with_results(self, df: pd.DataFrame, completed_tasks_map: Dict[int, Dict[str, Any]]):
        """
        Update DataFrame with completed task results
        
        Args:
            df: Target DataFrame
            completed_tasks_map: Map of completed task results
        """
        for row_idx, task_result in completed_tasks_map.items():
            if row_idx < len(df):
                extracted_options = task_result.get('extracted_options', [])
                df.at[row_idx, self.response_column] = extracted_options
                
                df.at[row_idx, self.response_details_column] = task_result.get('responses', [])
                
                success_count = task_result.get('success_count', 0)
                total_evaluations = task_result.get('total_evaluations', self.n_evaluations)
                success_rate = (success_count / total_evaluations) if total_evaluations > 0 else 0.0
                df.at[row_idx, self.response_avg_column] = round(success_rate, 3)
    
    def restore_results_to_dataframe(self, df: pd.DataFrame):
        """
        Restore completed task results to DataFrame
        
        Args:
            df: Target DataFrame
        """
        if self.completed_tasks_map:
            logger.info("Restoring completed task results to DataFrame...")
            self.update_dataframe_with_results(df, self.completed_tasks_map)
            logger.info(f"Restored {len(self.completed_tasks_map)} task results")
    
    def run_processing(self):
        """Run complete processing workflow"""
        start_time = datetime.now()
        logger.info(f"Starting CSV OpenAI processing task: {start_time}")
        logger.info(f"Each question will be evaluated {self.n_evaluations} times")
        logger.info(f"Max concurrent workers: {self.max_workers}")
        logger.info(f"Model for naming: {self.model}")
        logger.info(f"Real model for API: {self.real_model_name}")
        logger.info(f"Base URL: {self.base_url}")
        logger.info(f"Output directory: {os.path.dirname(self.output_file)}")
        logger.info(f"Use precomputed base64: {self.use_precomputed_base64}")
        
        df = self.load_data()
        completed_tasks = self.load_checkpoint_state()
        
        if completed_tasks:
            self.restore_results_to_dataframe(df)
        
        remaining_tasks = self.create_remaining_tasks(df, completed_tasks)
        total_tasks = len(remaining_tasks)
        
        logger.info(f"Total tasks: {len(completed_tasks) + total_tasks}")
        logger.info(f"Completed tasks: {len(completed_tasks)}")
        logger.info(f"Remaining tasks: {total_tasks}")
        
        if total_tasks == 0:
            logger.info("All tasks are already completed, no further processing needed")
            df.to_csv(self.output_file, index=False, encoding='utf-8')
            logger.info(f"Final results saved to: {self.output_file}")
            return
        
        completed_count = 0
        
        try:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_task = {
                    executor.submit(self.process_single_task, task): task 
                    for task in remaining_tasks
                }
                
                with tqdm(total=total_tasks, desc="Processing Progress") as pbar:
                    for future in as_completed(future_to_task):
                        try:
                            result = future.result()
                            
                            row_idx = result['row_idx']
                            with self.lock:
                                self.completed_tasks_map[row_idx] = result
                                completed_count += 1
                            
                            success_count = result.get('success_count', 0)
                            total_evals = result.get('total_evaluations', self.n_evaluations)
                            success_status = f"✓{success_count}/{total_evals}" if result['success'] else f"✗{success_count}/{total_evals}"
                            
                            overall_success = sum(r.get('success_count', 0) for r in self.completed_tasks_map.values())
                            overall_total = len(self.completed_tasks_map) * self.n_evaluations
                            
                            pbar.set_postfix({
                                'Current': f"Row {row_idx + 1} {success_status}",
                                'Overall': f"{overall_success}/{overall_total}"
                            })
                            pbar.update(1)
                            
                            if completed_count % self.save_interval == 0:
                                with self.lock:
                                    self.save_checkpoint_state(self.completed_tasks_map)
                                    self.update_dataframe_with_results(df, self.completed_tasks_map)
                                    df.to_csv(self.output_file, index=False, encoding='utf-8')
                                    logger.info(f"Completed {completed_count}/{total_tasks} tasks")
                            
                        except Exception as e:
                            task = future_to_task[future]
                            row_idx = task['row_idx']
                            logger.error(f"Task execution failed: row {row_idx + 1}: {str(e)}")
                            
                            error_result = {
                                'row_idx': row_idx,
                                'success': False,
                                'response': f"Task execution failed: {str(e)}",
                                'final_answer': "",
                                'error': str(e),
                                'attempts': 0
                            }
                            
                            with self.lock:
                                self.completed_tasks_map[row_idx] = error_result
                                completed_count += 1
                            
                            pbar.update(1)
            
            self.save_checkpoint_state(self.completed_tasks_map)
            
            logger.info("Updating DataFrame and saving final results...")
            self.update_dataframe_with_results(df, self.completed_tasks_map)
            
            logger.info(f"Saving final results to: {self.output_file}")
            df.to_csv(self.output_file, index=False, encoding='utf-8')
            
            end_time = datetime.now()
            duration = end_time - start_time
            logger.info(f"Processing task completed! Duration: {duration}")
            
            self.print_statistics()
            
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, saving current progress...")
            with self.lock:
                self.save_checkpoint_state(self.completed_tasks_map)
                logger.info(f"Saved results for {len(self.completed_tasks_map)} tasks")
            
        except Exception as e:
            logger.error(f"Serious error occurred during processing: {str(e)}")
            with self.lock:
                self.save_checkpoint_state(self.completed_tasks_map)
            raise
    
    def print_statistics(self):
        """Print processing statistics"""
        logger.info("=== Processing Statistics ===")
        
        total_tasks = len(self.completed_tasks_map)
        successful_tasks = sum(1 for result in self.completed_tasks_map.values() if result['success'])
        failed_tasks = total_tasks - successful_tasks
        
        total_evaluations = sum(result.get('total_evaluations', self.n_evaluations) for result in self.completed_tasks_map.values())
        successful_evaluations = sum(result.get('success_count', 0) for result in self.completed_tasks_map.values())
        
        total_options_extracted = 0
        total_possible_extractions = 0
        
        for result in self.completed_tasks_map.values():
            extracted_options = result.get('extracted_options', [])
            total_possible_extractions += len(extracted_options)
            total_options_extracted += sum(1 for opt in extracted_options if opt and opt != '')
        
        logger.info(f"Total processed tasks: {total_tasks}")
        logger.info(f"Successful tasks: {successful_tasks}")
        logger.info(f"Failed tasks: {failed_tasks}")
        logger.info(f"Evaluations per task: {self.n_evaluations}")
        logger.info(f"Total evaluations: {total_evaluations}")
        logger.info(f"Successful evaluations: {successful_evaluations}")
        logger.info(f"Total option extractions: {total_options_extracted}/{total_possible_extractions}")
        
        if total_tasks > 0:
            task_success_rate = (successful_tasks / total_tasks) * 100
            logger.info(f"Task success rate: {task_success_rate:.1f}%")
        
        if total_evaluations > 0:
            evaluation_success_rate = (successful_evaluations / total_evaluations) * 100
            logger.info(f"Evaluation success rate: {evaluation_success_rate:.1f}%")
        
        if total_possible_extractions > 0:
            option_extraction_rate = (total_options_extracted / total_possible_extractions) * 100
            logger.info(f"Option extraction rate: {option_extraction_rate:.1f}%")
        
        if self.completed_tasks_map:
            success_rates = []
            option_extraction_rates = []
            
            for result in self.completed_tasks_map.values():
                success_count = result.get('success_count', 0)
                total_evals = result.get('total_evaluations', self.n_evaluations)
                if total_evals > 0:
                    success_rates.append(success_count / total_evals)
                
                extracted_options = result.get('extracted_options', [])
                if len(extracted_options) > 0:
                    option_count = sum(1 for opt in extracted_options if opt and opt != '')
                    option_extraction_rates.append(option_count / len(extracted_options))
            
            if success_rates:
                avg_success_rate = np.mean(success_rates) * 100
                std_success_rate = np.std(success_rates) * 100
                logger.info(f"Average task success rate: {avg_success_rate:.1f}% ± {std_success_rate:.1f}%")
                logger.info(f"Best task success rate: {max(success_rates) * 100:.1f}%")
                logger.info(f"Worst task success rate: {min(success_rates) * 100:.1f}%")
            
            if option_extraction_rates:
                avg_option_rate = np.mean(option_extraction_rates) * 100
                std_option_rate = np.std(option_extraction_rates) * 100
                logger.info(f"Average option extraction rate: {avg_option_rate:.1f}% ± {std_option_rate:.1f}%")
                logger.info(f"Best option extraction rate: {max(option_extraction_rates) * 100:.1f}%")
                logger.info(f"Worst option extraction rate: {min(option_extraction_rates) * 100:.1f}%")
    
    def get_statistics(self):
        """Get processing statistics (for external calls)"""
        if os.path.exists(self.output_file):
            df = pd.read_csv(self.output_file)
            total = len(df)
            
            if self.response_column in df.columns:
                processed = 0
                for idx, row in df.iterrows():
                    try:
                        response_value = row[self.response_column]
                        if pd.notna(response_value) and response_value != '' and response_value != '[]':
                            if isinstance(response_value, str):
                                try:
                                    import ast
                                    parsed_list = ast.literal_eval(response_value)
                                    if isinstance(parsed_list, list) and len(parsed_list) > 0:
                                        non_empty_options = [opt for opt in parsed_list if opt and opt != '']
                                        if non_empty_options:
                                            processed += 1
                                except:
                                    pass
                            elif isinstance(response_value, list) and len(response_value) > 0:
                                non_empty_options = [opt for opt in response_value if opt and opt != '']
                                if non_empty_options:
                                    processed += 1
                    except:
                        continue
                
                if self.response_avg_column in df.columns:
                    avg_success_rates = df[self.response_avg_column].replace(0, np.nan).dropna()
                    if len(avg_success_rates) > 0:
                        overall_avg_success = avg_success_rates.mean() * 100
                        
                        total_options_extracted = 0
                        total_possible_options = 0
                        
                        for idx, row in df.iterrows():
                            try:
                                response_value = row[self.response_column]
                                if pd.notna(response_value) and response_value != '' and response_value != '[]':
                                    if isinstance(response_value, str):
                                        try:
                                            import ast
                                            parsed_list = ast.literal_eval(response_value)
                                            if isinstance(parsed_list, list):
                                                total_possible_options += len(parsed_list)
                                                total_options_extracted += sum(1 for opt in parsed_list if opt and opt != '')
                                        except:
                                            pass
                                    elif isinstance(response_value, list):
                                        total_possible_options += len(response_value)
                                        total_options_extracted += sum(1 for opt in response_value if opt and opt != '')
                            except:
                                continue
                        
                        option_extraction_rate = (total_options_extracted / total_possible_options * 100) if total_possible_options > 0 else 0
                        
                        print(f"\nProcessing Statistics:")
                        print(f"Total rows: {total}")
                        print(f"Processed rows: {processed}")
                        print(f"Evaluations per row: {self.n_evaluations}")
                        print(f"Average success rate per row: {overall_avg_success:.1f}%")
                        print(f"Best performing row: {avg_success_rates.max() * 100:.1f}%")
                        print(f"Worst performing row: {avg_success_rates.min() * 100:.1f}%")
                        print(f"Option extraction rate: {option_extraction_rate:.1f}%")
                        print(f"Total options extracted: {total_options_extracted}/{total_possible_options}")
                    else:
                        print(f"\nProcessing Statistics:")
                        print(f"Total rows: {total}")
                        print(f"Processed rows: {processed}")
                        print(f"No successful evaluations found")
                else:
                    print(f"\nProcessing Statistics:")
                    print(f"Total rows: {total}")
                    print(f"Processed rows: {processed}")
                    print(f"Evaluations per row: {self.n_evaluations}")
            else:
                print(f"\nProcessing Statistics:")
                print(f"Total rows: {total}")
                print(f"No processing results found")
        else:
            print("Output file not found. No statistics available.")

def main():
    """Main function - directly set parameters"""
    CSV_PATH = "/path/to/your/dataset.csv"
    MODEL = "qwen2.5-vl-7b-instruct"
    REAL_MODEL_NAME = "qwen2.5-vl-7b-instruct"
    OUTPUT_DIR = "/path/to/output/directory"
    TEMPERATURE = 1.0
    MAX_TOKENS = 16384
    MAX_WORKERS = 5
    SAVE_INTERVAL = 10
    MAX_RETRIES = 3
    RETRY_DELAY = 0.2
    N_EVALUATIONS = 5
    SHOW_STATS_ONLY = False
    USE_PRECOMPUTED_BASE64 = True
    API_TIMEOUT = 45.0
    
    logger.info("=== Configuration ===")
    logger.info(f"CSV Path: {CSV_PATH}")
    logger.info(f"Model (for naming): {MODEL}")
    logger.info(f"Real Model (for API): {REAL_MODEL_NAME}")
    logger.info(f"Output Directory: {OUTPUT_DIR}")
    logger.info(f"Max Workers: {MAX_WORKERS}")
    logger.info(f"Save Interval: {SAVE_INTERVAL}")
    logger.info(f"Max Retries: {MAX_RETRIES}")
    logger.info(f"Retry Delay: {RETRY_DELAY}")
    logger.info(f"N Evaluations: {N_EVALUATIONS}")
    logger.info(f"Use Precomputed Base64: {USE_PRECOMPUTED_BASE64}")
    logger.info(f"API Timeout: {API_TIMEOUT}s")
    logger.info(f"Output: Options will be extracted to {MODEL.replace('-', '_')}_response column as a list")
    logger.info("=" * 50)
    
    processor = CSVOpenAIProcessor(
        csv_path=CSV_PATH,
        model=MODEL,
        real_model_name=REAL_MODEL_NAME,
        output_dir=OUTPUT_DIR,
        max_workers=MAX_WORKERS,
        save_interval=SAVE_INTERVAL,
        max_retries=MAX_RETRIES,
        retry_delay=RETRY_DELAY,
        n_evaluations=N_EVALUATIONS,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        use_precomputed_base64=USE_PRECOMPUTED_BASE64,
        api_timeout=API_TIMEOUT
    )
    
    if SHOW_STATS_ONLY:
        processor.get_statistics()
    else:
        processor.run_processing()
        processor.get_statistics()

if __name__ == "__main__":
    main()