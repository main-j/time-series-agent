# Tool-fix validation v2（嵌套格式 + 证据链加固后）

## 改动摘要

1. **registry**：兼容 `{"replace_constant":{...}}` 嵌套格式与字符串 operation；`max_value_index` → `max_index`；`replace_with_mean` 默认同段均值源
2. **roles**：仅保留 `success=true` 且 `evidence_usable!=false` 的 cited_tool_call_ids；工具全失败时清空 candidate_preference
3. **Prompt**：counterfactual operation 统一为带 `"op"` 的 JSON 示例

## 端到端结果

| 样例 | Gold | 可行性测试 | CF v1 | CF v2 |
|---|---:|---:|---:|---:|
| `InWild:tsqa_1084:64` | B | A | B（幻觉） | **A**（工具一致） |
| `InWild:tsqa_1084:1080` | D | B | B | B |

## 工具层（v2 已打通）

**64**：Homo 成功调用 `{"op":"replace_with_mean",...}` → `max_index` 56→56，`evidence_usable=true`

**1080**：Homo 成功调用 `replace_constant(0–863, 3.5)` → `n_changed=839`；`cross_series_effect_supported=false`

## 解读

- **工具契约修复目标达成**：非法字段拒绝、嵌套格式可用、真实 `n_changed`、跨序列限制字段返回
- **64**：v2 答案与工具 ground truth 一致（A），但与 gold B 不符——需单独核查 gold 或「period average」语义
- **1080**：工具已成功修改 TS1，但 Agent 仍从 TS1 变化推断 TS2 选 B；属于跨序列反事实推理上限，非静默工具 bug
