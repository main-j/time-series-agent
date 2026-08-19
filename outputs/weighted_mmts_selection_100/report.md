# Weighted MMTS regression selection (100 unique samples)

- Seed: `20260802`
- Historical run: `/root/autodl-tmp/ts-agent-paper-repro/results/mmts_full_agent.jsonl`
- Policy: every taxonomy task has a minimum quota; weak and below-baseline strata are oversampled.
- Caveat: baseline references are subset-level choice accuracies, not paired per-task predictions.

| task | pool | quota | rate | historical arch | baseline ref | gap | historical errors | selected old errors |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CrossModal/Semantic→TS | 120 | 10 | 8.3% | 22.5% | 84.6% | -62.1% | 93 | 7 |
| Structural/Non-Stationarity | 100 | 8 | 8.0% | 10.0% | 37.7% | -27.7% | 90 | 6 |
| CrossModal/TS→Semantic | 120 | 8 | 6.7% | 45.8% | 84.6% | -38.8% | 65 | 6 |
| Matching/Localization | 100 | 7 | 7.0% | 43.0% | 54.8% | -11.8% | 57 | 5 |
| Feature/Season. | 264 | 6 | 2.3% | 31.4% | 47.0% | -15.5% | 181 | 4 |
| Feature/Noise | 248 | 6 | 2.4% | 30.2% | 46.6% | -16.4% | 173 | 4 |
| Feature/Volat. | 183 | 6 | 3.3% | 36.6% | 52.7% | -16.1% | 116 | 4 |
| Reasoning/Count. | 109 | 6 | 5.5% | 36.7% | 52.7% | -16.0% | 69 | 4 |
| Feature/Trend | 311 | 5 | 1.6% | 44.1% | 47.8% | -3.8% | 174 | 4 |
| Reasoning/Ded. | 194 | 5 | 2.6% | 41.2% | 52.7% | -11.4% | 114 | 4 |
| Reasoning/Ind. | 180 | 5 | 2.8% | 41.1% | 52.7% | -11.6% | 106 | 4 |
| Reasoning/Analog. | 151 | 5 | 3.3% | 43.7% | 52.7% | -9.0% | 85 | 4 |
| Feature/Basic | 392 | 4 | 1.0% | 60.5% | 45.0% | 15.4% | 155 | 3 |
| Reasoning/Causal | 129 | 4 | 3.1% | 43.4% | 52.7% | -9.3% | 73 | 3 |
| Structural/Local-Global | 100 | 3 | 3.0% | 90.0% | 37.7% | 52.3% | 10 | 2 |
| Structural/Uni.-Multi. | 700 | 3 | 0.4% | 48.7% | 37.7% | 11.1% | 359 | 2 |
| Matching/Robust | 100 | 3 | 3.0% | 95.0% | 54.8% | 40.2% | 5 | 2 |
| Matching/Isomorphic | 100 | 3 | 3.0% | 100.0% | 54.8% | 45.2% | 0 | 0 |
| Matching/Reverse | 100 | 3 | 3.0% | 100.0% | 54.8% | 45.2% | 0 | 0 |

## Selected samples

### CrossModal/Semantic→TS

- `Align:caption2ts_qa_120:119` · old-error · ['caption']
- `Align:caption2ts_qa_120:0` · old-error · ['caption']
- `Align:caption2ts_qa_120:80` · old-error · ['caption']
- `Align:caption2ts_qa_120:70` · old-error · ['caption']
- `Align:caption2ts_qa_120:114` · old-error · ['caption']
- `Align:caption2ts_qa_120:5` · old-error · ['caption']
- `Align:caption2ts_qa_120:112` · old-error · ['caption']
- `Align:caption2ts_qa_120:118` · control · ['caption']
- `Align:caption2ts_qa_120:19` · control · ['caption']
- `Align:caption2ts_qa_120:107` · control · ['caption']

### Structural/Non-Stationarity

