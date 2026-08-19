# MMTS 可行性测试报告（19 任务 × 1 样例）

- 运行时间：2026-08-02
- 模型：Qwen2.5-14B（本地）
- 样本来源：`weighted_mmts_selection_200`（每任务 1 条 historical old-error 优先）
- 结果目录：`outputs/feasibility_test_19/runs/`

---

## 1. 总体结论

**可行性：通过。** 19 个任务类型均可正常跑通全流程（Planner → Homo ×3 → Hetero → Integration → Baseline），无崩溃、无超时、无工具异常。

**准确率：Architecture 10/19（52.6%），Baseline 11/19（57.9%）。**

| 指标 | Architecture | Baseline |
|---|---:|---:|
| 正确 | 10 | 11 |
| 错误 | 9 | 8 |
| 两者都对 | 7 | — |
| 两者都错 | 5 | — |
| Architecture 独对 | 3 | — |
| Baseline 独对 | 4 | — |

**效率：** Architecture 平均延迟 88.4s/条（中位数 90.7s），19 条合计约 **28 分钟**（仅 arch 部分）；含 baseline 总墙钟约 **35–40 分钟**。

**与历史对比：** 所选 19 条均为 historical old-error 样例；本次 Architecture 在其中答对 10 条，说明 prompt/工具改进后已有明显提升，但 Temporal Reasoning 仍是主要短板。

---

## 2. 分维度结果

| 维度 | 任务数 | Arch 正确 | Base 正确 | 通过率 |
|---|---:|---:|---:|---:|
| Structural Awareness | 3 | 2 | 3 | 67% / 100% |
| Feature Analysis | 5 | 3 | 2 | 60% / 40% |
| Temporal Reasoning | 5 | 1 | 2 | **20% / 40%** |
| Sequence Matching | 4 | 3 | 3 | 75% / 75% |
| Cross-Modal | 2 | 1 | 2 | 50% / 100% |

**最弱维度：Temporal Reasoning（5 题仅对 1 题 Ded.）**

---

## 3. 逐任务明细

| 任务 | 样例 | Gold | Arch | Base | 结果 | Tools | 延迟(s) |
|---|---|---|---|---|---|---:|---:|
| Non-Stationarity | Base:496 | -934.95 | -934.95 | -934.95 | ✅✅ | 3 | 80 |
| Local-Global | Base:597 | D | D | D | ✅✅ | 4 | 55 |
| Uni.-Multi. | Base:648 | 635.14 | A | 616.06 | ❌✅ | 3 | 97 |
| Trend | Base:194 | 0.40 | 0.399 | 9.45 | ✅❌ | 2 | 57 |
| Season. | InWild:508 | B | B | B | ✅✅ | 2 | 59 |
| Noise | InWild:251 | B | B | A | ✅❌ | 1 | 52 |
| Volat. | InWild:627 | B | C | C | ❌❌ | 2 | 61 |
| Basic | InWild:64 | B | A | A | ❌❌ | 1 | 48 |
| Ded. | InWild:979 | A | A | A | ✅✅ | 3 | 99 |
| Ind. | InWild:880 | A | B | A | ❌✅ | 5 | 116 |
| Causal | InWild:281 | D | B | B | ❌❌ | 4 | 91 |
| Analog. | InWild:392 | A | B | B | ❌❌ | 2 | 94 |
| Count. | InWild:1080 | D | B | B | ❌❌ | 4 | 123 |
| Isomorphic | Match:248 | C | C | C | ✅✅ | 12 | 128 |
| Robust | Match:77 | C | C | C | ✅✅ | 4 | 53 |
| Localization | Match:181 | D | D | C | ✅❌ | 4 | 89 |
| Reverse | Match:380 | B | A | B | ❌✅ | 12 | 132 |
| TS→Semantic | Align:73 | B | A | B | ❌✅ | 16 | 108 |
| Semantic→TS | Align:119 | B | B | B | ✅✅ | 12 | 139 |

图例：✅✅=arch/base 均对；✅❌=仅 arch 对；❌✅=仅 base 对；❌❌=均错

---

## 4. 失败模式分析（9 条）

### 4.1 数值题输出格式错误（1 条）

- **Uni.-Multi. `:648`**：问 Time Series 1 的 range，gold=635.14，arch 输出 `A`（选择题字母）
- 根因：数值题被 Integration 当作选择题处理；只用了 `describe_series`，未直接输出 range 数值

### 4.2 反事实推理（3 条，均错）

| 样例 | 任务 | 工具 | 问题 |
|---|---|---|---|
| `:627` Volat. | 维持 20–25 段波动到 35–40 | `counterfactual_simulate`, `sliding_stats` | 模拟后仍选 C（arch/base 同错） |
| `:64` Basic | 32–38 段保持均值，max 是否仍在 56 | `counterfactual_simulate` | 选 A（arch/base 同错） |
| `:1080` Count. | TS1 维持 3.5% 对 TS2 的影响 | `counterfactual_simulate`, `cross_series_compare` | 选 B，gold=D |

