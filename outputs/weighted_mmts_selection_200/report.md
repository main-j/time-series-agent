# Weighted MMTS regression selection (200 unique samples)

- Seed: `20260802`
- Historical run: `/root/autodl-tmp/ts-agent-paper-repro/results/mmts_full_agent.jsonl`
- Policy: every taxonomy task has a minimum quota; weak and below-baseline strata are oversampled.
- Caveat: baseline references are subset-level choice accuracies, not paired per-task predictions.

| task | pool | quota | rate | historical arch | baseline ref | gap | historical errors | selected old errors |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CrossModal/Semantic→TS | 120 | 20 | 16.7% | 22.5% | 84.6% | -62.1% | 93 | 14 |
| Structural/Non-Stationarity | 100 | 16 | 16.0% | 10.0% | 37.7% | -27.7% | 90 | 11 |
| CrossModal/TS→Semantic | 120 | 16 | 13.3% | 45.8% | 84.6% | -38.8% | 65 | 11 |
| Matching/Localization | 100 | 14 | 14.0% | 43.0% | 54.8% | -11.8% | 57 | 10 |
| Feature/Season. | 264 | 12 | 4.5% | 31.4% | 47.0% | -15.5% | 181 | 8 |
| Feature/Noise | 248 | 12 | 4.8% | 30.2% | 46.6% | -16.4% | 173 | 8 |
| Feature/Volat. | 183 | 12 | 6.6% | 36.6% | 52.7% | -16.1% | 116 | 8 |
| Reasoning/Count. | 109 | 12 | 11.0% | 36.7% | 52.7% | -16.0% | 69 | 8 |
| Feature/Trend | 311 | 10 | 3.2% | 44.1% | 47.8% | -3.8% | 174 | 7 |
| Reasoning/Ded. | 194 | 10 | 5.2% | 41.2% | 52.7% | -11.4% | 114 | 7 |
| Reasoning/Ind. | 180 | 10 | 5.6% | 41.1% | 52.7% | -11.6% | 106 | 7 |
| Reasoning/Analog. | 151 | 10 | 6.6% | 43.7% | 52.7% | -9.0% | 85 | 7 |
| Feature/Basic | 392 | 8 | 2.0% | 60.5% | 45.0% | 15.4% | 155 | 6 |
| Reasoning/Causal | 129 | 8 | 6.2% | 43.4% | 52.7% | -9.3% | 73 | 6 |
| Structural/Local-Global | 100 | 6 | 6.0% | 90.0% | 37.7% | 52.3% | 10 | 4 |
| Structural/Uni.-Multi. | 700 | 6 | 0.9% | 48.7% | 37.7% | 11.1% | 359 | 4 |
| Matching/Robust | 100 | 6 | 6.0% | 95.0% | 54.8% | 40.2% | 5 | 4 |
| Matching/Isomorphic | 100 | 6 | 6.0% | 100.0% | 54.8% | 45.2% | 0 | 0 |
| Matching/Reverse | 100 | 6 | 6.0% | 100.0% | 54.8% | 45.2% | 0 | 0 |

## Selected samples

### CrossModal/Semantic→TS

- `Align:caption2ts_qa_120:119` · old-error · ['caption']
- `Align:caption2ts_qa_120:0` · old-error · ['caption']
- `Align:caption2ts_qa_120:80` · old-error · ['caption']
- `Align:caption2ts_qa_120:70` · old-error · ['caption']
- `Align:caption2ts_qa_120:114` · old-error · ['caption']
- `Align:caption2ts_qa_120:5` · old-error · ['caption']
- `Align:caption2ts_qa_120:112` · old-error · ['caption']
- `Align:caption2ts_qa_120:9` · old-error · ['caption']
- `Align:caption2ts_qa_120:115` · old-error · ['caption']
- `Align:caption2ts_qa_120:24` · old-error · ['caption']
- `Align:caption2ts_qa_120:101` · old-error · ['caption']
- `Align:caption2ts_qa_120:2` · old-error · ['caption']
- `Align:caption2ts_qa_120:71` · old-error · ['caption']
- `Align:caption2ts_qa_120:93` · old-error · ['caption']
- `Align:caption2ts_qa_120:88` · control · ['caption']
- `Align:caption2ts_qa_120:32` · control · ['caption']
- `Align:caption2ts_qa_120:90` · control · ['caption']
- `Align:caption2ts_qa_120:92` · control · ['caption']
- `Align:caption2ts_qa_120:8` · control · ['caption']
- `Align:caption2ts_qa_120:107` · control · ['caption']

