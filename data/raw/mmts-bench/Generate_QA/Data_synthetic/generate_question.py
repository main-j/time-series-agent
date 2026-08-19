import json
import random
import pandas as pd
from itertools import product
import numpy as np
from typing import List, Dict, Any
from generate_stationary_question import json2csv

def get_answer(q_type, template_id, template_params, template_list):
    if q_type == 'trend':
        trend_strength = template_params['trend_strength']
        hurst = template_params['hurst']
        slope = template_params['slope']

        if template_id == 0 or template_id == 2:
            if trend_strength > 0.9:
                if slope > 0.1:
                    answer = 'A'
                elif slope < -0.1:
                    answer = 'B'
                else:
                    answer = 'C'
            else:
                answer = 'D'
        elif template_id == 1:
            if hurst > 0.55:
                answer = 'A'
            elif hurst < 0.45:
                answer = 'B'
            elif hurst > 0.48 and hurst < 0.52:
                answer = 'C'
            else:
                answer = 'D'
        elif template_id == 3:
            if trend_strength < 0.5 or (slope < 0.1 and slope > -0.1):
                answer = '0'
            else:
                answer = f'{slope: .2f}'
    elif q_type == 'seasonal':
        seasonal_strength = template_params['seasonal_strength']
        period = template_params['period']
        if template_id == 0:
            if seasonal_strength < 0.2:
                answer = 'D'
            elif period < 100:
                answer = 'A'
            elif period <200:
                answer = 'B'
            else:
                answer = 'C'    
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
            if seasonal_strength < 0.2:
                answer = '0'
            else:
                answer = f'{period: .2f}'
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
            elif noise_type =='random_walk':
                answer = 'C'
            else:
                answer = 'D'
    elif q_type == 'basic':
        answer = template_list[template_id]['answer'].format(**template_params)
    return answer

templates = {
    'trend': [
        {
            "question": "Here is a list of values in a time series. Based on the time series data provided, please determine the overall trend direction of the time series (The direction can be roughly determined through indicators of linear fitting).",
            "options": "A) an upward trend \nB) a downward trend \nC) a vague trend \nD) undeterminable",
            "answer": ""
        },
        {
            "question": "Here is a list of values in a time series. Based on the provided time series, please determine whether the time series exhibits persistence (long-term positive correlation), which means that past trends are likely to continue into the future (For example, if the series has been increasing recently, it is highly likely to continue increasing in the future).It can be measured by the Hurst Exponent:{hurst:.2f}.",
            "options": "A) The Hurst exponent (H) is significantly greater than 0.5, indicating that the time series has strong persistence (long-term positive correlation).\nB) The Hurst exponent (H) is significantly less than 0.5, indicating that the time series has strong anti-persistence or mean-reverting behavior (long-term negative correlation).\nC) The Hurst exponent (H) is approximately 0.5, indicating that the time series behaves like a random walk with no long-term memory.\nD) The Hurst exponent (H) is close to 0.5, but the deviation is not statistically significant enough to make a definitive conclusion about its long-term correlation.",
            "answer": ""
        },
        {
            "question": "Here is a list of values in a time series. Based on the provided time series, if trend analysis is performed on a time series using linear regression, what is the approximate interval for the fitting slope k of the time series?",
            "options": "A) k is greater than 0.5, the time series shows an upward trend.\nB) k is less than -0.5,  the time series shows a downward trend.\nC) k is roughly 0, the time series approximately shows a constant trend.\nD) Linear regression is not suitable for this time series.",
            "answer": ""
        },
        {
            "question": "Based on the provided time series data, please provide the slope of the linear fit for the trend component.",
            "answer": ""
        }
    ],
    'seasonal': [
        {
            "question": "Here is a list of values in a time series. Based on the time series data provided, does the time series have significant periodicity? If so, what is the period length (e.g., 100, 200 units)?",
            "options": "A) The series has significant periodicity with around 50~100 units period length.\nB) The series has significant periodicity with around 100~200 units period length.\nC) The series has significant periodicity with more than 200 units period length.\nD) The series does not have significant periodicity.",
            "answer": ""
        },
        {
            "question": "Here is a list of values in a time series. Based on the time series data provided, according to the thresholds (<0.1 not significant, 0.1-0.5 weak, 0.5-0.8 moderate, >0.8 strong), which category does the seasonality strength of the time series fall into? The sesonality strength is {seasonal_strength:.2f}.",
            "options": "A) The seasonality strength is strong.\nB) The seasonality strength is moderate.\nC) The seasonality strength is weak.\nD) The seasonality strength is not significant.",
            "answer": ""
        },
        {
            "question": "Based on the provided time series data, if the time series exhibits strong seasonal strength, please provide the period length for the seasonal component. If not, the answer is 0.",
            "answer": ""
        }
    ],
    'noise': [
        {
            "question": "Here is a list of values in a time series. Based on the time series data provided, based on the ratio of the residual standard deviation to the sequence standard deviation (<0.33 for low, 0.33–0.66 for medium, >0.66 for high), which category does the noise level of the sequence belong to?",
            "options": "A) The noise level is low.\nB) The noise level is medium.\nC) The noise level is high.\nD) The noise level is not significant.",
            "answer": ""
        },
        {
            "question": "Here is a list of values in a time series. Based on the time series data provided, which type does the noise in the time series most resemble?",
            "options": "A) Uniform.\nB) Gauss.\nC) Random walk.\nD) Quantization.",
            "answer": ""
        }
    ],
    'basic': [
        {
            "question": "Here is a list of values in a time series. Based on the time series data provided, what is the maximum value in the series?",
            "answer": "{max: .2f}."
        },
        {
            "question": "Here is a list of values in a time series. Based on the time series data provided, what is the minimum value in the series?",
            "answer": "{min: .2f}."
        },
        {
            "question": "Here is a list of values in a time series. Based on the time series data provided, what is the mean value of the sequence?",
            "answer": "{mean: .2f}."
        },
        {
            "question": "Here is a list of values in a time series. Based on the time series data provided, what is the range of this sequence?",
            "answer": "{range_value: .2f}."
        },
        {
            "question": "Here is a list of values in a time series. Based on the time series data provided, what is the median value of the sequence?",
            "answer": "{median: .2f}."
        },
        {
            "question": "Here is a list of values in a time series. Based on the time series data provided, what is the standard deviation of the sequence?",
            "answer": "{std: .2f}."
        },
        {
            "question": "Here is a list of values in a time series. Based on the time series data provided, what is the 50th percentile value of the sequence?",
            "answer": "{PCT50: .2f}."
        },
        {
            "question": "Here is a list of values in a time series. Based on the time series data provided, what is the 90th percentile value of the sequence?",
            "answer": "{PCT90: .2f}."
        },
        {
            "question": "Here is a list of values in a time series. Based on the time series data provided, what is the 99th percentile value of the sequence?",
            "answer": "{PCT99: .2f}."
        }
    ]
}

