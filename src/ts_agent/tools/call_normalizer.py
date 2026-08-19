"""Normalize tool call arguments and build stable fingerprints."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Optional, Tuple

from ts_agent.tools.registry import _ARG_ALIASES, _normalize_arguments


def canonicalize_arguments(name: str, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Normalize aliases and drop nulls for stable fingerprinting."""
    del name  # reserved for future tool-specific rules
    args = _normalize_arguments(arguments)
    # Drop alias source keys once the canonical destination exists.
    for src, dst in _ARG_ALIASES.items():
        if src in args and dst in args:
            args.pop(src, None)
    # Drop None values so omitted vs explicit-null do not diverge.
    clean = {k: v for k, v in args.items() if v is not None}
    # Stable key order.
    return {k: clean[k] for k in sorted(clean.keys(), key=str)}


def fingerprint(name: str, arguments: Optional[Dict[str, Any]]) -> str:
    payload = {"name": name, "arguments": canonicalize_arguments(name, arguments)}
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def evidence_source_id(name: str, arguments: Optional[Dict[str, Any]]) -> str:
    args = canonicalize_arguments(name, arguments)
    series = args.get("series_index", "all")
    start = args.get("start", "None")
    end = args.get("end", "None")
    # Keep human-readable ids for debugging; fingerprint remains the cache key.
    return f"{name}:{series}:{start}:{end}"


def call_identity(name: str, arguments: Optional[Dict[str, Any]]) -> Tuple[str, str, Dict[str, Any]]:
    canon = canonicalize_arguments(name, arguments)
    return fingerprint(name, canon), evidence_source_id(name, canon), canon
