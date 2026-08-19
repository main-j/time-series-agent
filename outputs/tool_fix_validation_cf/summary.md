# 工具契约修复验证：反事实相关样本

## 选取样例

| 样例 | Gold | 历史预测 | 关联错误类型 |
|---|---:|---:|---|
| `InWild:tsqa_1084:64` | B | A | `replacement: period_average` 被静默忽略，仍返回 success |
| `InWild:tsqa_1084:1080` | D | B | `replace_segment` + `value` 导致 `n_changed=0` 仍被当作有效反事实证据 |

## 端到端结果

| 样例 | Gold | 修复前 | 修复后 | 是否改善 |
|---|---:|---:|---:|---|
| `InWild:tsqa_1084:64` | B | A | **B** | 是（答案正确） |
| `InWild:tsqa_1084:1080` | D | B | B | 否（仍错） |

输出目录：`outputs/tool_fix_validation_cf/`

## 工具层行为对比（直接调用 registry）

### 样例 64 — 拒绝非法字段

**修复前（可行性测试）：**
```json
{"op": "replace_segment", "start": 32, "end": 38, "replacement": "period_average"}
→ success=true, n_changed=6（语义错误：未按 period average 替换）
→ 架构推断 max 仍在 index 56 → 选 A
```

**修复后：**
```json
{"op": "replace_segment", "replacement": "period_average"}
→ success=false, error="replace_segment has unsupported fields: replacement"
```

**正确调用：**
```json
{"op": "replace_with_mean", "start": 32, "end": 38, "mean_source_start": 32, "mean_source_end": 38}
→ success=true, n_changed=7, max_index before/after = 56/56
```

### 样例 1080 — 拒绝无效应编辑

**修复前：**
```json
{"op": "replace_segment", "start": 0, "end": 863, "value": 3.5}
→ success=true, n_changed=0（静默无变化，仍被 Agent 当作「已替换为 3.5%」）
```

**修复后：**
```json
{"op": "replace_segment", "value": 3.5}
→ success=false, error="replace_segment has unsupported fields: value"

{"op": "replace_constant", "start": 0, "end": 863, "value": 3.5}
→ success=true, n_changed=839, evidence_usable=true
```

## 运行时观察

1. **静默语义错误已消除**：非法 operation 字段、`n_changed=0` 的伪成功不再返回可用证据。
2. **LLM 调用格式仍不匹配**：Agent 频繁发送 `{"replace_constant": {...}}` 嵌套格式，而解析器要求 `{"op": "replace_constant", ...}`。端到端两次运行中，**所有 counterfactual_simulate 调用均失败**，但 Agent 仍声称「已成功执行」并引用失败 call_id。
3. **64 答案改善但证据链不可靠**：最终选 B 与 gold 一致，但工具并未成功返回 `max_index`；属于 retry 后仍失败、推理层幻觉式补全，不能视为工具证据驱动。
4. **1080 仍错**：跨序列反事实（改 TS1 推断 TS2）本身超出工具能力；修复前靠「假成功 + cross_series_compare」误判为 B，修复后工具拒绝伪证据，但 Agent 仍忽略失败、维持 B，未转向 D。

## 结论

- **工具层修复有效**：目标错误模式（静默忽略字段、无效应 success）已在 registry 层被阻断。
- **端到端仅 1/2 样本答案改善**，且改善样本的证据链仍不完整。
- **下一步建议（最小代价）**：
  1. 在 `_canonical_counterfactual_operation` 中兼容 Prompt 描述的嵌套格式（`{"replace_constant":{...}}` → 归一化为 `op` 格式）。
  2. Prompt 中 operation 示例统一为 `{"op":"replace_constant","start":0,"end":863,"value":3.5}`。
  3. 强化 Integration/roles：禁止引用 `success=false` 或缺失 `evidence_usable=true` 的 tool call。
