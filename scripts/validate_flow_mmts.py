"""Pick real MMTS samples and validate full Baseline/Architecture flow compliance."""
from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

from ts_agent.core.llm import MockLLMProvider
from ts_agent.data.mmts import MMTSBenchDataset
from ts_agent.evaluation.metrics import compare_summaries, save_traces, summarize_traces
from ts_agent.pipelines.experiment import ExperimentPipeline
from ts_agent.schemas.models import HeterogeneousRole, ScaleName

ROOT = Path("/root/autodl-tmp/time-series-agent")
OUT = ROOT / "outputs" / "flow_validate_mmts"
PROMPTS = ROOT / "prompts"
SEED = 20260729
PER_SUBSET = 2  # 8 samples total


REQUIRED_PROMPT_VERSIONS = {
    "baseline_v1",
    "planner_v1",
    "homogeneous_v1",
    "heterogeneous_v1",
    "integration_v1",
}


def pick_samples(ds: MMTSBenchDataset) -> List[Any]:
    rng = random.Random(SEED)
    buckets: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for meta in ds.index:
        buckets[meta["subset"]].append(meta)
    selected_meta = []
    for subset in ["Base", "InWild", "Match", "Align"]:
        pool = buckets[subset][:]
        rng.shuffle(pool)
        selected_meta.extend(pool[:PER_SUBSET])
    return [ds.get(m) for m in selected_meta]


def check_baseline(trace) -> List[str]:
    errs = []
    if not trace.success:
        errs.append(f"baseline success=False error={trace.error}")
    if trace.tool_calls != 0:
        errs.append(f"baseline must not call tools, got {trace.tool_calls}")
    if trace.model_calls < 1:
        errs.append("baseline model_calls < 1")
    if not trace.predicted_answer:
        errs.append("baseline empty predicted_answer")
    if trace.question_type == "choice" and len(str(trace.predicted_answer).strip()) != 1:
        # mock may return letter; tolerate longer only if letter-like
        ans = str(trace.predicted_answer).strip().upper()
        if ans not in list("ABCDEFGH") and not (len(ans) == 1 and ans.isalpha()):
            errs.append(f"baseline choice answer not a letter: {trace.predicted_answer!r}")
    return errs


