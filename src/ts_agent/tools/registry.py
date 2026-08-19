from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
from pydantic import BaseModel, Field


class ToolSpec(BaseModel):
    name: str
    description: str
    roles: List[str] = Field(default_factory=list)
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    use_when: List[str] = Field(default_factory=list)
    avoid_when: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    produces: List[str] = Field(default_factory=list)
    consumes: List[str] = Field(default_factory=list)
    often_combined_with: List[str] = Field(default_factory=list)
    io_concepts: Dict[str, Any] = Field(default_factory=dict)


@dataclass
class ToolResult:
    name: str
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None


ToolFn = Callable[[Dict[str, Any], List[List[float]]], ToolResult]

_VARIANCE_EPS = 1e-12

_ARG_ALIASES = {
    "window_size": "window",
    "start_index": "start",
    "end_index": "end",
    "begin": "start",
    "begin_index": "start",
    "stop": "end",
    "stop_index": "end",
    "series_id": "series_index",
    "series_idx": "series_index",
    "ts_index": "series_index",
}


def _contains_nonfinite(obj: Any) -> bool:
    if isinstance(obj, dict):
        return any(_contains_nonfinite(v) for v in obj.values())
    if isinstance(obj, (list, tuple)):
        return any(_contains_nonfinite(v) for v in obj)
    if isinstance(obj, (float, np.floating)):
        return not np.isfinite(obj)
    if isinstance(obj, (int, np.integer, bool, type(None), str)):
        return False
    return False


def _validate_series(series: List[List[float]]) -> Optional[str]:
    if not series:
        return "Empty series"
    for i, s in enumerate(series):
        arr = np.asarray(s, dtype=float)
        if arr.size == 0:
            return f"Empty series at index {i + 1}"
        if not np.isfinite(arr).all():
            return f"Non-finite values (NaN/Inf) in series at index {i + 1}"
    return None


def _safe_corr(a: np.ndarray, b: np.ndarray) -> Tuple[Optional[float], Optional[str]]:
    if a.size < 2 or b.size < 2 or a.size != b.size:
        return None, "insufficient points for correlation"
    if float(np.std(a)) < _VARIANCE_EPS or float(np.std(b)) < _VARIANCE_EPS:
        return None, "zero-variance series; correlation undefined"
    c = float(np.corrcoef(a, b)[0, 1])
    if not np.isfinite(c):
        return None, "correlation produced non-finite value"
    return c, None


def _finalize(name: str, result: ToolResult) -> ToolResult:
    if result.success and _contains_nonfinite(result.data):
        return ToolResult(
            name=name,
            success=False,
            data={},
            error="Tool produced non-finite output; rejecting result",
        )
    return result


