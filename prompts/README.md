# Prompt Template Library

All prompts follow the Datawhaler Prompt Engineering guide:
https://datawhaler.feishu.cn/wiki/MgWgw5Zpfie8h9kfx4OcUUiYnJc

## Rules
1. Clear, specific instructions with delimiters (`<question>`, `<timeseries>`, ...)
2. Structured JSON outputs with explicit schemas
3. Numbered reasoning steps before conclusions
4. Self-check requirements before finalizing
5. Versioned filenames: `<role>_vN.yaml` — never overwrite silently

## Current versions
- `baseline_v1.yaml`
- `planner_v1.yaml`
- `homogeneous_v1.yaml`
- `heterogeneous_v1.yaml`
- `integration_v1.yaml`

## Iteration workflow
1. Change only development-set samples.
2. Bump version (e.g. `planner_v1` -> `planner_v2`) and update agent references if needed.
3. Freeze versions into the experiment output manifest/traces before full runs.
