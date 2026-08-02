#!/usr/bin/env python3
"""Run one InWild MMTS sample and dump all agent LLM I/O."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("PYTHONUNBUFFERED", "1")

from ts_agent.core.llm import build_provider
from ts_agent.core.utils import ensure_dir, load_yaml
from ts_agent.data.mmts import MMTSBenchDataset
from ts_agent.pipelines.experiment import ExperimentPipeline


SAMPLE_ID = "InWild:tsqa_1084:860"
EXP_NAME = "single_inwild_860_io"


def main() -> None:
    cfg = load_yaml(ROOT / "configs" / "experiment.yaml")
    cfg["experiment"]["use_mock_llm"] = False
    cfg["experiment"]["max_series_text_chars"] = None
    # avoid polluting shared cache with debug tags
    cfg["experiment"]["cache_dir"] = str(ROOT / "outputs" / EXP_NAME / "llm_cache")
    # keep full model on one GPU
    cfg["model"]["device_map"] = "cuda:0"

    print(f"[info] loading sample {SAMPLE_ID}", flush=True)
    ds = MMTSBenchDataset(
        cfg["data"]["processed_dir"],
        raw_dir=cfg["data"]["raw_dir"],
        max_series_text_chars=None,
    )
    samples = ds.filter(sample_ids=[SAMPLE_ID])
    if not samples:
        raise SystemExit(f"sample not found: {SAMPLE_ID}")
    sample = samples[0]
    print(
        f"[info] n_series={len(sample.series)} lens={[len(x) for x in sample.series]} "
        f"task={sample.task_type} gold={sample.answer}",
        flush=True,
    )
    print(f"[info] Q: {sample.question[:200]}", flush=True)

    print("[info] building LLM provider (Qwen2.5-14B)...", flush=True)
    llm = build_provider(cfg)
    llm.record_io = True
    pipe = ExperimentPipeline(
        llm,
        cfg["experiment"]["prompt_dir"],
        max_tool_rounds=int(cfg["experiment"].get("max_tool_rounds", 3)),
    )

    out_dir = ensure_dir(ROOT / "outputs" / EXP_NAME)
    print("[info] running architecture...", flush=True)
    arch = pipe.run_architecture(sample)
    print(
        f"[info] architecture pred={arch.predicted_answer} gold={arch.ground_truth} "
        f"ok={arch.success} calls={arch.model_calls} tools={arch.tool_calls} "
        f"latency={arch.latency_sec:.1f}s error={arch.error}",
        flush=True,
    )

    print("[info] running baseline...", flush=True)
    base = pipe.run_baseline(sample)
    print(
        f"[info] baseline pred={base.predicted_answer} gold={base.ground_truth} "
        f"ok={base.success} calls={base.model_calls} latency={base.latency_sec:.1f}s",
        flush=True,
    )

    payload = {
        "sample_id": sample.sample_id,
        "question": sample.question,
        "options": sample.option,
        "gold": sample.answer,
        "task_type": sample.task_type,
        "n_series": len(sample.series),
        "series_lengths": [len(x) for x in sample.series],
        "architecture": arch.model_dump(),
        "baseline": base.model_dump(),
    }
    out_json = out_dir / "full_io.json"
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    # also write a readable markdown dump of each LLM call
    md_lines = [
        f"# Single InWild IO dump: `{SAMPLE_ID}`",
        "",
        f"- Question: {sample.question}",
        f"- Options: {sample.option}",
        f"- Gold: `{sample.answer}`",
        f"- Architecture pred: `{arch.predicted_answer}` (success={arch.success})",
        f"- Baseline pred: `{base.predicted_answer}` (success={base.success})",
        f"- Architecture model_calls={arch.model_calls}, tool_calls={arch.tool_calls}, latency={arch.latency_sec:.1f}s",
        "",
    ]
    calls = (arch.details or {}).get("llm_calls") or []
    for c in calls:
        md_lines.append(f"## Call {c.get('call_index')}: `{c.get('call_tag')}`")
        md_lines.append("")
        md_lines.append(
            f"tokens prompt={c.get('prompt_tokens')} completion={c.get('completion_tokens')} "
            f"latency={c.get('latency_sec'):.2f}s cached={c.get('cached')}"
        )
        md_lines.append("")
        for m in c.get("messages") or []:
            md_lines.append(f"### INPUT role=`{m.get('role')}`")
            md_lines.append("")
            md_lines.append("```")
            md_lines.append(str(m.get("content", "")))
            md_lines.append("```")
            md_lines.append("")
        md_lines.append("### OUTPUT")
        md_lines.append("")
        md_lines.append("```")
        md_lines.append(str(c.get("response_text", "")))
        md_lines.append("```")
        md_lines.append("")

    # baseline calls
    md_lines.append("# Baseline LLM calls")
    md_lines.append("")
    for c in (base.details or {}).get("llm_calls") or []:
        md_lines.append(f"## Call {c.get('call_index')}: `{c.get('call_tag')}`")
        md_lines.append("")
        for m in c.get("messages") or []:
            md_lines.append(f"### INPUT role=`{m.get('role')}`")
            md_lines.append("")
            md_lines.append("```")
            md_lines.append(str(m.get("content", "")))
            md_lines.append("```")
            md_lines.append("")
        md_lines.append("### OUTPUT")
        md_lines.append("")
        md_lines.append("```")
        md_lines.append(str(c.get("response_text", "")))
        md_lines.append("```")
        md_lines.append("")

    out_md = out_dir / "full_io.md"
    out_md.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"[done] wrote {out_json}", flush=True)
    print(f"[done] wrote {out_md}", flush=True)
    print(f"[done] architecture llm_calls={len(calls)} baseline_llm_calls={len((base.details or {}).get('llm_calls') or [])}", flush=True)


if __name__ == "__main__":
    main()