### Structural/Non-Stationarity

- `Base:synthtic_qa_700:496` · old-error · ['stationarity']
- `Base:synthtic_qa_700:476` · old-error · ['stationarity']
- `Base:synthtic_qa_700:422` · old-error · ['stationarity']
- `Base:synthtic_qa_700:484` · old-error · ['stationarity']
- `Base:synthtic_qa_700:455` · old-error · ['stationarity']
- `Base:synthtic_qa_700:457` · old-error · ['stationarity']
- `Base:synthtic_qa_700:436` · old-error · ['stationarity']
- `Base:synthtic_qa_700:492` · old-error · ['stationarity']
- `Base:synthtic_qa_700:421` · old-error · ['stationarity']
- `Base:synthtic_qa_700:405` · old-error · ['stationarity']
- `Base:synthtic_qa_700:412` · old-error · ['stationarity']
- `Base:synthtic_qa_700:427` · control · ['stationarity']
- `Base:synthtic_qa_700:462` · control · ['stationarity']
- `Base:synthtic_qa_700:454` · control · ['stationarity']
- `Base:synthtic_qa_700:481` · control · ['stationarity']
- `Base:synthtic_qa_700:448` · control · ['stationarity']

### CrossModal/TS→Semantic

- `Align:ts2caption_qa_120:73` · old-error · caption
- `Align:ts2caption_qa_120:44` · old-error · caption
- `Align:ts2caption_qa_120:42` · old-error · caption
- `Align:ts2caption_qa_120:1` · old-error · caption
- `Align:ts2caption_qa_120:91` · old-error · caption
- `Align:ts2caption_qa_120:63` · old-error · caption
- `Align:ts2caption_qa_120:112` · old-error · caption
- `Align:ts2caption_qa_120:72` · old-error · caption
- `Align:ts2caption_qa_120:48` · old-error · caption
- `Align:ts2caption_qa_120:64` · old-error · caption
- `Align:ts2caption_qa_120:4` · old-error · caption
- `Align:ts2caption_qa_120:37` · control · caption
- `Align:ts2caption_qa_120:30` · control · caption
- `Align:ts2caption_qa_120:96` · control · caption
- `Align:ts2caption_qa_120:23` · control · caption
- `Align:ts2caption_qa_120:114` · control · caption

### Matching/Localization

- `Match:qats_400:181` · old-error · ['find it']
- `Match:qats_400:115` · old-error · ['find it']
- `Match:qats_400:167` · old-error · ['find it']
- `Match:qats_400:144` · old-error · ['find it']
- `Match:qats_400:163` · old-error · ['find it']
- `Match:qats_400:117` · old-error · ['find it']
- `Match:qats_400:157` · old-error · ['find it']
- `Match:qats_400:149` · old-error · ['find it']
- `Match:qats_400:143` · old-error · ['find it']
- `Match:qats_400:184` · old-error · ['find it']
- `Match:qats_400:108` · control · ['find it']
- `Match:qats_400:198` · control · ['find it']
- `Match:qats_400:154` · control · ['find it']
- `Match:qats_400:138` · control · ['find it']

### Feature/Season.

