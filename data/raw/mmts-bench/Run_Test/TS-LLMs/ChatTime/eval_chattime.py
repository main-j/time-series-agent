from transformers import AutoModelForCausalLM, AutoTokenizer
import json
import re
import string
from tqdm import tqdm
import csv
import ast

from transformers import AutoModelForCausalLM, AutoTokenizer, AutoProcessor
from model.model import ChatTime, ChatTimePlus
import torch
import numpy as np
import os

# Reuse the utils in the TS-LLMs folder
from utils_eval.get_prompt import get_full_prompt, get_prompt_content
from utils_eval.numpy_func import adopt_ts_array, split_ts_array
from utils_eval.extract_answer import extract_answer

# Load the model
model_path = "/ChatTime/model/path"
model = ChatTimePlus(model_path=model_path)

# ------------------------------------------------------------------------------- #
data_path = "/path/to/dataset"


log_path = "./log.json"
if "tsqa" in data_path:
    roll_path = "./log_roll_tsqa_1084_idk.json"
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
        array_list = split_ts_array(ts_array)       # Input array_list is a list of same length 1D np.ndarray

        question = row["question"]
        option = row["option"]
        option_instruct = option + "\nOnly answer (A), (B), (C) or (D)...\n"
        
        tqdm.write("\n------------------------------------------------------------------\n")
        tqdm.write(f"The {i+1}-th sample:")
        tqdm.write(f"Index: {row['num']}")
        tqdm.write(str(np.array(array_list).shape))
        tqdm.write("\nQuestion:")
        tqdm.write(row["question"])
        tqdm.write("\nOptions:")
        tqdm.write(row["option"])

        
        if do_roll:
            for j in range(n_roll):
                raw_answer = model.analyze(question=question+"\n"+option_instruct, series=array_list)
                extracted_answer = extract_answer(row["question"], row["option"], raw_answer)
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
            pass



