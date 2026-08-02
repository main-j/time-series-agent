from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import numpy as np

from ts_agent.schemas.models import RunTrace


def accuracy_within_percentage(ground_truth, answers, percentage=0.05):
    assert len(ground_truth) == len(answers)
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
    nonzero_mask = y_true != 0
    rel_acc[nonzero_mask] = 1.0 - np.abs(y_pred[nonzero_mask] - y_true[nonzero_mask]) / np.abs(y_true[nonzero_mask])
    rel_acc[nonzero_mask] = np.maximum(rel_acc[nonzero_mask], 0.0)
    zero_mask = ~nonzero_mask
    rel_acc[zero_mask] = (y_pred[zero_mask] == 0).astype(float)
    return float(np.mean(rel_acc)) if len(rel_acc) else 0.0


def normalize_choice(x: str) -> str:
    return str(x).strip().upper()[:1]


def summarize_traces(traces: List[RunTrace]) -> Dict:
    choice = [t for t in traces if t.question_type == "choice"]
    numerical = [t for t in traces if t.question_type == "numerical"]

    choice_correct = 0
    for t in choice:
        if t.success and normalize_choice(t.predicted_answer) == normalize_choice(t.ground_truth):
            choice_correct += 1
    choice_acc = choice_correct / len(choice) if choice else None

    num_metrics = None
    if numerical:
        yt, yp = [], []
        for t in numerical:
            try:
                yt.append(float(t.ground_truth))
                yp.append(float(t.predicted_answer))
            except Exception:
                continue
        if yt:
            num_metrics = {
                "n": len(yt),
                "Accuracy@5%": accuracy_within_percentage(yt, yp, 0.05),
                "RelativeAccuracy": relative_accuracy(yt, yp),
            }

    by_subset = defaultdict(list)
    for t in traces:
        subset = t.details.get("subset", "unknown") if t.details else "unknown"
        by_subset[subset].append(t)

    subset_acc = {}
    for subset, items in by_subset.items():
        citems = [x for x in items if x.question_type == "choice"]
        if not citems:
            continue
        correct = sum(
            1
            for x in citems
            if x.success and normalize_choice(x.predicted_answer) == normalize_choice(x.ground_truth)
        )
        subset_acc[subset] = correct / len(citems)

    return {
        "n_total": len(traces),
        "n_success": sum(1 for t in traces if t.success),
        "valid_output_rate": (sum(1 for t in traces if t.success) / len(traces)) if traces else 0.0,
        "choice_accuracy": choice_acc,
        "n_choice": len(choice),
        "numerical_metrics": num_metrics,
        "subset_choice_accuracy": subset_acc,
        "avg_latency_sec": float(np.mean([t.latency_sec for t in traces])) if traces else 0.0,
        "avg_model_calls": float(np.mean([t.model_calls for t in traces])) if traces else 0.0,
        "avg_tool_calls": float(np.mean([t.tool_calls for t in traces])) if traces else 0.0,
        "avg_prompt_tokens": float(np.mean([t.prompt_tokens for t in traces])) if traces else 0.0,
        "avg_completion_tokens": float(np.mean([t.completion_tokens for t in traces])) if traces else 0.0,
        "total_prompt_tokens": int(sum(t.prompt_tokens for t in traces)),
        "total_completion_tokens": int(sum(t.completion_tokens for t in traces)),
    }


def save_traces(traces: Iterable[RunTrace], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for t in traces:
            f.write(json.dumps(t.model_dump(), ensure_ascii=False) + "\n")


def load_traces(path: Path) -> List[RunTrace]:
    traces = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                traces.append(RunTrace.model_validate(json.loads(line)))
    return traces


def compare_summaries(baseline: Dict, architecture: Dict) -> Dict:
    def delta(a, b):
        if a is None or b is None:
            return None
        return b - a

    return {
        "choice_accuracy_delta": delta(baseline.get("choice_accuracy"), architecture.get("choice_accuracy")),
        "valid_output_rate_delta": delta(baseline.get("valid_output_rate"), architecture.get("valid_output_rate")),
        "avg_latency_sec_delta": delta(baseline.get("avg_latency_sec"), architecture.get("avg_latency_sec")),
        "avg_model_calls_delta": delta(baseline.get("avg_model_calls"), architecture.get("avg_model_calls")),
        "avg_tool_calls_delta": delta(baseline.get("avg_tool_calls"), architecture.get("avg_tool_calls")),
        "baseline": baseline,
        "architecture": architecture,
    }