def check_architecture(trace, sample) -> List[str]:
    errs = []
    if not trace.success:
        errs.append(f"architecture success=False error={trace.error}")
        return errs
    d = trace.details or {}
    plan = d.get("plan") or {}
    profile = d.get("temporal_profile") or {}
    evidences = d.get("evidences") or []
    final = d.get("final") or {}
    versions = d.get("prompt_versions") or {}

    # Planner
    if not plan.get("reasoning"):
        errs.append("plan.reasoning missing")
    scales = plan.get("scales") or []
    if not scales:
        errs.append("plan.scales empty")
    roles = plan.get("heterogeneous_agents") or []
    if not roles:
        errs.append("plan.heterogeneous_agents empty")
    for s in scales:
        if s not in {x.value for x in ScaleName}:
            errs.append(f"invalid scale in plan: {s}")
    for r in roles:
        if r not in {x.value for x in HeterogeneousRole}:
            errs.append(f"invalid role in plan: {r}")

    # Temporal profile covers requested scales
    for s in scales:
        if profile.get(s) is None:
            errs.append(f"temporal_profile missing scale={s}")
        else:
            obs = profile[s]
            if not obs.get("observations"):
                errs.append(f"scale={s} observations empty")
            # Homogeneous must not emit final MC answer as sole job; observations ok
            joined = " ".join(obs.get("observations") or []).upper()
            # soft: don't fail if letter appears inside text, but flag pure answer-only
            if obs.get("observations") == [sample.answer]:
                errs.append(f"scale={s} appears to leak final answer only")

    # Heterogeneous evidences match plan roles
    got_roles = [e.get("role") for e in evidences]
    if sorted(got_roles) != sorted(roles):
        errs.append(f"evidences roles {got_roles} != plan {roles}")
    for e in evidences:
        if not e.get("evidence"):
            errs.append(f"role={e.get('role')} evidence empty")

    # Integration final answer
    if not final.get("answer"):
        errs.append("final.answer missing")
    if not final.get("reasoning"):
        errs.append("final.reasoning missing")
    if sample.question_type == "choice":
        ans = str(final.get("answer", "")).strip().upper()
        if ans not in list("ABCDEFGH"):
            errs.append(f"final choice answer not letter A-H: {final.get('answer')!r}")

    # System metrics expectations for architecture
    if trace.model_calls < 2:
        errs.append(f"architecture model_calls too low: {trace.model_calls}")
    # Mock always uses tools on homo; expect some tool calls
    if trace.tool_calls < 1:
        errs.append("architecture expected >=1 tool calls on mock path")

    # Prompt versions frozen into trace
    missing_v = REQUIRED_PROMPT_VERSIONS - set(versions)
    if missing_v:
        errs.append(f"prompt_versions missing {sorted(missing_v)}")

    # Match/Align multi-series samples should still succeed
    if sample.subset.value in {"Match", "Align"} and len(sample.series) < 1:
        errs.append("multi-subset sample has empty series")

    return errs


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ds = MMTSBenchDataset(
        ROOT / "data/processed/mmts-bench",
        raw_dir=ROOT / "data/raw/mmts-bench",
        max_series_text_chars=4000,
    )
    samples = pick_samples(ds)
    pipe = ExperimentPipeline(MockLLMProvider(), str(PROMPTS), max_tool_rounds=3)

    baseline_traces = []
    arch_traces = []
    report_rows = []

    print(f"Picked {len(samples)} real MMTS samples (seed={SEED}, {PER_SUBSET}/subset)\n")
    for sample in samples:
        print("=" * 72)
        print(
            f"{sample.sample_id} | subset={sample.subset.value} | "
            f"n_series={len(sample.series)} lens={[len(s) for s in sample.series][:6]} | "
            f"qtype={sample.question_type} | task={sample.task_type}"
        )
        print(f"Q: {sample.question[:140]}")

        b = pipe.run_baseline(sample)
        a = pipe.run_architecture(sample)
        baseline_traces.append(b)
        arch_traces.append(a)

        b_errs = check_baseline(b)
        a_errs = check_architecture(a, sample)
        ok = not b_errs and not a_errs
        row = {
            "sample_id": sample.sample_id,
            "subset": sample.subset.value,
            "n_series": len(sample.series),
            "question_type": sample.question_type,
            "task_type": sample.task_type,
            "baseline_pred": b.predicted_answer,
            "architecture_pred": a.predicted_answer,
            "ground_truth": sample.answer,
            "baseline_ok": not b_errs,
            "architecture_ok": not a_errs,
            "baseline_errors": b_errs,
            "architecture_errors": a_errs,
            "architecture_model_calls": a.model_calls,
            "architecture_tool_calls": a.tool_calls,
            "plan_scales": (a.details or {}).get("plan", {}).get("scales"),
            "plan_roles": (a.details or {}).get("plan", {}).get("heterogeneous_agents"),
        }
        report_rows.append(row)
        status = "PASS" if ok else "FAIL"
        print(
            f"[{status}] baseline={b.predicted_answer!r} arch={a.predicted_answer!r} gt={sample.answer!r} "
            f"model_calls={a.model_calls} tool_calls={a.tool_calls} "
            f"scales={row['plan_scales']} roles={row['plan_roles']}"
        )
        if b_errs:
            print("  baseline errors:", b_errs)
        if a_errs:
            print("  architecture errors:", a_errs)

    save_traces(baseline_traces, OUT / "baseline_traces.jsonl")
    save_traces(arch_traces, OUT / "architecture_traces.jsonl")
    bsum = summarize_traces(baseline_traces)
    asum = summarize_traces(arch_traces)
    cmp = compare_summaries(bsum, asum)
    (OUT / "baseline_summary.json").write_text(json.dumps(bsum, indent=2), encoding="utf-8")
    (OUT / "architecture_summary.json").write_text(json.dumps(asum, indent=2), encoding="utf-8")
    (OUT / "comparison.json").write_text(json.dumps(cmp, indent=2), encoding="utf-8")
    (OUT / "flow_checks.json").write_text(json.dumps(report_rows, indent=2, ensure_ascii=False), encoding="utf-8")

    n_pass = sum(1 for r in report_rows if r["baseline_ok"] and r["architecture_ok"])
    n_fail = len(report_rows) - n_pass
    md = [
        "# MMTS Flow Validation Report",
        "",
        f"- Provider: MockLLM (pipeline/flow correctness; not model quality)",
        f"- Seed: {SEED}",
        f"- Samples: {len(report_rows)} stratified ({PER_SUBSET} per subset)",
        f"- Flow PASS: {n_pass}/{len(report_rows)} (fail={n_fail})",
        "",
        "## Per-sample",
        "",
        "| sample_id | subset | baseline | arch | gt | tools | scales | roles | flow |",
        "|---|---|---|---|---|---:|---|---|---|",
    ]
    for r in report_rows:
        flow = "PASS" if r["baseline_ok"] and r["architecture_ok"] else "FAIL"
        md.append(
            f"| `{r['sample_id']}` | {r['subset']} | {r['baseline_pred']} | {r['architecture_pred']} | "
            f"{r['ground_truth']} | {r['architecture_tool_calls']} | {r['plan_scales']} | {r['plan_roles']} | {flow} |"
        )
    md.extend(
        [
            "",
            "## Aggregate",
            f"- Baseline valid_output_rate: {bsum.get('valid_output_rate')}",
            f"- Architecture valid_output_rate: {asum.get('valid_output_rate')}",
            f"- Avg architecture tool_calls: {asum.get('avg_tool_calls')}",
            f"- Avg architecture model_calls: {asum.get('avg_model_calls')}",
            "",
            "## Checked requirements",
            "1. Baseline: single-shot, no tools, produces answer",
            "2. Architecture: Planner -> Homogeneous scales -> Temporal Profile -> Heterogeneous roles -> Integration",
            "3. Plan scales/roles executed and recorded",
            "4. Tool calls > 0 on architecture mock path; baseline tools == 0",
            "5. Prompt versions frozen into architecture traces",
            "6. Choice answers are letter-form from Integration",
            "",
        ]
    )
    (OUT / "report.md").write_text("\n".join(md), encoding="utf-8")
    print("\n" + "=" * 72)
    print(f"FLOW RESULT: {n_pass}/{len(report_rows)} PASS")
    print(f"Wrote {OUT}")
    raise SystemExit(0 if n_fail == 0 else 1)


if __name__ == "__main__":
    main()
