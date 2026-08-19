# MMTS 可行性测试：19 任务类型各 1 样例

从 `weighted_mmts_selection_200` 中，为每个 MMTS 任务类型选取 1 条样本，用于验证全流程（Planner → Homo → Hetero → Integration）能否正常跑通。

- 选取策略：每个任务取该分层中的第一条 **historical old-error** 样例（若存在），以优先覆盖历史薄弱项
- 输出目录：`outputs/feasibility_test_19/`
- 运行命令见下方

## 任务 × 样例对照

| 维度 | 任务 | 样例 ID | 子集 | 历史结果 | 标准答案 |
|---|---|---|---|---|---|
| Structural Awareness | Non-Stationarity | `Base:synthtic_qa_700:496` | Base | old-error | -934.95 |
| Structural Awareness | Local-Global | `Base:synthtic_qa_700:597` | Base | old-error | D |
| Structural Awareness | Uni.-Multi. | `Base:synthtic_qa_700:648` | Base | old-error | 635.14 |
| Feature Analysis | Trend | `Base:synthtic_qa_700:194` | Base | old-error | 0.40 |
| Feature Analysis | Season. | `InWild:tsqa_1084:508` | InWild | old-error | B |
| Feature Analysis | Noise | `InWild:tsqa_1084:251` | InWild | old-error | B |
| Feature Analysis | Volat. | `InWild:tsqa_1084:627` | InWild | old-error | B |
| Feature Analysis | Basic | `InWild:tsqa_1084:64` | InWild | old-error | B |
| Temporal Reasoning | Ded. | `InWild:tsqa_1084:979` | InWild | old-error | A |
| Temporal Reasoning | Ind. | `InWild:tsqa_1084:880` | InWild | old-error | A |
| Temporal Reasoning | Causal | `InWild:tsqa_1084:281` | InWild | old-error | D |
| Temporal Reasoning | Analog. | `InWild:tsqa_1084:392` | InWild | old-error | A |
| Temporal Reasoning | Count. | `InWild:tsqa_1084:1080` | InWild | old-error | D |
| Sequence Matching | Isomorphic | `Match:qats_400:248` | Match | control | C |
| Sequence Matching | Robust | `Match:qats_400:77` | Match | old-error | C |
| Sequence Matching | Localization | `Match:qats_400:181` | Match | old-error | D |
| Sequence Matching | Reverse | `Match:qats_400:380` | Match | control | B |
| Cross-Modal | TS→Semantic | `Align:ts2caption_qa_120:73` | Align | old-error | B |
| Cross-Modal | Semantic→TS | `Align:caption2ts_qa_120:119` | Align | old-error | B |

## 子集分布

- Base: 4
- InWild: 9
- Match: 4
- Align: 2

## 运行方式

```bash
cd /root/autodl-tmp/time-series-agent
python3 scripts/run_feasibility_batch.py
```

结果将写入 `outputs/feasibility_test_19/runs/`。
