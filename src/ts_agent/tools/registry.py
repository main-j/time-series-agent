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

    def catalog_text(self, roles: List[str]) -> str:
        lines = [
            "Tool binding rules:",
            "- Tools read pipeline-bound series; NEVER paste raw numeric arrays into arguments.",
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
        return "\n".join(lines)


def _level_tolerance(arr: np.ndarray) -> float:
    std = float(np.std(arr))
    span = float(np.max(arr) - np.min(arr)) if arr.size else 0.0
    return max(_VARIANCE_EPS, std * 1e-6, span * 1e-9, 1e-9)


def _step_level_stats(arr: np.ndarray) -> Dict[str, Any]:
    if arr.size == 0:
        return {"n_unique_levels": 0, "n_plateau_runs": 0, "levels": [], "plateau_runs": []}
    tol = _level_tolerance(arr)
    plateau_runs: List[float] = []
    for v in arr:
        if not plateau_runs or abs(float(v) - plateau_runs[-1]) > tol:
            plateau_runs.append(float(v))
    uniq: List[float] = []
    for v in arr:
        fv = float(v)
        if not any(abs(fv - u) <= tol for u in uniq):
            uniq.append(fv)
    return {
        "n_unique_levels": len(uniq),
        "n_plateau_runs": len(plateau_runs),
        "levels": uniq,
        "plateau_runs": plateau_runs,
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


def _hurst_exponent(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
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
                    "hurst": None,
                    "note": "series too short for Hurst estimate",
                }
            )
            continue
        lags = list(range(2, min(n // 2, 50)))
        tau = []
        for lag in lags:
            diffs = sub[lag:] - sub[:-lag]
            scale = float(np.std(diffs))
            if scale < _VARIANCE_EPS:
                # Perfectly linear segments have zero diff std; use mean abs increment.
                scale = float(np.mean(np.abs(diffs)))
            tau.append(max(scale, _VARIANCE_EPS))
        if len(tau) < 2 or min(tau) <= 0:
            items.append(
                {
                    "series_index": sid,
                    "start": s,
                    "end": e,
                    "hurst": None,
                    "note": "insufficient variance for Hurst estimate",
                }
            )
            continue
        hurst = float(np.polyfit(np.log(lags), np.log(tau), 1)[0])
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
            }
        )
    return _pack_per_series("hurst_exponent", items)


def _noise_decomposition(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    items = []
    for sid, arr in _selected_arrays(arguments, series):
        sub, s, e = _slice_window(arr, arguments)
        if len(sub) < 4:
            return ToolResult(name="noise_decomposition", success=False, data={}, error=f"series {sid} too short")
        period = int(arguments.get("period", 0))
        if period <= 1:
            if float(np.std(sub)) < _VARIANCE_EPS:
                period = max(2, len(sub) // 8)
            else:
                centered = sub - np.mean(sub)
                spec = np.abs(np.fft.rfft(centered))
                freqs = np.fft.rfftfreq(len(sub), d=1.0)
                if len(spec) > 1:
                    idx = int(np.argmax(spec[1:]) + 1)
                    period = int(1.0 / freqs[idx]) if freqs[idx] > 0 else max(2, len(sub) // 8)
                else:
                    period = max(2, len(sub) // 8)
        period = max(2, min(period, len(sub) // 2))
        try:
            from statsmodels.tsa.seasonal import STL

            stl = STL(sub, period=period, robust=True)
            res = stl.fit()
            resid = np.asarray(res.resid)
            seasonal = np.asarray(res.seasonal)
            trend = np.asarray(res.trend)
            series_std = float(np.std(sub))
            resid_std = float(np.std(resid))
            noise_ratio = float(resid_std / (series_std + 1e-12))
            seasonal_strength = float(max(0.0, 1.0 - np.var(resid) / (np.var(seasonal + resid) + 1e-12)))
            if noise_ratio < 0.33:
                noise_level = "low"
            elif noise_ratio <= 0.66:
                noise_level = "medium"
            else:
                noise_level = "high"
            # Heuristic noise-type guess for MMTS Base templates
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
                    "series_std": series_std,
                    "noise_ratio": noise_ratio,
                    "noise_level": noise_level,
                    "seasonal_strength": seasonal_strength,
                    "trend_strength": float(max(0.0, 1.0 - np.var(resid) / (np.var(trend + resid) + 1e-12))),
                    "noise_type_hint": noise_type_hint,
                    "acf_lag1": acf1,
                }
            )
        except Exception as ex:  # noqa: BLE001
            return ToolResult(name="noise_decomposition", success=False, data={}, error=str(ex))
    return _pack_per_series("noise_decomposition", items)


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
        items.append(
            {
                "series_index": sid,
                "start": s,
                "end": e,
                "slope": slope,
                "direction": direction,
                "mean": float(np.mean(sub)),
                "std": float(np.std(sub)),
                "start_value": float(sub[0]),
                "end_value": float(sub[-1]),
            }
        )
    return _pack_per_series("segment_trend", items)


def _acf(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    items = []
    for sid, arr in _selected_arrays(arguments, series):
        max_lag = int(arguments.get("max_lag", min(40, max(1, len(arr) // 4))))
        max_lag = max(1, min(max_lag, max(1, len(arr) - 1)))
        if float(np.std(arr)) < _VARIANCE_EPS:
            items.append(
                {
                    "series_index": sid,
                    "max_lag": max_lag,
                    "best_lag": 0,
                    "acf": [0.0] * min(20, max_lag),
                    "note": "zero-variance series",
                }
            )
            continue
        centered = arr - np.mean(arr)
        denom = float(np.dot(centered, centered))
        vals = []
        for lag in range(1, max_lag + 1):
            vals.append(float(np.dot(centered[:-lag], centered[lag:]) / denom))
        best = int(np.argmax(np.abs(vals))) + 1 if vals else 0
        items.append({"series_index": sid, "max_lag": max_lag, "best_lag": best, "acf": vals[:20]})
    return _pack_per_series("autocorr", items)


def _fft_period(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    items = []
    for sid, arr in _selected_arrays(arguments, series):
        if float(np.std(arr)) < _VARIANCE_EPS:
            items.append(
                {
                    "series_index": sid,
                    "dominant_period": None,
                    "spectral_strength": 0.0,
                    "note": "zero-variance series",
                }
            )
            continue
        centered = arr - np.mean(arr)
        spec = np.abs(np.fft.rfft(centered))
        freqs = np.fft.rfftfreq(len(arr), d=1.0)
        if len(spec) > 1:
            idx = int(np.argmax(spec[1:]) + 1)
            period = float(1.0 / freqs[idx]) if freqs[idx] > 0 else None
            strength = float(spec[idx] / (np.sum(spec) + 1e-12))
        else:
            period, strength = None, 0.0
        items.append({"series_index": sid, "dominant_period": period, "spectral_strength": strength})
    return _pack_per_series("fft_period", items)


def _stl_strength(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    items = []
    for sid, arr in _selected_arrays(arguments, series):
        if len(arr) < 4:
            return ToolResult(name="stl_strength", success=False, data={}, error=f"series {sid} too short for STL")
        period = int(arguments.get("period", 0))
        if period <= 1:
            fft = _fft_period({"series_index": sid}, series)
            if not fft.success:
                return ToolResult(name="stl_strength", success=False, data={}, error=fft.error or "FFT period failed")
            pdata = fft.data if "dominant_period" in fft.data else (fft.data.get("series") or [{}])[0]
            period = int(pdata["dominant_period"]) if pdata.get("dominant_period") else max(2, len(arr) // 8)
        period = max(2, min(period, len(arr) // 2))
        try:
            from statsmodels.tsa.seasonal import STL

            stl = STL(arr, period=period, robust=True)
            res = stl.fit()
            seasonal = np.asarray(res.seasonal)
            resid = np.asarray(res.resid)
            trend = np.asarray(res.trend)
            seasonal_strength = float(max(0.0, 1.0 - np.var(resid) / (np.var(seasonal + resid) + 1e-12)))
            trend_strength = float(max(0.0, 1.0 - np.var(resid) / (np.var(trend + resid) + 1e-12)))
            items.append(
                {
                    "series_index": sid,
                    "period": period,
                    "seasonal_strength": seasonal_strength,
                    "trend_strength": trend_strength,
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
    best_i, best_d = 0, float("inf")
    q_std = float(np.std(query))
    q = (query - np.mean(query)) / q_std if q_std >= _VARIANCE_EPS else query - np.mean(query)
    for i in range(0, len(long) - len(query) + 1):
        w = long[i : i + len(query)]
        w_std = float(np.std(w))
        w = (w - np.mean(w)) / w_std if w_std >= _VARIANCE_EPS else w - np.mean(w)
        d = float(np.linalg.norm(q - w))
        if d < best_d:
            best_d, best_i = d, i
    if not np.isfinite(best_d):
        return ToolResult(name="subsequence_locate", success=False, data={}, error="non-finite subsequence distance")
    return ToolResult(
        name="subsequence_locate",
        success=True,
        data={
            "best_start": best_i,
            "distance": best_d,
            "query_len": len(query),
            "query_series_index": q_idx + 1,
            "long_series_index": l_idx + 1,
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
                description="Autocorrelation up to max_lag.",
                roles=[*_CORE, "alignment"],
                input_schema={**_SERIES_INDEX_SCHEMA, "max_lag": "int"},
            ),
            _acf,
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
                input_schema={**_SERIES_INDEX_SCHEMA, "period": "int"},
            ),
            _stl_strength,
        ),
        (
            ToolSpec(
                name="hurst_exponent",
                description="Estimate Hurst exponent for long-memory / persistence questions.",
                roles=[*_CORE, "alignment"],
                input_schema=dict(_SERIES_INDEX_SCHEMA),
            ),
            _hurst_exponent,
        ),
        (
            ToolSpec(
                name="noise_decomposition",
                description=(
                    "STL residual noise ratio/level and noise-type hint "
                    "(low/medium/high; gauss/uniform/quantization/random_walk_like)."
                ),
                roles=[*_CORE, "alignment"],
                input_schema={**_SERIES_INDEX_SCHEMA, "period": "optional int"},
            ),
            _noise_decomposition,
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
                name="subsequence_locate",
                description="Locate best matching subsequence.",
                roles=["matching", "structure"],
                input_schema={"query_series_index": "1-based", "long_series_index": "1-based"},
            ),
            _subsequence_locate,
        ),
        (
            ToolSpec(
                name="caption_verify",
                description=(
                    "Verify structured caption claims against one or more candidate series "
                    "and rank candidates by passed claims. Supports trend, period, levels/runs, "
                    "extrema counts, volatility, anomaly, stationarity, range/endpoints/basic stats."
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
        reg.register(spec, fn)
    return reg
