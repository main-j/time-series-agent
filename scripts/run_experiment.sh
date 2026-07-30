#!/usr/bin/env bash
# Complete MMTS-Bench Baseline vs Architecture experiment runner.
# Usage examples are printed with:  bash scripts/run_experiment.sh help
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1
export HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-1}"
export TRANSFORMERS_OFFLINE="${TRANSFORMERS_OFFLINE:-1}"

CONFIG="${CONFIG:-${ROOT}/configs/experiment.yaml}"
LOG_DIR="${ROOT}/logs"
mkdir -p "$LOG_DIR" "${ROOT}/outputs"

ts_agent() {
  python -m ts_agent.cli --config "$CONFIG" "$@"
}

need_model() {
  local model_dir
  model_dir="$(python - <<'PY'
import yaml
from pathlib import Path
cfg=yaml.safe_load(Path("configs/experiment.yaml").read_text())
print(cfg["model"]["local_path"])
PY
)"
  if [[ ! -f "${model_dir}/config.json" ]]; then
    echo "[ERROR] Model config missing: ${model_dir}/config.json" >&2
    echo "Run: bash scripts/run_experiment.sh download-model" >&2
    exit 1
  fi
  local n
  n="$(ls -1 "${model_dir}"/model-*-of-*.safetensors 2>/dev/null | wc -l | tr -d ' ')"
  if [[ "$n" -lt 8 ]]; then
    echo "[ERROR] Expected 8 weight shards, found ${n} under ${model_dir}" >&2
    echo "Run: bash scripts/run_experiment.sh download-model" >&2
    exit 1
  fi
  echo "[OK] Model ready: ${model_dir} (${n} shards)"
}

need_data() {
  if [[ ! -f "${ROOT}/data/raw/mmts-bench/download_manifest.json" ]] && [[ ! -d "${ROOT}/data/raw/mmts-bench/Benchmark" ]]; then
    echo "[ERROR] MMTS-Bench raw data missing." >&2
    echo "Run: bash scripts/run_experiment.sh download-data" >&2
    exit 1
  fi
  if [[ ! -f "${ROOT}/data/processed/mmts-bench/index.jsonl" ]]; then
    echo "[INFO] Processed index missing; running preprocess..."
    cmd_preprocess
  fi
  echo "[OK] Data ready: $(wc -l < "${ROOT}/data/processed/mmts-bench/index.jsonl") samples indexed"
}

cmd_help() {
  cat <<'EOF'
MMTS hierarchical agent experiment script
========================================

# 0) Help
bash scripts/run_experiment.sh help

# 1) (Optional) Download assets if missing
bash scripts/run_experiment.sh download-data
bash scripts/run_experiment.sh download-model

# 2) Preprocess MMTS index
bash scripts/run_experiment.sh preprocess

# 3) Smoke test with Mock LLM (pipeline correctness only)
bash scripts/run_experiment.sh smoke

# 4) Small real-model pilot (stratified 8 samples, Qwen2.5-14B)
bash scripts/run_experiment.sh pilot

# 5) Full real-model comparison on all 2424 samples
bash scripts/run_experiment.sh full

# 6) Custom run (pass-through to CLI)
bash scripts/run_experiment.sh run --mode both --limit 40 --stratified \
  --no-use-mock-llm --exp-name my_run --max-series-text-chars 0

Outputs land in: outputs/<exp-name>/
  - baseline_traces.jsonl / architecture_traces.jsonl
  - *_summary.json / comparison.json / report.md / run_manifest.json
EOF
}

cmd_download_data() {
  python scripts/download_mmts.py
}

cmd_download_model() {
  if [[ -f scripts/download_model_lowmem.py ]]; then
    python scripts/download_model_lowmem.py
  else
    python scripts/download_model.py
  fi
}

cmd_preprocess() {
  ts_agent preprocess --subsets Base InWild Match Align
}

cmd_smoke() {
  need_data
  local exp="smoke_mock_$(date +%Y%m%d_%H%M%S)"
  local log="${LOG_DIR}/${exp}.log"
  echo "[INFO] Smoke (mock) -> outputs/${exp} (log: ${log})"
  ts_agent run \
    --mode both \
    --limit 8 \
    --stratified \
    --use-mock-llm \
    --exp-name "$exp" \
    --max-series-text-chars 4000 \
    2>&1 | tee "$log"
  echo "[DONE] ${ROOT}/outputs/${exp}/report.md"
}

cmd_pilot() {
  need_data
  need_model
  local exp="pilot_qwen14b_$(date +%Y%m%d_%H%M%S)"
  local log="${LOG_DIR}/${exp}.log"
  echo "[INFO] Pilot (real Qwen2.5-14B, stratified 8) -> outputs/${exp}"
  echo "[INFO] Log: ${log}"
  ts_agent run \
    --mode both \
    --limit 8 \
    --stratified \
    --no-use-mock-llm \
    --exp-name "$exp" \
    --max-series-text-chars 0 \
    2>&1 | tee "$log"
  echo "[DONE] ${ROOT}/outputs/${exp}/report.md"
}

cmd_full() {
  need_data
  need_model
  local exp="full_qwen14b_$(date +%Y%m%d_%H%M%S)"
  local log="${LOG_DIR}/${exp}.log"
  echo "[INFO] FULL (real Qwen2.5-14B, all samples) -> outputs/${exp}"
  echo "[INFO] This can take a long time. Log: ${log}"
  ts_agent run \
    --mode both \
    --no-use-mock-llm \
    --exp-name "$exp" \
    --max-series-text-chars 0 \
    2>&1 | tee "$log"
  echo "[DONE] ${ROOT}/outputs/${exp}/report.md"
}

cmd_run() {
  # pass-through: bash scripts/run_experiment.sh run --mode both ...
  ts_agent run "$@"
}

cmd="${1:-help}"
shift || true
case "$cmd" in
  help|-h|--help) cmd_help ;;
  download-data) cmd_download_data "$@" ;;
  download-model) cmd_download_model "$@" ;;
  preprocess) cmd_preprocess "$@" ;;
  smoke) cmd_smoke "$@" ;;
  pilot) cmd_pilot "$@" ;;
  full) cmd_full "$@" ;;
  run) cmd_run "$@" ;;
  *)
    echo "Unknown command: $cmd" >&2
    cmd_help
    exit 1
    ;;
esac
