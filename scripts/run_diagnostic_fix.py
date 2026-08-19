#!/usr/bin/env python3
"""Architecture-only diagnostic rerun for known failing Base samples.

Example:
  cd /root/autodl-tmp/time-series-agent
  python3 scripts/run_diagnostic_fix.py
  python3 scripts/run_diagnostic_fix.py --exp-name diagnostic_fix_validation --device cuda:0
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(SCRIPTS))
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("PYTHONUNBUFFERED", "1")

from ts_agent.core.llm import build_provider
from ts_agent.core.utils import ensure_dir, load_yaml
from ts_agent.data.mmts import MMTSBenchDataset
from ts_agent.pipelines.experiment import ExperimentPipeline
from run_feasibility_batch import run_one  # noqa: E402

DEFAULT_IDS_FILE = ROOT / "outputs" / "diagnostic_fix_validation" / "sample_ids.txt"


def _load_ids(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run architecture-only diagnostic fix validation.")
    parser.add_argument(
        "--exp-name",
        default="diagnostic_fix_validation",
        help="Output directory under outputs/<exp-name>/",
    )
    parser.add_argument("--device", default="cuda:0", help="Model device map, e.g. cuda:0")
    parser.add_argument(
        "--ids-file",
        type=Path,
        default=DEFAULT_IDS_FILE,
        help="Sample IDs to run (one per line)",
    )
    args = parser.parse_args()

    ids_file: Path = args.ids_file
    if not ids_file.is_file():
        raise SystemExit(f"missing ids file: {ids_file}")

    ids = _load_ids(ids_file)
    print(f"[info] loading {len(ids)} diagnostic samples from {ids_file}", flush=True)

    cfg = load_yaml(ROOT / "configs" / "experiment.yaml")
    cfg["experiment"]["use_mock_llm"] = False
    cfg["experiment"]["max_series_text_chars"] = None
    cfg["experiment"]["cache_dir"] = str(ROOT / "outputs" / args.exp_name / "llm_cache")
    cfg["model"]["device_map"] = args.device

    ds = MMTSBenchDataset(
        cfg["data"]["processed_dir"],
        raw_dir=cfg["data"]["raw_dir"],
        max_series_text_chars=None,
    )
    samples = ds.filter(sample_ids=ids)
    by_id = {s.sample_id: s for s in samples}
    ordered = [by_id[i] for i in ids if i in by_id]
    missing = [i for i in ids if i not in by_id]
    if missing:
        raise SystemExit(f"missing samples: {missing}")

    print("[info] building LLM provider...", flush=True)
    llm = build_provider(cfg)
    llm.record_io = True
    pipe = ExperimentPipeline(
        llm,
        cfg["experiment"]["prompt_dir"],
        max_tool_rounds=int(cfg["experiment"].get("max_tool_rounds", 3)),
    )

    out_root = ensure_dir(ROOT / "outputs" / args.exp_name / "runs")
    summary: list[dict] = []
    for sample in ordered:
        row = run_one(pipe, sample, out_root, run_baseline=False)
        summary.append(row)
        (out_root / "summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(
            f"[diag] {row['sample_id']} gold={row['gold']} pred={row['arch_pred']} "
            f"ok={row['arch_ok']} err={row['arch_error']}",
            flush=True,
        )

    n_ok = sum(1 for r in summary if r.get("arch_ok"))
    print(f"[done] diagnostic architecture accuracy {n_ok}/{len(summary)}", flush=True)


if __name__ == "__main__":
    main()
