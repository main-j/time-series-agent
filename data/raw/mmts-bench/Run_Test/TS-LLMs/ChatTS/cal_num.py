import json
import numpy as np
import re
import pandas as pd

# ---------- Metrics ----------
def accuracy_within_percentage(ground_truth, answers, percentage=0.5):

    assert len(ground_truth) == len(answers), "ground_truth and answers length should be the same"
    correct = 0
    for gt, ans in zip(ground_truth, answers):
        if gt == 0:
            if ans == 0:
                correct += 1
        else:
            if abs(ans - gt) / abs(gt) <= percentage:
                correct += 1
    return correct / len(ground_truth) if ground_truth else 0.0


def relative_accuracy(y_true, y_pred):
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    rel_acc = np.zeros_like(y_true, dtype=float)
    nonzero_mask = (y_true != 0)
    rel_acc[nonzero_mask] = 1.0 - np.abs(y_pred[nonzero_mask] - y_true[nonzero_mask]) / np.abs(y_true[nonzero_mask])
    rel_acc[nonzero_mask] = np.maximum(rel_acc[nonzero_mask], 0.0)
    zero_mask = ~nonzero_mask
    rel_acc[zero_mask] = (y_pred[zero_mask] == 0).astype(float)
    return float(np.mean(rel_acc))


def average_offset(y_true, y_pred):
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)

    mask_nonzero = (y_true != 0)
    if np.sum(mask_nonzero) == 0:
        return 0.0

    error = np.abs(y_pred[mask_nonzero] - y_true[mask_nonzero]) / np.abs(y_true[mask_nonzero])
    return float(np.mean(error))


# ---------- File Path ----------
json_path = "/path/to/json/file"
csv_path = "/path/to/csv/file"

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

records = []
for item in data:
    idx = item.get("index", None)

    try:
        gt = float(item.get("ground_truth", 0))
    except ValueError:
        gt = 0.0

    extracted = item.get("extracted_answer", "")
    match = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", extracted)
    if match:
        try:
            pred = float(match.group())
        except ValueError:
            pred = 0.0
    else:
        pred = 0.0

    records.append({"index": idx, "y_true": gt, "y_pred": pred})

df_json = pd.DataFrame(records)

df_csv = pd.read_csv(csv_path)
df_merged = pd.merge(df_csv, df_json, left_on="num", right_on="index", how="inner")

def compute_metrics(sub_df, percentage=0.05):
    y_true = sub_df["y_true"].tolist()
    y_pred = sub_df["y_pred"].tolist()
    acc = accuracy_within_percentage(y_true, y_pred, percentage=percentage)
    rel_acc = relative_accuracy(y_true, y_pred)
    avg_offset = average_offset(y_true, y_pred)
    return {
        f"Accuracy@{percentage*100:.1f}%": f"{acc*100:.2f}%",
        "Relative Accuracy": f"{rel_acc*100:.2f}%",
        "Average Offset": f"{avg_offset*100:.2f}%"
    }

group_cols = ["task_type", "local_overall", "stationarity", "is_univariate"]

for col in group_cols:
    print(f"\n===== Group by {col} Column =====")
    for val, sub_df in df_merged.groupby(col):
        metrics = compute_metrics(sub_df, percentage=0.05)
        print(f"{col} = {val}: {metrics}")

print("\n===== Overall Metrics =====")
total_metrics = compute_metrics(df_merged, percentage=0.05)
print(total_metrics)