def main():
    all_feature_dir = 'meta_info/non_stationary/all_features.json'
    default_total_num = 300
    q_types = ['basic']
    out_file = 'non_stationary_question.json'

    # load feature
    try:
        with open(all_feature_dir, 'r') as f:
            all_features = json.load(f)
    except Exception as e:
        print(f"Failed to open {all_feature_dir}: {e}")
        return
    
    total_num = min(default_total_num, len(all_features))
    print(f"using {all_feature_dir}, total_num={total_num}")

    all_questions: List[Dict[str, Any]] = []
    num_id = 0
    used_combinations = set()

    for q_type in q_types:
        
        template_list = templates[q_type]
        template_num = len(template_list)
        coms = list(product(range(total_num), range(template_num)))
        selected_coms = random.sample(coms, 100)

        for com in selected_coms:
            ts_id = com[0]
            template_id = com[1]
                # track used combinations to prevent repeats
            used_combinations = set(selected_coms)
            
            # If the answer is '0', reselect the ts_id.
            answer = '0'
            while answer == '0':
                features = all_features[ts_id].copy()
                values = np.load(features['values'])
                template_params = {
                    **features,
                    'range_value': max(values) - min(values),
                }
                question = template_list[template_id]['question'].format(**template_params)
                
                if "options" in template_list[template_id]:
                    options = template_list[template_id]['options'].format(**template_params)
                    answer = get_answer(q_type, template_id, template_params, template_list)

                else:
                    answer = get_answer(q_type, template_id, template_params, template_list)
                    # If the answer is '0', select a new ts_id and ensure the combination is unique
                if answer == '0':
                    available_ts_ids = [i for i in range(total_num) if (i, template_id) not in used_combinations]
                    if available_ts_ids:  # Ensure that there are still available ts_ids
                        ts_id = random.choice(available_ts_ids)
                        used_combinations.add((ts_id, template_id))
                    else:
                        break
            if "options" in template_list[template_id]:
                all_info = {
                    'num_id': num_id,
                    'ts_id': ts_id,
                    'qa_type': q_type,
                    'question': question,
                    'options': options,
                    'answer': answer,
                    'features': features
                }
            else:
                all_info = {
                    'num_id': num_id,
                    'ts_id': ts_id,
                    'qa_type': q_type,
                    'question': question,
                    'answer': answer,
                    'features': features
                } 
            all_questions.append(all_info)
            num_id += 1

    try:
        with open(out_file, 'w') as f:
            json.dump(all_questions, f, indent=4)
        print(f"Saved {len(all_questions)} QAs to {out_file}")
    except Exception as e:
        print(f"Failed to write output file {out_file}: {e}")
    
    csv_output_path = out_file.replace('.json', '.csv')
    selected_columns = ['num','qa_type','local_overall','task_type','stationarity', 'question','option','answer','domain','freq','is_univariate','value']
    json2csv(out_file, csv_output_path, selected_columns)
    print(f"CSV file saved to {csv_output_path}")

if __name__ == "__main__":
    main()
    df1 = pd.read_csv('stationary_and_multivar.csv')
    df2 = pd.read_csv('non_stationary_question.csv')
    result = pd.concat([df1, df2], ignore_index=True)
    result['num'] = range(1, len(result) + 1)
    result.to_csv('synthetic_700.csv', index=False)