- `Base:synthtic_qa_700:496` · old-error · ['stationarity']
- `Base:synthtic_qa_700:476` · old-error · ['stationarity']
- `Base:synthtic_qa_700:422` · old-error · ['stationarity']
- `Base:synthtic_qa_700:484` · old-error · ['stationarity']
- `Base:synthtic_qa_700:455` · old-error · ['stationarity']
- `Base:synthtic_qa_700:457` · old-error · ['stationarity']
- `Base:synthtic_qa_700:439` · control · ['stationarity']
- `Base:synthtic_qa_700:454` · control · ['stationarity']

### CrossModal/TS→Semantic

- `Align:ts2caption_qa_120:73` · old-error · caption
- `Align:ts2caption_qa_120:44` · old-error · caption
- `Align:ts2caption_qa_120:42` · old-error · caption
- `Align:ts2caption_qa_120:1` · old-error · caption
- `Align:ts2caption_qa_120:91` · old-error · caption
- `Align:ts2caption_qa_120:63` · old-error · caption
- `Align:ts2caption_qa_120:24` · control · caption
- `Align:ts2caption_qa_120:81` · control · caption

### Matching/Localization

- `Match:qats_400:181` · old-error · ['find it']
- `Match:qats_400:115` · old-error · ['find it']
- `Match:qats_400:167` · old-error · ['find it']
- `Match:qats_400:144` · old-error · ['find it']
- `Match:qats_400:163` · old-error · ['find it']
- `Match:qats_400:136` · control · ['find it']
- `Match:qats_400:154` · control · ['find it']

### Feature/Season.

- `InWild:tsqa_1084:508` · old-error · ['seasonality analysis']
- `InWild:tsqa_1084:742` · old-error · ['seasonality analysis', 'causal reasoning']
- `Base:synthtic_qa_700:143` · old-error · ['seasonality analysis']
- `InWild:tsqa_1084:644` · old-error · ['seasonality analysis', 'inductive reasoning']
- `InWild:tsqa_1084:258` · control · ['seasonality analysis']
- `InWild:tsqa_1084:816` · control · ['seasonality analysis', 'analogical reasoning']

### Feature/Noise

- `InWild:tsqa_1084:251` · old-error · ['noise analysis', 'causal reasoning']
- `InWild:tsqa_1084:853` · old-error · ['noise analysis']
- `InWild:tsqa_1084:665` · old-error · ['noise analysis', 'counterfactual reasoning']
- `Base:synthtic_qa_700:94` · old-error · ['noise analysis']
- `InWild:tsqa_1084:498` · control · ['noise analysis', 'deductive reasoning']
- `InWild:tsqa_1084:959` · control · ['noise analysis']

### Feature/Volat.

- `InWild:tsqa_1084:627` · old-error · ['volatility analysis', 'counterfactual reasoning']
- `InWild:tsqa_1084:772` · old-error · ['volatility analysis', 'analogical reasoning']
- `InWild:tsqa_1084:741` · old-error · ['volatility analysis', 'deductive reasoning']
- `InWild:tsqa_1084:191` · old-error · ['volatility analysis', 'causal reasoning']
- `InWild:tsqa_1084:983` · control · ['volatility analysis', 'inductive reasoning']
- `InWild:tsqa_1084:303` · control · ['volatility analysis', 'counterfactual reasoning']

### Reasoning/Count.

- `InWild:tsqa_1084:651` · old-error · ['counterfactual reasoning']
- `InWild:tsqa_1084:257` · old-error · ['trend analysis', 'counterfactual reasoning']
- `InWild:tsqa_1084:1062` · old-error · ['trend analysis', 'counterfactual reasoning']
- `InWild:tsqa_1084:601` · old-error · ['volatility analysis', 'counterfactual reasoning']
- `InWild:tsqa_1084:419` · control · ['basic analysis', 'counterfactual reasoning']
- `InWild:tsqa_1084:1007` · control · ['counterfactual reasoning']