- `InWild:tsqa_1084:508` · old-error · ['seasonality analysis']
- `InWild:tsqa_1084:742` · old-error · ['seasonality analysis', 'causal reasoning']
- `Base:synthtic_qa_700:143` · old-error · ['seasonality analysis']
- `InWild:tsqa_1084:644` · old-error · ['seasonality analysis', 'inductive reasoning']
- `InWild:tsqa_1084:279` · old-error · ['seasonality analysis', 'deductive reasoning']
- `InWild:tsqa_1084:299` · old-error · ['seasonality analysis', 'analogical reasoning']
- `Base:synthtic_qa_700:145` · old-error · ['seasonality analysis']
- `InWild:tsqa_1084:273` · old-error · ['seasonality analysis', 'counterfactual reasoning']
- `Base:synthtic_qa_700:74` · control · ['seasonality analysis']
- `InWild:tsqa_1084:876` · control · ['seasonality analysis']
- `InWild:tsqa_1084:1063` · control · ['seasonality analysis', 'causal reasoning']
- `InWild:tsqa_1084:70` · control · ['seasonality analysis', 'counterfactual reasoning']

### Feature/Noise

- `InWild:tsqa_1084:251` · old-error · ['noise analysis', 'causal reasoning']
- `InWild:tsqa_1084:853` · old-error · ['noise analysis']
- `InWild:tsqa_1084:665` · old-error · ['noise analysis', 'counterfactual reasoning']
- `Base:synthtic_qa_700:94` · old-error · ['noise analysis']
- `InWild:tsqa_1084:594` · old-error · ['noise analysis', 'causal reasoning']
- `InWild:tsqa_1084:203` · old-error · ['noise analysis', 'deductive reasoning']
- `InWild:tsqa_1084:65` · old-error · ['noise analysis', 'inductive reasoning']
- `InWild:tsqa_1084:1008` · old-error · ['noise analysis']
- `Base:synthtic_qa_700:251` · control · ['noise analysis']
- `InWild:tsqa_1084:477` · control · ['noise analysis']
- `InWild:tsqa_1084:956` · control · ['noise analysis', 'deductive reasoning']
- `InWild:tsqa_1084:101` · control · ['noise analysis', 'analogical reasoning']

### Feature/Volat.

- `InWild:tsqa_1084:627` · old-error · ['volatility analysis', 'counterfactual reasoning']
- `InWild:tsqa_1084:772` · old-error · ['volatility analysis', 'analogical reasoning']
- `InWild:tsqa_1084:741` · old-error · ['volatility analysis', 'deductive reasoning']
- `InWild:tsqa_1084:191` · old-error · ['volatility analysis', 'causal reasoning']
- `InWild:tsqa_1084:76` · old-error · ['volatility analysis', 'inductive reasoning']
- `InWild:tsqa_1084:57` · old-error · ['volatility analysis', 'analogical reasoning']
- `InWild:tsqa_1084:993` · old-error · ['volatility analysis']
- `InWild:tsqa_1084:346` · old-error · ['volatility analysis', 'analogical reasoning']
- `InWild:tsqa_1084:1005` · control · ['volatility analysis']
- `InWild:tsqa_1084:92` · control · ['volatility analysis', 'deductive reasoning']
- `InWild:tsqa_1084:374` · control · ['volatility analysis', 'inductive reasoning']
- `InWild:tsqa_1084:28` · control · ['volatility analysis', 'inductive reasoning']

### Reasoning/Count.

- `InWild:tsqa_1084:1080` · old-error · ['basic analysis', 'counterfactual reasoning']
- `InWild:tsqa_1084:152` · old-error · ['basic analysis', 'counterfactual reasoning']
- `InWild:tsqa_1084:257` · old-error · ['trend analysis', 'counterfactual reasoning']
- `InWild:tsqa_1084:312` · old-error · ['noise analysis', 'counterfactual reasoning']
- `InWild:tsqa_1084:651` · old-error · ['counterfactual reasoning']
- `InWild:tsqa_1084:296` · old-error · ['noise analysis', 'counterfactual reasoning']
- `InWild:tsqa_1084:1016` · old-error · ['counterfactual reasoning']
- `InWild:tsqa_1084:535` · old-error · ['basic analysis', 'counterfactual reasoning']
- `InWild:tsqa_1084:1083` · control · ['trend analysis', 'counterfactual reasoning']
- `InWild:tsqa_1084:328` · control · ['counterfactual reasoning']
- `InWild:tsqa_1084:120` · control · ['volatility analysis', 'counterfactual reasoning']
- `InWild:tsqa_1084:434` · control · ['seasonality analysis', 'counterfactual reasoning']

