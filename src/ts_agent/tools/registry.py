from __future__ import annotations

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
            return _finalize(name, self._fns[name](arguments or {}, series))
        except Exception as e:  # noqa: BLE001
            return ToolResult(name=name, success=False, data={}, error=str(e))

    def catalog_text(self, roles: List[str]) -> str:
        lines = []
        for spec in self.list_for_roles(roles):
            lines.append(f"- {spec.name}: {spec.description}")
        return "\n".join(lines)


def _primary(series: List[List[float]]) -> np.ndarray:
    if not series:
        raise ValueError("Empty series")
    arr = np.asarray(series[0], dtype=float)
    if arr.size == 0:
        raise ValueError("Empty series")
    return arr


def _describe(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    out = []
    for i, s in enumerate(series):
        arr = np.asarray(s, dtype=float)
        out.append(
            {
                "index": i + 1,
                "length": int(arr.size),
                "mean": float(np.mean(arr)),
                "std": float(np.std(arr)),
                "min": float(np.min(arr)),
                "max": float(np.max(arr)),
                "start": float(arr[0]),
                "end": float(arr[-1]),
                "slope": float((arr[-1] - arr[0]) / max(len(arr) - 1, 1)),
            }
        )
    return ToolResult(name="describe_series", success=True, data={"series": out})


def _sliding_stats(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    arr = _primary(series)
    window = int(arguments.get("window", max(5, len(arr) // 20)))
    window = max(2, min(window, len(arr)))
    means, stds = [], []
    for i in range(0, len(arr) - window + 1):
        seg = arr[i : i + window]
        means.append(float(np.mean(seg)))
        stds.append(float(np.std(seg)))
    return ToolResult(
        name="sliding_stats",
        success=True,
        data={"window": window, "mean_of_means": float(np.mean(means)), "mean_of_stds": float(np.mean(stds)), "max_local_std": float(np.max(stds))},
    )


def _diff_stats(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    arr = _primary(series)
    d = np.diff(arr)
    return ToolResult(
        name="diff_stats",
        success=True,
        data={
            "mean_diff": float(np.mean(d)) if len(d) else 0.0,
            "std_diff": float(np.std(d)) if len(d) else 0.0,
            "max_abs_diff": float(np.max(np.abs(d))) if len(d) else 0.0,
            "n_sign_changes": int(np.sum(d[1:] * d[:-1] < 0)) if len(d) > 1 else 0,
        },
    )


def _local_extrema(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    arr = _primary(series)
    peaks, troughs = [], []
    for i in range(1, len(arr) - 1):
        if arr[i] > arr[i - 1] and arr[i] > arr[i + 1]:
            peaks.append(i)
        if arr[i] < arr[i - 1] and arr[i] < arr[i + 1]:
            troughs.append(i)
    return ToolResult(
        name="local_extrema",
        success=True,
        data={"n_peaks": len(peaks), "n_troughs": len(troughs), "peak_idx": peaks[:20], "trough_idx": troughs[:20]},
    )


def _acf(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    arr = _primary(series)
    max_lag = int(arguments.get("max_lag", min(40, max(1, len(arr) // 4))))
    max_lag = max(1, min(max_lag, max(1, len(arr) - 1)))
    if float(np.std(arr)) < _VARIANCE_EPS:
        return ToolResult(
            name="autocorr",
            success=True,
            data={"max_lag": max_lag, "best_lag": 0, "acf": [0.0] * min(20, max_lag), "note": "zero-variance series"},
        )
    centered = arr - np.mean(arr)
    denom = float(np.dot(centered, centered))
    vals = []
    for lag in range(1, max_lag + 1):
        vals.append(float(np.dot(centered[:-lag], centered[lag:]) / denom))
    best = int(np.argmax(np.abs(vals))) + 1 if vals else 0
    return ToolResult(name="autocorr", success=True, data={"max_lag": max_lag, "best_lag": best, "acf": vals[:20]})


def _fft_period(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    arr = _primary(series)
    if float(np.std(arr)) < _VARIANCE_EPS:
        return ToolResult(
            name="fft_period",
            success=True,
            data={"dominant_period": None, "spectral_strength": 0.0, "note": "zero-variance series"},
        )
    centered = arr - np.mean(arr)
    spec = np.abs(np.fft.rfft(centered))
    freqs = np.fft.rfftfreq(len(arr), d=1.0)
    if len(spec) > 1:
        idx = int(np.argmax(spec[1:]) + 1)
        period = float(1.0 / freqs[idx]) if freqs[idx] > 0 else None
        strength = float(spec[idx] / (np.sum(spec) + 1e-12))
    else:
        period, strength = None, 0.0
    return ToolResult(name="fft_period", success=True, data={"dominant_period": period, "spectral_strength": strength})


def _stl_strength(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    arr = _primary(series)
    if len(arr) < 4:
        return ToolResult(name="stl_strength", success=False, data={}, error="series too short for STL")
    period = int(arguments.get("period", 0))
    if period <= 1:
        fft = _fft_period({}, series)
        if not fft.success:
            return ToolResult(name="stl_strength", success=False, data={}, error=fft.error or "FFT period failed")
        period = int(fft.data["dominant_period"]) if fft.data.get("dominant_period") else max(2, len(arr) // 8)
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
        return ToolResult(
            name="stl_strength",
            success=True,
            data={"period": period, "seasonal_strength": seasonal_strength, "trend_strength": trend_strength},
        )
    except Exception as e:  # noqa: BLE001
        return ToolResult(name="stl_strength", success=False, data={}, error=str(e))


def _stationarity(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    arr = _primary(series)
    try:
        from statsmodels.tsa.stattools import adfuller

        stat, pvalue, *_ = adfuller(arr, autolag="AIC")
        if not (np.isfinite(stat) and np.isfinite(pvalue)):
            return ToolResult(name="adf_stationarity", success=False, data={}, error="ADF produced non-finite stats")
        return ToolResult(
            name="adf_stationarity",
            success=True,
            data={"adf_stat": float(stat), "pvalue": float(pvalue), "is_stationary_at_5pct": bool(pvalue < 0.05)},
        )
    except Exception as e:  # noqa: BLE001
        return ToolResult(name="adf_stationarity", success=False, data={}, error=str(e))


def _change_points(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    arr = _primary(series)
    window = max(5, len(arr) // 20)
    scores = []
    for i in range(window, len(arr) - window):
        left = arr[i - window : i]
        right = arr[i : i + window]
        scores.append((i, abs(float(np.mean(right) - np.mean(left)))))
    scores.sort(key=lambda x: x[1], reverse=True)
    top = scores[:5]
    return ToolResult(name="change_points", success=True, data={"candidates": [{"index": i, "score": s} for i, s in top]})


def _interval_compare(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    arr = _primary(series)
    n = len(arr)
    start = int(arguments.get("start", 0))
    mid = int(arguments.get("mid", n // 2))
    end = int(arguments.get("end", n))
    # Clamp and enforce start <= mid <= end to avoid empty/inverted slices yielding NaNs.
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
            error="interval bounds produced an empty side after clamping",
        )
    return ToolResult(
        name="interval_compare",
        success=True,
        data={
            "left_mean": float(np.mean(a)),
            "right_mean": float(np.mean(b)),
            "left_std": float(np.std(a)),
            "right_std": float(np.std(b)),
            "mean_delta": float(np.mean(b) - np.mean(a)),
            "start": start,
            "mid": mid,
            "end": end,
        },
    )


def _lag_corr(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    if len(series) < 2:
        arr = _primary(series)
        lag = int(arguments.get("lag", 1))
        if lag <= 0:
            return ToolResult(name="lag_corr", success=False, data={}, error="auto lag must be >= 1")
        if lag >= len(arr):
            return ToolResult(name="lag_corr", success=False, data={}, error="lag too large")
        c, err = _safe_corr(arr[:-lag], arr[lag:])
        if err:
            return ToolResult(name="lag_corr", success=False, data={}, error=err)
        return ToolResult(name="lag_corr", success=True, data={"mode": "auto", "lag": lag, "corr": c})
    a = np.asarray(series[0], dtype=float)
    b = np.asarray(series[1], dtype=float)
    n = min(len(a), len(b))
    raw_lag = int(arguments.get("lag", 0))
    if abs(raw_lag) >= n:
        return ToolResult(name="lag_corr", success=False, data={}, error="lag too large")
    if raw_lag == 0:
        left, right = a[:n], b[:n]
    elif raw_lag > 0:
        left, right = a[: n - raw_lag], b[raw_lag:n]
    else:
        lag = -raw_lag
        left, right = a[lag:n], b[: n - lag]
    c, err = _safe_corr(left, right)
    if err:
        return ToolResult(name="lag_corr", success=False, data={}, error=err)
    return ToolResult(name="lag_corr", success=True, data={"mode": "cross", "lag": raw_lag, "corr": c})


def _pairwise_distance(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    method = arguments.get("method", "euclidean")
    if len(series) < 2:
        return ToolResult(name="pairwise_distance", success=False, data={}, error="Need >=2 series")
    ref = np.asarray(series[0], dtype=float)
    distances = []
    for i, s in enumerate(series[1:], start=2):
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
            # z-normalize then euclidean; constant series keep raw scale distance
            sa, sb = float(np.std(a)), float(np.std(b))
            if sa >= _VARIANCE_EPS:
                a = (a - np.mean(a)) / sa
            if sb >= _VARIANCE_EPS:
                b = (b - np.mean(b)) / sb
            dist = float(np.linalg.norm(a - b))
        if not np.isfinite(dist):
            return ToolResult(name="pairwise_distance", success=False, data={}, error=f"non-finite distance for series {i}")
        distances.append({"series_index": i, "distance": dist})
    best = min(distances, key=lambda x: x["distance"]) if distances else None
    return ToolResult(name="pairwise_distance", success=True, data={"method": method, "distances": distances, "nearest": best})


def _smooth_reverse(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    arr = _primary(series)
    window = int(arguments.get("window", 5))
    window = max(1, min(window, len(arr)))
    kernel = np.ones(window) / window
    smoothed = np.convolve(arr, kernel, mode="same")
    return ToolResult(
        name="smooth_reverse_stats",
        success=True,
        data={
            "smooth_mean": float(np.mean(smoothed)),
            "reverse_start_end_delta": float(arr[::-1][-1] - arr[::-1][0]),
            "original_start_end_delta": float(arr[-1] - arr[0]),
        },
    )


def _subsequence_locate(arguments: Dict[str, Any], series: List[List[float]]) -> ToolResult:
    if len(series) < 2:
        return ToolResult(name="subsequence_locate", success=False, data={}, error="Need query and longer series")
    query = np.asarray(series[0], dtype=float)
    long = np.asarray(series[1], dtype=float)
    if len(query) > len(long):
        query, long = long, query
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
    return ToolResult(name="subsequence_locate", success=True, data={"best_start": best_i, "distance": best_d, "query_len": len(query)})


def build_default_registry() -> ToolRegistry:
    reg = ToolRegistry()
    specs = [
        (ToolSpec(name="describe_series", description="Basic descriptive stats for each series.", roles=["short", "medium", "long", "structure", "alignment", "reasoning", "matching"]), _describe),
        (ToolSpec(name="sliding_stats", description="Sliding-window mean/std for local volatility.", roles=["short", "structure"]), _sliding_stats),
        (ToolSpec(name="diff_stats", description="First-difference stats and sign changes.", roles=["short", "structure"]), _diff_stats),
        (ToolSpec(name="local_extrema", description="Count local peaks and troughs.", roles=["short", "structure", "matching"]), _local_extrema),
        (ToolSpec(name="autocorr", description="Autocorrelation up to max_lag.", roles=["short", "medium", "long", "structure"]), _acf),
        (ToolSpec(name="fft_period", description="Dominant period via FFT.", roles=["medium", "structure", "matching"]), _fft_period),
        (ToolSpec(name="stl_strength", description="STL seasonal/trend strength.", roles=["medium", "long", "structure"]), _stl_strength),
        (ToolSpec(name="adf_stationarity", description="ADF stationarity test.", roles=["long", "structure", "reasoning"]), _stationarity),
        (ToolSpec(name="change_points", description="Mean-shift change-point candidates.", roles=["medium", "long", "structure", "reasoning"]), _change_points),
        (ToolSpec(name="interval_compare", description="Compare left/right interval statistics.", roles=["reasoning", "structure"]), _interval_compare),
        (ToolSpec(name="lag_corr", description="Auto or cross lag correlation.", roles=["reasoning", "structure"]), _lag_corr),
        (ToolSpec(name="pairwise_distance", description="Distance from series1 to others (euclidean/dtw).", roles=["matching", "alignment"]), _pairwise_distance),
        (ToolSpec(name="smooth_reverse_stats", description="Smoothing and reverse-direction stats.", roles=["matching"]), _smooth_reverse),
        (ToolSpec(name="subsequence_locate", description="Locate best matching subsequence.", roles=["matching"]), _subsequence_locate),
    ]
    for spec, fn in specs:
        reg.register(spec, fn)
    return reg