### Feature/Trend

- `Base:synthtic_qa_700:194` · old-error · ['trend analysis']
- `InWild:tsqa_1084:404` · old-error · ['trend analysis', 'analogical reasoning']
- `InWild:tsqa_1084:325` · old-error · ['trend analysis']
- `InWild:tsqa_1084:667` · old-error · ['trend analysis', 'counterfactual reasoning']
- `InWild:tsqa_1084:1083` · control · ['trend analysis', 'counterfactual reasoning']

### Reasoning/Ded.

- `InWild:tsqa_1084:464` · old-error · ['seasonality analysis', 'deductive reasoning']
- `InWild:tsqa_1084:965` · old-error · ['seasonality analysis', 'deductive reasoning']
- `InWild:tsqa_1084:503` · old-error · ['deductive reasoning']
- `InWild:tsqa_1084:576` · old-error · ['noise analysis', 'deductive reasoning']
- `InWild:tsqa_1084:996` · control · ['volatility analysis', 'deductive reasoning']

### Reasoning/Ind.

- `InWild:tsqa_1084:888` · old-error · ['trend analysis', 'inductive reasoning']
- `InWild:tsqa_1084:0` · old-error · ['seasonality analysis', 'inductive reasoning']
- `InWild:tsqa_1084:264` · old-error · ['basic analysis', 'inductive reasoning']
- `InWild:tsqa_1084:1047` · old-error · ['seasonality analysis', 'inductive reasoning']
- `InWild:tsqa_1084:309` · control · ['inductive reasoning']

### Reasoning/Analog.

- `InWild:tsqa_1084:131` · old-error · ['noise analysis', 'analogical reasoning']
- `InWild:tsqa_1084:813` · old-error · ['basic analysis', 'analogical reasoning']
- `InWild:tsqa_1084:25` · old-error · ['seasonality analysis', 'analogical reasoning']
- `InWild:tsqa_1084:418` · old-error · ['volatility analysis', 'analogical reasoning']
- `InWild:tsqa_1084:592` · control · ['analogical reasoning']

### Feature/Basic

- `InWild:tsqa_1084:75` · old-error · ['basic analysis', 'deductive reasoning']
- `Base:synthtic_qa_700:629` · old-error · ['basic analysis']
- `InWild:tsqa_1084:838` · old-error · ['basic analysis', 'causal reasoning']
- `Base:synthtic_qa_700:601` · control · ['basic analysis']

### Reasoning/Causal

- `InWild:tsqa_1084:281` · old-error · ['volatility analysis', 'causal reasoning']
- `InWild:tsqa_1084:1079` · old-error · ['causal reasoning']
- `InWild:tsqa_1084:288` · old-error · ['trend analysis', 'causal reasoning']
- `InWild:tsqa_1084:851` · control · ['seasonality analysis', 'causal reasoning']

### Structural/Local-Global

- `Base:synthtic_qa_700:597` · old-error · ['index']
- `Base:synthtic_qa_700:556` · old-error · ['index']
- `Base:synthtic_qa_700:521` · control · ['index']

### Structural/Uni.-Multi.

- `Base:synthtic_qa_700:16` · old-error · ['seasonality analysis']
- `Base:synthtic_qa_700:669` · old-error · ['basic analysis']
- `Base:synthtic_qa_700:564` · control · ['index']

### Matching/Robust

- `Match:qats_400:77` · old-error · ['smooth it']
- `Match:qats_400:47` · old-error · ['smooth it']
- `Match:qats_400:38` · control · ['smooth it']

### Matching/Isomorphic

- `Match:qats_400:248` · control · ['choose it']
- `Match:qats_400:290` · control · ['choose it']
- `Match:qats_400:271` · control · ['choose it']

### Matching/Reverse

- `Match:qats_400:380` · control · ['reverse it']
- `Match:qats_400:303` · control · ['reverse it']
- `Match:qats_400:376` · control · ['reverse it']
