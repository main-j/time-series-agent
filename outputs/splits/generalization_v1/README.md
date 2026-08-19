# Generalization splits (v1)

Policy: **metadata-only**, no historical correctness / old-error oversampling.

- Seed: `20260803`
- Generator: `scripts/select_generalization_split.py`
- Contaminants excluded: weighted_200, feasibility_19, diagnostic_5, ad-hoc debug IDs

| Split | Role | Size |
|-------|------|------|
| `smoke_76` | fast sanity | 76 |
| `dev_190` | prompt/code ablation | 190 |
| `heldout_190` | final generalization gate (do not tune against) | 190 |
| `reserve_*` | unused remainder | ~1763 |

## Commands

```bash
# regenerate splits
python3 scripts/select_generalization_split.py

# unit tests
pytest tests/ -q

# smoke (architecture only)
python3 scripts/run_checklist_batch.py \
  --checklist-file outputs/splits/generalization_v1/smoke_76/sample_ids.txt \
  --no-exclude-feasibility \
  --exp-name gen_smoke_v1_code_routing \
  --resume

# held-out gate (run once after choosing a variant on dev)
python3 scripts/run_checklist_batch.py \
  --checklist-file outputs/splits/generalization_v1/heldout_190/sample_ids.txt \
  --no-exclude-feasibility \
  --exp-name gen_heldout_v1_code_routing \
  --resume
```

Regression-only (not a generalization gate):
- `outputs/diagnostic_fix_validation/`
- `outputs/weighted_mmts_selection_200/`
- `outputs/feasibility_test_19/`
