# Full MMTS architecture evaluation — taxonomy stats

- Scored samples: 2222
- Skipped (tool/exception): 202
- Baseline not run in this experiment (base_ok columns are unused).

## Overall

- Architecture: **1211/2222** (54.5%)
- Baseline: **0/2222** (0.0%)

## By subset

| Subset | n | arch_ok | base_ok | arch_acc | base_acc |
|---|---:|---:|---:|---:|---:|
| Base | 684 | 504 | 0 | 73.7% | 0.0% |
| InWild | 961 | 468 | 0 | 48.7% | 0.0% |
| Match | 375 | 152 | 0 | 40.5% | 0.0% |
| Align | 202 | 87 | 0 | 43.1% | 0.0% |

## By task (MMTS taxonomy)

| Dimension | Task | Subset | n | arch_ok | base_ok | arch_acc | base_acc |
|---|---|---|---:|---:|---:|---:|---:|
| Structural Awareness | Non-Stationarity | Base | 99 | 86 | 0 | 86.9% | 0.0% |
| Structural Awareness | Local-Global | Base | 98 | 81 | 0 | 82.7% | 0.0% |
| Structural Awareness | Uni.-Multi. | Base | 684 | 504 | 0 | 73.7% | 0.0% |
| Feature Analysis | Trend | Base & InWild | 294 | 199 | 0 | 67.7% | 0.0% |
| Feature Analysis | Season. | Base & InWild | 239 | 111 | 0 | 46.4% | 0.0% |
| Feature Analysis | Noise | Base & InWild | 233 | 89 | 0 | 38.2% | 0.0% |
| Feature Analysis | Volat. | Base & InWild | 167 | 86 | 0 | 51.5% | 0.0% |
| Feature Analysis | Basic | Base & InWild | 357 | 244 | 0 | 68.3% | 0.0% |
| Temporal Reasoning | Ded. | InWild | 175 | 83 | 0 | 47.4% | 0.0% |
| Temporal Reasoning | Ind. | InWild | 163 | 78 | 0 | 47.9% | 0.0% |
| Temporal Reasoning | Causal | InWild | 116 | 60 | 0 | 51.7% | 0.0% |
| Temporal Reasoning | Analog. | InWild | 137 | 56 | 0 | 40.9% | 0.0% |
| Temporal Reasoning | Count. | InWild | 91 | 42 | 0 | 46.2% | 0.0% |
| Sequence Matching | Isomorphic | Match | 100 | 60 | 0 | 60.0% | 0.0% |
| Sequence Matching | Robust | Match | 100 | 41 | 0 | 41.0% | 0.0% |
| Sequence Matching | Localization | Match | 92 | 28 | 0 | 30.4% | 0.0% |
| Sequence Matching | Reverse | Match | 83 | 23 | 0 | 27.7% | 0.0% |
| Cross-Modal Understanding | TS→Semantic | Align | 109 | 57 | 0 | 52.3% | 0.0% |
| Cross-Modal Understanding | Semantic→TS | Align | 93 | 30 | 0 | 32.3% | 0.0% |

## By dimension (pool aggregate; samples may appear in multiple tasks within a dimension)

| Dimension | n | arch_ok | base_ok | arch_acc | base_acc |
|---|---:|---:|---:|---:|---:|
| Structural Awareness | 881 | 671 | 0 | 76.2% | 0.0% |
| Feature Analysis | 1290 | 729 | 0 | 56.5% | 0.0% |
| Temporal Reasoning | 682 | 319 | 0 | 46.8% | 0.0% |
| Sequence Matching | 375 | 152 | 0 | 40.5% | 0.0% |
| Cross-Modal Understanding | 202 | 87 | 0 | 43.1% | 0.0% |