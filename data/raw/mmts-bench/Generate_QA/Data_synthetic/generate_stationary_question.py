import json
import os
import random
import numpy as np
import pandas as pd

def json2csv(json_file, csv_file, selected_columns=None):
    """
    Args:
        json_file: json path
        csv_file: csv path
        selected_columns:  List of column names to retain, defaults to None meaning all columns are kept
    """
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: file {json_file} not exit!")
        return
    except json.JSONDecodeError:
        print(f"Error: file {json_file} is not a valid JSON.")
        return

    new_data = []
    
    for idx, item in enumerate(data, start=1):
        qa_type_map = {
            'a multiple choice question': 'a multiple choice question',
            'numerical': 'numerical'
        }
        qa_type = qa_type_map.get(item.get('qa_type', 'numerical'), 'numerical')   
        # Determine task type from task_type
        task_type_map = {
            'trend': 'trend analysis',
            'seasonal': 'seasonality analysis',
            'noise': 'noise analysis',
            'basic': 'basic analysis',
            'multivar': 'basic analysis'
        }
        task_type = task_type_map.get(item.get('task_type', 'basic'), 'basic analysis')
        
        # Check if single variable
        values = item.get('values', [])
        is_univariate = True
        if isinstance(values, dict):
            # Multi-variable case: 'values' is a dict
            is_univariate = False
            # Convert dict to list of lists
            value_list = [values.get('Time Series 1', []), values.get('Time Series 2', [])]
        elif isinstance(values, list) and len(values) > 0 and isinstance(values[0], list):
            # Multi-variable case: 'values' is a list of lists
            is_univariate = False
            value_list = values
        else:
            # Single variable
            value_list = values
        
        new_item = {
            'num': idx,
            'qa_type': qa_type,
            'local_overall': 'overall',
            'task_type': [task_type],
            'stationarity': True,
            'question': item.get('question', ''),
            'option': item.get('options', None),
            'answer': item.get('answer', ''),
            'domain': 'synthetic',
            'freq': 'unknown',
            'is_univariate': is_univariate,
            'value': value_list
        }
        
        new_data.append(new_item)
    
    output_dir = os.path.dirname(csv_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    df_output = pd.DataFrame(new_data)
    
    # If columns specified, keep only those
    if selected_columns:
        df_output = df_output[selected_columns]
    
    df_output.to_csv(csv_file, index=False, encoding='utf-8', na_rep='')
    print(f"Successfully converted {json_file} to {csv_file}, with a total of {len(new_data)} data entries.")

def get_answer(q_type, template_id, template_params, template_list):
    """Generate answer based on question type and template parameters.
    
    Args:
        q_type: Question type ('trend', 'seasonal', 'noise', 'basic', 'multivar')
        template_id: Template index
        template_params: Dictionary of time series parameters
        template_list: List of question templates
        
    Returns:
        Answer string (option letter or numerical value)
    """
    if q_type == 'trend':
        trend_strength = template_params['trend_strength']
        hurst = template_params['hurst']
        slope = template_params['slope']

        if template_id == 0:
            if slope > 0.1:
                answer = 'A'
            elif slope < -0.1:
                answer = 'B'
            else:
                answer = 'C'
        elif template_id == 1:
            if hurst > 0.55:
                answer = 'A'
            elif hurst < 0.45:
                answer = 'B'
            else:
                answer = 'C'
        elif template_id == 2:
            if trend_strength < 0.5 or (-0.1 < slope < 0.1):
                answer = '0'
            else:
                answer = f'{slope:.2f}'
    elif q_type == 'seasonal':
        seasonal_strength = template_params['seasonal_strength']
        period = template_params['period']
        wave_type = template_params['wave_type']
        noise_type = template_params['noise_type']
        if template_id == 0:
            if noise_type == 'no_noise':
                if wave_type == 'sine':
                    answer = 'A'
                elif wave_type == 'square':
                    answer = 'B'
                elif wave_type == 'triangle':
                    answer = 'C'
                elif wave_type == 'sawtooth':
                    answer = 'D'  
                else:
                    answer = '0'  
            else:
                answer = '0'
        elif template_id == 1:
            if seasonal_strength > 0.8:
                answer = 'A'
            elif seasonal_strength > 0.5:
                answer = 'B'
            elif seasonal_strength > 0.1:
                answer = 'C'
            else:
                answer = 'D'
        elif template_id == 2:
            if seasonal_strength < 0.1 or noise_type != 'no_noise':
                answer = '0'
            else:
                answer = f'{int(period)}'
    elif q_type == 'noise':
        noise_strength = template_params['noise_strength']
        noise_type = template_params['noise_type']
        if template_id == 0:
            if noise_strength > 0.66:
                answer = 'A'
            elif noise_strength > 0.33:
                answer = 'B'
            elif noise_strength > 0.1:
                answer = 'C'
            else:
                answer = 'D'
        elif template_id == 1:
            if noise_type == 'uniform':
                answer = 'A'
            elif noise_type == 'gauss':
                answer = 'B'
            elif noise_type == 'random_walk':
                answer = 'C'
            else:
                answer = 'D'
    elif q_type in {'basic', 'multivar'}:
        answer = template_list[template_id]['answer'].format(**template_params)
    return answer
# Generate numerical questions with balanced univariate and multivariate
def calculate_stats(values):
    """Calculate statistical features for a time series."""
    return {
        'max': max(values),
        'min': min(values),
        'mean': sum(values) / len(values),
        'median': float(np.median(values)),
        'std': float(np.std(values)),
        'PCT50': float(np.percentile(values, 50)),
        'PCT90': float(np.percentile(values, 90)),
        'PCT99': float(np.percentile(values, 99)),
        'range_value': max(values) - min(values),
    }

def load_and_process_values(ts_id):
    """Load and process time series values."""
    features = all_features[ts_id].copy()
    values = np.load(features['values']).astype(float).tolist()
    values = [round(v, 2) for v in values]
    if len(values) > MAX_VALUES_LENGTH:
        values = values[:MAX_VALUES_LENGTH]
    return features, values

def generate_multivariate_question(template_id, template_list):
    """Generate a multivariate question."""
    ts_id = random.sample(range(TOTAL_NUM), 2)
    value_list = []
    feature_list = []
    
    for series_id in ts_id:
        _, values = load_and_process_values(series_id)
        feature_list.append(calculate_stats(values))
        value_list.append(values)
    
    chosen_idx = random.randint(0, 1)
    ts_name = f'Time Series {chosen_idx + 1}'
    template_params = {**feature_list[chosen_idx], 'ts': ts_name}
    question_values = {'Time Series 1': value_list[0], 'Time Series 2': value_list[1]}
    
    return ts_id, template_params, question_values, ts_name

def generate_univariate_question(template_id, template_list):
    """Generate a univariate question."""
    ts_id = random.randint(0, TOTAL_NUM - 1)
    features, values = load_and_process_values(ts_id)
    ts_name = 'Time Series 1'
    
    template_params = {
        **features,
        **calculate_stats(values),
        'ts': ts_name,
    }
    
    return ts_id, template_params, values, ts_name

if __name__ == "__main__":
    # Configuration
    FEATURES_PATH = 'meta_info/stationary/all_features.json'        # Update this path to your features.json file
    OUTPUT_PATH = 'stationary_and_multivar.json'                    # Update this path to your desired output file
    TOTAL_NUM = 500                                                 # Total number of time series available
    TOTAL_QUESTIONS = 600                                           # Total number of questions to generate
    Q_TYPES = ['trend','seasonal','noise','basic','multivar']
    CHOICE_RATIO = 0.5                                              # Ratio of choice questions (0-1)
    MAX_ATTEMPTS = 200                                              # Maximum attempts to find matching answer
    MAX_VALUES_LENGTH = 512                                         # Maximum length of values to include
    templates = {
        'trend': [
            {
                "question":"Here is a list of values in the Time series 1. Based on the Time series 1 data provided, please determine the overall trend direction of the Time series 1.",
                "options": "A) an upward trend \nB) a downward trend \nC) a vague trend",
                "answer": ""
            },
            {
                "question":"Here is a list of values in the Time series 1. Based on the provided Time series 1, please determine whether the Time series 1 exhibits persistence (long-term positive correlation), which means that past trends are likely to continue into the future (For example, if the series has been increasing recently, it is highly likely to continue increasing in the future).It can be measured by the Hurst Exponent.",
                "options": "A) The Hurst exponent (H) is significantly greater than 0.5, indicating that the time series has strong persistence (long-term positive correlation).\nB) The Hurst exponent (H) is significantly less than 0.5, indicating that the time series has strong anti-persistence or mean-reverting behavior (long-term negative correlation).\nC) The Hurst exponent (H) is approximately 0.5, indicating that the time series behaves like a random walk with no long-term memory.\n",
                "answer": ""
            },
            {
                "question":"Based on the provided Time series 1 data, please provide the slope of the Time series 1.",
                "answer": ""
            }
        ],
        'seasonal': [
            {
                "question": "Here is a list of values in the Time series 1. Based on the Time series 1 data provided, what type of waveform does the Time series 1 most resemble?",
                "options": "A) Sine.\nB) Square.\nC) Triangle.\nD) Sawtooth.",
                "answer": ""
            },
            {
                "question": "Here is a list of values in the Time series 1. Based on the Time series 1 data provided, according to the thresholds (<0.2 no seasonality, 0.2-0.5 weak, 0.5-0.8 moderate, >0.8 strong), which category does the seasonality strength of the Time series 1 show?",
                "options": "A) The seasonality strength is strong.\nB) The seasonality strength is moderate.\nC) The seasonality strength is weak.\nD) Virtually no seasonality.",
                "answer": ""
            },
            {
                "question":"Based on the provided Time series 1 data, please provide the period length for the seasonal component.",
                "answer": ""
            }
        ],
        'noise':[
            {
                "question": "Here is a list of values in the Time series 1. Based on the Time series 1 data provided, based on the ratio of the residual standard deviation to the sequence standard deviation (<0.1 no noise, 0.1-0.33 for low, 0.33-0.66 for medium, >0.66 for high), which category does the noise level of the sequence belong to?",
                "options": "A) The noise level is high.\nB) The noise level is medium.\nC) The noise level is low.\nD) Virtually no noise.",
                "answer": ""
            },
            {
                "question": "Here is a list of values in the Time series 1. Based on the Time series 1 data provided, which type does the noise in the Time series 1 most resemble?",
                "options": "A) Uniform.\nB) Gauss.\nC) Random walk.\nD) Quantization.",
                "answer": ""
            }
        ],
        'basic':[
            {
                "question": "Given the values of Time Series 1, what is the maximum value in the Time Series 1?",
                "answer": "{max: .2f}."
            },
            {
                "question": "Given the values of Time Series 1, what is the minimum value in the Time Series 1?",
                "answer": "{min: .2f}."
            },
            {
                "question": "Given the values of Time Series 1, what is the mean value of the Time Series 1?",
                "answer": "{mean: .2f}."
            },
            {
                "question": "Given the values of Time Series 1, what is the range of this Time Series 1?",
                "answer": "{range_value: .2f}."
            },
            {
                "question": "Given the values of Time Series 1, what is the median value of the Time Series 1?",
                "answer": "{median: .2f}."
            },
            {
                "question": "Given the values of Time Series 1, what is the standard deviation of the Time Series 1?",
                "answer": "{std: .2f}."
            },
            {
                "question": "Given the values of Time Series 1, what is the 50th percentile value of the Time Series 1?",
                "answer": "{PCT50: .2f}."
            },
            {
                "question": "Given the values of Time Series 1, what is the 90th percentile value of the Time Series 1?",
                "answer": "{PCT90: .2f}."
            },
            {
                "question": "Given the values of Time Series 1, what is the 99th percentile value of the Time Series 1",
                "answer": "{PCT99: .2f}."
            }
        ],
        'multivar':[
            {
                "question": "Given the values of Time Series 1 and Time Series 2, what is the maximum value in the {ts}?",
                "answer": "{max: .2f}."
            },
            {
                "question": "Given the values of Time Series 1 and Time Series 2, what is the minimum value in the {ts}?",
                "answer": "{min: .2f}."
            },
            {
                "question": "Given the values of Time Series 1 and Time Series 2, what is the mean value of the {ts}?",
                "answer": "{mean: .2f}."
            },
            {
                "question": "Given the values of Time Series 1 and Time Series 2, what is the range of this {ts}?",
                "answer": "{range_value: .2f}."
            },
            {
                "question": "Given the values of Time Series 1 and Time Series 2, what is the median value of the {ts}?",
                "answer": "{median: .2f}."
            },
            {
                "question": "Given the values of Time Series 1 and Time Series 2, what is the standard deviation of the {ts}?",
                "answer": "{std: .2f}."
            },
            {
                "question": "Given the values of Time Series 1 and Time Series 2, what is the 50th percentile value of the {ts}?",
                "answer": "{PCT50: .2f}."
            },
            {
                "question": "Given the values of Time Series 1 and Time Series 2, what is the 90th percentile value of the {ts}?",
                "answer": "{PCT90: .2f}."
            },
            {
                "question": "Given the values of Time Series 1 and Time Series 2, what is the 99th percentile value of the {ts}",
                "answer": "{PCT99: .2f}."
            }
        ]
    }
    with open(FEATURES_PATH, 'r') as f:
        all_features = json.load(f)
  
    all_questions = []
    num_id = 0

    # Categorize templates into choice and value types
    choice_templates = []  # (q_type, template_id)
    value_templates = []  # (q_type, template_id)
    univariate_templates = []  # basic, trend, seasonal, noise
    multivariate_templates = []  # multivar
    
    for q_type in Q_TYPES:
        for idx, tpl in enumerate(templates[q_type]):
            if 'options' in tpl:
                choice_templates.append((q_type, idx))
            else:
                value_templates.append((q_type, idx))
                # Classify single-variable and multi-variable numerical problem templates
                if q_type == 'multivar':
                    multivariate_templates.append((q_type, idx))
                else:
                    univariate_templates.append((q_type, idx))

    # Allocate choice and value questions based on ratio
    num_choice = int(TOTAL_QUESTIONS * CHOICE_RATIO)
    num_value = TOTAL_QUESTIONS - num_choice

    # Generate choice questions with balanced answer distribution
    # Strategy: Generate more questions than needed, then select balanced subset
    print("Generating choice questions...")
    
    # Step 1: Generate a pool of candidate questions (2x the target for better balance)
    candidate_pool = []
    pool_size = int(num_choice * 2)
    
    for _ in range(pool_size):
        q_type, template_id = random.choice(choice_templates)
        template_list = templates[q_type]
        
        ts_id = random.randint(0, TOTAL_NUM - 1)
        features = all_features[ts_id].copy()
        values = np.load(features['values'])
        template_params = {
            **features,
            'range_value': float(max(values) - min(values)),
        }
        
        answer = get_answer(q_type, template_id, template_params, template_list)
        question = template_list[template_id]['question'].format(**template_params)
        options = template_list[template_id]['options'].format(**template_params)
        
        candidate_pool.append({
            'ts_id': ts_id,
            'qa_type': 'a multiple choice question',
            'task_type': q_type,
            'question': question,
            'options': options,
            'answer': answer,
            'features': features
        })
    
    # Step 2: Group candidates by answer
    from collections import defaultdict
    answer_groups = defaultdict(list)
    for candidate in candidate_pool:
        answer_groups[candidate['answer']].append(candidate)
    
    # Step 3: Select balanced subset
    all_answers = sorted([k for k in answer_groups.keys() if k != '0'])  # Exclude '0' answers
    target_per_answer = num_choice // len(all_answers)
    remainder = num_choice % len(all_answers)
    
    answer_distribution = {}
    choice_count = 0
    
    for idx, answer in enumerate(all_answers):
        # Allocate extra questions to first few answers to handle remainder
        target = target_per_answer + (1 if idx < remainder else 0)
        available = len(answer_groups[answer])
        selected_count = min(target, available)
        
        # Randomly select from this answer group
        selected = random.sample(answer_groups[answer], selected_count)
        
        for item in selected:
            item['num_id'] = num_id
            all_questions.append(item)
            num_id += 1
            choice_count += 1
        
        answer_distribution[answer] = selected_count
    
    print(f"Selected {choice_count} choice questions from {pool_size} candidates")

    
    # Balance univariate and multivariate questions
    num_univariate = num_value // 2
    num_multivariate = num_value - num_univariate
    univariate_count = 0
    multivariate_count = 0
    value_count = 0
    
    while value_count < num_value:
        # Decide whether to generate univariate or multivariate
        should_generate_univariate = (
            univariate_count < num_univariate and 
            (multivariate_count >= num_multivariate or value_count % 2 == 0)
        )
        
        if should_generate_univariate:
            q_type, template_id = random.choice(univariate_templates)
            is_multivar = False
        else:
            q_type, template_id = random.choice(multivariate_templates)
            is_multivar = True
        
        template_list = templates[q_type]
        
        # Generate question based on type
        if is_multivar:
            ts_id, template_params, question_values, ts_name = generate_multivariate_question(template_id, template_list)
        else:
            ts_id, template_params, question_values, ts_name = generate_univariate_question(template_id, template_list)
        
        answer = get_answer(q_type, template_id, template_params, template_list)
        
        # Skip invalid answers
        if answer != '0':
            question = template_list[template_id]['question'].format(ts=ts_name)
            
            all_questions.append({
                'num_id': num_id,
                'ts_id': ts_id,
                'qa_type': 'numerical',
                'task_type': q_type,
                'question': question,
                'answer': answer,
                'values': question_values,
                'features': template_params,
            })
            
            num_id += 1
            value_count += 1
            
            if is_multivar:
                multivariate_count += 1
            else:
                univariate_count += 1

    with open(OUTPUT_PATH, 'w') as f:
        json.dump(all_questions, f, indent=4)
    
    print(f"\nGenerated {len(all_questions)} questions and saved to {OUTPUT_PATH}")
    print(f"  - Choice questions: {choice_count}")
    print(f"    Answer distribution: {dict(sorted(answer_distribution.items()))}")
    
    # Calculate balance score
    if answer_distribution:
        counts = list(answer_distribution.values())
        balance_score = (min(counts) / max(counts)) * 100 if max(counts) > 0 else 0
        print(f"    Balance score: {balance_score:.1f}% (100% = perfect balance)")
    
    print(f"  - Numerical questions: {value_count} (Univariate: {univariate_count}, Multivariate: {multivariate_count})")
    
    # JSON to csv
    csv_output_path = OUTPUT_PATH.replace('.json', '.csv')
    selected_columns = ['num','qa_type','local_overall','task_type','stationarity', 'question','option','answer','domain','freq','is_univariate','value']
    json2csv(OUTPUT_PATH, csv_output_path, selected_columns)
    print(f"CSV file saved to {csv_output_path}")