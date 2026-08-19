# Per-task selection (2 per task, seed=20260803)

- Taxonomy tasks: 19
- Total picks (with duplicates): 38
- Unique samples to run: 38

| Task | Subset | Pool | Picked | Sample IDs |
|---|---|---|---:|---|
| Non-Stationarity | Base | 100 | 2 | `Base:synthtic_qa_700:459`, `Base:synthtic_qa_700:488` |
| Local-Global | Base | 100 | 2 | `Base:synthtic_qa_700:531`, `Base:synthtic_qa_700:585` |
| Uni.-Multi. | Base | 700 | 2 | `Base:synthtic_qa_700:423`, `Base:synthtic_qa_700:321` |
| Trend | Base & InWild | 311 | 2 | `InWild:tsqa_1084:831`, `InWild:tsqa_1084:189` |
| Season. | Base & InWild | 264 | 2 | `Base:synthtic_qa_700:112`, `Base:synthtic_qa_700:108` |
| Noise | Base & InWild | 248 | 2 | `InWild:tsqa_1084:453`, `Base:synthtic_qa_700:91` |
| Volat. | Base & InWild | 183 | 2 | `InWild:tsqa_1084:662`, `InWild:tsqa_1084:1005` |
| Basic | Base & InWild | 392 | 2 | `Base:synthtic_qa_700:384`, `Base:synthtic_qa_700:379` |
| Ded. | InWild | 194 | 2 | `InWild:tsqa_1084:956`, `InWild:tsqa_1084:878` |
| Ind. | InWild | 180 | 2 | `InWild:tsqa_1084:250`, `InWild:tsqa_1084:47` |
| Causal | InWild | 129 | 2 | `InWild:tsqa_1084:663`, `InWild:tsqa_1084:944` |
| Analog. | InWild | 151 | 2 | `InWild:tsqa_1084:88`, `InWild:tsqa_1084:908` |
| Count. | InWild | 109 | 2 | `InWild:tsqa_1084:172`, `InWild:tsqa_1084:303` |
| Isomorphic | Match | 100 | 2 | `Match:qats_400:239`, `Match:qats_400:226` |
| Robust | Match | 100 | 2 | `Match:qats_400:57`, `Match:qats_400:15` |
| Localization | Match | 100 | 2 | `Match:qats_400:136`, `Match:qats_400:161` |
| Reverse | Match | 100 | 2 | `Match:qats_400:340`, `Match:qats_400:314` |
| TS→Semantic | Align | 120 | 2 | `Align:ts2caption_qa_120:56`, `Align:ts2caption_qa_120:38` |
| Semantic→TS | Align | 120 | 2 | `Align:caption2ts_qa_120:47`, `Align:caption2ts_qa_120:97` |

## By subset (unique samples)

### Base (11)

- `Base:synthtic_qa_700:459` — tasks=['Structural/Non-Stationarity', 'Structural/Uni.-Multi.'], task_type=['stationarity']
- `Base:synthtic_qa_700:488` — tasks=['Structural/Non-Stationarity', 'Structural/Uni.-Multi.'], task_type=['stationarity']
- `Base:synthtic_qa_700:531` — tasks=['Structural/Local-Global', 'Structural/Uni.-Multi.'], task_type=['index']
- `Base:synthtic_qa_700:585` — tasks=['Structural/Local-Global', 'Structural/Uni.-Multi.'], task_type=['index']
- `Base:synthtic_qa_700:423` — tasks=['Structural/Non-Stationarity', 'Structural/Uni.-Multi.'], task_type=['stationarity']
- `Base:synthtic_qa_700:321` — tasks=['Structural/Uni.-Multi.', 'Feature/Basic'], task_type=['basic analysis']
- `Base:synthtic_qa_700:112` — tasks=['Structural/Uni.-Multi.', 'Feature/Season.'], task_type=['seasonality analysis']
- `Base:synthtic_qa_700:108` — tasks=['Structural/Uni.-Multi.', 'Feature/Season.'], task_type=['seasonality analysis']
- `Base:synthtic_qa_700:91` — tasks=['Structural/Uni.-Multi.', 'Feature/Noise'], task_type=['noise analysis']
- `Base:synthtic_qa_700:384` — tasks=['Structural/Uni.-Multi.', 'Feature/Basic'], task_type=['basic analysis']
- `Base:synthtic_qa_700:379` — tasks=['Structural/Uni.-Multi.', 'Feature/Basic'], task_type=['basic analysis']

