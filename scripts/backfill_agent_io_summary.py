#!/usr/bin/env python3
"""Backfill agent_io_summary.md for runs that only have full_io.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_feasibility_batch import _write_agent_io_summary  # noqa: E402


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs_dir", type=Path, help="Directory containing per-sample run folders.")
    args = parser.parse_args()

    n = 0
    for run_dir in sorted(args.runs_dir.iterdir()):
        if not run_dir.is_dir():
            continue
        full_io = run_dir / "full_io.json"
        if not full_io.is_file():
            continue
        payload = json.loads(full_io.read_text(encoding="utf-8"))
        arch_data = payload.get("architecture") or {}
        if not arch_data:
            continue

        class _Arch:
            predicted_answer = arch_data.get("predicted_answer")
            success = arch_data.get("success")
            model_calls = arch_data.get("model_calls", 0)
            tool_calls = arch_data.get("tool_calls", 0)
            latency_sec = float(arch_data.get("latency_sec") or 0)
            details = arch_data.get("details") or {}

        sid = str(payload.get("sample_id") or run_dir.name)
        _write_agent_io_summary(run_dir / "agent_io_summary.md", sid, _Arch())
        n += 1
    print(f"[done] wrote {n} agent_io_summary.md files under {args.runs_dir}")


if __name__ == "__main__":
    main()
