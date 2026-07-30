# Time-Series Hierarchical Agent (Prompt-only)

Prompt-only hierarchical agent for comparing a **Baseline** single-shot Qwen2.5-14B-Instruct against a full **Architecture** (Planner → Homogeneous multi-scale agents → Temporal Profile → Heterogeneous task agents → Integration) on **MMTS-Bench**.

## What is in this repo

- `configs/` — experiment config
- `scripts/` — download helpers + `run_experiment.sh`
- `prompts/` — versioned role prompts
- `src/ts_agent/` — pipeline, agents, tools, evaluation
- `tests/` — unit / compliance tests
- `data/raw/mmts-bench/` — original MMTS-Bench
- `data/processed/mmts-bench/` — processed index for lazy loading

## What is NOT in this repo

- `models/Qwen2.5-14B-Instruct/` (~28GB weights) — download locally with:

```bash
bash scripts/run_experiment.sh download-model
# or: python scripts/download_model_lowmem.py
```

## Quickstart

```bash
cd time-series-agent
pip install -e .

# Data (already present if you cloned this repo with data/)
# bash scripts/run_experiment.sh download-data
bash scripts/run_experiment.sh preprocess

# Mock smoke
bash scripts/run_experiment.sh smoke

# Real model pilot / full (needs GPU + local weights)
bash scripts/run_experiment.sh pilot
bash scripts/run_experiment.sh full   # prefer tmux/screen
```

## Notes

- Planner / Integration are non-tool; Homogeneous / Heterogeneous use a deterministic tool whitelist.
- Official MMTS Text series formatting is reproduced via `format_raw_value_text`.
- Align/Match routing is guarded by Planner sanitization (`subset` metadata).
