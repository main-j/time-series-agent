# Qwen2.5-14B Prompt-only Architecture Comparison Report

## Setup
- Model path: `/root/autodl-tmp/time-series-agent/models/Qwen2.5-14B-Instruct`
- Data: MMTS-Bench processed at `/root/autodl-tmp/time-series-agent/data/processed/mmts-bench`
- Modes: baseline vs architecture
- Limit: 8
- Provider mode config: `True` (effective depends on GPU)

## Results
| Metric | Baseline | Architecture | Delta |
|---|---:|---:|---:|
| Choice Accuracy | 0.375 | 0.375 | 0.0 |
| Valid Output Rate | 1.0 | 1.0 | 0.0 |
| Avg Latency (s) | 0.0001 | 0.0849 | 0.08473733067512512 |
| Avg Model Calls | 1.00 | 11.00 | 10.0 |
| Avg Tool Calls | 0.00 | 4.50 | 4.5 |

### Subset Choice Accuracy
- Baseline: {"Align": 0.0, "Base": 0.5, "InWild": 0.5, "Match": 0.5}
- Architecture: {"Align": 0.0, "Base": 0.5, "InWild": 0.5, "Match": 0.5}

## Interpretation
- This stage compares the full hierarchical Prompt+Tools architecture against a single-shot baseline.
- Module-level attribution requires future ablations (explicitly out of scope for this stage).
- If provider is mock (no GPU), metrics validate pipeline correctness only, not model quality.