### Feature/Trend

- `Base:synthtic_qa_700:194` · old-error · ['trend analysis']
- `InWild:tsqa_1084:982` · old-error · ['trend analysis']
- `InWild:tsqa_1084:673` · old-error · ['trend analysis']
- `InWild:tsqa_1084:111` · old-error · ['trend analysis', 'deductive reasoning']
- `InWild:tsqa_1084:209` · old-error · ['trend analysis', 'analogical reasoning']
- `Base:synthtic_qa_700:192` · old-error · ['trend analysis']
- `InWild:tsqa_1084:472` · old-error · ['trend analysis', 'deductive reasoning']
- `Base:synthtic_qa_700:166` · control · ['trend analysis']
- `InWild:tsqa_1084:668` · control · ['trend analysis', 'analogical reasoning']
- `InWild:tsqa_1084:595` · control · ['trend analysis', 'analogical reasoning']

### Reasoning/Ded.

- `InWild:tsqa_1084:979` · old-error · ['seasonality analysis', 'deductive reasoning']
- `InWild:tsqa_1084:130` · old-error · ['trend analysis', 'deductive reasoning']
- `InWild:tsqa_1084:519` · old-error · ['noise analysis', 'deductive reasoning']
- `InWild:tsqa_1084:518` · old-error · ['trend analysis', 'deductive reasoning']
- `InWild:tsqa_1084:1` · old-error · ['noise analysis', 'deductive reasoning']
- `InWild:tsqa_1084:237` · old-error · ['seasonality analysis', 'deductive reasoning']
- `InWild:tsqa_1084:989` · old-error · ['noise analysis', 'deductive reasoning']
- `InWild:tsqa_1084:180` · control · ['deductive reasoning']
- `InWild:tsqa_1084:915` · control · ['basic analysis', 'deductive reasoning']
- `InWild:tsqa_1084:981` · control · ['basic analysis', 'deductive reasoning']

### Reasoning/Ind.

- `InWild:tsqa_1084:880` · old-error · ['basic analysis', 'inductive reasoning']
- `InWild:tsqa_1084:506` · old-error · ['seasonality analysis', 'inductive reasoning']
- `InWild:tsqa_1084:617` · old-error · ['inductive reasoning']
- `InWild:tsqa_1084:775` · old-error · ['inductive reasoning']
- `InWild:tsqa_1084:232` · old-error · ['seasonality analysis', 'inductive reasoning']
- `InWild:tsqa_1084:250` · old-error · ['seasonality analysis', 'inductive reasoning']
- `InWild:tsqa_1084:747` · old-error · ['volatility analysis', 'inductive reasoning']
- `InWild:tsqa_1084:702` · control · ['inductive reasoning']
- `InWild:tsqa_1084:268` · control · ['noise analysis', 'inductive reasoning']
- `InWild:tsqa_1084:817` · control · ['seasonality analysis', 'inductive reasoning']

### Reasoning/Analog.

- `InWild:tsqa_1084:392` · old-error · ['noise analysis', 'analogical reasoning']
- `InWild:tsqa_1084:813` · old-error · ['basic analysis', 'analogical reasoning']
- `InWild:tsqa_1084:556` · old-error · ['noise analysis', 'analogical reasoning']
- `InWild:tsqa_1084:400` · old-error · ['trend analysis', 'analogical reasoning']
- `InWild:tsqa_1084:824` · old-error · ['trend analysis', 'analogical reasoning']
- `InWild:tsqa_1084:509` · old-error · ['trend analysis', 'analogical reasoning']
- `InWild:tsqa_1084:957` · old-error · ['analogical reasoning']
- `InWild:tsqa_1084:792` · control · ['analogical reasoning']
- `InWild:tsqa_1084:409` · control · ['trend analysis', 'analogical reasoning']
- `InWild:tsqa_1084:265` · control · ['analogical reasoning']