### InWild (15)

- `InWild:tsqa_1084:831` — tasks=['Feature/Trend'], task_type=['trend analysis']
- `InWild:tsqa_1084:189` — tasks=['Feature/Trend', 'Reasoning/Ded.'], task_type=['trend analysis', 'deductive reasoning']
- `InWild:tsqa_1084:453` — tasks=['Feature/Noise', 'Reasoning/Ind.'], task_type=['noise analysis', 'inductive reasoning']
- `InWild:tsqa_1084:662` — tasks=['Feature/Volat.'], task_type=['volatility analysis']
- `InWild:tsqa_1084:1005` — tasks=['Feature/Volat.'], task_type=['volatility analysis']
- `InWild:tsqa_1084:956` — tasks=['Feature/Noise', 'Reasoning/Ded.'], task_type=['noise analysis', 'deductive reasoning']
- `InWild:tsqa_1084:878` — tasks=['Feature/Noise', 'Reasoning/Ded.'], task_type=['noise analysis', 'deductive reasoning']
- `InWild:tsqa_1084:250` — tasks=['Feature/Season.', 'Reasoning/Ind.'], task_type=['seasonality analysis', 'inductive reasoning']
- `InWild:tsqa_1084:47` — tasks=['Feature/Trend', 'Reasoning/Ind.'], task_type=['trend analysis', 'inductive reasoning']
- `InWild:tsqa_1084:663` — tasks=['Reasoning/Causal'], task_type=['causal reasoning']
- `InWild:tsqa_1084:944` — tasks=['Reasoning/Causal'], task_type=['causal reasoning']
- `InWild:tsqa_1084:88` — tasks=['Feature/Trend', 'Reasoning/Analog.'], task_type=['trend analysis', 'analogical reasoning']
- `InWild:tsqa_1084:908` — tasks=['Feature/Season.', 'Reasoning/Analog.'], task_type=['seasonality analysis', 'analogical reasoning']
- `InWild:tsqa_1084:172` — tasks=['Reasoning/Count.'], task_type=['counterfactual reasoning']
- `InWild:tsqa_1084:303` — tasks=['Feature/Volat.', 'Reasoning/Count.'], task_type=['volatility analysis', 'counterfactual reasoning']

### Match (8)

- `Match:qats_400:239` — tasks=['Matching/Isomorphic'], task_type=['choose it']
- `Match:qats_400:226` — tasks=['Matching/Isomorphic'], task_type=['choose it']
- `Match:qats_400:57` — tasks=['Matching/Robust'], task_type=['smooth it']
- `Match:qats_400:15` — tasks=['Matching/Robust'], task_type=['smooth it']
- `Match:qats_400:136` — tasks=['Matching/Localization'], task_type=['find it']
- `Match:qats_400:161` — tasks=['Matching/Localization'], task_type=['find it']
- `Match:qats_400:340` — tasks=['Matching/Reverse'], task_type=['reverse it']
- `Match:qats_400:314` — tasks=['Matching/Reverse'], task_type=['reverse it']

### Align (4)

- `Align:ts2caption_qa_120:56` — tasks=['CrossModal/TS→Semantic'], task_type=caption
- `Align:ts2caption_qa_120:38` — tasks=['CrossModal/TS→Semantic'], task_type=caption
- `Align:caption2ts_qa_120:47` — tasks=['CrossModal/Semantic→TS'], task_type=['caption']
- `Align:caption2ts_qa_120:97` — tasks=['CrossModal/Semantic→TS'], task_type=['caption']
