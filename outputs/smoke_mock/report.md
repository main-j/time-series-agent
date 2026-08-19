# Qwen2.5-14B Prompt-only Architecture Comparison Report

## Setup
- Model path: `/root/autodl-tmp/time-series-agent/models/Qwen2.5-14B-Instruct`
- Data: MMTS-Bench processed at `/root/autodl-tmp/time-series-agent/data/processed/mmts-bench`
- Modes: baseline vs architecture
- Limit: 8
- Provider mode config: `auto` (effective depends on GPU)

## Results
| Metric | Baseline | Architecture | Delta |
|---|---:|---:|---:|
| Choice Accuracy | 0.375 | 0.375 | 0.0 |
| Valid Output Rate | 1.0 | 1.0 | 0.0 |
| Avg Latency (s) | 0.0003 | 0.0126 | 0.012310653924942017 |
| Avg Model Calls | 1.00 | 13.00 | 12.0 |
| Avg Tool Calls | 0.00 | 9.00 | 9.0 |

### Subset Choice Accuracy
- Baseline: {"Base": 0.375}
- Architecture: {"Base": 0.375}

## Interpretation
- This stage compares the full hierarchical Prompt+Tools architecture against a single-shot baseline.
- Module-level attribution requires future ablations (explicitly out of scope for this stage).
- If provider is mock (no GPU), metrics validate pipeline correctness only, not model quality.