def _normalize_arguments(arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    out: Dict[str, Any] = dict(arguments or {})
    for src, dst in _ARG_ALIASES.items():
        if src in out and dst not in out:
            out[dst] = out[src]
    return out


def _looks_like_raw_series_values(value: Any, n_series: int, series: List[List[float]]) -> bool:
    """Detect LLM pasting full float arrays into arguments.series."""
    if not isinstance(value, (list, tuple)) or not value:
        return False
    if all(isinstance(x, str) for x in value):
        return False
    # Valid series_index lists are short ints in 1..n
    if all(isinstance(x, (int, np.integer)) or (isinstance(x, float) and float(x).is_integer()) for x in value):
        ints = [int(x) for x in value]
        if len(ints) <= n_series and all(1 <= i <= n_series for i in ints):
            return False
    # Long numeric list ≈ series length → raw values
    if not all(isinstance(x, (int, float, np.integer, np.floating)) for x in value):
        return False
    lengths = {len(s) for s in series}
    return len(value) >= 4 and (len(value) in lengths or len(value) > n_series)


def _parse_one_series_token(token: Any, n: int) -> int:
    """Parse one 1-based series selector into 0-based index."""
    if isinstance(token, (int, np.integer)):
        idx = int(token) - 1
    elif isinstance(token, float) and float(token).is_integer():
        idx = int(token) - 1
    elif isinstance(token, str):
        s = token.strip().lower().replace("_", " ")
        if s in {"all", "*", "every", "each"}:
            raise ValueError("all")
        m = re.fullmatch(r"(?:time\s*series|series|ts)\s*(\d+)", s)
        if m:
            idx = int(m.group(1)) - 1
        elif re.fullmatch(r"\d+", s):
            idx = int(s) - 1
        else:
            raise ValueError(f"Unrecognized series selector: {token!r}")
    else:
        raise ValueError(f"Unrecognized series selector type: {type(token).__name__}")
    if not (0 <= idx < n):
        raise ValueError(f"series_index out of range: {token!r} (valid 1..{n})")
    return idx


def _resolve_series_indices(
    arguments: Dict[str, Any],
    series: List[List[float]],
    *,
    default_all_when_multi: bool = True,
) -> List[int]:
    """
    Resolve which series to analyze (0-based).

    Accepts series_index / series as:
      - missing -> all series if n>1 and default_all_when_multi, else [0]
      - "all" / "*"
      - int / "2" / "Time Series 2" / "ts2"
      - [1, 2, 3]
    Rejects raw float arrays pasted as series values.
    """
    n = len(series)
    raw = arguments.get("series_index", arguments.get("series"))
    if raw is None:
        if n > 1 and default_all_when_multi:
            return list(range(n))
        return [0]

    if _looks_like_raw_series_values(raw, n, series):
        raise ValueError(
            "Do not pass raw series values in arguments; "
            "use series_index=1..N (1-based), a list of indices, or series_index='all'."
        )

    if isinstance(raw, str) and raw.strip().lower() in {"all", "*", "every", "each"}:
        return list(range(n))

    if isinstance(raw, (list, tuple)):
        if not raw:
            raise ValueError("empty series_index list")
        if all(isinstance(x, str) for x in raw):
            return [_parse_one_series_token(x, n) for x in raw]
        # numeric index list
        return [_parse_one_series_token(x, n) for x in raw]

    try:
        return [_parse_one_series_token(raw, n)]
    except ValueError as e:
        if str(e) == "all":
            return list(range(n))
        raise


def _selected_arrays(
    arguments: Dict[str, Any],
    series: List[List[float]],
    *,
    default_all_when_multi: bool = True,
) -> List[Tuple[int, np.ndarray]]:
    idxs = _resolve_series_indices(arguments, series, default_all_when_multi=default_all_when_multi)
    out: List[Tuple[int, np.ndarray]] = []
    for i in idxs:
        arr = np.asarray(series[i], dtype=float)
        if arr.size == 0:
            raise ValueError(f"Empty series at index {i + 1}")
        out.append((i + 1, arr))  # 1-based label
    return out


def _pack_per_series(name: str, items: List[Dict[str, Any]]) -> ToolResult:
    if len(items) == 1:
        return ToolResult(name=name, success=True, data=items[0])
    return ToolResult(name=name, success=True, data={"series": items, "n_series": len(items)})


def _slice_window(arr: np.ndarray, arguments: Dict[str, Any]) -> Tuple[np.ndarray, Optional[int], Optional[int]]:
    """Optional start/end (inclusive end if end provided) slice."""
    start = arguments.get("start")
    end = arguments.get("end")
    if start is None and end is None:
        return arr, None, None
    n = len(arr)
    s = int(start) if start is not None else 0
    e = int(end) if end is not None else n - 1
    s = max(0, min(s, n - 1))
    e = max(0, min(e, n - 1))
    if e < s:
        s, e = e, s
    return arr[s : e + 1], s, e


class ToolRegistry:
    def __init__(self):
        self._specs: Dict[str, ToolSpec] = {}
        self._fns: Dict[str, ToolFn] = {}

    def register(self, spec: ToolSpec, fn: ToolFn) -> None:
        required = {
            "description": spec.description,
            "input_schema": spec.input_schema,
            "output_schema": spec.output_schema,
            "use_when": spec.use_when,
            "avoid_when": spec.avoid_when,
            "limitations": spec.limitations,
        }
        missing = [field for field, value in required.items() if not value]
        if missing:
            raise ValueError(f"incomplete ToolSpec contract for {spec.name}: {', '.join(missing)}")
        if spec.name in self._specs:
            raise ValueError(f"duplicate tool registration: {spec.name}")
        self._specs[spec.name] = spec
        self._fns[spec.name] = fn

    def list_for_roles(self, roles: List[str]) -> List[ToolSpec]:
        role_set = set(roles)
        return [s for s in self._specs.values() if role_set.intersection(s.roles) or not s.roles]

    def get_spec(self, name: str) -> ToolSpec:
        return self._specs[name]

    def run(self, name: str, arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
        if name not in self._fns:
            return ToolResult(name=name, success=False, data={}, error=f"Unknown tool: {name}")
        err = _validate_series(series)
        if err:
            return ToolResult(name=name, success=False, data={}, error=err)
        try:
            args = _normalize_arguments(arguments)
            return _finalize(name, self._fns[name](args, series))
        except Exception as e:  # noqa: BLE001
            return ToolResult(name=name, success=False, data={}, error=str(e))

    def _filter_specs(self, roles: List[str], tools: Optional[List[str]] = None) -> List[ToolSpec]:
        specs = self.list_for_roles(roles)
        if tools is None:
            return specs
        wanted = {str(t).strip() for t in tools if str(t).strip()}
        return [s for s in specs if s.name in wanted]

    def capabilities_text(self, roles: List[str], tools: Optional[List[str]] = None) -> str:
        """S1S2: function/capability semantics only — no args/schema."""
        lines = [
            "Tool capability library (for selection only; do NOT invent argument formats here):",
            "",
        ]
        for spec in self._filter_specs(roles, tools):
            lines.append(f"- {spec.name}: {spec.description}")
            if spec.produces:
                lines.append(f"  produces: {', '.join(spec.produces)}")
            elif spec.output_schema:
                keys = ", ".join(spec.output_schema.keys())
                lines.append(f"  produces: {keys}")
            if spec.use_when:
                lines.append(f"  use_when: {'; '.join(spec.use_when)}")
            if spec.avoid_when:
                lines.append(f"  avoid_when: {'; '.join(spec.avoid_when)}")
            if spec.limitations:
                lines.append(f"  limitations: {'; '.join(spec.limitations)}")
            if spec.often_combined_with:
                lines.append(f"  often_combined_with: {', '.join(spec.often_combined_with)}")
        return "\n".join(lines)

    def io_concepts_text(self, roles: List[str], tools: Optional[List[str]] = None) -> str:
        """S3: input/output concepts and dependency hints — not full schema."""
        lines = [
            "Tool IO concepts (for workflow planning; not full argument schemas):",
            "",
        ]
        for spec in self._filter_specs(roles, tools):
            lines.append(f"- {spec.name}")
            io = spec.io_concepts or {}
            inputs = io.get("inputs")
            outputs = io.get("outputs")
            depends = io.get("depends")
            if inputs is None and spec.consumes:
                inputs = ", ".join(spec.consumes)
            if outputs is None and spec.produces:
                outputs = ", ".join(spec.produces)
            if inputs is None and spec.input_schema:
                inputs = ", ".join(f"{k}" for k in spec.input_schema.keys())
            if outputs is None and spec.output_schema:
                outputs = ", ".join(f"{k}" for k in spec.output_schema.keys())
            if inputs:
                lines.append(f"  inputs: {inputs}")
            if outputs:
                lines.append(f"  outputs: {outputs}")
            if depends:
                lines.append(f"  depends: {depends}")
            elif spec.often_combined_with:
                lines.append(f"  often_combined_with: {', '.join(spec.often_combined_with)}")
        return "\n".join(lines)

    def invocation_text(self, roles: List[str], tools: Optional[List[str]] = None) -> str:
        """S4: full invocation protocol and argument schemas."""
        lines = [
            "Runtime tool invocation protocol:",
            "- Tools read pipeline-bound series; NEVER paste raw numeric arrays into arguments.",
            "- Optional parameters: omit the key; never JSON null.",
            "- Multi-round / workflow: pass numeric literals OR $stepN.field references resolved by Runtime.",
            "- Placeholders/strings naming other tools are not valid argument values.",
            "- Use series_index (1-based): int, list like [1,2,3], 'Time Series 2', or 'all'.",
            "- If n_series>1 and series_index is omitted, tools fan out over ALL series.",
            "- lag_corr is pairwise: use series_index_1/2 as ints, or set either to 'all' for all pairs.",
            "- Optional window args: start/end (inclusive indices), window (alias window_size).",
            "",
        ]
        for spec in self._filter_specs(roles, tools):
            lines.append(f"- {spec.name}: {spec.description}")
            if spec.input_schema:
                keys = ", ".join(f"{k}={v}" for k, v in spec.input_schema.items())
                lines.append(f"  args: {{{keys}}}")
            if spec.output_schema:
                keys = ", ".join(f"{k}={v}" for k, v in spec.output_schema.items())
                lines.append(f"  returns: {{{keys}}}")
        return "\n".join(lines)

    def catalog_text(self, roles: List[str]) -> str:
        """Deprecated aggregate catalog (capabilities + invocation). Prefer split methods."""
        lines = [
            "Runtime tool protocol:",
            "- Tools read pipeline-bound series; NEVER paste raw numeric arrays into arguments.",
            "- Select tools by reading each tool's purpose, returns, use_when, avoid_when,",
            "  and limitations. Do not select by keyword alone.",
            "- Use series_index (1-based): int, list like [1,2,3], 'Time Series 2', or 'all'.",
            "- If n_series>1 and series_index is omitted, tools fan out over ALL series.",
            "- lag_corr is pairwise: use series_index_1/2 as ints, or set either to 'all' for all pairs.",
            "- Optional window args: start/end (inclusive indices), window (alias window_size).",
            "",
        ]
        for spec in self.list_for_roles(roles):
            lines.append(f"- {spec.name}: {spec.description}")
            if spec.input_schema:
                keys = ", ".join(f"{k}={v}" for k, v in spec.input_schema.items())
                lines.append(f"  args: {{{keys}}}")
            if spec.output_schema:
                keys = ", ".join(f"{k}={v}" for k, v in spec.output_schema.items())
                lines.append(f"  returns: {{{keys}}}")
            if spec.use_when:
                lines.append(f"  use_when: {'; '.join(spec.use_when)}")
            if spec.avoid_when:
                lines.append(f"  avoid_when: {'; '.join(spec.avoid_when)}")
            if spec.limitations:
                lines.append(f"  limitations: {'; '.join(spec.limitations)}")
            if spec.produces:
                lines.append(f"  produces: {', '.join(spec.produces)}")
            if spec.often_combined_with:
                lines.append(f"  often_combined_with: {', '.join(spec.often_combined_with)}")
        return "\n".join(lines)


def _level_tolerance(arr: np.ndarray) -> float:
    """Adaptive plateau tolerance for drifted synthetic steps/square waves."""
    std = float(np.std(arr))
    span = float(np.max(arr) - np.min(arr)) if arr.size else 0.0
    mad = float(np.median(np.abs(arr - np.median(arr)))) if arr.size else 0.0
    return max(_VARIANCE_EPS, std * 0.02, span * 0.01, mad * 0.05, 1e-3)


def _step_level_stats(arr: np.ndarray) -> Dict[str, Any]:
    if arr.size == 0:
        return {"n_unique_levels": 0, "n_plateau_runs": 0, "levels": [], "plateau_runs": []}
    tol = _level_tolerance(arr)
    plateau_runs: List[float] = []
    plateau_lens: List[int] = []
    for v in arr:
        fv = float(v)
        if not plateau_runs or abs(fv - plateau_runs[-1]) > tol:
            plateau_runs.append(fv)
            plateau_lens.append(1)
        else:
            n = plateau_lens[-1]
            plateau_runs[-1] = (plateau_runs[-1] * n + fv) / (n + 1)
            plateau_lens[-1] = n + 1
    uniq: List[float] = []
    for lv in plateau_runs:
        if not any(abs(lv - u) <= tol for u in uniq):
            uniq.append(lv)
    return {
        "n_unique_levels": len(uniq),
        "n_plateau_runs": len(plateau_runs),
        "levels": uniq[:40],
        "plateau_runs": plateau_runs[:80],
        "plateau_lengths": plateau_lens[:80],
        "tolerance": tol,
    }


def _describe(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    # Always describe all series (ignore selection); keeps multi-series entry point.
    out = []
    for i, s in enumerate(series):
        arr = np.asarray(s, dtype=float)
        out.append(
            {
                "series_index": i + 1,
                "index": i + 1,
                "length": int(arr.size),
                "mean": float(np.mean(arr)),
                "std": float(np.std(arr)),
                "min": float(np.min(arr)),
                "max": float(np.max(arr)),
                "median": float(np.median(arr)),
                "range": float(np.max(arr) - np.min(arr)),
                "p50": float(np.percentile(arr, 50)),
                "p90": float(np.percentile(arr, 90)),
                "p99": float(np.percentile(arr, 99)),
                "start": float(arr[0]),
                "end": float(arr[-1]),
                "slope": float((arr[-1] - arr[0]) / max(len(arr) - 1, 1)),
            }
        )
    return ToolResult(name="describe_series", success=True, data={"series": out})


def _count_peaks_troughs(sub: np.ndarray) -> Tuple[List[int], List[int]]:
    """Count local peaks/troughs; prominence filter aligns with MMTS Base index tasks."""
    if len(sub) < 3:
        return [], []
    std = float(np.std(sub))
    if std < _VARIANCE_EPS:
        return [], []
    try:
        from scipy.signal import find_peaks

        prom = max(0.05 * std, _VARIANCE_EPS)
        peak_idx, _ = find_peaks(sub, prominence=prom)
        trough_idx, _ = find_peaks(-sub, prominence=prom)
        return [int(i) for i in peak_idx], [int(i) for i in trough_idx]
    except Exception:
        peaks, troughs = [], []
        for i in range(1, len(sub) - 1):
            if sub[i] > sub[i - 1] and sub[i] > sub[i + 1]:
                peaks.append(i)
            if sub[i] < sub[i - 1] and sub[i] < sub[i + 1]:
                troughs.append(i)
        return peaks, troughs


def _segment_summary(sub: np.ndarray, offset: int = 0) -> Dict[str, Any]:
    """Aggregate stats for one segment (used by interval/cross-series compare)."""
    if sub.size == 0:
        return {
            "mean": 0.0,
            "std": 0.0,
            "min": 0.0,
            "max": 0.0,
            "min_index": offset,
            "max_index": offset,
            "n_peaks": 0,
            "n_troughs": 0,
            "slope": 0.0,
            "direction": "flat",
        }
    peaks, troughs = _count_peaks_troughs(sub)
    peaks = [offset + i for i in peaks]
    troughs = [offset + i for i in troughs]
    rel_max = int(np.argmax(sub))
    rel_min = int(np.argmin(sub))
    slope = float((sub[-1] - sub[0]) / max(len(sub) - 1, 1))
    if slope > 1e-9:
        direction = "upward"
    elif slope < -1e-9:
        direction = "downward"
    else:
        direction = "flat"
    return {
        "mean": float(np.mean(sub)),
        "std": float(np.std(sub)),
        "min": float(np.min(sub)),
        "max": float(np.max(sub)),
        "min_index": offset + rel_min,
        "max_index": offset + rel_max,
        "n_peaks": len(peaks),
        "n_troughs": len(troughs),
        "peak_indices": peaks[:20],
        "trough_indices": troughs[:20],
        "slope": slope,
        "direction": direction,
    }


def _sliding_stats(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    items = []
    for sid, arr in _selected_arrays(arguments, series):
        window = int(arguments.get("window", max(5, len(arr) // 20)))
        window = max(2, min(window, len(arr)))
        means, stds = [], []
        for i in range(0, len(arr) - window + 1):
            seg = arr[i : i + window]
            means.append(float(np.mean(seg)))
            stds.append(float(np.std(seg)))
        items.append(
            {
                "series_index": sid,
                "window": window,
                "mean_of_means": float(np.mean(means)),
                "mean_of_stds": float(np.mean(stds)),
                "max_local_std": float(np.max(stds)),
            }
        )
    return _pack_per_series("sliding_stats", items)


def _diff_stats(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    items = []
    for sid, arr in _selected_arrays(arguments, series):
        sub, s, e = _slice_window(arr, arguments)
        d = np.diff(sub)
        items.append(
            {
                "series_index": sid,
                "start": s,
                "end": e,
                "mean_diff": float(np.mean(d)) if len(d) else 0.0,
                "std_diff": float(np.std(d)) if len(d) else 0.0,
                "max_abs_diff": float(np.max(np.abs(d))) if len(d) else 0.0,
                "n_sign_changes": int(np.sum(d[1:] * d[:-1] < 0)) if len(d) > 1 else 0,
            }
        )
    return _pack_per_series("diff_stats", items)


def _local_extrema(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    items = []
    for sid, arr in _selected_arrays(arguments, series):
        sub, s, e = _slice_window(arr, arguments)
        offset = s or 0
        peaks, troughs = _count_peaks_troughs(sub)
        peaks = [offset + i for i in peaks]
        troughs = [offset + i for i in troughs]
        items.append(
            {
                "series_index": sid,
                "start": s,
                "end": e,
                "n_peaks": len(peaks),
                "n_troughs": len(troughs),
                "peak_idx": peaks[:20],
                "trough_idx": troughs[:20],
            }
        )
    return _pack_per_series("local_extrema", items)


def _step_levels(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    """Count discrete step/plateau levels in a window (NOT the same as local extrema)."""
    items = []
    for sid, arr in _selected_arrays(arguments, series):
        sub, s, e = _slice_window(arr, arguments)
        stats = _step_level_stats(sub)
        items.append(
            {
                "series_index": sid,
                "start": s,
                "end": e,
                **stats,
            }
        )
    return _pack_per_series("step_levels", items)


def _value_at_index(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    items = []
    for sid, arr in _selected_arrays(arguments, series):
        idx = arguments.get("index")
        if idx is None:
            raise ValueError("index is required (0-based unless index_base=1)")
        index_base = int(arguments.get("index_base", 0))
        pos = int(idx) - index_base if index_base == 1 else int(idx)
        if not (0 <= pos < len(arr)):
            raise ValueError(f"index {idx!r} out of range for series {sid} (length={len(arr)})")
        items.append(
            {
                "series_index": sid,
                "index": int(idx),
                "position": pos,
                "value": float(arr[pos]),
            }
        )
    return _pack_per_series("value_at_index", items)


def _estimate_stl_period(sub: np.ndarray, requested: int = 0) -> Tuple[int, List[str]]:
    """Choose an STL period that avoids half-/full-length overfitting."""
    warnings: List[str] = []
    n = len(sub)
    max_period = max(2, min(n // 4, 64 if n < 256 else n // 6))
    if requested > 1:
        period = max(2, min(int(requested), max_period))
        if int(requested) > max_period:
            warnings.append(f"requested_period={requested} capped to {period} to avoid STL overfitting")
        return period, warnings
    if float(np.std(sub)) < _VARIANCE_EPS:
        return max(2, min(max_period, max(2, n // 8))), warnings
    centered = sub - np.mean(sub)
    spec = np.abs(np.fft.rfft(centered))
    freqs = np.fft.rfftfreq(n, d=1.0)
    candidates: List[int] = []
    if len(spec) > 1:
        order = np.argsort(spec[1:])[::-1] + 1
        for idx in order[:5]:
            if freqs[idx] <= 0:
                continue
            p = int(round(1.0 / float(freqs[idx])))
            if 2 <= p <= max_period and p not in candidates:
                candidates.append(p)
    if not candidates:
        candidates = [max(2, min(max_period, max(2, n // 8)))]
    best_period = candidates[0]
    best_score = -1.0
    try:
        from statsmodels.tsa.seasonal import STL

        series_var = float(np.var(sub)) + 1e-12
        for p in candidates:
            try:
                resid = np.asarray(STL(sub, period=p, robust=True).fit().resid)
                score = float(np.var(resid) / series_var)
                score -= 0.05 * (p / max_period)
                if score > best_score:
                    best_score = score
                    best_period = p
            except Exception:  # noqa: BLE001
                continue
    except Exception:  # noqa: BLE001
        best_period = candidates[0]
    if best_period >= max(16, n // 5):
        warnings.append(
            f"auto_period={best_period} is large relative to length={n}; estimates may be unstable"
        )
    return int(best_period), warnings


def _noise_level_from_variance_ratio(ratio: float) -> str:
    """MMTS Base thresholds on Var(noise)/Var(series)."""
    if ratio < 0.1:
        return "none"
    if ratio < 0.33:
        return "low"
    if ratio <= 0.66:
        return "medium"
    return "high"


def _season_strength_bin(strength: float) -> str:
    """MMTS seasonality bins from question text (<0.2 / 0.2-0.5 / 0.5-0.8 / >0.8)."""
    if strength < 0.2:
        return "none"
    if strength < 0.5:
        return "weak"
    if strength <= 0.8:
        return "moderate"
    return "strong"


def _highpass_residual_var(sub: np.ndarray) -> float:
    if len(sub) < 8:
        return float(np.var(sub))
    kernel = max(3, min(len(sub) // 8, 16))
    if kernel % 2 == 0:
        kernel += 1
    pad = kernel // 2
    kernel_arr = np.ones(kernel, dtype=float) / kernel
    smooth = np.convolve(sub, kernel_arr, mode="same")
    # Edge-aware: shrink endpoints toward local mean.
    resid = sub - smooth
    return float(np.var(resid))


def _hurst_exponent(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    """Estimate Hurst with the same compute_Hc estimator used by MMTS label generation."""
    items = []
    for sid, arr in _selected_arrays(arguments, series):
        sub, s, e = _slice_window(arr, arguments)
        n = len(sub)
        if n < 20:
            items.append(
                {
                    "series_index": sid,
                    "start": s,
                    "end": e,
                    "hurst": None,
                    "estimator": "hurst.compute_Hc",
                    "metric_definition": "MMTS-compatible R/S Hurst via hurst.compute_Hc",
                    "n_effective": n,
                    "kind": "random_walk",
                    "note": "series too short for compute_Hc (need >= 20)",
                    "warnings": ["too_short_for_compute_Hc"],
                }
            )
            continue
        warnings: List[str] = []
        if abs(float(sub[-1] - sub[0]) / max(n - 1, 1)) > 0.05 * float(np.std(sub) + 1e-12):
            warnings.append("strong_endpoint_trend_may_bias_hurst")
        try:
            from hurst import compute_Hc

            hurst_val, _c, _data = compute_Hc(
                np.asarray(sub, dtype=float), kind="random_walk", simplified=True
            )
            hurst = float(hurst_val)
            estimator = "hurst.compute_Hc"
            kind = "random_walk"
        except Exception as ex:  # noqa: BLE001
            lags = list(range(2, min(n // 2, 50)))
            tau = []
            for lag in lags:
                diffs = sub[lag:] - sub[:-lag]
                scale = float(np.std(diffs))
                if scale < _VARIANCE_EPS:
                    scale = float(np.mean(np.abs(diffs)))
                tau.append(max(scale, _VARIANCE_EPS))
            if len(tau) < 2 or min(tau) <= 0:
                items.append(
                    {
                        "series_index": sid,
                        "start": s,
                        "end": e,
                        "hurst": None,
                        "estimator": "fallback_lag_diff_failed",
                        "metric_definition": "MMTS-compatible R/S Hurst via hurst.compute_Hc",
                        "n_effective": n,
                        "note": f"compute_Hc failed: {ex}",
                        "warnings": warnings + ["compute_Hc_failed"],
                    }
                )
                continue
            hurst = float(np.polyfit(np.log(lags), np.log(tau), 1)[0])
            estimator = "fallback_lag_diff"
            kind = "fallback"
            warnings.append(f"compute_Hc_failed_used_fallback:{ex}")
        persistence = (
            "persistent" if hurst > 0.55 else "anti_persistent" if hurst < 0.45 else "random_walk_like"
        )
        items.append(
            {
                "series_index": sid,
                "start": s,
                "end": e,
                "hurst": hurst,
                "persistence_hint": persistence,
                "estimator": estimator,
                "metric_definition": "MMTS-compatible R/S Hurst via hurst.compute_Hc",
                "n_effective": n,
                "kind": kind,
                "simplified": True,
                "warnings": warnings,
            }
        )
    return _pack_per_series("hurst_exponent", items)


def _noise_decomposition(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    items = []
    for sid, arr in _selected_arrays(arguments, series):
        sub, s, e = _slice_window(arr, arguments)
        if len(sub) < 4:
            return ToolResult(name="noise_decomposition", success=False, data={}, error=f"series {sid} too short")
        requested = int(arguments.get("period", 0) or 0)
        period, period_warnings = _estimate_stl_period(sub, requested)
        try:
            from statsmodels.tsa.seasonal import STL

            stl = STL(sub, period=period, robust=True)
            res = stl.fit()
            resid = np.asarray(res.resid)
            seasonal = np.asarray(res.seasonal)
            trend = np.asarray(res.trend)
            series_std = float(np.std(sub))
            resid_std = float(np.std(resid))
            residual_rmse = float(np.sqrt(np.mean(np.square(resid))))
            series_var = float(np.var(sub)) + 1e-12
            resid_var = float(np.var(resid))
            stl_ratio = float(max(0.0, min(1.0, resid_var / series_var)))
            # Conservative: also consider a high-pass residual so strong STL seasonals
            # cannot silently collapse noise toward "none".
            hp_var = _highpass_residual_var(sub)
            hp_ratio = float(max(0.0, min(1.0, hp_var / series_var)))
            noise_ratio = float(max(stl_ratio, hp_ratio))
            noise_level = _noise_level_from_variance_ratio(noise_ratio)
            seasonal_strength = float(max(0.0, 1.0 - np.var(resid) / (np.var(seasonal + resid) + 1e-12)))
            d = np.diff(sub)
            acf1 = float(np.corrcoef(sub[:-1], sub[1:])[0, 1]) if len(sub) > 2 else 0.0
            n_unique = len({round(float(x), 8) for x in sub})
            uniq_ratio = n_unique / max(len(sub), 1)
            if acf1 > 0.85 and float(np.std(d)) > 0:
                noise_type_hint = "random_walk_like"
            elif uniq_ratio < 0.15:
                noise_type_hint = "quantization_like"
            elif abs(float(np.mean(((sub - np.mean(sub)) / (series_std + 1e-12)) ** 3))) < 0.5:
                noise_type_hint = "gauss_like"
            else:
                noise_type_hint = "uniform_like"
            items.append(
                {
                    "series_index": sid,
                    "start": s,
                    "end": e,
                    "period": period,
                    "residual_std": resid_std,
                    "residual_rmse": residual_rmse,
                    "series_std": series_std,
                    "residual_var": resid_var,
                    "series_var": float(np.var(sub)),
                    "stl_noise_ratio": stl_ratio,
                    "highpass_noise_ratio": hp_ratio,
                    "noise_ratio": noise_ratio,
                    "noise_level": noise_level,
                    "metric_definition": (
                        "Var(residual)/Var(series) (conservative max of STL residual and high-pass); "
                        "thresholds none<0.1, low<0.33, medium<=0.66, else high"
                    ),
                    "estimator": "STL_residual_variance_ratio",
                    "seasonal_strength": seasonal_strength,
                    "trend_strength": float(max(0.0, 1.0 - np.var(resid) / (np.var(trend + resid) + 1e-12))),
                    "noise_type_hint": noise_type_hint,
                    "acf_lag1": acf1,
                    "warnings": period_warnings,
                }
            )
        except Exception as ex:  # noqa: BLE001
            return ToolResult(name="noise_decomposition", success=False, data={}, error=str(ex))
    return _pack_per_series("noise_decomposition", items)


def _zscore_1d(arr: np.ndarray) -> np.ndarray:
    std = float(np.std(arr))
    if std < _VARIANCE_EPS:
        return arr - float(np.mean(arr))
    return (arr - float(np.mean(arr))) / std


def _synth_waveform_templates(period: int) -> Dict[str, np.ndarray]:
    t = np.arange(period, dtype=float)
    phase = 2.0 * np.pi * t / period
    sine = np.sin(phase)
    square = np.where((t % period) < (period / 2.0), 1.0, -1.0)
    triangle = 2.0 * np.abs(2.0 * (t / period - np.floor(t / period + 0.5))) - 1.0
    sawtooth = 2.0 * (t / period) - 1.0
    return {
        "sine": _zscore_1d(sine),
        "square": _zscore_1d(square),
        "triangle": _zscore_1d(triangle),
        "sawtooth": _zscore_1d(sawtooth),
    }


def _best_template_corr(folded: np.ndarray, templates: Dict[str, np.ndarray]) -> Dict[str, Any]:
    x = _zscore_1d(folded)
    scores: Dict[str, float] = {}
    for name, tmpl in templates.items():
        if len(tmpl) != len(x):
            continue
        # Phase-insensitive: try circular shifts over a coarse grid.
        best = -1.0
        step = max(1, len(x) // 16)
        for shift in range(0, len(x), step):
            y = np.roll(tmpl, shift)
            corr = float(np.dot(x, y) / max(len(x), 1))
            if corr > best:
                best = corr
        scores[name] = best
    if not scores:
        return {"best": None, "margin": 0.0, "scores": {}}
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    best_name, best_score = ranked[0]
    second = ranked[1][1] if len(ranked) > 1 else -1.0
    return {
        "best": best_name,
        "best_corr": float(best_score),
        "margin": float(best_score - second),
        "scores": {k: float(v) for k, v in scores.items()},
    }


def _estimate_waveform_period(sub: np.ndarray) -> Tuple[Optional[int], bool, List[str], Dict[str, Any]]:
    """Prefer jump-spacing / ACF periods; mark near-length FFT peaks untrusted."""
    warnings: List[str] = []
    n = len(sub)
    jump_info: Dict[str, Any] = {
        "n_large_jumps": 0,
        "alternation_rate": None,
        "spacing_cv": None,
        "jump_to_intra_ratio": None,
        "median_spacing": None,
    }
    diffs = np.diff(sub)
    abs_diffs = np.abs(diffs)
    span = float(np.max(sub) - np.min(sub)) + 1e-12
    thr = max(0.15 * span, float(np.percentile(abs_diffs, 95)) if abs_diffs.size else 0.0)
    jump_idx = np.where(abs_diffs >= thr)[0]
    jump_info["n_large_jumps"] = int(len(jump_idx))
    if len(jump_idx) >= 2:
        signs = np.sign(diffs[jump_idx])
        flips = int(np.sum(signs[1:] * signs[:-1] < 0))
        jump_info["alternation_rate"] = float(flips / max(len(signs) - 1, 1))
        spacings = np.diff(jump_idx.astype(float))
        med_space = float(np.median(spacings))
        jump_info["median_spacing"] = med_space
        jump_info["spacing_cv"] = float(np.std(spacings) / (med_space + 1e-12))
        # Intra-plateau slope magnitude vs jump size.
        segs: List[float] = []
        prev = 0
        for j in list(jump_idx) + [n - 1]:
            seg = sub[prev : j + 1]
            if len(seg) >= 2:
                segs.append(abs(float(seg[-1] - seg[0])) / max(len(seg) - 1, 1))
            prev = int(j) + 1
        intra = float(np.median(segs)) if segs else 0.0
        jump_info["jump_to_intra_ratio"] = float(np.median(abs_diffs[jump_idx]) / (intra + 1e-12))

    period: Optional[int] = None
    trusted = False
    # 1) Regular alternating jumps → use 2 * median spacing as full period.
    if (
        jump_info["n_large_jumps"] >= 4
        and jump_info["median_spacing"]
        and (jump_info["spacing_cv"] or 1.0) < 0.35
    ):
        cand = int(round(2.0 * float(jump_info["median_spacing"])))
        if 4 <= cand <= n // 2:
            period = cand
            trusted = True
    # 2) FFT fallback with trust flags.
    if period is None and float(np.std(sub)) >= _VARIANCE_EPS:
        centered = sub - np.mean(sub)
        spec = np.abs(np.fft.rfft(centered))
        freqs = np.fft.rfftfreq(n, d=1.0)
        if len(spec) > 1:
            idx = int(np.argmax(spec[1:]) + 1)
            if freqs[idx] > 0:
                period = int(max(2, min(n // 2, round(1.0 / float(freqs[idx])))))
                if period >= 0.9 * n:
                    trusted = False
                    warnings.append("dominant_period_near_series_length")
                elif period >= 0.5 * n:
                    trusted = False
                    warnings.append("dominant_period_near_half_length")
                else:
                    trusted = True
    if period is None:
        warnings.append("no_dominant_period")
    return period, trusted, warnings, jump_info


def _waveform_features(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    """Discriminate sine/square/triangle/sawtooth beyond mere periodicity."""
    items = []
    for sid, arr in _selected_arrays(arguments, series):
        sub, s, e = _slice_window(arr, arguments)
        n = len(sub)
        if n < 8:
            items.append(
                {
                    "series_index": sid,
                    "start": s,
                    "end": e,
                    "waveform_hint": None,
                    "note": "too short for waveform features",
                }
            )
            continue
        diffs = np.diff(sub)
        abs_diffs = np.abs(diffs)
        span = float(np.max(sub) - np.min(sub)) + 1e-12
        jump_thr = max(0.2 * span, float(np.percentile(abs_diffs, 90)))
        large_jumps = int(np.sum(abs_diffs >= jump_thr))
        jump_ratio = float(large_jumps / max(len(abs_diffs), 1))
        max_abs_diff = float(np.max(abs_diffs)) if abs_diffs.size else 0.0
        max_jump_frac = float(max_abs_diff / span)
        step_stats = _step_level_stats(sub)
        hist, _edges = np.histogram(sub, bins=min(40, max(8, n // 20)))
        top2 = sorted(hist, reverse=True)[:2]
        bimodality = float(sum(top2) / max(hist.sum(), 1))
        period, period_trusted, period_warnings, jump_info = _estimate_waveform_period(sub)
        centered = sub - np.mean(sub)
        spec = np.abs(np.fft.rfft(centered))
        folded_slope_abs = None
        rise_fall_asymmetry = None
        template_match: Dict[str, Any] = {"best": None, "margin": 0.0, "scores": {}}
        if period and period >= 4 and n >= period:
            n_cycles = max(1, n // period)
            folded = sub[: n_cycles * period].reshape(n_cycles, period).mean(axis=0)
            fd = np.diff(folded)
            folded_slope_abs = float(np.mean(np.abs(fd)))
            pos = fd[fd > 0]
            neg = fd[fd < 0]
            if len(pos) and len(neg):
                rise_fall_asymmetry = float(
                    abs(np.mean(pos) + np.mean(neg)) / (np.mean(np.abs(fd)) + 1e-12)
                )
            if period_trusted:
                template_match = _best_template_corr(folded, _synth_waveform_templates(period))
        harmonic = {
            "fundamental_share": 0.0,
            "odd_even_ratio": None,
            "high_harmonic_share": 0.0,
        }
        if len(spec) > 2:
            power = spec ** 2
            total = float(np.sum(power[1:]) + 1e-12)
            fund_idx = int(np.argmax(power[1:]) + 1)
            harmonic["fundamental_share"] = float(power[fund_idx] / total)
            odd = even = 0.0
            for k in range(1, 8):
                j = fund_idx * k
                if j >= len(power):
                    break
                if k % 2 == 1:
                    odd += float(power[j])
                else:
                    even += float(power[j])
            if even > 0:
                harmonic["odd_even_ratio"] = float(odd / (even + 1e-12))
            harmonic["high_harmonic_share"] = float(np.sum(power[fund_idx + 1 :]) / total)

        n_levels = int(step_stats["n_unique_levels"])
        alt = jump_info.get("alternation_rate")
        j2i = jump_info.get("jump_to_intra_ratio")
        square_regime = (
            int(jump_info.get("n_large_jumps") or 0) >= 4
            and alt is not None
            and alt >= 0.7
            and j2i is not None
            and j2i >= 20.0
            and (jump_info.get("spacing_cv") is None or float(jump_info["spacing_cv"]) < 0.4)
        )
        plateauish = n_levels <= max(6, int(0.08 * n)) and (
            jump_ratio >= 0.008 or max_jump_frac >= 0.5
        )
        triangleish = (
            jump_ratio < 0.05
            and max_jump_frac < 0.35
            and harmonic["fundamental_share"] < 0.85
            and (harmonic["odd_even_ratio"] or 0) > 2.0
            and rise_fall_asymmetry is not None
            and rise_fall_asymmetry < 0.35
            and not square_regime
        )
        sawish = (
            rise_fall_asymmetry is not None
            and rise_fall_asymmetry > 0.45
            and harmonic["high_harmonic_share"] > 0.25
            and max_jump_frac < 0.5
            and not square_regime
            and (alt is None or alt < 0.5)
        )
        sineish = (
            harmonic["fundamental_share"] >= 0.55
            and jump_ratio < 0.008
            and max_jump_frac < 0.35
            and n_levels > 8
            and not square_regime
        )
        if square_regime or (plateauish and (bimodality >= 0.3 or max_jump_frac >= 0.5)):
            hint = "square"
        elif sawish:
            hint = "sawtooth"
        elif triangleish:
            hint = "triangle"
        elif sineish:
            hint = "sine"
        else:
            hint = "ambiguous"
        # Template correlation can break ties / rescue ambiguous cases,
        # but must not override a strong square-regime signature (drifted plateaus).
        tmpl_best = template_match.get("best")
        tmpl_margin = float(template_match.get("margin") or 0.0)
        tmpl_corr = float(template_match.get("best_corr") or 0.0)
        if (
            not square_regime
            and period_trusted
            and tmpl_best
            and tmpl_corr >= 0.55
            and tmpl_margin >= 0.05
        ):
            if hint == "ambiguous" or hint == tmpl_best:
                hint = str(tmpl_best)
            elif tmpl_margin >= 0.15 and tmpl_corr >= 0.7:
                hint = str(tmpl_best)
        warnings = ["periodicity_is_not_waveform_type"]
        warnings.extend(period_warnings)
        if period and not period_trusted:
            warnings.append("untrusted_fold_period")
        items.append(
            {
                "series_index": sid,
                "start": s,
                "end": e,
                "dominant_period": period,
                "period_trusted": period_trusted,
                "jump_ratio": jump_ratio,
                "n_large_jumps": large_jumps,
                "jump_threshold": jump_thr,
                "max_abs_diff": max_abs_diff,
                "max_jump_frac": max_jump_frac,
                "jump_regime": jump_info,
                "amplitude_bimodality": bimodality,
                "n_unique_levels": n_levels,
                "n_plateau_runs": int(step_stats["n_plateau_runs"]),
                "level_tolerance": float(step_stats["tolerance"]),
                "folded_mean_abs_slope": folded_slope_abs,
                "rise_fall_asymmetry": rise_fall_asymmetry,
                "harmonic": harmonic,
                "template_match": template_match,
                "waveform_hint": hint,
                "metric_definition": (
                    "waveform_hint from jump regime + plateau/harmonic/template features; "
                    "periodicity alone does not imply sine"
                ),
                "evidence_source_id": f"waveform_features:{sid}:{s}:{e}",
                "warnings": warnings,
            }
        )
    return _pack_per_series("waveform_features", items)


def _anomaly_detect(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    items = []
    threshold = float(arguments.get("z_threshold", 3.0))
    for sid, arr in _selected_arrays(arguments, series):
        sub, s, e = _slice_window(arr, arguments)
        offset = s or 0
        std = float(np.std(sub))
        if std < _VARIANCE_EPS:
            items.append(
                {
                    "series_index": sid,
                    "start": s,
                    "end": e,
                    "n_anomalies": 0,
                    "anomaly_indices": [],
                    "max_abs_z": 0.0,
                }
            )
            continue
        z = (sub - float(np.mean(sub))) / std
        idxs = [int(offset + i) for i, zv in enumerate(z) if abs(float(zv)) >= threshold]
        max_abs_z = float(np.max(np.abs(z))) if z.size else 0.0
        items.append(
            {
                "series_index": sid,
                "start": s,
                "end": e,
                "z_threshold": threshold,
                "n_anomalies": len(idxs),
                "anomaly_indices": idxs[:30],
                "max_abs_z": max_abs_z,
            }
        )
    return _pack_per_series("anomaly_detect", items)


def _global_extrema(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    """Global max/min indices and optional per-index classification (Base index tasks)."""
    items = []
    index_base = int(arguments.get("index_base", 0))
    query_index = arguments.get("index")
    for sid, arr in _selected_arrays(arguments, series):
        sub, s, e = _slice_window(arr, arguments)
        offset = s or 0
        if sub.size == 0:
            raise ValueError(f"empty window for series {sid}")
        rel_max = int(np.argmax(sub))
        rel_min = int(np.argmin(sub))
        max_val = float(sub[rel_max])
        min_val = float(sub[rel_min])
        # MMTS Base index tasks: first global max index; last global min index on ties.
        max_rel = int(np.where(sub == max_val)[0][0])
        min_rel = int(np.where(sub == min_val)[0][-1])
        max_idx = offset + max_rel
        min_idx = offset + min_rel
        peaks, troughs = _count_peaks_troughs(sub)
        peaks = [offset + i for i in peaks]
        troughs = [offset + i for i in troughs]
        item: Dict[str, Any] = {
            "series_index": sid,
            "start": s,
            "end": e,
            "max_index": max_idx,
            "min_index": min_idx,
            "max_value": float(arr[max_idx]),
            "min_value": float(arr[min_idx]),
            "n_peaks": len(peaks),
            "n_troughs": len(troughs),
            "peak_indices": peaks[:30],
            "trough_indices": troughs[:30],
        }
        if query_index is not None:
            pos = int(query_index) - index_base if index_base == 1 else int(query_index)
            if not (0 <= pos < len(arr)):
                raise ValueError(f"index {query_index!r} out of range for series {sid} (length={len(arr)})")
            val = float(arr[pos])
            tol = _level_tolerance(arr)
            item.update(
                {
                    "query_index": int(query_index),
                    "query_position": pos,
                    "query_value": val,
                    "is_global_max": pos == max_idx or abs(val - item["max_value"]) <= tol,
                    "is_global_min": pos == min_idx or abs(val - item["min_value"]) <= tol,
                    "is_local_peak": pos in peaks,
                    "is_local_trough": pos in troughs,
                }
            )
        items.append(item)
    return _pack_per_series("global_extrema", items)


def _segment_trend(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    """Linear trend direction/slope for a segment (Base index / local trend questions)."""
    items = []
    flat_eps = float(arguments.get("flat_eps", 1e-6))
    for sid, arr in _selected_arrays(arguments, series):
        sub, s, e = _slice_window(arr, arguments)
        if len(sub) < 2:
            items.append(
                {
                    "series_index": sid,
                    "start": s,
                    "end": e,
                    "slope": 0.0,
                    "direction": "flat",
                    "mean": float(np.mean(sub)) if len(sub) else 0.0,
                    "std": float(np.std(sub)) if len(sub) else 0.0,
                }
            )
            continue
        slope = float((sub[-1] - sub[0]) / (len(sub) - 1))
        if slope > flat_eps:
            direction = "upward"
        elif slope < -flat_eps:
            direction = "downward"
        else:
            direction = "flat"
        # MMTS trend-direction choice uses ±0.1 as vague/flat boundary.
        if slope > 0.1:
            direction_class = "upward"
        elif slope < -0.1:
            direction_class = "downward"
        else:
            direction_class = "vague"
        items.append(
            {
                "series_index": sid,
                "start": s,
                "end": e,
                "slope": slope,
                "direction": direction,
                "direction_class": direction_class,
                "trend_method": "endpoint",
                "mean": float(np.mean(sub)),
                "std": float(np.std(sub)),
                "start_value": float(sub[0]),
                "end_value": float(sub[-1]),
            }
        )
    return _pack_per_series("segment_trend", items)


def _acf_at_lag(arr: np.ndarray, lag: int) -> Optional[float]:
    """γ_lag / γ_0 using the same unbiased-dot form as seas_acf1."""
    lag = int(lag)
    if lag <= 0 or lag >= len(arr):
        return None
    if float(np.std(arr)) < _VARIANCE_EPS:
        return 0.0
    centered = arr - np.mean(arr)
    denom = float(np.dot(centered, centered))
    if abs(denom) < _VARIANCE_EPS:
        return 0.0
    return float(np.dot(centered[:-lag], centered[lag:]) / denom)


def _acf(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    items = []
    requested_lags = arguments.get("lags")
    lag_list: Optional[List[int]] = None
    if isinstance(requested_lags, (list, tuple)) and requested_lags:
        lag_list = [int(x) for x in requested_lags]
    for sid, arr in _selected_arrays(arguments, series):
        sub, s, e = _slice_window(arr, arguments)
        max_lag = int(arguments.get("max_lag", min(40, max(1, len(sub) // 4))))
        if lag_list:
            max_lag = max(max_lag, max(lag_list))
        max_lag = max(1, min(max_lag, max(1, len(sub) - 1)))
        if float(np.std(sub)) < _VARIANCE_EPS:
            items.append(
                {
                    "series_index": sid,
                    "start": s,
                    "end": e,
                    "max_lag": max_lag,
                    "best_lag": 0,
                    "acf": [0.0] * max_lag,
                    "acf_at_lags": {str(l): 0.0 for l in (lag_list or [])},
                    "note": "zero-variance series",
                }
            )
            continue
        vals = []
        for lag in range(1, max_lag + 1):
            v = _acf_at_lag(sub, lag)
            vals.append(0.0 if v is None else v)
        best = int(np.argmax(np.abs(vals))) + 1 if vals else 0
        at_lags = {}
        for lag in lag_list or []:
            v = _acf_at_lag(sub, lag)
            if v is not None:
                at_lags[str(lag)] = v
        items.append(
            {
                "series_index": sid,
                "start": s,
                "end": e,
                "max_lag": max_lag,
                "best_lag": best,
                "acf": vals,
                "acf_at_lags": at_lags,
            }
        )
    return _pack_per_series("autocorr", items)


def _seas_acf(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    """MMTS seas_acf1: ρ_m = γ_m / γ_0 at a seasonal lag m (e.g. 26 weeks)."""
    lag = arguments.get("lag", arguments.get("m", arguments.get("frequency", arguments.get("period"))))
    if lag is None:
        return ToolResult(
            name="seas_acf",
            success=False,
            data={},
            error="seas_acf requires lag/m/frequency (e.g. 26 for weekly half-year)",
        )
    lag_i = int(lag)
    items = []
    for sid, arr in _selected_arrays(arguments, series):
        sub, s, e = _slice_window(arr, arguments)
        val = _acf_at_lag(sub, lag_i)
        if val is None:
            items.append(
                {
                    "series_index": sid,
                    "start": s,
                    "end": e,
                    "lag": lag_i,
                    "seas_acf1": None,
                    "strength_hint": "unavailable",
                    "note": f"lag {lag_i} invalid for length {len(sub)}",
                }
            )
            continue
        strength = (
            "strong" if abs(val) >= 0.6 else "moderate" if abs(val) >= 0.3 else "weak"
        )
        items.append(
            {
                "series_index": sid,
                "start": s,
                "end": e,
                "lag": lag_i,
                "seas_acf1": val,
                "strength_hint": strength,
                "metric_definition": "ρ_m=γ_m/γ_0 (MMTS seas_acf1)",
            }
        )
    return _pack_per_series("seas_acf", items)


def _fft_period(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    items = []
    for sid, arr in _selected_arrays(arguments, series):
        n = len(arr)
        if float(np.std(arr)) < _VARIANCE_EPS:
            items.append(
                {
                    "series_index": sid,
                    "dominant_period": None,
                    "spectral_strength": 0.0,
                    "period_trusted": False,
                    "note": "zero-variance series",
                    "warnings": ["zero_variance"],
                }
            )
            continue
        centered = arr - np.mean(arr)
        spec = np.abs(np.fft.rfft(centered))
        freqs = np.fft.rfftfreq(n, d=1.0)
        warnings: List[str] = []
        if len(spec) > 1:
            idx = int(np.argmax(spec[1:]) + 1)
            period = float(1.0 / freqs[idx]) if freqs[idx] > 0 else None
            strength = float(spec[idx] / (np.sum(spec) + 1e-12))
        else:
            period, strength = None, 0.0
        trusted = True
        if period is None:
            trusted = False
            warnings.append("no_dominant_period")
        elif period >= 0.9 * n:
            trusted = False
            warnings.append("dominant_period_near_series_length")
        elif period >= 0.5 * n:
            trusted = False
            warnings.append("dominant_period_near_half_length")
        items.append(
            {
                "series_index": sid,
                "dominant_period": period,
                "spectral_strength": strength,
                "period_trusted": trusted,
                "warnings": warnings,
            }
        )
    return _pack_per_series("fft_period", items)


def _stl_strength(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    items = []
    for sid, arr in _selected_arrays(arguments, series):
        sub, s, e = _slice_window(arr, arguments)
        if len(sub) < 4:
            return ToolResult(name="stl_strength", success=False, data={}, error=f"series {sid} too short for STL")
        raw_period = arguments.get("period", None)
        if raw_period is None or raw_period == "" or (
            isinstance(raw_period, str) and raw_period.strip().lower() in {"null", "none", "auto"}
        ):
            requested = 0
        elif isinstance(raw_period, str) and not re.fullmatch(r"-?\d+", raw_period.strip()):
            return ToolResult(
                name="stl_strength",
                success=False,
                data={},
                error=(
                    "invalid argument 'period': expected positive integer or omitted "
                    f"(see tool catalog → inputs.period); got {raw_period!r}"
                ),
            )
        else:
            try:
                requested = int(raw_period)
            except (TypeError, ValueError):
                return ToolResult(
                    name="stl_strength",
                    success=False,
                    data={},
                    error=f"invalid argument 'period': expected positive integer or omitted; got {raw_period!r}",
                )
        period, period_warnings = _estimate_stl_period(sub, requested if requested > 1 else 0)
        try:
            from statsmodels.tsa.seasonal import STL

            stl = STL(sub, period=period, robust=True)
            res = stl.fit()
            seasonal = np.asarray(res.seasonal)
            resid = np.asarray(res.resid)
            trend = np.asarray(res.trend)
            seasonal_strength = float(max(0.0, 1.0 - np.var(resid) / (np.var(seasonal + resid) + 1e-12)))
            trend_strength = float(max(0.0, 1.0 - np.var(resid) / (np.var(trend + resid) + 1e-12)))
            period_trusted = period < 0.5 * len(sub) and period <= max(2, len(sub) // 4)
            items.append(
                {
                    "series_index": sid,
                    "start": s,
                    "end": e,
                    "period": period,
                    "period_trusted": period_trusted,
                    "period_source": "requested" if requested > 1 else "auto_fft_capped",
                    "seasonal_strength": seasonal_strength,
                    "season_strength_bin": _season_strength_bin(seasonal_strength),
                    "trend_strength": trend_strength,
                    "metric_definition": (
                        "seasonal_strength=1-Var(resid)/Var(seasonal+resid) (STL proxy for MMTS "
                        "1-Var(n)/Var(s+n)); bins none<0.2, weak<0.5, moderate<=0.8, else strong"
                    ),
                    "warnings": period_warnings
                    + ([] if period_trusted else ["untrusted_period_strength_may_be_inflated"]),
                }
            )
        except Exception as e:  # noqa: BLE001
            return ToolResult(name="stl_strength", success=False, data={}, error=str(e))
    return _pack_per_series("stl_strength", items)


def _stationarity(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    items = []
    for sid, arr in _selected_arrays(arguments, series):
        try:
            from statsmodels.tsa.stattools import adfuller

            stat, pvalue, *_ = adfuller(arr, autolag="AIC")
            if not (np.isfinite(stat) and np.isfinite(pvalue)):
                return ToolResult(
                    name="adf_stationarity",
                    success=False,
                    data={},
                    error=f"ADF produced non-finite stats for series {sid}",
                )
            items.append(
                {
                    "series_index": sid,
                    "adf_stat": float(stat),
                    "pvalue": float(pvalue),
                    "is_stationary_at_5pct": bool(pvalue < 0.05),
                }
            )
        except Exception as e:  # noqa: BLE001
            return ToolResult(name="adf_stationarity", success=False, data={}, error=str(e))
    return _pack_per_series("adf_stationarity", items)


def _change_points(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    items = []
    for sid, arr in _selected_arrays(arguments, series):
        window = max(5, len(arr) // 20)
        scores = []
        for i in range(window, len(arr) - window):
            left = arr[i - window : i]
            right = arr[i : i + window]
            scores.append((i, abs(float(np.mean(right) - np.mean(left)))))
        scores.sort(key=lambda x: x[1], reverse=True)
        top = scores[:5]
        items.append(
            {
                "series_index": sid,
                "candidates": [{"index": i, "score": s} for i, s in top],
            }
        )
    return _pack_per_series("change_points", items)


def _interval_compare(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    items = []
    for sid, arr in _selected_arrays(arguments, series):
        n = len(arr)
        left = arguments.get("left_interval")
        right = arguments.get("right_interval")
        if (
            isinstance(left, (list, tuple))
            and isinstance(right, (list, tuple))
            and len(left) >= 2
            and len(right) >= 2
        ):
            ls, le = int(left[0]), int(left[1])
            rs, re = int(right[0]), int(right[1])
            ls, le = max(0, min(ls, n - 1)), max(0, min(le, n - 1))
            rs, re = max(0, min(rs, n - 1)), max(0, min(re, n - 1))
            if le < ls:
                ls, le = le, ls
            if re < rs:
                rs, re = re, rs
            a = arr[ls : le + 1]
            b = arr[rs : re + 1]
            if len(a) == 0 or len(b) == 0:
                return ToolResult(
                    name="interval_compare",
                    success=False,
                    data={},
                    error=f"series {sid}: interval bounds produced an empty side",
                )
            left_stats = _segment_summary(a, ls)
            right_stats = _segment_summary(b, rs)
            items.append(
                {
                    "series_index": sid,
                    "mode": "pair",
                    "left_interval": [ls, le],
                    "right_interval": [rs, re],
                    "left_mean": left_stats["mean"],
                    "right_mean": right_stats["mean"],
                    "left_std": left_stats["std"],
                    "right_std": right_stats["std"],
                    "left_max": left_stats["max"],
                    "right_max": right_stats["max"],
                    "left_min": left_stats["min"],
                    "right_min": right_stats["min"],
                    "left_max_index": left_stats["max_index"],
                    "right_max_index": right_stats["max_index"],
                    "left_n_peaks": left_stats["n_peaks"],
                    "right_n_peaks": right_stats["n_peaks"],
                    "left_n_troughs": left_stats["n_troughs"],
                    "right_n_troughs": right_stats["n_troughs"],
                    "left_direction": left_stats["direction"],
                    "right_direction": right_stats["direction"],
                    "left_slope": left_stats["slope"],
                    "right_slope": right_stats["slope"],
                    "mean_delta": float(right_stats["mean"] - left_stats["mean"]),
                    "max_delta": float(right_stats["max"] - left_stats["max"]),
                    "same_trend_direction": left_stats["direction"] == right_stats["direction"],
                }
            )
            continue

        start = int(arguments.get("start", 0))
        mid = int(arguments.get("mid", n // 2))
        end = int(arguments.get("end", n))
        start = max(0, min(start, n))
        end = max(0, min(end, n))
        mid = max(start, min(mid, end))
        a = arr[start:mid]
        b = arr[mid:end]
        if len(a) == 0 or len(b) == 0:
            return ToolResult(
                name="interval_compare",
                success=False,
                data={},
                error=f"series {sid}: interval bounds produced an empty side after clamping",
            )
        items.append(
            {
                "series_index": sid,
                "mode": "split",
                "left_mean": float(np.mean(a)),
                "right_mean": float(np.mean(b)),
                "left_std": float(np.std(a)),
                "right_std": float(np.std(b)),
                "mean_delta": float(np.mean(b) - np.mean(a)),
                "start": start,
                "mid": mid,
                "end": end,
            }
        )
    return _pack_per_series("interval_compare", items)


def _cross_series_compare(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    """Compare the same (or specified) windows across two series (MMTS analogical tasks)."""
    if len(series) < 2:
        return ToolResult(name="cross_series_compare", success=False, data={}, error="Need >=2 series")
    s1_raw = arguments.get("series_index_1", arguments.get("series_index", 1))
    s2_raw = arguments.get("series_index_2", 2)
    i1 = _parse_one_series_token(s1_raw, len(series))
    i2 = _parse_one_series_token(s2_raw, len(series))
    if i1 == i2:
        return ToolResult(name="cross_series_compare", success=False, data={}, error="series_index_1 and _2 must differ")

    a_full = np.asarray(series[i1], dtype=float)
    b_full = np.asarray(series[i2], dtype=float)

    # Window: explicit start/end, or left/right intervals per series, or full overlap length
    start = arguments.get("start")
    end = arguments.get("end")
    left = arguments.get("left_interval")
    right = arguments.get("right_interval")

    if isinstance(left, (list, tuple)) and len(left) >= 2:
        ls, le = int(left[0]), int(left[1])
    elif start is not None and end is not None:
        ls, le = int(start), int(end)
    else:
        ls, le = 0, min(len(a_full), len(b_full)) - 1

    if isinstance(right, (list, tuple)) and len(right) >= 2:
        rs, re = int(right[0]), int(right[1])
    elif start is not None and end is not None:
        rs, re = int(start), int(end)
    else:
        rs, re = ls, le

    ls, le = max(0, min(ls, len(a_full) - 1)), max(0, min(le, len(a_full) - 1))
    rs, re = max(0, min(rs, len(b_full) - 1)), max(0, min(re, len(b_full) - 1))
    if le < ls:
        ls, le = le, ls
    if re < rs:
        rs, re = re, rs

    a = a_full[ls : le + 1]
    b = b_full[rs : re + 1]
    n = min(len(a), len(b))
    if n == 0:
        return ToolResult(name="cross_series_compare", success=False, data={}, error="empty segment after slicing")
    a = a[:n]
    b = b[:n]

    stats_a = _segment_summary(a, ls)
    stats_b = _segment_summary(b, rs)
    sa, sb = float(np.std(a)), float(np.std(b))
    if sa >= _VARIANCE_EPS:
        an = (a - np.mean(a)) / sa
    else:
        an = a - np.mean(a)
    if sb >= _VARIANCE_EPS:
        bn = (b - np.mean(b)) / sb
    else:
        bn = b - np.mean(b)
    corr, corr_err = _safe_corr(an, bn)
    dist = float(np.linalg.norm(an - bn))

    return ToolResult(
        name="cross_series_compare",
        success=True,
        data={
            "series_index_1": i1 + 1,
            "series_index_2": i2 + 1,
            "interval_1": [ls, le],
            "interval_2": [rs, re],
            "series_1": stats_a,
            "series_2": stats_b,
            "same_trend_direction": stats_a["direction"] == stats_b["direction"],
            "mean_delta": float(stats_b["mean"] - stats_a["mean"]),
            "max_delta": float(stats_b["max"] - stats_a["max"]),
            "euclidean_distance": dist,
            "corr": corr,
            "corr_error": corr_err,
        },
    )


def _is_all_series_token(value: Any) -> bool:
    return isinstance(value, str) and value.strip().lower() in {"all", "*", "every", "each"}


def _cross_lag_corr_arrays(a: np.ndarray, b: np.ndarray, raw_lag: int) -> Tuple[Optional[float], Optional[str], int]:
    m = min(len(a), len(b))
    if abs(raw_lag) >= m:
        return None, "lag too large", raw_lag
    if raw_lag == 0:
        left, right = a[:m], b[:m]
    elif raw_lag > 0:
        left, right = a[: m - raw_lag], b[raw_lag:m]
    else:
        lag = -raw_lag
        left, right = a[lag:m], b[: m - lag]
    c, err = _safe_corr(left, right)
    return c, err, raw_lag


def _lag_corr(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    # Pair selection for cross-corr
    i1 = arguments.get("series_index_1", arguments.get("series_1", arguments.get("series1")))
    i2 = arguments.get("series_index_2", arguments.get("series_2", arguments.get("series2")))
    raw_lag = int(arguments.get("lag", 0 if len(series) >= 2 else 1))

    if len(series) < 2 and i1 is None and i2 is None:
        arr = np.asarray(series[0], dtype=float)
        lag = int(arguments.get("lag", 1))
        if lag <= 0:
            return ToolResult(name="lag_corr", success=False, data={}, error="auto lag must be >= 1")
        if lag >= len(arr):
            return ToolResult(name="lag_corr", success=False, data={}, error="lag too large")
        c, err = _safe_corr(arr[:-lag], arr[lag:])
        if err:
            return ToolResult(name="lag_corr", success=False, data={}, error=err)
        return ToolResult(
            name="lag_corr",
            success=True,
            data={"mode": "auto", "lag": lag, "corr": c, "series_index": 1},
        )

    n = len(series)
    for key, val in (
        ("series_1", i1),
        ("series_2", i2),
        ("series1", arguments.get("series1")),
        ("series2", arguments.get("series2")),
    ):
        if _looks_like_raw_series_values(val, n, series):
            raise ValueError(
                f"Do not pass raw series values in {key}; use series_index_1 / series_index_2 (1-based)."
            )

    # series_index_1/2 = "all" (or either side all) => all unordered pairs
    if _is_all_series_token(i1) or _is_all_series_token(i2):
        if n < 2:
            return ToolResult(name="lag_corr", success=False, data={}, error="Need >=2 series for pairwise lag_corr")
        pairs = []
        errors = []
        for ai in range(n):
            for bi in range(ai + 1, n):
                a = np.asarray(series[ai], dtype=float)
                b = np.asarray(series[bi], dtype=float)
                c, err, _ = _cross_lag_corr_arrays(a, b, raw_lag)
                if err:
                    errors.append({"series_index_1": ai + 1, "series_index_2": bi + 1, "error": err})
                else:
                    pairs.append(
                        {
                            "series_index_1": ai + 1,
                            "series_index_2": bi + 1,
                            "lag": raw_lag,
                            "corr": c,
                        }
                    )
        if not pairs:
            return ToolResult(
                name="lag_corr",
                success=False,
                data={"errors": errors},
                error="all pairwise lag_corr failed",
            )
        return ToolResult(
            name="lag_corr",
            success=True,
            data={"mode": "cross_all", "lag": raw_lag, "pairs": pairs, "errors": errors},
        )

    if i1 is not None or i2 is not None:
        a_idx = _parse_one_series_token(i1 if i1 is not None else 1, n)
        b_idx = _parse_one_series_token(i2 if i2 is not None else 2, n)
    else:
        a_idx, b_idx = 0, 1

    a = np.asarray(series[a_idx], dtype=float)
    b = np.asarray(series[b_idx], dtype=float)
    c, err, _ = _cross_lag_corr_arrays(a, b, raw_lag)
    if err:
        return ToolResult(name="lag_corr", success=False, data={}, error=err)
    return ToolResult(
        name="lag_corr",
        success=True,
        data={
            "mode": "cross",
            "lag": raw_lag,
            "corr": c,
            "series_index_1": a_idx + 1,
            "series_index_2": b_idx + 1,
        },
    )


def _pairwise_distance(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    method = arguments.get("method", "euclidean")
    if len(series) < 2:
        return ToolResult(name="pairwise_distance", success=False, data={}, error="Need >=2 series")
    # Optional reference series (default 1)
    ref_raw = arguments.get("series_index", arguments.get("ref_series_index", 1))
    if _looks_like_raw_series_values(ref_raw, len(series), series):
        raise ValueError("Do not pass raw series values; use series_index for the reference series.")
    if isinstance(ref_raw, str) and ref_raw.strip().lower() in {"all", "*"}:
        ref_idx = 0
    else:
        ref_idx = _parse_one_series_token(ref_raw if ref_raw is not None else 1, len(series))
    ref = np.asarray(series[ref_idx], dtype=float)
    distances = []
    for i, s in enumerate(series):
        if i == ref_idx:
            continue
        arr = np.asarray(s, dtype=float)
        n = min(len(ref), len(arr))
        if n == 0:
            return ToolResult(name="pairwise_distance", success=False, data={}, error="empty overlap between series")
        a, b = ref[:n], arr[:n]
        if method == "dtw":
            try:
                from dtaidistance import dtw

                dist = float(dtw.distance_fast(a.astype(np.double), b.astype(np.double)))
            except Exception:
                dist = float(np.linalg.norm(a - b))
        else:
            sa, sb = float(np.std(a)), float(np.std(b))
            if sa >= _VARIANCE_EPS:
                a = (a - np.mean(a)) / sa
            if sb >= _VARIANCE_EPS:
                b = (b - np.mean(b)) / sb
            dist = float(np.linalg.norm(a - b))
        if not np.isfinite(dist):
            return ToolResult(
                name="pairwise_distance",
                success=False,
                data={},
                error=f"non-finite distance for series {i + 1}",
            )
        distances.append({"series_index": i + 1, "distance": dist})
    best = min(distances, key=lambda x: x["distance"]) if distances else None
    return ToolResult(
        name="pairwise_distance",
        success=True,
        data={
            "method": method,
            "ref_series_index": ref_idx + 1,
            "distances": distances,
            "nearest": best,
        },
    )


def _smooth_reverse(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    items = []
    for sid, arr in _selected_arrays(arguments, series):
        window = int(arguments.get("window", 5))
        window = max(1, min(window, len(arr)))
        kernel = np.ones(window) / window
        smoothed = np.convolve(arr, kernel, mode="same")
        items.append(
            {
                "series_index": sid,
                "smooth_mean": float(np.mean(smoothed)),
                "reverse_start_end_delta": float(arr[::-1][-1] - arr[::-1][0]),
                "original_start_end_delta": float(arr[-1] - arr[0]),
            }
        )
    return _pack_per_series("smooth_reverse_stats", items)


def _subsequence_locate(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    if len(series) < 2:
        return ToolResult(name="subsequence_locate", success=False, data={}, error="Need query and longer series")
    q_raw = arguments.get("query_series_index", arguments.get("series_index_1", 1))
    l_raw = arguments.get("long_series_index", arguments.get("series_index_2", 2))
    q_idx = _parse_one_series_token(q_raw, len(series))
    l_idx = _parse_one_series_token(l_raw, len(series))
    query = np.asarray(series[q_idx], dtype=float)
    long = np.asarray(series[l_idx], dtype=float)
    if len(query) > len(long):
        query, long = long, query
        q_idx, l_idx = l_idx, q_idx
    method = str(arguments.get("method", "dtw")).strip().lower()
    best_i, best_d = 0, float("inf")
    if method in {"euclidean", "l2", "z_euclidean"}:
        q_std = float(np.std(query))
        q = (query - np.mean(query)) / q_std if q_std >= _VARIANCE_EPS else query - np.mean(query)
        for i in range(0, len(long) - len(query) + 1):
            w = long[i : i + len(query)]
            w_std = float(np.std(w))
            w = (w - np.mean(w)) / w_std if w_std >= _VARIANCE_EPS else w - np.mean(w)
            d = float(np.linalg.norm(q - w))
            if d < best_d:
                best_d, best_i = d, i
    else:
        # MMTS find-it uses sliding-window DTW (fastdtw-equivalent via dtaidistance).
        try:
            from dtaidistance import dtw as dtw_mod

            dist_fn = getattr(dtw_mod, "distance_fast", None) or dtw_mod.distance
        except Exception as ex:  # noqa: BLE001
            return ToolResult(
                name="subsequence_locate",
                success=False,
                data={},
                error=f"dtw backend unavailable: {ex}",
            )
        q = np.asarray(query, dtype=np.double)
        for i in range(0, len(long) - len(query) + 1):
            w = np.asarray(long[i : i + len(query)], dtype=np.double)
            d = float(dist_fn(q, w))
            if d < best_d:
                best_d, best_i = d, i
        method = "dtw"
    if not np.isfinite(best_d):
        return ToolResult(name="subsequence_locate", success=False, data={}, error="non-finite subsequence distance")
    return ToolResult(
        name="subsequence_locate",
        success=True,
        data={
            "best_start": best_i,
            "best_end": best_i + len(query) - 1,
            "distance": best_d,
            "method": method,
            "query_len": len(query),
            "query_series_index": q_idx + 1,
            "long_series_index": l_idx + 1,
        },
    )


def _moving_average(arr: np.ndarray, window: int = 3) -> np.ndarray:
    """Centered MA matching MMTS SmoothitProcessor (window=3 default)."""
    window = max(1, int(window))
    out = np.empty_like(arr, dtype=float)
    half = window // 2
    for i in range(len(arr)):
        a = max(0, i - half)
        b = min(len(arr), i + half + 1)
        out[i] = float(np.mean(arr[a:b]))
    return out


def _smooth_shape_match(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    """Rank candidates after MA smoothing (MMTS smooth-it). Query stays series 1 by default."""
    if len(series) < 2:
        return ToolResult(name="smooth_shape_match", success=False, data={}, error="Need >=2 series")
    window = int(arguments.get("window", arguments.get("smooth_window", 3)) or 3)
    method = str(arguments.get("method", "dtw")).strip().lower()
    query_idx = _parse_one_series_token(arguments.get("query_series_index", 1), len(series))
    query = np.asarray(series[query_idx], dtype=float)
    # If candidates are already baked-smoothed in MMTS CSV, still smooth consistently.
    ranking = []
    for idx, raw in enumerate(series):
        if idx == query_idx:
            continue
        cand = _moving_average(np.asarray(raw, dtype=float), window)
        q = query
        c = cand
        n = min(len(q), len(c))
        q, c = q[:n], c[:n]
        if method in {"euclidean", "l2"}:
            qn = _zscore_1d(q)
            cn = _zscore_1d(c)
            dist = float(np.linalg.norm(qn - cn))
        else:
            try:
                from dtaidistance import dtw as dtw_mod

                dist_fn = getattr(dtw_mod, "distance_fast", None) or dtw_mod.distance
                dist = float(dist_fn(np.asarray(q, dtype=np.double), np.asarray(c, dtype=np.double)))
                method = "dtw"
            except Exception as ex:  # noqa: BLE001
                return ToolResult(name="smooth_shape_match", success=False, data={}, error=str(ex))
        ranking.append({"series_index": idx + 1, "distance": dist})
    ranking.sort(key=lambda x: x["distance"])
    return ToolResult(
        name="smooth_shape_match",
        success=True,
        data={
            "query_series_index": query_idx + 1,
            "smooth_window": window,
            "method": method,
            "ranking": ranking,
            "nearest": ranking[0] if ranking else None,
        },
    )


def _peaks_above_threshold(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    """Count local peaks/troughs with optional absolute height threshold (InWild-style)."""
    items = []
    thr = arguments.get("threshold", arguments.get("min_height"))
    thr_v = float(thr) if thr is not None else None
    for sid, arr in _selected_arrays(arguments, series):
        sub, s, e = _slice_window(arr, arguments)
        offset = s or 0
        peaks, troughs = _count_peaks_troughs(sub)
        if thr_v is not None:
            peaks = [i for i in peaks if float(sub[i]) >= thr_v]
            troughs = [i for i in troughs if float(sub[i]) <= thr_v]
        peaks = [offset + i for i in peaks]
        troughs = [offset + i for i in troughs]
        items.append(
            {
                "series_index": sid,
                "start": s,
                "end": e,
                "threshold": thr_v,
                "n_peaks": len(peaks),
                "n_troughs": len(troughs),
                "peak_idx": peaks[:30],
                "trough_idx": troughs[:30],
            }
        )
    return _pack_per_series("peaks_above_threshold", items)


def _bimodal_detect(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    items = []
    for sid, arr in _selected_arrays(arguments, series):
        sub, s, e = _slice_window(arr, arguments)
        hist, edges = np.histogram(sub, bins=min(40, max(8, len(sub) // 20)))
        # Simple valley-between-two-peaks heuristic.
        order = np.argsort(hist)[::-1]
        is_bimodal = False
        separation = 0.0
        if len(order) >= 2:
            p1, p2 = int(order[0]), int(order[1])
            lo, hi = sorted([p1, p2])
            if hi > lo + 1:
                valley = float(np.min(hist[lo : hi + 1]))
                peak_min = float(min(hist[p1], hist[p2]))
                is_bimodal = peak_min > 0 and valley <= 0.6 * peak_min
                separation = abs(float((edges[p1] + edges[p1 + 1]) / 2 - (edges[p2] + edges[p2 + 1]) / 2))
        items.append(
            {
                "series_index": sid,
                "start": s,
                "end": e,
                "is_bimodal": bool(is_bimodal),
                "mode_separation": separation,
                "amplitude_bimodality": float(sum(sorted(hist, reverse=True)[:2]) / max(hist.sum(), 1)),
            }
        )
    return _pack_per_series("bimodal_detect", items)


def _terasvirta_stat(x: np.ndarray, lag: int = 1) -> float:
    """Nixtla/tsfeatures-compatible Terasvirta NN linearity statistic (χ² form)."""
    import statsmodels.api as sm

    x = np.asarray(x, dtype=float).ravel()
    if float(np.std(x)) >= _VARIANCE_EPS:
        x = (x - float(np.mean(x))) / float(np.std(x, ddof=1))
    size_x = len(x)
    # embed(x, lag+1): rows [x_t, x_{t-1}, ..., x_{t-lag}]
    cols = [np.roll(x, k) for k in range(lag + 1)]
    y_mat = np.column_stack(cols)[lag:]
    y = y_mat[:, 0]
    X = sm.add_constant(y_mat[:, 1:])
    ols = sm.OLS(y, X).fit()
    u = ols.resid
    ssr0 = float(np.sum(u ** 2))
    nn_cols = []
    for i in range(lag):
        for j in range(i, lag):
            nn_cols.append(X[:, i + 1] * X[:, j + 1])
    for i in range(lag):
        for j in range(i, lag):
            for k in range(j, lag):
                nn_cols.append(X[:, i + 1] * X[:, j + 1] * X[:, k + 1])
    X_nn = np.column_stack([X] + nn_cols)
    ols_nn = sm.OLS(u, X_nn).fit()
    ssr = float(np.sum(ols_nn.resid ** 2))
    if ssr <= 0 or ssr0 <= 0:
        return 0.0
    return float(size_x * np.log(ssr0 / ssr))


def _nonlinearity_terasvirta(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    """MMTS nonlinearity = 10 * Terasvirta_stat / N."""
    lag = int(arguments.get("lag", 1) or 1)
    items = []
    for sid, arr in _selected_arrays(arguments, series):
        sub, s, e = _slice_window(arr, arguments)
        n = len(sub)
        if n < max(20, lag + 5):
            items.append(
                {
                    "series_index": sid,
                    "start": s,
                    "end": e,
                    "nonlinearity": None,
                    "terasvirta_stat": None,
                    "n": n,
                    "note": "series too short for Terasvirta test",
                }
            )
            continue
        try:
            stat = _terasvirta_stat(sub, lag=lag)
            score = float(10.0 * stat / n)
            strength = "strong" if score >= 1.0 else "moderate" if score >= 0.3 else "weak"
            items.append(
                {
                    "series_index": sid,
                    "start": s,
                    "end": e,
                    "nonlinearity": score,
                    "terasvirta_stat": stat,
                    "n": n,
                    "lag": lag,
                    "strength_hint": strength,
                    "metric_definition": "10 * Terasvirta_stat / N (MMTS/tsfeatures)",
                }
            )
        except Exception as ex:  # noqa: BLE001
            items.append(
                {
                    "series_index": sid,
                    "start": s,
                    "end": e,
                    "nonlinearity": None,
                    "error": str(ex),
                }
            )
    return _pack_per_series("nonlinearity_terasvirta", items)


_WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
_WEEKDAY_ALIASES = {name.lower(): i for i, name in enumerate(_WEEKDAY_NAMES)}
_WEEKDAY_ALIASES.update({"mon": 0, "tue": 1, "wed": 2, "thu": 3, "thur": 3, "thurs": 3, "fri": 4, "sat": 5, "sun": 6})


def _parse_anchor_weekday(raw: Any, default: int = 3) -> int:
    if raw is None:
        return default
    if isinstance(raw, (int, float, np.integer, np.floating)):
        return int(raw) % 7
    text = str(raw).strip().lower()
    if text.isdigit():
        return int(text) % 7
    return _WEEKDAY_ALIASES.get(text, default)


def _index_calendar_map(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    """Map indices → weekday/hour using MMTS InWild hourly anchor (default Thu 00:00)."""
    freq_hours = int(arguments.get("freq_hours", arguments.get("freq", 1)) or 1)
    anchor_weekday = _parse_anchor_weekday(arguments.get("anchor_weekday", arguments.get("start_weekday", 3)))
    anchor_hour = int(arguments.get("anchor_hour", arguments.get("start_hour", 0)) or 0)
    indices_raw = arguments.get("indices", arguments.get("index"))
    if indices_raw is None:
        start = arguments.get("start", 0)
        end = arguments.get("end")
        if end is None and series:
            end = len(series[0]) - 1
        if end is None:
            return ToolResult(
                name="index_calendar_map",
                success=False,
                data={},
                error="Provide indices or start/end",
            )
        indices = list(range(int(start), int(end) + 1))
    elif isinstance(indices_raw, (list, tuple)):
        indices = [int(x) for x in indices_raw]
    else:
        indices = [int(indices_raw)]

    records = []
    for idx in indices:
        hours_passed = int(idx) * freq_hours + anchor_hour
        days_passed = hours_passed // 24
        hour = hours_passed % 24
        weekday = (anchor_weekday + days_passed) % 7
        records.append(
            {
                "index": int(idx),
                "weekday": _WEEKDAY_NAMES[weekday],
                "weekday_index": weekday,
                "hour": int(hour),
                "is_weekend": weekday >= 5,
                "is_weekday": weekday < 5,
            }
        )
    return ToolResult(
        name="index_calendar_map",
        success=True,
        data={
            "anchor_weekday": _WEEKDAY_NAMES[anchor_weekday],
            "anchor_hour": anchor_hour,
            "freq_hours": freq_hours,
            "records": records,
            "n_weekend": sum(1 for r in records if r["is_weekend"]),
            "n_weekday": sum(1 for r in records if r["is_weekday"]),
        },
    )


def _subsequence_rank(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    """Rank multiple long candidates by sliding-window DTW distance to a short query (Match find-it)."""
    if len(series) < 2:
        return ToolResult(name="subsequence_rank", success=False, data={}, error="Need query and candidates")
    q_idx = _parse_one_series_token(arguments.get("query_series_index", 1), len(series))
    raw_cands = arguments.get("candidate_series_indices")
    if raw_cands is None:
        cand_idxs = [i for i in range(len(series)) if i != q_idx]
    else:
        if not isinstance(raw_cands, (list, tuple)):
            return ToolResult(
                name="subsequence_rank",
                success=False,
                data={},
                error="candidate_series_indices must be a list",
            )
        cand_idxs = [_parse_one_series_token(x, len(series)) for x in raw_cands]
    method = str(arguments.get("method", "dtw")).strip().lower()
    ranking = []
    for c_idx in cand_idxs:
        one = _subsequence_locate(
            {
                "query_series_index": q_idx + 1,
                "long_series_index": c_idx + 1,
                "method": method,
            },
            series,
        )
        if not one.success:
            ranking.append({"series_index": c_idx + 1, "distance": float("inf"), "error": one.error})
            continue
        ranking.append(
            {
                "series_index": c_idx + 1,
                "distance": one.data["distance"],
                "best_start": one.data["best_start"],
                "best_end": one.data["best_end"],
                "method": one.data["method"],
            }
        )
    ranking.sort(key=lambda x: float(x.get("distance", float("inf"))))
    return ToolResult(
        name="subsequence_rank",
        success=True,
        data={
            "query_series_index": q_idx + 1,
            "method": method,
            "ranking": ranking,
            "nearest": ranking[0] if ranking else None,
        },
    )


def _window_shape_compare(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    """Compare two or more windows on one series by DTW / z-euclidean distance."""
    windows = arguments.get("windows")
    if not isinstance(windows, list) or len(windows) < 2:
        return ToolResult(
            name="window_shape_compare",
            success=False,
            data={},
            error="windows must be a list of >=2 [start,end] intervals",
        )
    sid = _parse_one_series_token(arguments.get("series_index", 1), len(series))
    arr = np.asarray(series[sid], dtype=float)
    method = str(arguments.get("method", "z_euclidean")).strip().lower()
    segs = []
    for w in windows:
        if not isinstance(w, (list, tuple)) or len(w) < 2:
            return ToolResult(
                name="window_shape_compare",
                success=False,
                data={},
                error="each window must be [start,end]",
            )
        a, b = int(w[0]), int(w[1])
        if a < 0 or b >= len(arr) or a > b:
            return ToolResult(
                name="window_shape_compare",
                success=False,
                data={},
                error=f"window [{a},{b}] out of range for length {len(arr)}",
            )
        segs.append({"start": a, "end": b, "values": arr[a : b + 1]})

    def _dist(u: np.ndarray, v: np.ndarray) -> float:
        n = min(len(u), len(v))
        u, v = u[:n], v[:n]
        if method in {"dtw"}:
            from dtaidistance import dtw as dtw_mod

            dist_fn = getattr(dtw_mod, "distance_fast", None) or dtw_mod.distance
            return float(dist_fn(np.asarray(u, dtype=np.double), np.asarray(v, dtype=np.double)))
        return float(np.linalg.norm(_zscore_1d(u) - _zscore_1d(v)))

    pairs = []
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            d = _dist(segs[i]["values"], segs[j]["values"])
            pairs.append(
                {
                    "window_i": i,
                    "window_j": j,
                    "interval_i": [segs[i]["start"], segs[i]["end"]],
                    "interval_j": [segs[j]["start"], segs[j]["end"]],
                    "distance": d,
                }
            )
    pairs.sort(key=lambda x: x["distance"])
    return ToolResult(
        name="window_shape_compare",
        success=True,
        data={
            "series_index": sid + 1,
            "method": "dtw" if method == "dtw" else "z_euclidean",
            "n_windows": len(segs),
            "pairs": pairs,
            "nearest_pair": pairs[0] if pairs else None,
        },
    )


def _joint_threshold_events(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    """Count indices where multiple series simultaneously satisfy threshold rules."""
    rules = arguments.get("rules")
    if not isinstance(rules, list) or not rules:
        return ToolResult(
            name="joint_threshold_events",
            success=False,
            data={},
            error="rules must be a non-empty list of {series_index, op, value}",
        )
    mode = str(arguments.get("mode", "and")).strip().lower()
    start = arguments.get("start")
    end = arguments.get("end")
    n = min(len(s) for s in series)
    lo = 0 if start is None else max(0, int(start))
    hi = n - 1 if end is None else min(n - 1, int(end))
    parsed = []
    for rule in rules:
        if not isinstance(rule, dict):
            return ToolResult(name="joint_threshold_events", success=False, data={}, error="invalid rule")
        sid = _parse_one_series_token(rule.get("series_index", 1), len(series))
        op = str(rule.get("op", ">")).strip()
        val = float(rule["value"])
        parsed.append((sid, op, val))

    def _ok(v: float, op: str, thr: float) -> bool:
        if op in {">", "gt"}:
            return v > thr
        if op in {">=", "ge"}:
            return v >= thr
        if op in {"<", "lt"}:
            return v < thr
        if op in {"<=", "le"}:
            return v <= thr
        if op in {"==", "eq"}:
            return abs(v - thr) <= 1e-9
        raise ValueError(f"unsupported op {op}")

    hits = []
    for i in range(lo, hi + 1):
        flags = [_ok(float(series[sid][i]), op, thr) for sid, op, thr in parsed]
        if (mode == "and" and all(flags)) or (mode == "or" and any(flags)):
            hits.append(i)
    return ToolResult(
        name="joint_threshold_events",
        success=True,
        data={
            "mode": mode,
            "start": lo,
            "end": hi,
            "n_events": len(hits),
            "indices": hits[:50],
            "rules": [{"series_index": s + 1, "op": o, "value": v} for s, o, v in parsed],
        },
    )


def _crossing_summary(arr: np.ndarray, threshold: Optional[float] = None, offset: int = 0) -> Dict[str, Any]:
    """Count transitions across a threshold; equality belongs to the lower side."""
    if arr.size == 0:
        raise ValueError("crossing_points requires at least one value")
    value = float(np.median(arr) if threshold is None else threshold)
    below_or_equal = arr <= value
    local = np.flatnonzero(below_or_equal[:-1] != below_or_equal[1:]) + 1
    return {
        "threshold": value,
        "n_crossings": int(local.size),
        "crossing_indices": [int(i + offset) for i in local],
        "n_below_or_equal": int(np.sum(below_or_equal)),
        "n_above": int(np.sum(~below_or_equal)),
    }


def _crossing_points(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    mode = str(arguments.get("threshold", arguments.get("threshold_mode", "median"))).strip().lower()
    if mode not in {"median", "mean", "zero", "0", "value"}:
        raise ValueError("threshold mode must be median, mean, zero, or value")
    threshold_scope = str(arguments.get("threshold_scope", "series")).strip().lower()
    if threshold_scope not in {"series", "window"}:
        raise ValueError("threshold_scope must be series or window")
    explicit = arguments.get("threshold_value")
    if mode == "value" and explicit is None:
        raise ValueError("threshold_value is required when threshold mode is value")
    items = []
    for sid, arr in _selected_arrays(arguments, series):
        sub, start, end = _slice_window(arr, arguments)
        threshold_values = arr if threshold_scope == "series" else sub
        if explicit is not None:
            threshold = float(explicit)
            mode_used = "value"
        elif mode == "mean":
            threshold = float(np.mean(threshold_values))
            mode_used = "mean"
        elif mode in {"zero", "0"}:
            threshold = 0.0
            mode_used = "zero"
        else:
            threshold = float(np.median(threshold_values))
            mode_used = "median"
        item = {
            "series_index": sid,
            "start": 0 if start is None else start,
            "end": len(arr) - 1 if end is None else end,
            "threshold_mode": mode_used,
            "threshold_scope": "explicit" if explicit is not None else threshold_scope,
            "equality_rule": "values equal to the threshold are on the lower-or-equal side",
            **_crossing_summary(sub, threshold, 0 if start is None else start),
        }
        items.append(item)
    return _pack_per_series("crossing_points", items)


def _safe_shape_moments(arr: np.ndarray) -> Tuple[float, float]:
    centered = arr - np.mean(arr)
    std = float(np.std(arr))
    if std < _VARIANCE_EPS:
        return 0.0, 0.0
    z = centered / std
    return float(np.mean(z**3)), float(np.mean(z**4) - 3.0)


def _histogram_entropy(arr: np.ndarray, bins: Optional[int] = None) -> Tuple[float, float, int]:
    if arr.size < 2 or float(np.ptp(arr)) < _VARIANCE_EPS:
        return 0.0, 0.0, 1
    n_bins = int(bins or max(2, min(20, round(np.sqrt(arr.size)))))
    counts, _ = np.histogram(arr, bins=n_bins)
    probs = counts[counts > 0].astype(float)
    probs /= np.sum(probs)
    entropy = float(-np.sum(probs * np.log2(probs)))
    normalized = float(entropy / np.log2(n_bins)) if n_bins > 1 else 0.0
    return entropy, normalized, n_bins


def _spectral_entropy(arr: np.ndarray) -> Tuple[float, float, int]:
    """Shannon entropy of the non-DC power spectrum, normalized to [0, 1]."""
    if arr.size < 4 or float(np.std(arr)) < _VARIANCE_EPS:
        return 0.0, 0.0, max(0, arr.size // 2)
    power = np.abs(np.fft.rfft(arr - np.mean(arr))) ** 2
    power = power[1:]
    total = float(np.sum(power))
    if power.size < 2 or total < _VARIANCE_EPS:
        return 0.0, 0.0, int(power.size)
    probs = power[power > 0] / total
    entropy = float(-np.sum(probs * np.log2(probs)))
    normalized = float(entropy / np.log2(power.size))
    return entropy, max(0.0, min(1.0, normalized)), int(power.size)


def _chunk_variability(arr: np.ndarray, chunk_size: Optional[int] = None) -> Tuple[float, float, int]:
    size = int(chunk_size or max(4, len(arr) // 10))
    size = max(2, min(size, len(arr)))
    chunks = [arr[i : i + size] for i in range(0, len(arr), size) if len(arr[i : i + size]) >= 2]
    if len(chunks) < 2:
        return 0.0, 0.0, len(chunks)
    means = np.asarray([np.mean(c) for c in chunks], dtype=float)
    variances = np.asarray([np.var(c) for c in chunks], dtype=float)
    return float(np.var(means)), float(np.var(variances)), len(chunks)


def _arch_lm_stat(
    arr: np.ndarray, lags: int = 5
) -> Tuple[Optional[float], Optional[float], Optional[float], int, str]:
    """Regress x_t^2 on lagged squared values and return LM=nR², R², and p-value."""
    n = len(arr)
    p = max(1, min(int(lags), max(1, n // 5)))
    if n <= p + 2:
        return None, None, None, p, "insufficient_points"
    y = arr**2
    target = y[p:]
    x = np.column_stack([np.ones(len(target))] + [y[p - lag : n - lag] for lag in range(1, p + 1)])
    beta, *_ = np.linalg.lstsq(x, target, rcond=None)
    fitted = x @ beta
    ss_tot = float(np.sum((target - np.mean(target)) ** 2))
    if ss_tot < _VARIANCE_EPS:
        return 0.0, 0.0, 1.0, p, "constant_squared_values"
    r2 = max(0.0, min(1.0, 1.0 - float(np.sum((target - fitted) ** 2)) / ss_tot))
    lm = float(len(target) * r2)
    try:
        from scipy.stats import chi2

        pvalue = float(chi2.sf(lm, p))
        status = "ok"
    except ImportError:
        pvalue = None
        status = "pvalue_unavailable_scipy_missing"
    return lm, r2, pvalue, p, status


def _advanced_features(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    items = []
    for sid, arr in _selected_arrays(arguments, series):
        sub, start, end = _slice_window(arr, arguments)
        q1, median, q3 = (float(x) for x in np.percentile(sub, [25, 50, 75]))
        skewness, excess_kurtosis = _safe_shape_moments(sub)
        histogram_entropy, normalized_histogram_entropy, bins = _histogram_entropy(sub, arguments.get("bins"))
        spectral_entropy, normalized_spectral_entropy, spectral_bins = _spectral_entropy(sub)
        stability, lumpiness, n_chunks = _chunk_variability(sub, arguments.get("chunk_size"))
        lm, lm_r2, lm_pvalue, lm_lags, lm_status = _arch_lm_stat(sub, int(arguments.get("arch_lags", 5)))
        crossing_threshold = float(np.median(arr))
        items.append(
            {
                "series_index": sid,
                "start": 0 if start is None else start,
                "end": len(arr) - 1 if end is None else end,
                "q1": q1,
                "median": median,
                "q3": q3,
                "iqr": q3 - q1,
                "skewness": skewness,
                "excess_kurtosis": excess_kurtosis,
                "histogram_entropy": histogram_entropy,
                "normalized_histogram_entropy": normalized_histogram_entropy,
                "entropy_bins": bins,
                "spectral_entropy": spectral_entropy,
                "normalized_spectral_entropy": normalized_spectral_entropy,
                "spectral_bins": spectral_bins,
                "normalized_entropy": normalized_spectral_entropy,
                "entropy_definition": "normalized non-DC power spectral entropy",
                "stability": stability,
                "lumpiness": lumpiness,
                "n_chunks": n_chunks,
                "arch_lm_stat": lm,
                "arch_lm_r2": lm_r2,
                "arch_lm_pvalue": lm_pvalue,
                "arch_lags": lm_lags,
                "arch_status": lm_status,
                **_crossing_summary(sub, crossing_threshold, 0 if start is None else start),
            }
        )
    return _pack_per_series("advanced_features", items)


def _counterfactual_summary(arr: np.ndarray) -> Dict[str, Any]:
    peaks, troughs = _count_peaks_troughs(arr)
    q1, median, q3 = (float(x) for x in np.percentile(arr, [25, 50, 75]))
    slope = float(np.polyfit(np.arange(len(arr), dtype=float), arr, 1)[0]) if len(arr) >= 2 else 0.0
    _, normalized_spectral_entropy, _ = _spectral_entropy(arr)
    if len(arr) >= 4 and float(np.std(arr)) >= _VARIANCE_EPS:
        power = np.abs(np.fft.rfft(arr - np.mean(arr)))
        power[0] = 0.0
        dominant_bin = int(np.argmax(power))
        dominant_period = float(len(arr) / dominant_bin) if dominant_bin > 0 else None
    else:
        dominant_period = None
    summary = {
        "length": int(len(arr)),
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "median": median,
        "q1": q1,
        "q3": q3,
        "iqr": q3 - q1,
        "min": float(np.min(arr)),
        "min_index": int(np.argmin(arr)),
        "max": float(np.max(arr)),
        "max_index": int(np.argmax(arr)),
        "slope": slope,
        "start_value": float(arr[0]),
        "end_value": float(arr[-1]),
        "n_peaks": len(peaks),
        "n_troughs": len(troughs),
        "dominant_period": dominant_period,
        "normalized_spectral_entropy": normalized_spectral_entropy,
        **_crossing_summary(arr, median),
    }
    return summary


def _parse_operations(arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    raw = arguments.get("operations")
    if raw is None:
        raw = [arguments.get("operation") or arguments]
    if isinstance(raw, dict):
        raw = [raw]
    if not isinstance(raw, list) or not raw or not all(isinstance(x, dict) for x in raw):
        raise ValueError("operations must be a non-empty list of operation objects")
    return [dict(x) for x in raw]


def _cf_position(value: Any, n: int, index_base: int, name: str) -> int:
    pos = int(value) - (1 if index_base == 1 else 0)
    if not 0 <= pos < n:
        valid = f"1..{n}" if index_base == 1 else f"0..{n - 1}"
        raise ValueError(f"{name} out of range: {value!r} (valid {valid})")
    return pos


def _cf_interval(
    op: Dict[str, Any],
    n: int,
    index_base: int,
    *,
    start_key: str = "start",
    end_key: str = "end",
) -> Tuple[int, int]:
    default_start = 1 if index_base == 1 else 0
    default_end = n if index_base == 1 else n - 1
    start = _cf_position(op.get(start_key, default_start), n, index_base, start_key)
    end = _cf_position(op.get(end_key, default_end), n, index_base, end_key)
    if end < start:
        start, end = end, start
    return start, end


def _counterfactual_simulate(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    idx = _parse_one_series_token(arguments.get("series_index", 1), len(series))
    original = np.asarray(series[idx], dtype=float)
    modified = original.copy()
    applied = []
    for op in _parse_operations(arguments):
        kind = str(op.get("op", op.get("type", ""))).strip().lower()
        index_base = int(op.get("index_base", arguments.get("index_base", 0)))
        if kind in {"set_value", "replace_value"}:
            pos = _cf_position(op["index"], len(modified), index_base, "index")
            modified[pos] = float(op["value"])
        elif kind in {"shift", "scale", "scale_values", "scale_std", "cap"}:
            start, end = _cf_interval(op, len(modified), index_base)
            segment = modified[start : end + 1]
            if kind == "shift":
                segment += float(op.get("amount", op.get("value", 0.0)))
            elif kind in {"scale", "scale_values"}:
                segment *= float(op.get("factor", 1.0))
            elif kind == "scale_std":
                center = float(np.mean(segment))
                segment[:] = center + float(op.get("factor", 1.0)) * (segment - center)
            else:
                if op.get("min") is not None:
                    segment[:] = np.maximum(segment, float(op["min"]))
                if op.get("max") is not None:
                    segment[:] = np.minimum(segment, float(op["max"]))
        elif kind == "replace_segment":
            if "start" not in op or "end" not in op:
                raise ValueError("replace_segment requires start and end")
            start, end = _cf_interval(op, len(modified), index_base)
            source_idx = _parse_one_series_token(op.get("source_series_index", idx + 1), len(series))
            source = np.asarray(series[source_idx], dtype=float)
            source_default_start = 1 if index_base == 1 else 0
            source_start = _cf_position(
                op.get("source_start", source_default_start), len(source), index_base, "source_start"
            )
            if "source_end" in op:
                source_end = _cf_position(op["source_end"], len(source), index_base, "source_end")
            else:
                source_end = min(len(source) - 1, source_start + end - start)
            if source_end < source_start:
                source_start, source_end = source_end, source_start
            replacement = source[source_start : source_end + 1]
            target_len = end - start + 1
            if len(replacement) != target_len:
                if len(replacement) < 2:
                    replacement = np.repeat(replacement, target_len)
                else:
                    replacement = np.interp(
                        np.linspace(0, len(replacement) - 1, target_len),
                        np.arange(len(replacement)),
                        replacement,
                    )
            modified[start : end + 1] = replacement
        elif kind == "extrapolate_slope":
            interval_op = dict(op)
            if "start" not in interval_op and "from_index" in interval_op:
                interval_op["start"] = interval_op["from_index"]
            start, end = _cf_interval(interval_op, len(modified), index_base)
            anchor = max(0, min(start - 1, len(modified) - 1))
            slope = op.get("slope")
            if slope is None:
                if "fit_start" in op:
                    fit_start = _cf_position(op["fit_start"], len(original), index_base, "fit_start")
                else:
                    fit_start = max(0, start - 10)
                if "fit_end" in op:
                    fit_end = _cf_position(op["fit_end"], len(original), index_base, "fit_end")
                else:
                    fit_end = anchor
                if fit_end < fit_start:
                    fit_start, fit_end = fit_end, fit_start
                fit = original[fit_start : fit_end + 1]
                slope = float(np.polyfit(np.arange(len(fit)), fit, 1)[0]) if len(fit) >= 2 else 0.0
            for pos in range(start, end + 1):
                modified[pos] = modified[anchor] + float(slope) * (pos - anchor)
            op["resolved_slope"] = float(slope)
        else:
            raise ValueError(
                "unsupported counterfactual op; use set_value, replace_segment, shift, "
                "scale_values, scale_std, cap, or extrapolate_slope"
            )
        applied.append(op)

    before = _counterfactual_summary(original)
    after = _counterfactual_summary(modified)
    changed_idx = np.flatnonzero(~np.isclose(original, modified, rtol=1e-12, atol=1e-12)).tolist()
    numeric_delta = {
        key: float(after[key] - before[key])
        for key in ("mean", "std", "median", "iqr", "min", "max", "slope", "n_crossings", "n_peaks", "n_troughs")
    }
    if len(changed_idx) <= 20:
        preview_idx = changed_idx
    else:
        preview_idx = changed_idx[:10] + changed_idx[-10:]
    preview = [
        {"index": i, "before": float(original[i]), "after": float(modified[i])}
        for i in preview_idx
    ]
    report_raw = arguments.get("report_indices", [])
    if not isinstance(report_raw, (list, tuple)):
        report_raw = [report_raw]
    report_indices = [
        _cf_position(value, len(modified), int(arguments.get("index_base", 0)), "report_index")
        for value in report_raw
    ]
    reported_values = [
        {"index": i, "before": float(original[i]), "after": float(modified[i])} for i in report_indices
    ]
    original_median = float(np.median(original))
    return ToolResult(
        name="counterfactual_simulate",
        success=True,
        data={
            "series_index": idx + 1,
            "operations": applied,
            "n_changed": len(changed_idx),
            "changed_index_range": [min(changed_idx), max(changed_idx)] if changed_idx else None,
            "changed_preview": preview,
            "reported_values": reported_values,
            "before": before,
            "after": after,
            "after_crossings_at_original_median": _crossing_summary(modified, original_median),
            "delta": numeric_delta,
        },
    )


def _event_indices(arr: np.ndarray, kind: str) -> List[int]:
    peaks, troughs = _count_peaks_troughs(arr)
    if kind == "peaks":
        return peaks
    if kind == "troughs":
        return troughs
    return sorted(peaks + troughs)


def _extrema_align(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    if len(series) < 2:
        return ToolResult(name="extrema_align", success=False, data={}, error="Need >=2 series")
    i1 = _parse_one_series_token(arguments.get("series_index_1", 1), len(series))
    i2 = _parse_one_series_token(arguments.get("series_index_2", 2), len(series))
    kind = str(arguments.get("kind", "both")).lower()
    if kind not in {"both", "peaks", "troughs"}:
        raise ValueError("kind must be both, peaks, or troughs")

    def get_interval(arr: np.ndarray, key: str) -> Tuple[np.ndarray, int, int]:
        raw = arguments.get(key)
        if isinstance(raw, (list, tuple)) and len(raw) >= 2:
            start, end = int(raw[0]), int(raw[1])
        else:
            start = int(arguments.get("start", 0))
            end = int(arguments.get("end", len(arr) - 1))
        start, end = max(0, min(start, len(arr) - 1)), max(0, min(end, len(arr) - 1))
        if end < start:
            start, end = end, start
        return arr[start : end + 1], start, end

    a, a_start, a_end = get_interval(np.asarray(series[i1], dtype=float), "interval_1")
    b, b_start, b_end = get_interval(np.asarray(series[i2], dtype=float), "interval_2")
    events_a = _event_indices(a, kind)
    events_b = _event_indices(b, kind)
    norm_a = [x / max(len(a) - 1, 1) for x in events_a]
    norm_b = [x / max(len(b) - 1, 1) for x in events_b]
    nearest = []
    if norm_a and norm_b:
        for local_a, pos_a in zip(events_a, norm_a):
            j = int(np.argmin(np.abs(np.asarray(norm_b) - pos_a)))
            nearest.append(
                {
                    "series_1_index": int(a_start + local_a),
                    "series_2_index": int(b_start + events_b[j]),
                    "normalized_position_delta": float(norm_b[j] - pos_a),
                }
            )
    mean_abs_delta = (
        float(np.mean([abs(x["normalized_position_delta"]) for x in nearest])) if nearest else None
    )

    max_lag = max(0, int(arguments.get("max_lag", min(20, max(len(a), len(b)) // 4))))
    m = min(len(a), len(b))
    lag_scores = []
    for lag in range(-min(max_lag, m - 1), min(max_lag, m - 1) + 1):
        shifted_a = {x + lag for x in events_a}
        set_b = set(events_b)
        matches = len(shifted_a.intersection(set_b))
        union = len(shifted_a.union(set_b))
        score = float(matches / union) if union else None
        coverage = float(matches / max(len(events_a), len(events_b))) if events_a and events_b else 0.0
        lag_scores.append(
            {
                "lag": lag,
                "event_jaccard": score,
                "matches": matches,
                "match_coverage": coverage,
            }
        )
    valid_lags = [x for x in lag_scores if x["event_jaccard"] is not None]
    best_lag = (
        max(valid_lags, key=lambda x: (x["event_jaccard"], x["match_coverage"], x["matches"], -abs(x["lag"])))
        if valid_lags
        else None
    )
    global_max_delta = int((b_start + int(np.argmax(b))) - (a_start + int(np.argmax(a))))
    global_min_delta = int((b_start + int(np.argmin(b))) - (a_start + int(np.argmin(a))))
    return ToolResult(
        name="extrema_align",
        success=True,
        data={
            "series_index_1": i1 + 1,
            "series_index_2": i2 + 1,
            "interval_1": [a_start, a_end],
            "interval_2": [b_start, b_end],
            "kind": kind,
            "events_1": [int(a_start + x) for x in events_a],
            "events_2": [int(b_start + x) for x in events_b],
            "nearest_event_pairs": nearest,
            "mean_abs_normalized_position_delta": mean_abs_delta,
            "best_event_lag": None if best_lag is None else best_lag["lag"],
            "best_event_jaccard": None if best_lag is None else best_lag["event_jaccard"],
            "best_event_match_coverage": None if best_lag is None else best_lag["match_coverage"],
            "alignment_status": "ok" if best_lag is not None else "insufficient_extrema",
            "global_max_index_delta": global_max_delta,
            "global_min_index_delta": global_min_delta,
            "lag_scores": lag_scores,
        },
    )


def _lag_corr_scan(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    if len(series) < 2:
        return ToolResult(name="lag_corr_scan", success=False, data={}, error="Need >=2 series")
    i1 = _parse_one_series_token(arguments.get("series_index_1", 1), len(series))
    i2 = _parse_one_series_token(arguments.get("series_index_2", 2), len(series))
    a, _, _ = _slice_window(np.asarray(series[i1], dtype=float), arguments)
    b, _, _ = _slice_window(np.asarray(series[i2], dtype=float), arguments)
    m = min(len(a), len(b))
    if m < 3:
        return ToolResult(name="lag_corr_scan", success=False, data={}, error="insufficient overlap")
    default_min_overlap = min(m, max(8, int(np.ceil(0.1 * m))))
    min_overlap = int(arguments.get("min_overlap", default_min_overlap))
    if not 3 <= min_overlap <= m:
        raise ValueError(f"min_overlap must be between 3 and {m}")
    max_lag = max(0, min(int(arguments.get("max_lag", min(20, m // 4))), m - min_overlap))
    scans = []
    for lag in range(-max_lag, max_lag + 1):
        corr, err, _ = _cross_lag_corr_arrays(a, b, lag)
        overlap = m - abs(lag)
        pvalue = None
        if corr is not None:
            try:
                from scipy.stats import pearsonr

                if lag < 0:
                    left, right = a[-lag:m], b[: m + lag]
                elif lag > 0:
                    left, right = a[: m - lag], b[lag:m]
                else:
                    left, right = a[:m], b[:m]
                pvalue = float(pearsonr(left, right).pvalue)
            except ImportError:
                pass
        scans.append({"lag": lag, "corr": corr, "pvalue": pvalue, "overlap": overlap, "error": err})
    valid = [x for x in scans if x["corr"] is not None]
    if not valid:
        return ToolResult(name="lag_corr_scan", success=False, data={"lags": scans}, error="all lags failed")
    best = max(
        valid,
        key=lambda x: (
            round(abs(float(x["corr"])), 12),
            x["overlap"],
            -abs(x["lag"]),
        ),
    )
    zero = next((x for x in valid if x["lag"] == 0), None)
    if best["lag"] > 0:
        hint = "series_1_leads_series_2"
    elif best["lag"] < 0:
        hint = "series_2_leads_series_1"
    else:
        hint = "synchronous"
    return ToolResult(
        name="lag_corr_scan",
        success=True,
        data={
            "series_index_1": i1 + 1,
            "series_index_2": i2 + 1,
            "max_lag": max_lag,
            "min_overlap": min_overlap,
            "best_lag": best["lag"],
            "best_corr": best["corr"],
            "best_pvalue": best["pvalue"],
            "best_overlap": best["overlap"],
            "zero_lag_corr": None if zero is None else zero["corr"],
            "lead_lag_hint": hint,
            "causality_warning": "Lead-lag correlation is association, not proof of causality.",
            "lags": scans,
        },
    )


def _z_normalize(arr: np.ndarray) -> np.ndarray:
    std = float(np.std(arr))
    return (arr - np.mean(arr)) / std if std >= _VARIANCE_EPS else arr - np.mean(arr)


def _resample_to(arr: np.ndarray, length: int) -> np.ndarray:
    if len(arr) == length:
        return arr.copy()
    if len(arr) == 1:
        return np.repeat(arr, length)
    return np.interp(np.linspace(0, len(arr) - 1, length), np.arange(len(arr)), arr)


def _dtw_distance(a: np.ndarray, b: np.ndarray) -> Tuple[float, str]:
    try:
        from dtaidistance import dtw

        return float(dtw.distance_fast(a.astype(np.double), b.astype(np.double))), "dtw"
    except ImportError:
        aa, bb = _resample_to(a, max(len(a), len(b))), _resample_to(b, max(len(a), len(b)))
        return float(np.linalg.norm(aa - bb)), "euclidean_fallback"


def _candidate_series(arguments: Dict[str, Any], series: List[List[float]], query_idx: int) -> List[int]:
    raw = arguments.get("candidate_series_indices")
    if raw is None or (isinstance(raw, str) and raw.lower() in {"all", "*"}):
        return [i for i in range(len(series)) if i != query_idx]
    if not isinstance(raw, (list, tuple)):
        raw = [raw]
    out = [_parse_one_series_token(x, len(series)) for x in raw]
    return list(dict.fromkeys(i for i in out if i != query_idx))


def _reverse_match(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    if len(series) < 2:
        return ToolResult(name="reverse_match", success=False, data={}, error="Need query and candidates")
    query_idx = _parse_one_series_token(arguments.get("query_series_index", 1), len(series))
    candidates = _candidate_series(arguments, series, query_idx)
    if not candidates:
        return ToolResult(name="reverse_match", success=False, data={}, error="No candidate series remain")
    query = _z_normalize(np.asarray(series[query_idx], dtype=float))
    method = str(arguments.get("method", "dtw")).lower()
    if method not in {"dtw", "euclidean"}:
        raise ValueError("method must be dtw or euclidean")
    items = []
    for idx in candidates:
        candidate = _z_normalize(np.asarray(series[idx], dtype=float)[::-1])
        if method == "dtw":
            distance, used = _dtw_distance(query, candidate)
            distance = float(distance / max(np.sqrt(len(query) + len(candidate)), 1.0))
        else:
            n = max(len(query), len(candidate))
            distance = float(np.linalg.norm(_resample_to(query, n) - _resample_to(candidate, n)) / np.sqrt(n))
            used = "z_euclidean"
        items.append({"series_index": idx + 1, "reverse_distance": distance, "method_used": used})
    items.sort(key=lambda x: x["reverse_distance"])
    margin = float(items[1]["reverse_distance"] - items[0]["reverse_distance"]) if len(items) >= 2 else None
    return ToolResult(
        name="reverse_match",
        success=True,
        data={
            "query_series_index": query_idx + 1,
            "ranking": items,
            "nearest": items[0],
            "winner_margin": margin,
        },
    )


def _robust_shape_match(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    if len(series) < 2:
        return ToolResult(name="robust_shape_match", success=False, data={}, error="Need query and candidates")
    query_idx = _parse_one_series_token(arguments.get("query_series_index", 1), len(series))
    candidates = _candidate_series(arguments, series, query_idx)
    if not candidates:
        return ToolResult(name="robust_shape_match", success=False, data={}, error="No candidate series remain")
    smooth_window = int(arguments.get("smooth_window", 5))
    if smooth_window < 1:
        raise ValueError("smooth_window must be >= 1")
    winsor = float(arguments.get("winsor_percentile", 2.0))
    if not np.isfinite(winsor) or not 0.0 <= winsor < 50.0:
        raise ValueError("winsor_percentile must be finite and in [0, 50)")

    def prep(arr: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        clean = arr.copy()
        if winsor > 0 and len(clean) >= 4:
            lo, hi = np.percentile(clean, [winsor, 100 - winsor])
            clean = np.clip(clean, lo, hi)
        window = min(smooth_window, len(clean))
        smooth = np.convolve(clean, np.ones(window) / window, mode="same")
        return _z_normalize(clean), _z_normalize(smooth)

    query_raw, query_smooth = prep(np.asarray(series[query_idx], dtype=float))
    items = []
    for idx in candidates:
        cand_raw, cand_smooth = prep(np.asarray(series[idx], dtype=float))
        n = max(len(query_raw), len(cand_raw))
        q, c = _resample_to(query_raw, n), _resample_to(cand_raw, n)
        qs, cs = _resample_to(query_smooth, n), _resample_to(cand_smooth, n)
        raw_distance = float(np.linalg.norm(q - c) / np.sqrt(n))
        smooth_distance = float(np.linalg.norm(qs - cs) / np.sqrt(n))
        corr, _ = _safe_corr(q, c)
        corr_distance = 1.0 - float(corr) if corr is not None else 2.0
        dtw_distance, dtw_used = _dtw_distance(query_raw, cand_raw)
        dtw_normalized = float(dtw_distance / max(np.sqrt(len(query_raw) + len(cand_raw)), 1.0))
        score = float(np.median([raw_distance, smooth_distance, corr_distance, dtw_normalized]))
        items.append(
            {
                "series_index": idx + 1,
                "robust_score": score,
                "raw_z_distance": raw_distance,
                "smoothed_z_distance": smooth_distance,
                "correlation_distance": corr_distance,
                "dtw_normalized_distance": dtw_normalized,
                "dtw_method_used": dtw_used,
            }
        )
    items.sort(key=lambda x: x["robust_score"])
    margin = float(items[1]["robust_score"] - items[0]["robust_score"]) if len(items) >= 2 else None
    return ToolResult(
        name="robust_shape_match",
        success=True,
        data={
            "query_series_index": query_idx + 1,
            "smooth_window": smooth_window,
            "winsor_percentile": winsor,
            "ranking": items,
            "nearest": items[0] if items else None,
            "winner_margin": margin,
        },
    )


def _strict_bool(value: Any, name: str = "expected") -> bool:
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (int, np.integer)) and int(value) in {0, 1}:
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "yes", "1"}:
            return True
        if normalized in {"false", "no", "0"}:
            return False
    raise ValueError(f"{name} must be a boolean or true/false string")


def _bounded_numeric_claim(observed: float, claim: Dict[str, Any], expected: Any) -> bool:
    if claim.get("min") is not None and observed < float(claim["min"]):
        return False
    if claim.get("max") is not None and observed > float(claim["max"]):
        return False
    if claim.get("min") is not None or claim.get("max") is not None:
        return True
    if expected is None:
        raise ValueError("numeric claim requires expected, min, or max")
    tolerance = float(claim.get("tolerance", 0.0))
    return abs(observed - float(expected)) <= tolerance


def _caption_claim_observation(claim: Dict[str, Any], arr: np.ndarray) -> Tuple[Any, bool, str]:
    kind = str(claim.get("type", claim.get("claim_type", ""))).strip().lower()
    expected = claim.get("expected", claim.get("value"))
    if kind == "trend":
        if expected is None:
            raise ValueError("trend claim requires expected")
        slope = float(np.polyfit(np.arange(len(arr)), arr, 1)[0]) if len(arr) >= 2 else 0.0
        tol = max(float(np.std(arr)) * 1e-3, 1e-9)
        observed = "upward" if slope > tol else "downward" if slope < -tol else "flat"
        return {"direction": observed, "slope": slope}, str(expected).lower() == observed, "segment_trend"
    if kind in {"period", "dominant_period"}:
        if expected is None:
            raise ValueError("period claim requires expected")
        if len(arr) < 4:
            return None, False, "fft_period"
        centered = arr - np.mean(arr)
        power = np.abs(np.fft.rfft(centered))
        power[0] = 0
        k = int(np.argmax(power))
        observed = float(len(arr) / k) if k > 0 else None
        tolerance = float(claim.get("tolerance", max(1.0, 0.2 * float(expected))))
        return observed, observed is not None and abs(observed - float(expected)) <= tolerance, "fft_period"
    if kind in {"step_levels", "plateau_levels", "plateau_runs"}:
        stats = _step_level_stats(arr)
        observed = stats["n_plateau_runs"] if kind == "plateau_runs" else stats["n_unique_levels"]
        return observed, _bounded_numeric_claim(float(observed), claim, expected), "step_levels"
    if kind in {"n_peaks", "peaks"}:
        observed = len(_count_peaks_troughs(arr)[0])
        return observed, _bounded_numeric_claim(float(observed), claim, expected), "local_extrema"
    if kind in {"n_troughs", "troughs"}:
        observed = len(_count_peaks_troughs(arr)[1])
        return observed, _bounded_numeric_claim(float(observed), claim, expected), "local_extrema"
    if kind in {"volatility", "std"}:
        observed = float(np.std(arr))
        if claim.get("min") is not None or claim.get("max") is not None:
            passed = (claim.get("min") is None or observed >= float(claim["min"])) and (
                claim.get("max") is None or observed <= float(claim["max"])
            )
        else:
            if expected is None:
                raise ValueError("volatility claim requires expected, min, or max")
            passed = abs(observed - float(expected)) <= float(
                claim.get("tolerance", 0.1 * max(abs(float(expected)), 1.0))
            )
        return observed, passed, "describe_series"
    scalar_getters = {
        "min": lambda x: float(np.min(x)),
        "max": lambda x: float(np.max(x)),
        "range": lambda x: float(np.ptp(x)),
        "mean": lambda x: float(np.mean(x)),
        "median": lambda x: float(np.median(x)),
        "start": lambda x: float(x[0]),
        "end": lambda x: float(x[-1]),
        "min_index": lambda x: float(np.argmin(x)),
        "max_index": lambda x: float(np.argmax(x)),
    }
    if kind in scalar_getters:
        observed = scalar_getters[kind](arr)
        return observed, _bounded_numeric_claim(observed, claim, expected), "describe_series"
    if kind in {"constant", "is_constant"}:
        observed = float(np.ptp(arr)) <= float(claim.get("tolerance", 1e-9))
        return observed, observed == _strict_bool(expected), "describe_series"
    if kind in {"anomaly", "has_anomaly"}:
        std = float(np.std(arr))
        count = 0 if std < _VARIANCE_EPS else int(np.sum(np.abs((arr - np.mean(arr)) / std) >= float(claim.get("z_threshold", 3.0))))
        return count, (count > 0) == _strict_bool(expected), "anomaly_detect"
    if kind in {"stationary", "stationarity"}:
        try:
            from statsmodels.tsa.stattools import adfuller

            pvalue = float(adfuller(arr, autolag="AIC")[1])
            observed = pvalue < 0.05
            return {
                "stationary": observed,
                "pvalue": pvalue,
            }, observed == _strict_bool(expected), "adf_stationarity"
        except ImportError as exc:
            raise ValueError("stationarity claim unavailable: statsmodels is not installed") from exc
        except Exception as exc:
            raise ValueError(f"stationarity claim could not be estimated: {exc}") from exc
    if kind in {"value_band", "baseline_band", "oscillates_between"}:
        lo = claim.get("min", claim.get("low"))
        hi = claim.get("max", claim.get("high"))
        if lo is None or hi is None:
            raise ValueError("value_band claim requires min and max")
        lo_f, hi_f = float(lo), float(hi)
        frac = float(np.mean((arr >= lo_f) & (arr <= hi_f)))
        min_frac = float(claim.get("min_fraction", 0.8))
        observed = {"in_band_fraction": frac, "min": float(np.min(arr)), "max": float(np.max(arr))}
        return observed, frac >= min_frac, "describe_series"
    if kind in {"spike", "has_spike"}:
        std = float(np.std(arr))
        z_thr = float(claim.get("z_threshold", 3.0))
        if std < _VARIANCE_EPS:
            count = 0
        else:
            count = int(np.sum(np.abs((arr - np.mean(arr)) / std) >= z_thr))
        near = claim.get("near_index", claim.get("index"))
        if near is not None:
            tol = int(claim.get("tolerance", 3))
            near_i = int(near)
            peaks, _ = _count_peaks_troughs(arr)
            hit = any(abs(p - near_i) <= tol and (std < _VARIANCE_EPS or abs((arr[p] - np.mean(arr)) / std) >= z_thr * 0.7) for p in peaks)
            return {"n_spikes": count, "near_hit": hit}, hit == _strict_bool(expected if expected is not None else True), "anomaly_detect"
        return count, (count > 0) == _strict_bool(expected if expected is not None else True), "anomaly_detect"
    if kind in {"zero_gap", "has_zero_gap"}:
        tol = float(claim.get("tolerance", 1e-9))
        zeroish = np.abs(arr) <= tol
        # longest consecutive run of near-zeros
        best = cur = 0
        for flag in zeroish:
            if flag:
                cur += 1
                best = max(best, cur)
            else:
                cur = 0
        min_len = int(claim.get("min_length", claim.get("expected", 2) or 2))
        observed = {"longest_zero_run": best}
        return observed, best >= min_len, "describe_series"
    if kind in {"peak_at", "peaks_near"}:
        targets = claim.get("indices", claim.get("expected", []))
        if not isinstance(targets, (list, tuple)):
            targets = [targets]
        tol = int(claim.get("tolerance", 2))
        peaks, _ = _count_peaks_troughs(arr)
        hits = []
        for t in targets:
            ti = int(t)
            hits.append(any(abs(p - ti) <= tol for p in peaks))
        observed = {"targets": [int(t) for t in targets], "hits": hits, "peak_idx": peaks[:30]}
        return observed, all(hits) if hits else False, "local_extrema"
    if kind in {"drop_magnitude", "dramatic_drop"}:
        # max peak-to-subsequent-trough drop
        peaks, troughs = _count_peaks_troughs(arr)
        drop = 0.0
        for p in peaks:
            later = [t for t in troughs if t > p]
            if later:
                drop = max(drop, float(arr[p] - arr[later[0]]))
        # also consider global max-to-later-min
        imax = int(np.argmax(arr))
        if imax < len(arr) - 1:
            drop = max(drop, float(arr[imax] - np.min(arr[imax:])))
        min_drop = claim.get("min", expected)
        if min_drop is None:
            raise ValueError("drop_magnitude claim requires min or expected")
        return drop, drop >= float(min_drop), "local_extrema"
    if kind in {"high_freq", "high_frequency", "high_freq_ratio"}:
        if len(arr) < 8:
            return 0.0, False, "fft_period"
        centered = arr - np.mean(arr)
        power = np.abs(np.fft.rfft(centered)) ** 2
        power[0] = 0.0
        freqs = np.fft.rfftfreq(len(arr))
        total = float(np.sum(power)) + 1e-12
        # high-freq: periods shorter than length/8
        mask = freqs >= (8.0 / max(len(arr), 1))
        ratio = float(np.sum(power[mask]) / total)
        min_ratio = float(claim.get("min", expected if expected is not None else 0.35))
        return ratio, ratio >= min_ratio, "fft_period"
    if kind in {"reaching_up_to", "reaches"}:
        if expected is None and claim.get("max") is None:
            raise ValueError("reaching_up_to requires expected/max")
        target = float(expected if expected is not None else claim.get("max"))
        tol = float(claim.get("tolerance", 0.05 * max(abs(target), 1.0)))
        observed = float(np.max(arr))
        return observed, abs(observed - target) <= tol or observed >= target - tol, "describe_series"
    raise ValueError(f"unsupported caption claim type: {kind}")


def _caption_verify(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    claims = arguments.get("claims")
    if not isinstance(claims, list) or not claims or not all(isinstance(x, dict) for x in claims):
        raise ValueError("claims must be a non-empty list of structured claim objects")
    raw_candidates = arguments.get("candidate_series_indices", arguments.get("series_index", "all"))
    selector_args = {"series_index": raw_candidates}
    selected = _selected_arrays(selector_args, series)
    candidates_out = []
    for sid, full in selected:
        results = []
        for claim in claims:
            target = claim.get("series_index")
            if target is not None and _parse_one_series_token(target, len(series)) + 1 != sid:
                continue
            arr, start, end = _slice_window(full, claim)
            observed, passed, evidence_tool = _caption_claim_observation(claim, arr)
            results.append(
                {
                    "claim": claim,
                    "observed": observed,
                    "passed": bool(passed),
                    "evidence_tool": evidence_tool,
                    "interval": [0 if start is None else start, len(full) - 1 if end is None else end],
                }
            )
        passed_count = sum(int(x["passed"]) for x in results)
        candidates_out.append(
            {
                "series_index": sid,
                "claims": results,
                "passed_claims": passed_count,
                "total_claims": len(results),
                "score": float(passed_count / len(results)) if results else 0.0,
            }
        )
    candidates_out.sort(
        key=lambda x: (
            x["total_claims"] == 0,
            -x["score"],
            -x["passed_claims"],
            -x["total_claims"],
            x["series_index"],
        )
    )
    applicable = [x for x in candidates_out if x["total_claims"] > 0]
    if not applicable:
        return ToolResult(
            name="caption_verify",
            success=False,
            data={"candidates": candidates_out},
            error="No claims apply to any selected candidate",
        )
    return ToolResult(
        name="caption_verify",
        success=True,
        data={
            "candidates": candidates_out,
            "best_match": applicable[0],
        },
    )


_SERIES_INDEX_SCHEMA = {
    "series_index": "int|list|'all'|str (1-based; default=all if multi)",
    "start": "optional inclusive start index",
    "end": "optional inclusive end index",
}


_SERIES_INDEX_WITH_QUERY = {
    **_SERIES_INDEX_SCHEMA,
    "index": "optional int; if set, classify that index (global_extrema)",
    "index_base": "0 (default) or 1",
}

# Role sets tuned against MMTS-Bench task coverage (2424 samples).
_HOMO = ["short", "medium", "long"]
_CORE = [*_HOMO, "structure", "reasoning"]
_ALL = [*_CORE, "matching", "alignment"]

# Complete contracts used by agents for goal-driven tool selection.
_TOOL_CONTRACTS: Dict[str, Dict[str, Any]] = {
    "describe_series": {
        "output_schema": {"series": "per-series length and descriptive statistics"},
        "use_when": ["Need an initial global statistical overview or exact basic statistics."],
        "avoid_when": ["The requested fact is local to a window or concerns temporal ordering only."],
        "limitations": ["Global summaries can hide local regimes, timing, and waveform shape."],
    },
    "sliding_stats": {
        "output_schema": {"series": "per-series windowed mean/std aggregates and max_local_std"},
        "use_when": ["Local volatility or rolling level variation must be measured."],
        "avoid_when": ["An exact point value, global extremum, or discrete event count is requested."],
        "limitations": ["Results depend on window size and summarize rather than return every rolling value."],
    },
    "diff_stats": {
        "output_schema": {"series": "per-series first-difference mean/std/range and sign changes"},
        "use_when": ["Changes, roughness, direction switches, or increment variability are relevant."],
        "avoid_when": ["The task asks only for level statistics without temporal differences."],
        "limitations": ["Differencing removes level information and can amplify measurement noise."],
    },
    "local_extrema": {
        "output_schema": {"series": "per-series peak/trough counts and indices"},
        "use_when": ["Turning-point counts or local peak/trough locations are required."],
        "avoid_when": ["Counting plateaus/step levels, or only global extrema, is requested."],
        "limitations": ["Prominence filtering may omit weak extrema; not a substitute for step_levels."],
    },
    "global_extrema": {
        "output_schema": {"series": "per-series max/min values and indices plus optional queried-index flags"},
        "use_when": ["Global extrema values/locations or classification of one index is required."],
        "avoid_when": ["All local turning points or anomaly scores are requested."],
        "limitations": ["Tie breaking uses earliest maximum and latest minimum."],
    },
    "segment_trend": {
        "output_schema": {"series": "per-series slope/direction for a segment"},
        "use_when": ["Direction or slope over a specified segment is the target."],
        "avoid_when": ["Nonlinear trend shape or internal regime changes are the primary target."],
        "limitations": ["Endpoint/linear summaries can miss mid-segment fluctuations."],
    },
    "step_levels": {
        "output_schema": {"series": "unique level count, plateau runs, lengths, and tolerance"},
        "use_when": ["Discrete steps, staircase levels, or plateau runs must be counted."],
        "avoid_when": ["Turning points in a continuously varying signal are requested."],
        "limitations": ["Level counts depend on adaptive tolerance; not interchangeable with local_extrema."],
    },
    "value_at_index": {
        "output_schema": {"series": "selected series, requested index/position, and exact value"},
        "use_when": ["An exact value at a known index is required."],
        "avoid_when": ["The index is unknown or a neighborhood statistic is needed."],
        "limitations": ["Index base must match the question; out-of-range indices fail."],
    },
    "anomaly_detect": {
        "output_schema": {"series": "anomaly count/indices and max absolute z-score"},
        "use_when": ["Point spikes or z-score outliers must be detected in a window."],
        "avoid_when": ["Contextual/collective anomalies or mean-shift change points are intended."],
        "limitations": ["Sensitive to z_threshold and distribution assumptions."],
    },
    "autocorr": {
        "output_schema": {
            "series": "best_lag and full autocorrelation values through max_lag; optional acf_at_lags"
        },
        "use_when": ["Lag dependence or periodic repetition needs independent evidence."],
        "avoid_when": [
            "A single seasonal lag seas_acf1 is the only needed metric — prefer seas_acf.",
            "Strong trend has not been considered or max_lag cannot cover the expected period.",
        ],
        "limitations": [
            "Trend can dominate low lags; ACF alone does not establish waveform type.",
            "Pass lags=[m] when only specific lags are needed.",
        ],
        "produces": ["best_lag", "autocorrelation", "acf_at_lags"],
        "consumes": ["series", "max_lag", "lags"],
        "often_combined_with": ["seas_acf", "fft_period", "stl_strength"],
        "io_concepts": {
            "inputs": "series, max_lag or lags[]",
            "outputs": "best_lag, acf, acf_at_lags",
            "depends": "max_lag should cover candidate period when validating fft_period",
        },
    },
    "seas_acf": {
        "output_schema": {"series": "seas_acf1 at lag m with strength_hint"},
        "use_when": ["InWild seas_acf1 questions with an explicit seasonal lag/frequency (e.g. 26 weeks)."],
        "avoid_when": ["You need a full ACF curve rather than one seasonal lag."],
        "limitations": ["Requires lag < series length; strength_hint is heuristic."],
        "produces": ["seas_acf1", "strength_hint"],
        "consumes": ["series_window", "lag"],
        "often_combined_with": ["autocorr", "stl_strength", "fft_period"],
    },
    "nonlinearity_terasvirta": {
        "output_schema": {"series": "nonlinearity=10*T_stat/N and raw Terasvirta statistic"},
        "use_when": ["InWild nonlinearity / Terasvirta questions."],
        "avoid_when": ["Only linear trend or basic stats are requested."],
        "limitations": ["Uses Nixtla/tsfeatures Terasvirta NN test; short series may fail."],
        "produces": ["nonlinearity", "terasvirta_stat"],
        "consumes": ["series_window", "lag"],
        "often_combined_with": ["advanced_features", "adf_stationarity"],
    },
    "index_calendar_map": {
        "output_schema": {"records": "per-index weekday/hour/is_weekend", "n_weekend/n_weekday": "counts"},
        "use_when": ["Questions map indices to weekday/hour (InWild hourly series starting Thursday 00:00)."],
        "avoid_when": ["No calendar/weekday semantics appear in the question."],
        "limitations": ["Defaults match MMTS generator (anchor Thursday, 1H); override from question text."],
        "produces": ["weekday", "hour", "is_weekend"],
        "consumes": ["indices", "anchor_weekday", "freq_hours"],
        "often_combined_with": ["interval_compare", "segment_trend", "value_at_index"],
    },
    "subsequence_rank": {
        "output_schema": {"ranking": "per-candidate best window distance", "nearest": "winner"},
        "use_when": ["Match find-it: rank several longer candidates against one short query via sliding DTW."],
        "avoid_when": ["Whole-series choose-it ranking (use pairwise_distance) or single long series locate."],
        "limitations": ["Calls sliding DTW per candidate; expensive on long series."],
        "produces": ["nearest", "ranking"],
        "consumes": ["query_and_candidates", "method"],
        "often_combined_with": ["subsequence_locate", "pairwise_distance"],
    },
    "window_shape_compare": {
        "output_schema": {"pairs": "pairwise window distances", "nearest_pair": "most similar windows"},
        "use_when": ["Analogical / pattern-similarity questions comparing two intervals on one series."],
        "avoid_when": ["Cross-series comparison is required (use cross_series_compare)."],
        "limitations": ["Unequal window lengths are truncated for z-euclidean; DTW handles unequal lengths."],
        "produces": ["pairs", "nearest_pair"],
        "consumes": ["series_index", "windows"],
        "often_combined_with": ["subsequence_locate", "interval_compare"],
    },
    "joint_threshold_events": {
        "output_schema": {"n_events": "count", "indices": "matching positions"},
        "use_when": ["Multi-series simultaneous threshold conditions (e.g. TS1>a while TS2<b)."],
        "avoid_when": ["Single-series peak counting is enough."],
        "limitations": ["Pointwise logic only; no event duration merging."],
        "produces": ["n_events", "indices"],
        "consumes": ["rules", "mode"],
        "often_combined_with": ["peaks_above_threshold", "cross_series_compare"],
    },
    "fft_period": {
        "output_schema": {"series": "dominant_period, spectral_strength, period_trusted"},
        "use_when": ["A dominant spectral period candidate is needed."],
        "avoid_when": ["A full-series-length period or weak peak would be accepted without validation."],
        "limitations": [
            "Trend/leakage can select very long periods; validate weak or boundary estimates.",
            "spectral_strength is NOT seasonal_strength.",
            "period_trusted=false when dominant_period is near series length or half-length.",
            "FFT period alone does not identify waveform type (sine/square/triangle/sawtooth).",
        ],
        "produces": ["dominant_period", "spectral_strength", "period_trusted"],
        "consumes": ["series"],
        "often_combined_with": ["stl_strength", "autocorr", "waveform_features"],
        "io_concepts": {
            "inputs": "series",
            "outputs": "dominant_period, spectral_strength, period_trusted",
            "depends": "none; typically precedes stl_strength",
        },
    },
    "stl_strength": {
        "output_schema": {
            "series": "period, period_trusted, seasonal_strength, season_strength_bin, trend_strength"
        },
        "use_when": ["A candidate period must be tested for seasonal/trend decomposition strength."],
        "avoid_when": ["An automatically selected period would be treated as ground truth without validation."],
        "limitations": [
            "Depends on STL assumptions; automatic period is capped to avoid half-length overfitting.",
            "Untrusted period yields misleading seasonal_strength — check period_trusted.",
        ],
        "produces": ["period", "seasonal_strength", "season_strength_bin", "trend_strength", "period_trusted"],
        "consumes": ["series", "period(optional)"],
        "often_combined_with": ["fft_period", "autocorr"],
        "io_concepts": {
            "inputs": "series, period(optional; omit→auto capped FFT)",
            "outputs": "period, seasonal_strength, season_strength_bin, trend_strength",
            "depends": "period often bound from fft_period.dominant_period when trusted",
        },
    },
    "hurst_exponent": {
        "output_schema": {"series": "Hurst via compute_Hc, persistence_hint, estimator metadata"},
        "use_when": ["Long-memory or persistence is the requested measurement (MMTS Hurst bins)."],
        "avoid_when": ["The series is shorter than ~20 points or dominated by deterministic trend."],
        "limitations": ["Uses hurst.compute_Hc(kind=random_walk) to match MMTS labels; trend can still bias."],
        "produces": ["hurst", "persistence_hint"],
        "consumes": ["series"],
    },
    "noise_decomposition": {
        "output_schema": {
            "series": "noise_ratio=Var(resid)/Var(series), noise_level bins none/low/medium/high, type hint"
        },
        "use_when": ["Residual noise strength / noise level bins are required (MMTS noise questions)."],
        "avoid_when": ["A known ground-truth noise component is expected but unavailable."],
        "limitations": [
            "Approximates MMTS Var(n)/Var(ts) via STL/high-pass residuals; noise_type_hint is heuristic.",
        ],
        "produces": ["noise_ratio", "noise_level", "noise_type_hint"],
        "consumes": ["series", "period(optional)"],
    },
    "waveform_features": {
        "output_schema": {
            "series": "waveform_hint plus jump/plateau/harmonic/template-match diagnostics"
        },
        "use_when": [
            "The question asks which waveform type (sine/square/triangle/sawtooth) a series resembles.",
            "Shape discrimination is needed beyond period or seasonal strength.",
        ],
        "avoid_when": [
            "Only period/seasonal strength is needed without shape type.",
            "Matching across candidate series (use pairwise/robust matching instead).",
        ],
        "limitations": [
            "periodicity_is_not_waveform_type: FFT period alone never implies sine.",
            "Hints can be ambiguous under heavy noise or non-periodic shapes.",
        ],
        "produces": ["waveform_hint", "jump_ratio", "template_match"],
        "consumes": ["series", "optional_window"],
        "often_combined_with": ["fft_period", "step_levels", "diff_stats"],
        "io_concepts": {
            "inputs": "series, optional start/end",
            "outputs": "waveform_hint, jump_ratio, harmonic, template_match",
        },
    },
    "adf_stationarity": {
        "output_schema": {"series": "ADF statistic, p-value, and stationarity flag"},
        "use_when": ["Statistical unit-root stationarity evidence is required."],
        "avoid_when": ["Stationarity is meant only as visual constancy or the window is too short."],
        "limitations": ["Sensitive to specification and structural breaks."],
    },
    "change_points": {
        "output_schema": {"series": "ranked mean-shift candidate indices and scores"},
        "use_when": ["Potential level/regime transitions must be localized."],
        "avoid_when": ["Exact guaranteed change points or variance-only shifts are required."],
        "limitations": ["Candidates are heuristic mean-shift locations."],
    },
    "interval_compare": {
        "output_schema": {"left/right": "interval statistics, trends, extrema counts, and deltas"},
        "use_when": ["Two intervals within one series must be compared quantitatively."],
        "avoid_when": ["The intervals belong to different series."],
        "limitations": ["Bounds may be clamped/reordered; adjusted results must be qualified."],
    },
    "crossing_points": {
        "output_schema": {"series": "threshold, crossing count/indices, and scope metadata"},
        "use_when": ["Crossings of zero, mean, median, or an explicit threshold are requested."],
        "avoid_when": ["Peaks/troughs or change points are intended instead of threshold crossings."],
        "limitations": ["Counts depend on threshold and threshold_scope."],
    },
    "advanced_features": {
        "output_schema": {"series": "distribution, entropy, stability, lumpiness, ARCH proxy, crossings"},
        "use_when": ["Higher-order distribution or volatility summaries are needed."],
        "avoid_when": ["A simple exact statistic or localized event is sufficient."],
        "limitations": ["Several outputs are proxies and depend on bin/chunk/lag parameters."],
    },
    "counterfactual_simulate": {
        "output_schema": {"before": "original summaries", "after": "edited summaries", "deltas": "changes", "status": "usability metadata"},
        "use_when": ["The question asks about an explicit edit and its consequences on the same series."],
        "avoid_when": ["Inferring causal effects on another series or answering from the unedited series."],
        "limitations": ["Edits are deterministic simulations, not causal models."],
    },
    "cross_series_compare": {
        "output_schema": {"series_1/series_2": "segment stats", "comparison": "trend agreement, distance, correlation"},
        "use_when": ["Aligned or specified windows from two series must be compared."],
        "avoid_when": ["More than two candidates need ranking or one-series intervals are compared."],
        "limitations": ["Correlation/distance require compatible overlap and do not prove causality."],
        "produces": ["correlation", "distance", "trend_agreement"],
        "consumes": ["series_pair", "optional_window"],
        "often_combined_with": ["lag_corr", "pairwise_distance"],
        "io_concepts": {
            "inputs": "series_index_1, series_index_2, optional start/end",
            "outputs": "comparison stats, correlation, distance",
        },
    },
    "extrema_align": {
        "output_schema": {"alignment": "event coverage, position deltas, Jaccard, best lag, extrema deltas"},
        "use_when": ["Peak/trough event timing across two series or intervals must be aligned."],
        "avoid_when": ["Amplitude similarity or dense pointwise matching is the objective."],
        "limitations": ["Reliability depends on detected event coverage and prominence filtering."],
    },
    "lag_corr": {
        "output_schema": {"correlation": "auto/cross lag correlation or pairwise records"},
        "use_when": ["Correlation at one specified lag is required."],
        "avoid_when": ["The best lag is unknown or causal direction must be established."],
        "limitations": ["Association is not causation; large lags reduce overlap."],
        "produces": ["lag_correlation"],
        "consumes": ["series_pair_or_all", "lag"],
        "often_combined_with": ["lag_corr_scan", "cross_series_compare"],
        "io_concepts": {
            "inputs": "series_index_1/2 or all, lag",
            "outputs": "correlation at lag",
        },
    },
    "lag_corr_scan": {
        "output_schema": {"best_lag/best_corr": "strongest association", "lags": "scanned records", "warnings": "overlap notes"},
        "use_when": ["The strongest lead-lag association over a bounded lag range is required."],
        "avoid_when": ["Causal proof is requested or overlap is insufficient."],
        "limitations": ["Multiple-lag search can find spurious associations; inspect overlap."],
    },
    "pairwise_distance": {
        "output_schema": {"distances": "per-candidate distances", "nearest": "winner", "method": "distance metadata"},
        "use_when": ["One query series must be ranked against multiple candidate series."],
        "avoid_when": ["Reverse, subsequence, or robust-outlier matching semantics are required."],
        "limitations": ["Distance meaning depends on normalization/method; unequal lengths may be truncated."],
    },
    "reverse_match": {
        "output_schema": {"ranking": "reversed-candidate distances and winner"},
        "use_when": ["Candidates must be reversed before comparison with a query."],
        "avoid_when": ["Ordinary forward matching or trend direction alone is requested."],
        "limitations": ["Winner reliability depends on distance margin and method fallback."],
    },
    "robust_shape_match": {
        "output_schema": {"ranking": "robust composite scores and winner margin"},
        "use_when": ["Candidate ranking must tolerate spikes, scaling, and moderate noise."],
        "avoid_when": ["Exact raw-value equality or explicit reverse matching is required."],
        "limitations": ["Depends on smoothing/winsorization; small margins can be ambiguous."],
    },
    "smooth_reverse_stats": {
        "output_schema": {"series": "smoothed mean and forward/reverse endpoint direction"},
        "use_when": ["Auxiliary direction summaries before and after reversal are needed."],
        "avoid_when": ["A winning candidate or similarity ranking is required."],
        "limitations": ["Does not compare a query or identify a winner."],
    },
    "smooth_shape_match": {
        "output_schema": {"ranking": "distances after MA smoothing", "nearest": "winner"},
        "use_when": ["MMTS smooth-it: rank candidates after moving-average smoothing."],
        "avoid_when": ["Candidates must not be smoothed or reverse matching is required."],
        "limitations": ["Default window=3 matches MMTS SmoothitProcessor; distance depends on method."],
        "produces": ["nearest", "ranking"],
        "consumes": ["query_and_candidates", "smooth_window"],
        "often_combined_with": ["pairwise_distance", "robust_shape_match"],
    },
    "subsequence_locate": {
        "output_schema": {"best_start/best_end": "window", "distance": "dtw or z-euclidean", "method": "backend"},
        "use_when": ["MMTS find-it: locate a short query inside a longer series (prefer method=dtw)."],
        "avoid_when": ["Whole-series candidate ranking is required."],
        "limitations": ["Default method=dtw via dtaidistance; euclidean is a faster fallback."],
        "produces": ["best_start", "best_end", "distance"],
        "consumes": ["query_series_index", "long_series_index", "method"],
    },
    "peaks_above_threshold": {
        "output_schema": {"series": "peak/trough counts filtered by absolute height threshold"},
        "use_when": ["Count peaks/troughs above/below an absolute value threshold."],
        "avoid_when": ["Unfiltered local extrema counts are sufficient."],
        "limitations": ["Uses the same prominence filter as local_extrema then applies threshold."],
    },
    "bimodal_detect": {
        "output_schema": {"series": "is_bimodal flag, mode separation, amplitude bimodality"},
        "use_when": ["Questions ask whether the amplitude distribution is bimodal."],
        "avoid_when": ["Only mean/std summaries are needed."],
        "limitations": ["Histogram heuristic; sensitive to binning."],
    },
    "caption_verify": {
        "output_schema": {"candidates": "per-candidate claim checks and scores", "best_match": "top candidate"},
        "use_when": ["Explicit numeric/structural claims from a caption must be checked against candidates."],
        "avoid_when": ["The caption requires open-ended semantics not representable as supported claim types."],
        "limitations": [
            "Structured claim checker, not free-form language understanding.",
            "Supports trend/period/levels/extrema/volatility/anomaly/stationarity/"
            "value_band/spike/zero_gap/peak_at/drop_magnitude/high_freq/reaching_up_to.",
        ],
    },
}


def build_default_registry() -> ToolRegistry:
    reg = ToolRegistry()
    specs = [
        (
            ToolSpec(
                name="describe_series",
                description=(
                    "Descriptive stats for EVERY series: mean/std/min/max/median/range/"
                    "p50/p90/p99/slope (preferred multi-series overview)."
                ),
                roles=_ALL,
                input_schema={"note": "no series_index needed; always returns all series"},
            ),
            _describe,
        ),
        (
            ToolSpec(
                name="sliding_stats",
                description="Sliding-window mean/std for local volatility.",
                roles=[*_CORE, "alignment"],
                input_schema={**_SERIES_INDEX_SCHEMA, "window": "int (alias window_size)"},
            ),
            _sliding_stats,
        ),
        (
            ToolSpec(
                name="diff_stats",
                description="First-difference stats and sign changes.",
                roles=[*_CORE, "alignment"],
                input_schema=dict(_SERIES_INDEX_SCHEMA),
            ),
            _diff_stats,
        ),
        (
            ToolSpec(
                name="local_extrema",
                description=(
                    "Count local peaks and troughs (global indices). "
                    "Do NOT use for step/plateau level counting—use step_levels instead."
                ),
                roles=_ALL,
                input_schema=dict(_SERIES_INDEX_SCHEMA),
            ),
            _local_extrema,
        ),
        (
            ToolSpec(
                name="global_extrema",
                description=(
                    "Global max/min indices and values; optional index classifies a point "
                    "as global/local peak/trough (Base index tasks)."
                ),
                roles=_ALL,
                input_schema=dict(_SERIES_INDEX_WITH_QUERY),
            ),
            _global_extrema,
        ),
        (
            ToolSpec(
                name="segment_trend",
                description="Linear slope and direction (upward/downward/flat) for a segment.",
                roles=[*_CORE, "alignment"],
                input_schema=dict(_SERIES_INDEX_SCHEMA),
            ),
            _segment_trend,
        ),
        (
            ToolSpec(
                name="step_levels",
                description=(
                    "Count discrete step/plateau levels (unique values and plateau runs) "
                    "in a window. Use for stepwise/staircase/plateau questions."
                ),
                roles=[*_CORE, "alignment"],
                input_schema=dict(_SERIES_INDEX_SCHEMA),
            ),
            _step_levels,
        ),
        (
            ToolSpec(
                name="value_at_index",
                description="Return the numeric value at a specific index (0-based by default).",
                roles=[*_CORE, "alignment"],
                input_schema={
                    **_SERIES_INDEX_SCHEMA,
                    "index": "required int index",
                    "index_base": "0 (default) or 1 if question uses 1-based indices",
                },
            ),
            _value_at_index,
        ),
        (
            ToolSpec(
                name="anomaly_detect",
                description="Detect spikes/outliers via z-score threshold in a window.",
                roles=[*_CORE, "alignment"],
                input_schema={**_SERIES_INDEX_SCHEMA, "z_threshold": "float (default 3.0)"},
            ),
            _anomaly_detect,
        ),
        (
            ToolSpec(
                name="autocorr",
                description=(
                    "Autocorrelation up to max_lag (full ACF list). "
                    "Optional lags=[...] returns acf_at_lags for specific lags."
                ),
                roles=[*_CORE, "alignment"],
                input_schema={
                    **_SERIES_INDEX_SCHEMA,
                    "max_lag": "int",
                    "lags": "optional list of specific lags",
                },
            ),
            _acf,
        ),
        (
            ToolSpec(
                name="seas_acf",
                description=(
                    "MMTS seas_acf1: seasonal autocorrelation ρ_m=γ_m/γ_0 at lag m "
                    "(e.g. lag=26 for weekly half-year frequency)."
                ),
                roles=[*_CORE, "alignment"],
                input_schema={
                    **_SERIES_INDEX_SCHEMA,
                    "lag": "required seasonal lag m (aliases: m, frequency, period)",
                },
            ),
            _seas_acf,
        ),
        (
            ToolSpec(
                name="nonlinearity_terasvirta",
                description=(
                    "MMTS nonlinearity via Terasvirta NN test: returns 10*T_stat/N "
                    "(larger ⇒ stronger nonlinear structure)."
                ),
                roles=[*_CORE, "alignment"],
                input_schema={**_SERIES_INDEX_SCHEMA, "lag": "AR lag order (default 1)"},
            ),
            _nonlinearity_terasvirta,
        ),
        (
            ToolSpec(
                name="index_calendar_map",
                description=(
                    "Map indices to weekday/hour using an hourly calendar anchor "
                    "(MMTS InWild default: index 0 = Thursday 00:00)."
                ),
                roles=[*_CORE, "alignment"],
                input_schema={
                    "indices": "int or list of indices",
                    "start/end": "optional inclusive range if indices omitted",
                    "anchor_weekday": "Thursday (default) or 0-6 Mon-Sun",
                    "anchor_hour": "default 0",
                    "freq_hours": "sampling step in hours (default 1)",
                },
            ),
            _index_calendar_map,
        ),
        (
            ToolSpec(
                name="fft_period",
                description="Dominant period via FFT.",
                roles=[*_CORE, "matching", "alignment"],
                input_schema=dict(_SERIES_INDEX_SCHEMA),
            ),
            _fft_period,
        ),
        (
            ToolSpec(
                name="stl_strength",
                description="STL seasonal/trend strength.",
                roles=[*_CORE, "alignment"],
                input_schema={
                    **_SERIES_INDEX_SCHEMA,
                    "period": "optional positive int | omit → auto via fft_period; never null/placeholder strings",
                },
            ),
            _stl_strength,
        ),
        (
            ToolSpec(
                name="hurst_exponent",
                description=(
                    "Estimate Hurst exponent via hurst.compute_Hc(kind=random_walk), "
                    "matching MMTS label generation. Returns persistence_hint at 0.45/0.55."
                ),
                roles=[*_CORE, "alignment"],
                input_schema=dict(_SERIES_INDEX_SCHEMA),
            ),
            _hurst_exponent,
        ),
        (
            ToolSpec(
                name="noise_decomposition",
                description=(
                    "MMTS-style residual noise strength: Var(residual)/Var(series) after STL "
                    "(conservative vs high-pass), with bins none/low/medium/high at 0.1/0.33/0.66 "
                    "and a heuristic noise_type_hint."
                ),
                roles=[*_CORE, "alignment"],
                input_schema={**_SERIES_INDEX_SCHEMA, "period": "optional int"},
            ),
            _noise_decomposition,
        ),
        (
            ToolSpec(
                name="waveform_features",
                description=(
                    "Classify waveform shape (sine/square/triangle/sawtooth/ambiguous) using "
                    "jump ratio, plateau clustering, harmonic structure, and folded-template match. "
                    "Do NOT treat FFT period alone as evidence of a sine wave."
                ),
                roles=[*_CORE, "matching", "alignment"],
                input_schema=dict(_SERIES_INDEX_SCHEMA),
            ),
            _waveform_features,
        ),
        (
            ToolSpec(
                name="adf_stationarity",
                description="ADF stationarity test.",
                roles=[*_CORE, "alignment"],
                input_schema=dict(_SERIES_INDEX_SCHEMA),
            ),
            _stationarity,
        ),
        (
            ToolSpec(
                name="change_points",
                description="Mean-shift change-point candidates.",
                roles=[*_CORE, "alignment"],
                input_schema=dict(_SERIES_INDEX_SCHEMA),
            ),
            _change_points,
        ),
        (
            ToolSpec(
                name="interval_compare",
                description=(
                    "Compare left/right interval statistics on one series "
                    "(mean/std/max/min/n_peaks/trend per side)."
                ),
                roles=[*_CORE, "alignment"],
                input_schema={
                    **_SERIES_INDEX_SCHEMA,
                    "left_interval": "[start,end] inclusive",
                    "right_interval": "[start,end] inclusive",
                    "start/mid/end": "alt split mode",
                },
            ),
            _interval_compare,
        ),
        (
            ToolSpec(
                name="crossing_points",
                description=(
                    "Count crossings inside an optional window using a whole-series median/mean "
                    "by default; threshold_scope='window' opts into a window-derived threshold."
                ),
                roles=[*_CORE, "alignment"],
                input_schema={
                    **_SERIES_INDEX_SCHEMA,
                    "threshold": "median|mean|zero (default median)",
                    "threshold_value": "optional explicit float",
                    "threshold_scope": "series (default, MMTS) | window",
                },
            ),
            _crossing_points,
        ),
        (
            ToolSpec(
                name="advanced_features",
                description=(
                    "Advanced basic/volatility features: IQR, skewness, excess kurtosis, "
                    "spectral and histogram entropy, stability, lumpiness, ARCH LM/R², and median crossings."
                ),
                roles=[*_CORE, "alignment"],
                input_schema={
                    **_SERIES_INDEX_SCHEMA,
                    "bins": "optional entropy histogram bins",
                    "chunk_size": "optional stability/lumpiness chunk size",
                    "arch_lags": "optional ARCH-LM lags (default 5)",
                },
            ),
            _advanced_features,
        ),
        (
            ToolSpec(
                name="counterfactual_simulate",
                description=(
                    "Apply counterfactual edits to a copied series and compare before/after "
                    "statistics. Supports set_value, replace_segment, shift, scale_values, "
                    "scale_std, cap, and extrapolate_slope."
                ),
                roles=_CORE,
                input_schema={
                    "series_index": "target 1-based series (default 1)",
                    "operations": "list of {op, ...} edit objects",
                    "index_base": "0 (default) or 1",
                    "report_indices": "optional indices whose exact before/after values are returned",
                },
            ),
            _counterfactual_simulate,
        ),
        (
            ToolSpec(
                name="cross_series_compare",
                description=(
                    "Compare windows across TWO series (analogical / multi-series segment tasks). "
                    "Returns per-series segment stats, trend match, distance, correlation."
                ),
                roles=_CORE,
                input_schema={
                    "series_index_1": "1-based int (default 1)",
                    "series_index_2": "1-based int (default 2)",
                    "start": "optional shared window start",
                    "end": "optional shared window end",
                    "left_interval": "optional [start,end] for series 1",
                    "right_interval": "optional [start,end] for series 2",
                },
            ),
            _cross_series_compare,
        ),
        (
            ToolSpec(
                name="extrema_align",
                description=(
                    "Align peaks/troughs across two series or intervals; returns normalized "
                    "event-position deltas, best event lag, and global-extrema index deltas."
                ),
                roles=_CORE,
                input_schema={
                    "series_index_1": "1-based int",
                    "series_index_2": "1-based int",
                    "interval_1": "optional [start,end]",
                    "interval_2": "optional [start,end]",
                    "kind": "both|peaks|troughs",
                    "max_lag": "optional event lag scan bound",
                },
            ),
            _extrema_align,
        ),
        (
            ToolSpec(
                name="lag_corr",
                description="Auto or cross lag correlation. Use series_index_1/2 ints, or 'all' for all pairs.",
                roles=_CORE,
                input_schema={
                    "lag": "int",
                    "series_index_1": "1-based int|'all'",
                    "series_index_2": "1-based int|'all'",
                },
            ),
            _lag_corr,
        ),
        (
            ToolSpec(
                name="lag_corr_scan",
                description=(
                    "Scan cross-correlation over positive and negative lags and report the "
                    "strongest lead-lag association; association is not causal proof."
                ),
                roles=_CORE,
                input_schema={
                    "series_index_1": "1-based int",
                    "series_index_2": "1-based int",
                    "start": "optional shared inclusive start",
                    "end": "optional shared inclusive end",
                    "max_lag": "scan bound (default min(20,n/4))",
                    "min_overlap": "minimum paired points per lag (default max(8,10% of length))",
                },
            ),
            _lag_corr_scan,
        ),
        (
            ToolSpec(
                name="pairwise_distance",
                description="Distance from reference series to others (euclidean/dtw).",
                roles=["matching", "alignment", "structure", "reasoning"],
                input_schema={"method": "euclidean|dtw", "series_index": "reference 1-based (default 1)"},
            ),
            _pairwise_distance,
        ),
        (
            ToolSpec(
                name="reverse_match",
                description=(
                    "Reverse each candidate series and rank candidates against the query "
                    "using length-normalized z-DTW or Euclidean distance."
                ),
                roles=["matching", "structure", "reasoning"],
                input_schema={
                    "query_series_index": "1-based query (default 1)",
                    "candidate_series_indices": "optional 1-based list (default all others)",
                    "method": "dtw|euclidean",
                },
            ),
            _reverse_match,
        ),
        (
            ToolSpec(
                name="robust_shape_match",
                description=(
                    "Robust candidate ranking using winsorization, smoothing, z-distance, "
                    "correlation distance, and DTW with an explicit winner margin."
                ),
                roles=["matching", "structure", "reasoning"],
                input_schema={
                    "query_series_index": "1-based query (default 1)",
                    "candidate_series_indices": "optional 1-based list (default all others)",
                    "smooth_window": "moving-average window (default 5)",
                    "winsor_percentile": "tail clipping percentile in [0,50) (default 2)",
                },
            ),
            _robust_shape_match,
        ),
        (
            ToolSpec(
                name="smooth_reverse_stats",
                description="Smoothing and reverse-direction stats.",
                roles=["matching", "structure"],
                input_schema={**_SERIES_INDEX_SCHEMA, "window": "int"},
            ),
            _smooth_reverse,
        ),
        (
            ToolSpec(
                name="smooth_shape_match",
                description=(
                    "MMTS smooth-it matching: apply centered moving-average (default window=3) "
                    "to candidates, then rank by DTW/euclidean distance to the query series."
                ),
                roles=["matching", "structure"],
                input_schema={
                    "query_series_index": "1-based query (default 1)",
                    "window": "MA window (default 3)",
                    "method": "dtw (default) | euclidean",
                },
            ),
            _smooth_shape_match,
        ),
        (
            ToolSpec(
                name="subsequence_locate",
                description=(
                    "Locate best matching subsequence of a query inside a longer series. "
                    "Default method=dtw (MMTS find-it); method=euclidean uses z-normalized L2."
                ),
                roles=["matching", "structure"],
                input_schema={
                    "query_series_index": "1-based",
                    "long_series_index": "1-based",
                    "method": "dtw (default) | euclidean",
                },
            ),
            _subsequence_locate,
        ),
        (
            ToolSpec(
                name="subsequence_rank",
                description=(
                    "Match find-it multi-candidate ranking: sliding-window DTW of a short query "
                    "against each longer candidate; returns nearest by distance."
                ),
                roles=["matching", "structure"],
                input_schema={
                    "query_series_index": "1-based query (default 1)",
                    "candidate_series_indices": "optional 1-based list (default all others)",
                    "method": "dtw (default) | euclidean",
                },
            ),
            _subsequence_rank,
        ),
        (
            ToolSpec(
                name="window_shape_compare",
                description=(
                    "Compare two or more windows on one series (analogical pattern similarity) "
                    "via z-euclidean or DTW distance."
                ),
                roles=_CORE,
                input_schema={
                    "series_index": "1-based (default 1)",
                    "windows": "list of [start,end] inclusive intervals",
                    "method": "z_euclidean (default) | dtw",
                },
            ),
            _window_shape_compare,
        ),
        (
            ToolSpec(
                name="joint_threshold_events",
                description=(
                    "Count timesteps where multiple series jointly satisfy threshold rules "
                    "(e.g. series1>20 and series2<78)."
                ),
                roles=_CORE,
                input_schema={
                    "rules": "list of {series_index, op, value}",
                    "mode": "and (default) | or",
                    "start/end": "optional inclusive window",
                },
            ),
            _joint_threshold_events,
        ),
        (
            ToolSpec(
                name="peaks_above_threshold",
                description=(
                    "Count local peaks/troughs optionally filtered by absolute height threshold "
                    "(InWild peak-above-value style questions)."
                ),
                roles=[*_CORE, "alignment"],
                input_schema={
                    **_SERIES_INDEX_SCHEMA,
                    "threshold": "optional absolute height filter (alias min_height)",
                },
            ),
            _peaks_above_threshold,
        ),
        (
            ToolSpec(
                name="bimodal_detect",
                description="Detect amplitude bimodality via histogram peak/valley heuristic.",
                roles=[*_CORE, "alignment"],
                input_schema=dict(_SERIES_INDEX_SCHEMA),
            ),
            _bimodal_detect,
        ),
        (
            ToolSpec(
                name="caption_verify",
                description=(
                    "Verify structured caption claims against one or more candidate series "
                    "and rank candidates by passed claims. Supports trend, period, levels/runs, "
                    "extrema, volatility, anomaly, stationarity, value_band, spike, zero_gap, "
                    "peak_at, drop_magnitude, high_freq, reaching_up_to, and basic stats."
                ),
                roles=["alignment"],
                input_schema={
                    "claims": "list of structured {type, expected, optional start/end/tolerance}",
                    "candidate_series_indices": "optional 1-based list or all",
                },
            ),
            _caption_verify,
        ),
    ]
    for spec, fn in specs:
        contract = _TOOL_CONTRACTS.get(spec.name)
        if contract is None:
            raise ValueError(f"missing tool contract for {spec.name}")
        spec.output_schema = dict(contract["output_schema"])
        spec.use_when = list(contract["use_when"])
        spec.avoid_when = list(contract["avoid_when"])
        spec.limitations = list(contract["limitations"])
        spec.produces = list(contract.get("produces") or [])
        spec.consumes = list(contract.get("consumes") or [])
        spec.often_combined_with = list(contract.get("often_combined_with") or [])
        spec.io_concepts = dict(contract.get("io_concepts") or {})
        reg.register(spec, fn)
    return reg
