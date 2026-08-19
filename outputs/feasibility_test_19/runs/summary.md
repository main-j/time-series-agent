# Feasibility test summary (19 tasks)

| sample | subset | n_series | task | gold | arch | base | arch_ok | base_ok | tools | latency_s |
|---|---|---:|---|---|---|---|---|---|---:|---:|
| `Base:synthtic_qa_700:496` | SubsetName.BASE | 1 | ['stationarity'] | -934.95 | -934.95 | -934.95 | True | True | 3 | 79.5 |
| `Base:synthtic_qa_700:597` | SubsetName.BASE | 1 | ['index'] | D | D | D | True | True | 4 | 54.6 |
| `Base:synthtic_qa_700:648` | SubsetName.BASE | 2 | ['basic analysis'] | 635.14 | A | 616.06 | False | True | 3 | 96.5 |
| `Base:synthtic_qa_700:194` | SubsetName.BASE | 1 | ['trend analysis'] |  0.40 | 0.399 | 9.45 | True | False | 2 | 56.6 |
| `InWild:tsqa_1084:508` | SubsetName.INWILD | 1 | ['seasonality analysis'] | B | B | B | True | True | 2 | 59.2 |
| `InWild:tsqa_1084:251` | SubsetName.INWILD | 1 | ['noise analysis', 'causal reasoning'] | B | B | A | True | False | 1 | 51.9 |
| `InWild:tsqa_1084:627` | SubsetName.INWILD | 1 | ['volatility analysis', 'counterfactual reasoning'] | B | C | C | False | False | 2 | 61.0 |
| `InWild:tsqa_1084:64` | SubsetName.INWILD | 1 | ['basic analysis', 'counterfactual reasoning'] | B | A | A | False | False | 1 | 48.4 |
| `InWild:tsqa_1084:979` | SubsetName.INWILD | 2 | ['seasonality analysis', 'deductive reasoning'] | A | A | A | True | True | 3 | 99.1 |
| `InWild:tsqa_1084:880` | SubsetName.INWILD | 3 | ['basic analysis', 'inductive reasoning'] | A | B | A | False | True | 5 | 115.8 |
| `InWild:tsqa_1084:281` | SubsetName.INWILD | 1 | ['volatility analysis', 'causal reasoning'] | D | B | B | False | False | 4 | 90.7 |
| `InWild:tsqa_1084:392` | SubsetName.INWILD | 1 | ['noise analysis', 'analogical reasoning'] | A | B | B | False | False | 2 | 93.8 |
| `InWild:tsqa_1084:1080` | SubsetName.INWILD | 2 | ['basic analysis', 'counterfactual reasoning'] | D | B | B | False | False | 4 | 123.1 |
| `Match:qats_400:248` | SubsetName.MATCH | 5 | ['choose it'] | C | C | C | True | True | 12 | 127.5 |
| `Match:qats_400:77` | SubsetName.MATCH | 5 | ['smooth it'] | C | C | C | True | True | 4 | 52.6 |
| `Match:qats_400:181` | SubsetName.MATCH | 5 | ['find it'] | D | D | C | True | False | 4 | 89.3 |
| `Match:qats_400:380` | SubsetName.MATCH | 5 | ['reverse it'] | B | A | B | False | True | 12 | 132.4 |
| `Align:ts2caption_qa_120:73` | SubsetName.ALIGN | 1 | caption | B | A | B | False | True | 16 | 107.9 |
| `Align:caption2ts_qa_120:119` | SubsetName.ALIGN | 4 | ['caption'] | B | B | B | True | True | 12 | 138.9 |

Architecture correct: **10/19**