from transformers import AutoModelForCausalLM, AutoTokenizer
import json
import re
import string
from tqdm import tqdm
import csv
import ast

from transformers import AutoModelForCausalLM, AutoTokenizer, AutoProcessor
import torch
import numpy as np
import os

from utils.get_prompt import get_full_prompt, get_prompt_content
from utils.numpy_func import adopt_ts_array, split_ts_array
from utils.extract_answer import extract_answer

new_model_path = "/path/to/ChatTS/model"

device_num = 0
os.environ["CUDA_VISIBLE_DEVICES"] = str(device_num)

# Load the model, tokenizer and processor
model = AutoModelForCausalLM.from_pretrained(new_model_path, trust_remote_code=True, device_map=device_num, torch_dtype=torch.float16)
tokenizer = AutoTokenizer.from_pretrained(new_model_path, trust_remote_code=True)
processor = AutoProcessor.from_pretrained(new_model_path, trust_remote_code=True, tokenizer=tokenizer)
device=torch.device(f'cuda:{device_num}')
model.eval()

# ------------------------------------------------------------------------------- #
data_path = "/path/to/dataset"


question_type = "choice" # default is choice

log_path = "./log.json"
if "tsqa" in data_path:
    roll_path = "./log_roll_tsqa_1084_0918.json" 
    total_lines = 1084
elif "qats" in data_path:
    roll_path = "./log_roll_qats_400.json"
    total_lines = 400
elif "caption2ts_qa" in data_path:
    roll_path = "./log_roll_caption2ts_qa_120.json"
    total_lines = 120
elif "ts2caption_qa" in data_path:
    roll_path = "./log_roll_ts2caption_qa_120.json"
    total_lines = 120
elif "choice" in data_path:
    roll_path = "./log_roll_synthetic_qa_choice.json"
    total_lines = 568
elif "numerical" in data_path:
    roll_path = "./log_roll_synthetic_qa_numerical.json"
    total_lines = 292
    question_type = "numerical"
elif "multivar" in data_path:
    roll_path = "./log_roll_added_multivar_numerical_ab.json"
    total_lines = 100
    question_type = "numerical"
else:
    roll_path = "./log_roll_unknown.json"
    total_lines = 1000


do_roll = True
n_roll = 5

if do_roll:
    with open(roll_path, "w", encoding="utf-8") as roll_file:
        json.dump([], roll_file)
else:
    with open(log_path, "w", encoding="utf-8") as log_file:
        json.dump([], log_file)


with open(data_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(tqdm(reader, total=total_lines)):
        ts_list = ast.literal_eval(row['value'])
        try:
            ts_array = adopt_ts_array(ts_list)
        except ValueError as e:
            tqdm.write(f"Skipping row {i+1} due to ValueError: {e}")
            continue
        array_list = split_ts_array(ts_array)

        prompt_content = get_prompt_content(row["question"], row["option"], question_type)
        flag, prefix, full_prompt = get_full_prompt(array_list, prompt_content, data_path)
        tqdm.write("\n------------------------------------------------------------------\n")
        tqdm.write(f"The {i+1}-th sample:")
        tqdm.write(f"Index: {row['num']}")
        tqdm.write(str(np.array(array_list).shape))
        tqdm.write(str(flag))
        if not flag:
            tqdm.write("\nSkipping this sample due to invalid time series length.\n\n")
            continue
        tqdm.write(prefix)
        tqdm.write("\nQuestion:")
        tqdm.write(row["question"])
        tqdm.write("\nOptions:")
        tqdm.write(row["option"])

        
        
        inputs = processor(text=[full_prompt], timeseries=array_list, padding=True, return_tensors="pt").to(device)
        
        if do_roll:
            for j in range(n_roll):
                outputs = model.generate(**inputs, max_new_tokens=1024)
                raw_answer = tokenizer.decode(outputs[0][len(inputs['input_ids'][0]):], skip_special_tokens=True)
                extracted_answer = extract_answer(row["question"], row["option"], raw_answer, question_type)
                tqdm.write(f"\n\nAnswer{j+1}:")
                tqdm.write(raw_answer)
                tqdm.write("\n\n")

                log_entry = {
                    "index": i+1,
                    "roll": j+1,
                    "question": row["question"],
                    "options": row["option"],
                    "raw_answer": raw_answer,
                    "extracted_answer": extracted_answer,
                    "ground_truth": row["answer"], 
                }

                with open(roll_path, "r", encoding="utf-8") as log_file:
                    try:
                        existing_data = json.load(log_file)
                    except (json.JSONDecodeError, FileNotFoundError):
                        existing_data = []
                
                existing_data.append(log_entry)
                
                with open(roll_path, "w", encoding="utf-8") as log_file:
                    json.dump(existing_data, log_file, ensure_ascii=False, indent=4)
        
        else:
            outputs = model.generate(**inputs, max_new_tokens=1024)
            raw_answer = tokenizer.decode(outputs[0][len(inputs['input_ids'][0]):], skip_special_tokens=True)
            extracted_answer = extract_answer(row["question"], row["option"], raw_answer, question_type)
            tqdm.write("\n\nAnswer:")
            tqdm.write(raw_answer)
            tqdm.write("\n\n")

            log_entry = {
                "index": i+1,
                "question": row["question"],
                "options": row["option"],
                "raw_answer": raw_answer,
                "extracted_answer": extracted_answer,
                "ground_truth": row["answer"],
            }

            with open(log_path, "r", encoding="utf-8") as log_file:
                try:
                    existing_data = json.load(log_file)
                except (json.JSONDecodeError, FileNotFoundError):
                    existing_data = []
            
            existing_data.append(log_entry)
            
            with open(log_path, "w", encoding="utf-8") as log_file:
                json.dump(existing_data, log_file, ensure_ascii=False, indent=4)



