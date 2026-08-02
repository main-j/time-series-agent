from __future__ import annotations

import argparse
import json
from pathlib import Path

from tqdm import tqdm

from ts_agent.core.llm import build_provider
from ts_agent.core.utils import ensure_dir, load_yaml
from ts_agent.data.mmts import MMTSBenchAdapter, MMTSBenchDataset
from ts_agent.evaluation.metrics import compare_summaries, save_traces, summarize_traces
from ts_agent.pipelines.experiment import ExperimentPipeline


def cmd_preprocess(cfg: dict, args: argparse.Namespace) -> None:
    adapter = MMTSBenchAdapter(cfg["data"]["raw_dir"], schema_version=cfg["data"]["schema_version"])
    out = adapter.build_processed(cfg["data"]["processed_dir"], subsets=args.subsets or cfg["experiment"]["subsets"])
    print(f"Processed dataset written to {out}")


def cmd_run(cfg: dict, args: argparse.Namespace) -> None:
    if getattr(args, "use_mock_llm", None) is not None:
        cfg.setdefault("experiment", {})["use_mock_llm"] = bool(args.use_mock_llm)
    if getattr(args, "max_series_text_chars", None) is not None:
        cfg.setdefault("experiment", {})["max_series_text_chars"] = args.max_series_text_chars
    llm = build_provider(cfg)
    pipe = ExperimentPipeline(
        llm=llm,
        prompt_dir=cfg["experiment"]["prompt_dir"],
        max_tool_rounds=cfg["experiment"].get("max_tool_rounds", 3),
    )
    ds = MMTSBenchDataset(
        cfg["data"]["processed_dir"],
        raw_dir=cfg["data"]["raw_dir"],
        max_series_text_chars=cfg["experiment"].get("max_series_text_chars", 8000),
    )
    samples = ds.filter(
        subsets=args.subsets or cfg["experiment"]["subsets"],
        limit=args.limit if args.limit is not None else cfg["experiment"].get("dev_limit"),
        stratified=args.stratified,
    )
    print(
        f"Running mode={args.mode} samples={len(samples)} "
        f"use_mock_llm={cfg['experiment'].get('use_mock_llm')} exp_name={args.exp_name}"
    )
    out_dir = ensure_dir(Path(cfg["experiment"]["output_dir"]) / args.exp_name)
    modes = ["baseline", "architecture"] if args.mode == "both" else [args.mode]
    summaries = {}
    for mode in modes:
        traces = []
        n_ok = 0
        pbar = tqdm(
            samples,
            total=len(samples),
            desc=f"{mode}",
            unit="sample",
            dynamic_ncols=True,
            mininterval=0.5,
        )
        for sample in pbar:
            if mode == "baseline":
                trace = pipe.run_baseline(sample)
            else:
                trace = pipe.run_architecture(sample)
            traces.append(trace)
            if trace.success:
                n_ok += 1
            done = len(traces)
            pbar.set_postfix(
                ok=f"{n_ok}/{done}",
                tools=trace.tool_calls,
                sid=sample.sample_id[:28],
                refresh=False,
            )
            # Checkpoint every 20 samples so full runs survive interruptions.
            if done % 20 == 0 or done == len(samples):
                save_traces(traces, out_dir / f"{mode}_traces.jsonl")
        pbar.close()
        trace_path = out_dir / f"{mode}_traces.jsonl"
        save_traces(traces, trace_path)
        summary = summarize_traces(traces)
        summaries[mode] = summary
        (out_dir / f"{mode}_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(json.dumps({mode: summary}, indent=2))
    if "baseline" in summaries and "architecture" in summaries:
        cmp = compare_summaries(summaries["baseline"], summaries["architecture"])
        (out_dir / "comparison.json").write_text(json.dumps(cmp, indent=2), encoding="utf-8")
        report = _render_report(cmp, cfg, args)
        (out_dir / "report.md").write_text(report, encoding="utf-8")
        print(report)
    # write run manifest
    manifest = {
        "exp_name": args.exp_name,
        "mode": args.mode,
        "n_samples": len(samples),
        "sample_ids": [s.sample_id for s in samples],
        "use_mock_llm": cfg["experiment"].get("use_mock_llm"),
        "max_series_text_chars": cfg["experiment"].get("max_series_text_chars"),
        "subsets": args.subsets or cfg["experiment"]["subsets"],
        "stratified": bool(args.stratified),
        "limit": args.limit,
        "prompt_dir": cfg["experiment"]["prompt_dir"],
        "model_path": cfg["model"]["local_path"],
    }
    (out_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Artifacts written to {out_dir}")


def _render_report(cmp: dict, cfg: dict, args: argparse.Namespace) -> str:
    b = cmp["baseline"]
    a = cmp["architecture"]
    provider = "mock" if cfg["experiment"].get("use_mock_llm") in (True, "auto") else "local_hf"
    return f"""# Qwen2.5-14B Prompt-only Architecture Comparison Report

## Setup
- Model path: `{cfg['model']['local_path']}`
- Data: MMTS-Bench processed at `{cfg['data']['processed_dir']}`
- Modes: baseline vs architecture
- Limit: {args.limit}
- Provider mode config: `{cfg['experiment'].get('use_mock_llm')}` (effective depends on GPU)

## Results
| Metric | Baseline | Architecture | Delta |
|---|---:|---:|---:|
| Choice Accuracy | {b.get('choice_accuracy')} | {a.get('choice_accuracy')} | {cmp.get('choice_accuracy_delta')} |
| Valid Output Rate | {b.get('valid_output_rate')} | {a.get('valid_output_rate')} | {cmp.get('valid_output_rate_delta')} |
| Avg Latency (s) | {b.get('avg_latency_sec'):.4f} | {a.get('avg_latency_sec'):.4f} | {cmp.get('avg_latency_sec_delta')} |
| Avg Model Calls | {b.get('avg_model_calls'):.2f} | {a.get('avg_model_calls'):.2f} | {cmp.get('avg_model_calls_delta')} |
| Avg Tool Calls | {b.get('avg_tool_calls'):.2f} | {a.get('avg_tool_calls'):.2f} | {cmp.get('avg_tool_calls_delta')} |

### Subset Choice Accuracy
- Baseline: {json.dumps(b.get('subset_choice_accuracy'), ensure_ascii=False)}
- Architecture: {json.dumps(a.get('subset_choice_accuracy'), ensure_ascii=False)}

## Interpretation
- This stage compares the full hierarchical Prompt+Tools architecture against a single-shot baseline.
- Module-level attribution requires future ablations (explicitly out of scope for this stage).
- If provider is mock (no GPU), metrics validate pipeline correctness only, not model quality.
"""


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="TS hierarchical agent experiments")
    p.add_argument("--config", default="/root/autodl-tmp/time-series-agent/configs/experiment.yaml")
    sub = p.add_subparsers(dest="command", required=True)

    pre = sub.add_parser("preprocess")
    pre.add_argument("--subsets", nargs="*")

    run = sub.add_parser("run")
    run.add_argument("--mode", choices=["baseline", "architecture", "both"], default="both")
    run.add_argument("--limit", type=int, default=None)
    run.add_argument("--subsets", nargs="*")
    run.add_argument("--exp-name", default="default")
    run.add_argument("--stratified", action="store_true", help="Sample evenly across subsets when --limit is set")
    run.add_argument(
        "--use-mock-llm",
        dest="use_mock_llm",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Override config experiment.use_mock_llm (e.g. --use-mock-llm / --no-use-mock-llm)",
    )
    run.add_argument(
        "--max-series-text-chars",
        type=int,
        default=None,
        help="Override series text truncation; use 0 for no truncation",
    )
    return p


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    cfg = load_yaml(Path(args.config))
    if args.command == "preprocess":
        cmd_preprocess(cfg, args)
    elif args.command == "run":
        # 0 means disable truncation
        if getattr(args, "max_series_text_chars", None) == 0:
            args.max_series_text_chars = None
            cfg.setdefault("experiment", {})["max_series_text_chars"] = None
        cmd_run(cfg, args)
    else:
        raise SystemExit(f"Unknown command {args.command}")


if __name__ == "__main__":
    main()
