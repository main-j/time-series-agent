# Fix validation notes (post MMTS accuracy repair)
#
# Archive: outputs/full_benchmark_2424 is a pre-fix diagnostic run.
# Do NOT merge it with new results.
#
# This diagnostic set (5 IDs) is REGRESSION-ONLY. It is not a generalization gate.
# Use outputs/splits/generalization_v1/{smoke_76,dev_190,heldout_190} for generalization.
#
# New experiment directory: outputs/full_benchmark_2424_fixed
# Default: architecture only (RUN_BASELINE=0)
#
# Commands:
#   bash scripts/run_diagnostic_fix.sh
#   python3 scripts/select_generalization_split.py
#   python3 scripts/run_checklist_batch.py --checklist-file outputs/splits/generalization_v1/smoke_76/sample_ids.txt --no-exclude-feasibility --exp-name gen_smoke_v1_code_routing --resume
#   EXP_NAME=full_benchmark_2424_fixed RUN_BASELINE=0 bash scripts/run_full_benchmark.sh
