#!/usr/bin/env bash
# Run the full MMTS-Bench with the current code and prompts.
# Existing feasibility results predate tool/prompt fixes, so the scientifically
# valid default reruns all 2424 samples. Mixed-version reuse must be explicit.
#
# Usage:
#   bash scripts/run_full_benchmark.sh              # start / resume
#   bash scripts/run_full_benchmark.sh status
#   bash scripts/run_full_benchmark.sh merge
#   EXP_NAME=my_run bash scripts/run_full_benchmark.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1
export HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-1}"
export TRANSFORMERS_OFFLINE="${TRANSFORMERS_OFFLINE:-1}"

EXP_NAME="${EXP_NAME:-full_benchmark_2424_fixed}"
DEVICE="${DEVICE:-cuda:0}"
ALLOW_MIXED_FEASIBILITY="${ALLOW_MIXED_FEASIBILITY:-0}"
MAX_ATTEMPTS="${MAX_ATTEMPTS:-3}"
RETRY_DELAY="${RETRY_DELAY:-2}"
RUN_BASELINE="${RUN_BASELINE:-0}"
LOG_DIR="${ROOT}/logs"
mkdir -p "$LOG_DIR" "${ROOT}/outputs"

need_model() {
  local model_dir
  model_dir="$(python - <<'PY'
import yaml
from pathlib import Path
cfg = yaml.safe_load(Path("configs/experiment.yaml").read_text())
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
  if [[ ! -f "${ROOT}/data/processed/mmts-bench/index.jsonl" ]]; then
    echo "[ERROR] Processed index missing: data/processed/mmts-bench/index.jsonl" >&2
    echo "Run: bash scripts/run_experiment.sh preprocess" >&2
    exit 1
  fi
  if [[ ! -f "${ROOT}/outputs/feasibility_test_19/sample_ids.txt" ]]; then
    echo "[ERROR] Feasibility exclude list missing: outputs/feasibility_test_19/sample_ids.txt" >&2
    exit 1
  fi
  local total
  total="$(wc -l < "${ROOT}/data/processed/mmts-bench/index.jsonl" | tr -d ' ')"
  echo "[OK] MMTS-Bench universe: ${total} samples"
  if [[ "$ALLOW_MIXED_FEASIBILITY" == "1" ]]; then
    echo "[WARN] Reusing feasibility_test_19 from an older tool/prompt version"
    echo "[WARN] Result will be a mixed-version diagnostic, not a controlled experiment"
    echo "[OK] Pending batch run: $((total - 19)) samples"
  else
    echo "[OK] Pending batch run: ${total} samples (single current version)"
  fi
}

cmd_help() {
  cat <<'EOF'
MMTS-Bench full benchmark (2424 samples)
======================================

Runs architecture (default) on all 2424 MMTS-Bench samples using one
current code/prompt version. Baseline is OFF by default; set RUN_BASELINE=1
only if you intentionally want to recompute baseline.

Do NOT mix results from outputs/full_benchmark_2424 (pre-fix diagnostic)
into this experiment directory. The old 19 feasibility results also predate
current fixes and are therefore not reused by default.
Each sample checkpoint is written to outputs/<EXP_NAME>/runs/summary.json.

Commands:
  bash scripts/run_full_benchmark.sh              Start or resume full run (2424)
  bash scripts/run_full_benchmark.sh merge        Build unified 2424 statistics
  bash scripts/run_full_benchmark.sh status       Show progress for current EXP_NAME
  bash scripts/run_full_benchmark.sh help

Environment:
  EXP_NAME   Output directory name (default: full_benchmark_2424_fixed)
  DEVICE     CUDA device map (default: cuda:0)
  MAX_ATTEMPTS
             Maximum attempts per failed sample (default: 3)
  RETRY_DELAY
             Seconds between attempts (default: 2)
  RUN_BASELINE=1
             Also run baseline (default: 0 / architecture-only)
  ALLOW_MIXED_FEASIBILITY=1
             Explicitly reuse the old 19 results and run only 2405. This is
             provided for diagnostics only and is not version-consistent.

After the batch finishes, merge results for full 2424-sample statistics:
  bash scripts/run_full_benchmark.sh merge

Outputs:
  outputs/<EXP_NAME>/runs/          Per-sample full_io.json / full_io.md
  outputs/<EXP_NAME>/runs/summary.json
  outputs/<EXP_NAME>/merged_2424/   Unified 2424 summary (after merge)
    summary.json                    Per-sample results + taxonomy_tasks
    stats.json                      Overall + by subset + by task + by dimension
    stats_by_task.json              19-task breakdown (MMTS taxonomy table)
    summary.md / stats_by_task.md   Human-readable reports
  logs/<EXP_NAME>.log
EOF
}

