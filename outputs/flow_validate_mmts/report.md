# MMTS Flow Validation Report

- Provider: MockLLM (pipeline/flow correctness; not model quality)
- Seed: 20260729
- Samples: 8 stratified (2 per subset)
- Flow PASS: 8/8 (fail=0)

## Per-sample

| sample_id | subset | baseline | arch | gt | tools | scales | roles | flow |
|---|---|---|---|---|---:|---|---|---|
| `Base:synthtic_qa_700:106` | Base | A | A | D | 4 | [<ScaleName.SHORT: 'short'>, <ScaleName.MEDIUM: 'medium'>, <ScaleName.LONG: 'long'>] | [<HeterogeneousRole.MATCHING: 'matching'>] | PASS |
| `Base:synthtic_qa_700:43` | Base | A | A | A | 4 | [<ScaleName.SHORT: 'short'>, <ScaleName.MEDIUM: 'medium'>, <ScaleName.LONG: 'long'>] | [<HeterogeneousRole.MATCHING: 'matching'>] | PASS |
| `InWild:tsqa_1084:573` | InWild | A | A | A | 4 | [<ScaleName.SHORT: 'short'>, <ScaleName.MEDIUM: 'medium'>, <ScaleName.LONG: 'long'>] | [<HeterogeneousRole.MATCHING: 'matching'>] | PASS |
| `InWild:tsqa_1084:859` | InWild | A | A | A | 4 | [<ScaleName.SHORT: 'short'>, <ScaleName.MEDIUM: 'medium'>, <ScaleName.LONG: 'long'>] | [<HeterogeneousRole.MATCHING: 'matching'>] | PASS |
| `Match:qats_400:217` | Match | A | A | A | 4 | [<ScaleName.SHORT: 'short'>, <ScaleName.MEDIUM: 'medium'>, <ScaleName.LONG: 'long'>] | [<HeterogeneousRole.MATCHING: 'matching'>] | PASS |
| `Match:qats_400:286` | Match | A | A | B | 4 | [<ScaleName.SHORT: 'short'>, <ScaleName.MEDIUM: 'medium'>, <ScaleName.LONG: 'long'>] | [<HeterogeneousRole.MATCHING: 'matching'>] | PASS |
| `Align:ts2caption_qa_120:45` | Align | A | A | B | 4 | [<ScaleName.SHORT: 'short'>, <ScaleName.MEDIUM: 'medium'>, <ScaleName.LONG: 'long'>] | [<HeterogeneousRole.MATCHING: 'matching'>] | PASS |
| `Align:ts2caption_qa_120:57` | Align | A | A | A | 4 | [<ScaleName.SHORT: 'short'>, <ScaleName.MEDIUM: 'medium'>, <ScaleName.LONG: 'long'>] | [<HeterogeneousRole.MATCHING: 'matching'>] | PASS |

## Aggregate
- Baseline valid_output_rate: 1.0
- Architecture valid_output_rate: 1.0
- Avg architecture tool_calls: 4.0
- Avg architecture model_calls: 10.0

## Checked requirements
1. Baseline: single-shot, no tools, produces answer
2. Architecture: Planner -> Homogeneous scales -> Temporal Profile -> Heterogeneous roles -> Integration
3. Plan scales/roles executed and recorded
4. Tool calls > 0 on architecture mock path; baseline tools == 0
5. Prompt versions frozen into architecture traces
6. Choice answers are letter-form from Integration
