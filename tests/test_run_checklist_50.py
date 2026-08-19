"""Tests for proportional downsampling of the weighted checklist."""
from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_checklist_50.py"
SPEC = importlib.util.spec_from_file_location("run_checklist_50", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_largest_remainder_allocation_is_exact_and_proportional():
    quotas = MODULE._allocate_proportionally({"large": 20, "medium": 14, "small": 6}, 10)
    assert quotas == {"large": 5, "medium": 4, "small": 1}
    assert sum(quotas.values()) == 10


def test_select_50_from_weighted_manifest_is_unique_and_reproducible():
    manifest = MODULE.json.loads(
        (ROOT / "outputs" / "weighted_mmts_selection_200" / "manifest.json").read_text(
            encoding="utf-8"
        )
    )
    first, quotas = MODULE.select_subset(manifest["samples"], count=50, seed=20260803)
    second, _ = MODULE.select_subset(manifest["samples"], count=50, seed=20260803)

    first_ids = [row["sample_id"] for row in first]
    assert first_ids == [row["sample_id"] for row in second]
    assert len(first_ids) == len(set(first_ids)) == 50
    assert sum(quotas.values()) == 50
    assert set(quotas) == {row["assigned_task"] for row in manifest["samples"]}
