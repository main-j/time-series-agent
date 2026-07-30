# Qwen2.5-14B Prompt-only Architecture Comparison Report

## Environment constraints
- CUDA available: `False`
- Container cgroup memory.max: `2147483648` (~2.0 GiB)
- Conclusion: current instance **cannot load Qwen2.5-14B-Instruct for inference** (needs GPU + >>2GiB RAM). Validation below uses deterministic `MockLLMProvider` to verify the architecture pipeline, tool loop, prompts, and metrics plumbing.

## Data
- Source: MMTS-Bench anonymous archive
- SHA256: `ce380e9d549bd011ac38f155a73a9109d268b86e03faa6366c7dc3c18ed2d783`
- Processed counts: `{'Base': 700, 'InWild': 1084, 'Match': 400, 'Align': 240}` (total 2424)

## Experiment
- Modes: Baseline (single prompt) vs Architecture (Planner → Homogeneous scales → Heterogeneous roles → Integration)
- Tools enabled only for homogeneous/heterogeneous agents
- Prompt versions: baseline/planner/homogeneous/heterogeneous/integration `v1`
- Sample limit: stratified 12 across Base/InWild/Match/Align

## Results (Mock LLM — pipeline correctness only)
| Metric | Baseline | Architecture | Delta |
|---|---:|---:|---:|
| Choice Accuracy | 0.25 | 0.25 | 0.0 |
| Valid Output Rate | 1.0 | 1.0 | 0.0 |
| Avg Model Calls | 1.00 | 10.00 | 9.0 |
| Avg Tool Calls | 0.00 | 4.00 | 4.0 |

Subset accuracy baseline: `{"Align": 0.0, "Base": 0.3333333333333333, "InWild": 0.3333333333333333, "Match": 0.3333333333333333}`
Subset accuracy architecture: `{"Align": 0.0, "Base": 0.3333333333333333, "InWild": 0.3333333333333333, "Match": 0.3333333333333333}`

## Effectiveness judgment (this stage)
- Pipeline status: **PASS** (end-to-end traces written, tools invoked, structured outputs parsed)
- Model-quality judgment: **BLOCKED** until a GPU instance with sufficient memory is allocated and local Qwen2.5-14B-Instruct weights finish downloading
- Next action: allocate GPU, finish `python scripts/download_model_lowmem.py`, set `experiment.use_mock_llm: false`, rerun:
  `python -m ts_agent.cli run --mode both --stratified --limit 40 --exp-name qwen14b_dev`
  then full benchmark without `--limit`