cmd_status() {
  local summary="${ROOT}/outputs/${EXP_NAME}/runs/summary.json"
  local target="${ROOT}/outputs/${EXP_NAME}/sample_ids.txt"
  if [[ ! -f "$target" ]]; then
    echo "[status] EXP_NAME=${EXP_NAME}: not started yet"
    exit 0
  fi
  local total done arch_ok base_ok
  total="$(wc -l < "$target" | tr -d ' ')"
  if [[ -f "$summary" ]]; then
    read -r done arch_ok base_ok <<< "$(python - <<PY
import json
from pathlib import Path
rows = json.loads(Path("${summary}").read_text())
print(len(rows), sum(1 for r in rows if r.get("arch_ok")), sum(1 for r in rows if r.get("baseline_ok")))
PY
)"
    echo "[status] EXP_NAME=${EXP_NAME}: batch ${done}/${total} completed"
    echo "[status] batch architecture correct: ${arch_ok}/${done}"
    echo "[status] batch baseline correct:    ${base_ok}/${done}"
    if [[ -f "${ROOT}/outputs/${EXP_NAME}/merged_2424/stats.json" ]]; then
      python - <<PY
import json
from pathlib import Path
s = json.loads(Path("${ROOT}/outputs/${EXP_NAME}/merged_2424/stats.json").read_text())
print(f"[status] merged 2424 architecture: {s['architecture_correct']}/{s['total']} ({s['architecture_accuracy']:.1%})")
print(f"[status] merged 2424 baseline:    {s['baseline_correct']}/{s['total']} ({s['baseline_accuracy']:.1%})")
print(f"[status] missing after merge:     {s['missing']}")
PY
    fi
  else
    echo "[status] EXP_NAME=${EXP_NAME}: 0/${total} completed"
  fi
}

cmd_merge() {
  python3 "${ROOT}/scripts/merge_full_benchmark_results.py" \
    --batch-dir "${ROOT}/outputs/${EXP_NAME}"
}

cmd_run() {
  need_data
  need_model
  local log="${LOG_DIR}/${EXP_NAME}.log"
  local reuse_args=()
  if [[ "$ALLOW_MIXED_FEASIBILITY" == "1" ]]; then
    reuse_args+=(--reuse-feasibility)
  fi
  echo "[INFO] Full MMTS-Bench run → outputs/${EXP_NAME}/"
  if [[ "$ALLOW_MIXED_FEASIBILITY" == "1" ]]; then
    echo "[WARN] Universe 2424 − old feasibility 19 = 2405 to run (mixed version)"
  else
    echo "[INFO] Universe 2424; all samples run with current code/prompts"
  fi
  echo "[INFO] Log: ${log}"
  echo "[INFO] Resume enabled — safe to restart after interruption"
  local baseline_args=(--no-run-baseline)
  if [[ "$RUN_BASELINE" == "1" ]]; then
    baseline_args=(--run-baseline)
    echo "[INFO] RUN_BASELINE=1 — architecture + baseline"
  else
    echo "[INFO] RUN_BASELINE=0 — architecture only"
  fi
  python3 "${ROOT}/scripts/run_full_benchmark_batch.py" \
    --exp-name "${EXP_NAME}" \
    --device "${DEVICE}" \
    --max-attempts "${MAX_ATTEMPTS}" \
    --retry-delay "${RETRY_DELAY}" \
    --resume \
    "${baseline_args[@]}" \
    "${reuse_args[@]}" \
    2>&1 | tee -a "${log}"
  echo "[DONE] Batch finished. Merge to 2424-sample summary:"
  echo "       bash scripts/run_full_benchmark.sh merge"
  echo "       # or: EXP_NAME=${EXP_NAME} bash scripts/run_full_benchmark.sh merge"
}

cmd="${1:-run}"
shift || true
case "$cmd" in
  help|-h|--help) cmd_help ;;
  status) cmd_status ;;
  merge) cmd_merge ;;
  run|"") cmd_run "$@" ;;
  *)
    echo "Unknown command: $cmd" >&2
    cmd_help
    exit 1
    ;;
esac
