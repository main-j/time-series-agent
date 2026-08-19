#!/usr/bin/env bash
# Architecture-only diagnostic rerun for the known failing Base samples.
# Keeps outputs separate from the pre-fix full_benchmark_2424 archive.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1
export HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-1}"
export TRANSFORMERS_OFFLINE="${TRANSFORMERS_OFFLINE:-1}"

EXP_NAME="${EXP_NAME:-diagnostic_fix_validation}"
DEVICE="${DEVICE:-cuda:0}"
IDS_FILE="${IDS_FILE:-${ROOT}/outputs/diagnostic_fix_validation/sample_ids.txt}"
LOG="${ROOT}/logs/${EXP_NAME}.log"
mkdir -p "${ROOT}/logs" "${ROOT}/outputs/${EXP_NAME}"

if [[ ! -f "$IDS_FILE" ]]; then
  echo "[ERROR] Missing diagnostic IDs: $IDS_FILE" >&2
  exit 1
fi

echo "[INFO] Diagnostic fix validation → outputs/${EXP_NAME}/"
echo "[INFO] Samples: $(grep -cve '^$' "$IDS_FILE")"
echo "[INFO] Architecture only (baseline skipped)"
echo "[INFO] Log: ${LOG}"

python3 "${ROOT}/scripts/run_diagnostic_fix.py" \
  --exp-name "$EXP_NAME" \
  --device "$DEVICE" \
  --ids-file "$IDS_FILE" \
  2>&1 | tee -a "$LOG"
