from transformers import AutoModelForCausalLM, AutoTokenizer
import json
import re
import string
from tqdm import tqdm
import csv
import ast

from transformers import AutoModelForCausalLM, AutoTokenizer, AutoProcessor
from modeling_qwen2 import Qwen2TSForCausalLM
import torch
import numpy as np
import os
import argparse

from utils.get_prompt import get_full_prompt, get_prompt_content
from utils.numpy_func import adopt_ts_array, split_ts_array
from utils.extract_answer import extract_answer

def main(args):
    mlp_path = "/path/to/mlp/model"
    cnn_path = "/path/to/cnn/model"
    tsfm_path = "/path/to/transformer/model"
    layer_1 = "/path/to/layer1/model"
    layer_2 = "/path/to/layer2/model"
    layer_3 = "/path/to/layer3/model"
    layer_4 = "/path/to/layer4/model"
    layer_7 = "/path/to/layer7/model"
    no_cheat = "/path/to/no_cheat/model"
    pos_idx = "/path/to/pos_idx/model"
    no_emb = "/path/to/no_emb/model"
    if args.model == "mlp":
        new_model_path = mlp_path
    elif args.model == "cnn":
        new_model_path = cnn_path
    elif args.model == "tsfm":
        new_model_path = tsfm_path
    elif args.model == "1layer":
        new_model_path = layer_1
    elif args.model == "2layer":
        new_model_path = layer_2
    elif args.model == "3layer":
        new_model_path = layer_3
    elif args.model == "4layer":
        new_model_path = layer_4
    elif args.model == "7layer":
        new_model_path = layer_7
    elif args.model == "no_cheat":
        new_model_path = no_cheat
    elif args.model == "pos_idx":
        new_model_path = pos_idx
    elif args.model == "no_emb":
        new_model_path = no_emb

    device_num = args.device
    os.environ["CUDA_VISIBLE_DEVICES"] = str(device_num)
    
    # Load the model, tokenizer and processor
    model = AutoModelForCausalLM.from_pretrained(new_model_path, trust_remote_code=True, device_map=device_num)
    tokenizer = AutoTokenizer.from_pretrained(new_model_path, trust_remote_code=True)
    processor = AutoProcessor.from_pretrained(new_model_path, trust_remote_code=True, tokenizer=tokenizer)
    device=torch.device(f'cuda:{device_num}')
    model.eval()


    dataset_name = args.dataset
    if dataset_name == "tsqa":
        data_path = "/path/to/tsqa"
    elif dataset_name == "qats":
        data_path = "/path/to/qats"
    elif dataset_name == "caption2ts":
        data_path = "/path/to/caption2ts"
    elif dataset_name == "ts2caption":
        data_path = "/path/to/ts2caption"
    elif dataset_name == "numerical":
        data_path = "/path/to/numerical"
    elif dataset_name == "choice":
        data_path = "/path/to/choice"
    else:
        raise ValueError("Unknown dataset name.")

    question_type = "choice" # default is choice

    notes = str(args.model)+"_"+str(args.notes)

    log_path = "./log.json"
    save_folder = "new_results"
    if "tsqa" in data_path:
        roll_path = f"./{save_folder}/log_roll_tsqa_1084_{notes}.json" 
        total_lines = 1084
    elif "qats" in data_path:
        roll_path = f"./{save_folder}/log_roll_qats_400_{notes}.json"
        total_lines = 400
    elif "caption2ts_qa" in data_path:
        roll_path = f"./{save_folder}/log_roll_caption2ts_qa_120_{notes}.json"
        total_lines = 120
    elif "ts2caption_qa" in data_path:
        roll_path = f"./{save_folder}/log_roll_ts2caption_qa_120_{notes}.json"
        total_lines = 120
    elif "choice" in data_path:
        roll_path = f"./{save_folder}/log_roll_synthetic_qa_choice_{notes}.json" 
        total_lines = 568
    elif "numerical" in data_path:
        roll_path = f"./{save_folder}/log_roll_synthetic_qa_numerical_{notes}.json" 
        total_lines = 292
        question_type = "numerical"
    else:
        roll_path = f"./{save_folder}/log_roll_unknown_{notes}.json"
        total_lines = 1000


    do_roll = True
    n_roll = 5

    if do_roll:
        with open(roll_path, "w", encoding="utf-8") as roll_file:
            json.dump([], roll_file)
    else:
        with open(log_path, "w", encoding="utf-8") as log_file:
            json.dump([], log_file)


    with torch.no_grad():
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--model", type=str, default="mlp")
    parser.add_argument("--dataset", type=str, default="tsqa")
    parser.add_argument("--notes", type=str, default="")
    args = parser.parse_args()
    main(args)
