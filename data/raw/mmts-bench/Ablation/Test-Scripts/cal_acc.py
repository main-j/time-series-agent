import json
import csv
import re
from collections import defaultdict
import ast

# file_path
json_path = "/your/json/path"
csv_path = "/dataset/csv/path"

index2domain = {}
index2tasks = {}
with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            idx = int(row["num"])
            domain = row["domain"].strip()

            raw_task = row.get("task_type", "Unknown").strip()
            tasks = []
            try:
                parsed = ast.literal_eval(raw_task)
                if isinstance(parsed, list):
                    tasks = [t.strip() for t in parsed]
                else:
                    tasks = [str(parsed).strip()]
            except Exception:
                tasks = [raw_task]  

            index2domain[idx] = domain
            index2tasks[idx] = tasks
        except Exception as e:
            print(f"Skip for: {row}, Error: {e}")

domain_correct = defaultdict(int)
domain_total = defaultdict(int)

task_correct = defaultdict(int)
task_total = defaultdict(int)

overall_correct = 0
overall_total = 0

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    idx = item["index"]
    extracted = item["extracted_answer"].strip()
    gt = item["ground_truth"].strip()

    if "Final answer is" in extracted:
        extracted = extracted.split(":")[-1].strip()

    extracted = re.sub(r"[^\w\s]", "", extracted)  
    correct = gt in extracted or extracted in gt

    domain = index2domain.get(idx, "Unknown")
    tasks = index2tasks.get(idx, ["Unknown"])

    domain_total[domain] += 1
    if correct:
        domain_correct[domain] += 1

    for task in tasks:
        task_total[task] += 1
        if correct:
            task_correct[task] += 1

    overall_total += 1
    if correct:
        overall_correct += 1

print("Acc per domain:")
for domain in sorted(domain_total.keys()):
    acc = domain_correct[domain] / domain_total[domain] * 100
    print(f"{domain}: {acc:.4f} ({domain_correct[domain]}/{domain_total[domain]})")

print("\nAcc per task_type:")
for task in sorted(task_total.keys()):
    acc = task_correct[task] / task_total[task] * 100
    print(f"{task}: {acc:.4f} ({task_correct[task]}/{task_total[task]})")

print("\nOverall Acc:")
overall_acc = overall_correct / overall_total * 100
print(f"Overall: {overall_acc:.4f} ({overall_correct}/{overall_total})")