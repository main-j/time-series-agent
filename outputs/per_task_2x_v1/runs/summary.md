# Checklist batch summary (per_task_2x_v1)

| sample | subset | n_series | task | gold | arch | base | arch_ok | base_ok | tools | latency_s |
|---|---|---:|---|---|---|---|---|---|---:|---:|
| `Base:synthtic_qa_700:459` | SubsetName.BASE | 1 | ['stationarity'] | -250.66 | -250.66 | None | True | None | 6 | 125.4 |
| `Base:synthtic_qa_700:488` | SubsetName.BASE | 1 | ['stationarity'] |  115.36 | 115.36162873024024 | None | True | None | 3 | 77.4 |
| `Base:synthtic_qa_700:531` | SubsetName.BASE | 1 | ['index'] | A | A | None | True | None | 2 | 85.7 |
| `Base:synthtic_qa_700:585` | SubsetName.BASE | 1 | ['index'] | 7 | 7 | None | True | None | 1 | 58.7 |
| `Base:synthtic_qa_700:423` | SubsetName.BASE | 1 | ['stationarity'] |  690.83 | 690.822 | None | True | None | 3 | 75.2 |
| `Base:synthtic_qa_700:321` | SubsetName.BASE | 1 | ['basic analysis'] |  134.44 | 134.445 | None | True | None | 3 | 111.5 |
| `InWild:tsqa_1084:831` | SubsetName.INWILD | 2 | ['trend analysis'] | A | A | None | True | None | 10 | 219.3 |
| `InWild:tsqa_1084:189` | SubsetName.INWILD | 1 | ['trend analysis', 'deductive reasoning'] | B | B | None | True | None | 4 | 65.3 |
| `Base:synthtic_qa_700:112` | SubsetName.BASE | 1 | ['seasonality analysis'] | D | D | None | True | None | 7 | 95.9 |
| `Base:synthtic_qa_700:108` | SubsetName.BASE | 1 | ['seasonality analysis'] | B | A | None | False | None | 4 | 78.2 |
| `InWild:tsqa_1084:453` | SubsetName.INWILD | 1 | ['noise analysis', 'inductive reasoning'] | A | A | None | True | None | 2 | 51.2 |
| `Base:synthtic_qa_700:91` | SubsetName.BASE | 1 | ['noise analysis'] | A | C | None | False | None | 6 | 122.1 |
| `InWild:tsqa_1084:662` | SubsetName.INWILD | 2 | ['volatility analysis'] | B | B | None | True | None | 4 | 83.8 |
| `InWild:tsqa_1084:1005` | SubsetName.INWILD | 2 | ['volatility analysis'] | B | B | None | True | None | 4 | 133.7 |
| `Base:synthtic_qa_700:384` | SubsetName.BASE | 1 | ['basic analysis'] |  37.88 | 37.88 | None | True | None | 1 | 52.2 |
| `Base:synthtic_qa_700:379` | SubsetName.BASE | 1 | ['basic analysis'] | -133.47 | -133.47 | None | True | None | 6 | 106.4 |
| `InWild:tsqa_1084:956` | SubsetName.INWILD | 2 | ['noise analysis', 'deductive reasoning'] | C | C | None | True | None | 3 | 116.4 |
| `InWild:tsqa_1084:878` | SubsetName.INWILD | 3 | ['noise analysis', 'deductive reasoning'] | A | A | None | True | None | 5 | 103.7 |
| `InWild:tsqa_1084:250` | SubsetName.INWILD | 1 | ['seasonality analysis', 'inductive reasoning'] | A | A | None | True | None | 13 | 118.0 |
| `InWild:tsqa_1084:47` | SubsetName.INWILD | 1 | ['trend analysis', 'inductive reasoning'] | D | C | None | False | None | 10 | 96.8 |
| `InWild:tsqa_1084:663` | SubsetName.INWILD | 2 | ['causal reasoning'] | A | A | None | True | None | 10 | 217.9 |
| `InWild:tsqa_1084:944` | SubsetName.INWILD | 4 | ['causal reasoning'] | C |  | None | False | None | 0 | 42.3 |
| `InWild:tsqa_1084:88` | SubsetName.INWILD | 1 | ['trend analysis', 'analogical reasoning'] | B | B | None | True | None | 2 | 68.0 |
| `InWild:tsqa_1084:908` | SubsetName.INWILD | 3 | ['seasonality analysis', 'analogical reasoning'] | B | A | None | False | None | 3 | 113.7 |
| `InWild:tsqa_1084:172` | SubsetName.INWILD | 1 | ['counterfactual reasoning'] | B | B | None | True | None | 5 | 98.9 |
| `InWild:tsqa_1084:303` | SubsetName.INWILD | 1 | ['volatility analysis', 'counterfactual reasoning'] | A | B | None | False | None | 4 | 83.4 |
| `Match:qats_400:239` | SubsetName.MATCH | 5 | ['choose it'] | B | B | None | True | None | 4 | 72.8 |
| `Match:qats_400:226` | SubsetName.MATCH | 5 | ['choose it'] | B | C | None | False | None | 3 | 75.3 |
| `Match:qats_400:57` | SubsetName.MATCH | 5 | ['smooth it'] | A | B | None | False | None | 15 | 145.8 |
| `Match:qats_400:15` | SubsetName.MATCH | 5 | ['smooth it'] | C | C | None | True | None | 18 | 142.7 |
| `Match:qats_400:136` | SubsetName.MATCH | 5 | ['find it'] | A | D | None | False | None | 19 | 140.7 |
| `Match:qats_400:161` | SubsetName.MATCH | 5 | ['find it'] | D | D | None | True | None | 22 | 193.1 |
| `Match:qats_400:340` | SubsetName.MATCH | 5 | ['reverse it'] | A | C | None | False | None | 20 | 185.2 |
| `Match:qats_400:314` | SubsetName.MATCH | 5 | ['reverse it'] | D | D | None | True | None | 24 | 193.4 |
| `Align:ts2caption_qa_120:56` | SubsetName.ALIGN | 1 | caption | D | D | None | True | None | 11 | 95.8 |
| `Align:ts2caption_qa_120:38` | SubsetName.ALIGN | 1 | caption | D | D | None | True | None | 11 | 104.7 |
| `Align:caption2ts_qa_120:47` | SubsetName.ALIGN | 4 | ['caption'] | B | B | None | True | None | 15 | 128.1 |
| `Align:caption2ts_qa_120:97` | SubsetName.ALIGN | 4 | ['caption'] | A | A | None | True | None | 17 | 128.3 |

Architecture correct: **28/38**
Baseline correct: **0/38**