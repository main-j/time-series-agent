#!/usr/bin/env python3
"""Audit MMTS-Bench sample capabilities against agent role tool whitelists."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ts_agent.core.utils import load_yaml
from ts_agent.tools.coverage import audit_mmts_dataset


def main() -> None:
    cfg = load_yaml(ROOT / "configs" / "experiment.yaml")
    report = audit_mmts_dataset(cfg["data"]["processed_dir"], cfg["data"]["raw_dir"])
    out = ROOT / "outputs" / "mmts_tool_coverage.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"samples={report['n_samples']} gaps={report['n_gaps']} samples_with_gaps={report['n_samples_with_gaps']}")
    print("role tool counts:", report["role_tool_counts"])
    if report["gaps"]:
        print("\nTop gap capabilities:")
        for cap, n in sorted(report["gap_by_capability"].items(), key=lambda x: -x[1])[:10]:
            print(f"  {cap}: {n}")
        print(f"\nReport written to {out}")
        raise SystemExit(1)
    print(f"OK — full MMTS coverage. Report: {out}")


if __name__ == "__main__":
    main()
