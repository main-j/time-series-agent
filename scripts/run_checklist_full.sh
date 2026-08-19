#!/usr/bin/env bash
# Run the full weighted MMTS checklist (181 samples), excluding the 19
# feasibility-tested samples. Results can be merged back to 200 via
# scripts/merge_checklist_results.py.
#
# Usage:
#   bash scripts/run_checklist_full.sh              # start / resume full run
#   bash scripts/run_checklist_full.sh help
#   EXP_NAME=my_run bash scripts/run_checklist_full.sh
#   DEVICE=cuda:0 bash scripts/run_checklist_full.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1
export HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-1}"
export TRANSFORMERS_OFFLINE="${TRANSFORMERS_OFFLINE:-1}"

EXP_NAME="${EXP_NAME:-checklist_full_181}"
DEVICE="${DEVICE:-cuda:0}"
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
  if [[ ! -f "${ROOT}/outputs/weighted_mmts_selection_200/sample_ids.txt" ]]; then
    echo "[ERROR] Checklist missing: outputs/weighted_mmts_selection_200/sample_ids.txt" >&2
    exit 1
  fi
  if [[ ! -f "${ROOT}/outputs/feasibility_test_19/sample_ids.txt" ]]; then
    echo "[ERROR] Feasibility exclude list missing: outputs/feasibility_test_19/sample_ids.txt" >&2
    exit 1
  fi
  echo "[OK] Checklist 200 − feasibility 19 = 181 pending samples"
}

cmd_help() {
  cat <<'EOF'
Weighted MMTS checklist — full run (181 samples)
================================================

Runs architecture + baseline on the 200-sample regression checklist,
skipping the 19 samples already covered by feasibility_test_19.
Each sample checkpoint is written to outputs/<EXP_NAME>/runs/summary.json.

Commands:
  bash scripts/run_checklist_full.sh              Start or resume full run
  bash scripts/run_checklist_full.sh merge        Merge feasibility + batch → 200
  bash scripts/run_checklist_full.sh status       Show progress for current EXP_NAME
  bash scripts/run_checklist_full.sh help

Environment:
  EXP_NAME   Output directory name (default: checklist_full_181)
  DEVICE     CUDA device map (default: cuda:0)

After the batch finishes, merge results for full 200-sample statistics:
  bash scripts/run_checklist_full.sh merge
  # or
  python3 scripts/merge_checklist_results.py --batch-dir outputs/checklist_full_181

Outputs:
  outputs/<EXP_NAME>/runs/          Per-sample full_io.json / full_io.md
  outputs/<EXP_NAME>/runs/summary.json
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
    echo "[status] EXP_NAME=${EXP_NAME}: ${done}/${total} completed"
    echo "[status] architecture correct: ${arch_ok}/${done}"
    echo "[status] baseline correct:    ${base_ok}/${done}"
  else
    echo "[status] EXP_NAME=${EXP_NAME}: 0/${total} completed"
  fi
}

cmd_merge() {
  python3 "${ROOT}/scripts/merge_checklist_results.py" \
    --batch-dir "${ROOT}/outputs/${EXP_NAME}"
}

cmd_run() {
  need_data
  need_model
  local log="${LOG_DIR}/${EXP_NAME}.log"
  echo "[INFO] Full checklist run → outputs/${EXP_NAME}/"
  echo "[INFO] Excluding feasibility_test_19 (19 samples, reused at merge time)"
  echo "[INFO] Log: ${log}"
  echo "[INFO] Resume enabled — safe to restart after interruption"
  python3 "${ROOT}/scripts/run_checklist_batch.py" \
    --exp-name "${EXP_NAME}" \
    --device "${DEVICE}" \
    --resume \
    2>&1 | tee -a "${log}"
  echo "[DONE] Batch finished. Merge to 200-sample summary:"
  echo "       bash scripts/run_checklist_full.sh merge"
  echo "       # or: EXP_NAME=${EXP_NAME} bash scripts/run_checklist_full.sh merge"
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