- 根因：`counterfactual_simulate` 已被调用，但 Agent 对 before/after 差异的解读与选项语义对齐不足；Integration 未严格依据 delta 字段仲裁

### 4.3 推理类选项误判（4 条）

| 样例 | 任务 | 工具 | 问题 |
|---|---|---|---|
| `:880` Ind. | 三序列分布特征 | `describe_series`, `segment_trend` | 选 B，gold=A；base 正确 |
| `:281` Causal | 两窗口因果/波动 | `diff_stats`, `sliding_stats` | 选 B，gold=D |
| `:392` Analog. | 两段噪声是否相似 | `noise_decomposition` | 选 B，gold=A |

- 根因：工具给出了局部统计，但 Agent 未将证据映射到具体选项措辞；缺少跨段对比工具（如 `advanced_features` 的 spectral entropy 对比）

### 4.4 专用匹配/对齐工具未使用（2 条）

| 样例 | 任务 | 实际工具 | 应使用 |
|---|---|---|---|
| `:380` Reverse | reverse it | `cross_series_compare` ×12 | **`reverse_match`** |
| `:73` TS→Semantic | ts→caption | `describe/global/local_extrema`, `segment_trend` | **`caption_verify`** |

- 根因：Planner 已提示使用 `reverse_match` / `caption_verify`，但 Hetero Agent 仍回退到通用 `cross_series_compare` 或原子工具
- 对比：`:119` Semantic→TS **成功**，Planner 同样建议 `caption_verify`，说明工具链在该方向可用但不稳定

---

## 5. 新工具使用情况

| 工具 | 调用次数 | 使用样例 | 评价 |
|---|---:|---|---|
| `counterfactual_simulate` | 4 | :627, :64, :1080 等 | ✅ 被调用，但 3/3 反事实题仍错 |
| `cross_series_compare` | 34 | Match 全系列 + 多 InWild | ⚠️ 过度使用，挤压专用工具 |
| `caption_verify` | 0（arch 路径） | — | ❌ TS→Semantic 失败样本未使用 |
| `reverse_match` | 0 | — | ❌ Reverse 失败样本未使用 |
| `robust_shape_match` | 0 | — | Robust 题 `:77` 碰巧用 cross_series_compare 答对 |
| `advanced_features` | 0 | — | Noise/Analog 题未用 spectral entropy |
| `crossing_points` | 0 | — | — |
| `lag_corr_scan` | 0 | — | Causal 题未用 |
| `extrema_align` | 0 | — | — |

**结论：新工具已注册且可调用，但 Agent 工具选择存在明显「路径依赖」——倾向复用 `cross_series_compare` / 原子工具，专用工具采纳率低。**

---

## 6. 成功亮点

1. **Structural/Base 数值题**：Non-Stationarity、Trend slope 均正确（`:496`, `:194`）
2. **Feature 基础题**：Seasonality `:508`、Noise `:251` 正确
3. **Matching 3/4**：Isomorphic、Robust、Localization 全对；Reverse 是唯一失败
4. **CrossModal Semantic→TS**：`:119` 在 caption_verify 路线下正确
5. **Deductive reasoning**：`:979` 双序列 seasonality 比较正确
6. **全流程稳定性**：19/19 无 crash，延迟可控（48–139s）

---

## 7. 200 条大规模实验建议

### 7.1 可以直接启动

- 流水线稳定，工具注册完整，单条约 1.5–2.5 分钟
- 200 条预计 **5–8 小时**（含 baseline），4×50 分块 checkpoint 已就绪

### 7.2 优先修复项（建议在 200 条前或并行进行）

| 优先级 | 问题 | 建议 |
|---|---|---|
| P0 | 数值题输出选择题字母 | Integration prompt 加强 question_type=numerical 分支 |
| P0 | 专用工具不被选用 | Hetero prompt 对 reverse/caption 任务强制首调专用工具 |
| P1 | 反事实题解读 | counterfactual 结果中 highlight delta + 选项映射示例 |
| P1 | Temporal Reasoning 20% | 推理 agent 增加选项逐条核验步骤 |
| P2 | cross_series_compare 滥用 | Homo/Hetero 限制 Match 题外的无差别调用 |

### 7.3 预期 200 条准确率区间

基于本次 52.6%（old-error 样本）及历史 weak-task 分布，修正工具选择后预期 **55–65%**；不修复则可能在 **50–55%** 区间。

---

## 8. 附件

- 逐条 IO：`outputs/feasibility_test_19/runs/<sample>/full_io.md`
- 汇总 JSON：`outputs/feasibility_test_19/runs/summary.json`
- 运行日志：`outputs/feasibility_test_19/run.log`
