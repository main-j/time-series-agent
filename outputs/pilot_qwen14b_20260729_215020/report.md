# Qwen2.5-14B Prompt-only Architecture Comparison Report

## Setup
- Model path: `/root/autodl-tmp/time-series-agent/models/Qwen2.5-14B-Instruct`
- Data: MMTS-Bench processed at `/root/autodl-tmp/time-series-agent/data/processed/mmts-bench`
- Modes: baseline vs architecture
- Limit: 8
- Provider mode config: `False` (effective depends on GPU)

## Results
| Metric | Baseline | Architecture | Delta |
|---|---:|---:|---:|
| Choice Accuracy | 0.5 | 0.625 | 0.125 |
| Valid Output Rate | 1.0 | 1.0 | 0.0 |
| Avg Latency (s) | 11.4739 | 84.2731 | 72.79921129345894 |
| Avg Model Calls | 1.00 | 8.62 | 7.625 |
| Avg Tool Calls | 0.00 | 9.75 | 9.75 |

### Subset Choice Accuracy
- Baseline: {"Align": 1.0, "Base": 0.0, "InWild": 1.0, "Match": 0.0}
- Architecture: {"Align": 1.0, "Base": 0.5, "InWild": 0.5, "Match": 0.5}

## Interpretation
- This stage compares the full hierarchical Prompt+Tools architecture against a single-shot baseline.
- Module-level attribution requires future ablations (explicitly out of scope for this stage).
- If provider is mock (no GPU), metrics validate pipeline correctness only, not model quality.