### Feature/Basic

- `InWild:tsqa_1084:64` · old-error · ['basic analysis', 'counterfactual reasoning']
- `Base:synthtic_qa_700:696` · old-error · ['basic analysis']
- `InWild:tsqa_1084:562` · old-error · ['basic analysis', 'deductive reasoning']
- `InWild:tsqa_1084:760` · old-error · ['basic analysis']
- `InWild:tsqa_1084:796` · old-error · ['basic analysis']
- `Base:synthtic_qa_700:374` · old-error · ['basic analysis']
- `Base:synthtic_qa_700:667` · control · ['basic analysis']
- `InWild:tsqa_1084:194` · control · ['basic analysis', 'deductive reasoning']

### Reasoning/Causal

- `InWild:tsqa_1084:281` · old-error · ['volatility analysis', 'causal reasoning']
- `InWild:tsqa_1084:1079` · old-error · ['causal reasoning']
- `InWild:tsqa_1084:288` · old-error · ['trend analysis', 'causal reasoning']
- `InWild:tsqa_1084:2` · old-error · ['noise analysis', 'causal reasoning']
- `InWild:tsqa_1084:939` · old-error · ['volatility analysis', 'causal reasoning']
- `InWild:tsqa_1084:389` · old-error · ['trend analysis', 'causal reasoning']
- `InWild:tsqa_1084:391` · control · ['seasonality analysis', 'causal reasoning']
- `InWild:tsqa_1084:680` · control · ['causal reasoning']

### Structural/Local-Global

- `Base:synthtic_qa_700:597` · old-error · ['index']
- `Base:synthtic_qa_700:556` · old-error · ['index']
- `Base:synthtic_qa_700:582` · old-error · ['index']
- `Base:synthtic_qa_700:573` · old-error · ['index']
- `Base:synthtic_qa_700:518` · control · ['index']
- `Base:synthtic_qa_700:540` · control · ['index']

### Structural/Uni.-Multi.

- `Base:synthtic_qa_700:648` · old-error · ['basic analysis']
- `Base:synthtic_qa_700:553` · old-error · ['index']
- `Base:synthtic_qa_700:247` · old-error · ['noise analysis']
- `Base:synthtic_qa_700:694` · old-error · ['basic analysis']
- `Base:synthtic_qa_700:153` · control · ['trend analysis']
- `Base:synthtic_qa_700:568` · control · ['index']

### Matching/Robust

- `Match:qats_400:77` · old-error · ['smooth it']
- `Match:qats_400:47` · old-error · ['smooth it']
- `Match:qats_400:57` · old-error · ['smooth it']
- `Match:qats_400:7` · old-error · ['smooth it']
- `Match:qats_400:79` · control · ['smooth it']
- `Match:qats_400:40` · control · ['smooth it']

### Matching/Isomorphic

- `Match:qats_400:248` · control · ['choose it']
- `Match:qats_400:290` · control · ['choose it']
- `Match:qats_400:271` · control · ['choose it']
- `Match:qats_400:244` · control · ['choose it']
- `Match:qats_400:285` · control · ['choose it']
- `Match:qats_400:241` · control · ['choose it']

### Matching/Reverse

- `Match:qats_400:380` · control · ['reverse it']
- `Match:qats_400:303` · control · ['reverse it']
- `Match:qats_400:376` · control · ['reverse it']
- `Match:qats_400:309` · control · ['reverse it']
- `Match:qats_400:357` · control · ['reverse it']
- `Match:qats_400:315` · control · ['reverse it']
