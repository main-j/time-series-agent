from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

import pandas as pd

from ts_agent.schemas.models import MMTSSample, SubsetName

SUBSET_FILES = {
    SubsetName.BASE: ["Benchmark/Base/synthtic_qa_700.csv"],
    SubsetName.INWILD: ["Benchmark/InWild/tsqa_1084.csv"],
    SubsetName.MATCH: ["Benchmark/Match/qats_400.csv"],
    SubsetName.ALIGN: [
        "Benchmark/Align/ts2caption_qa_120.csv",
        "Benchmark/Align/caption2ts_qa_120.csv",
    ],
}


def _parse_series(value: Any) -> List[List[float]]:
    if isinstance(value, list):
        obj = value
    else:
        obj = ast.literal_eval(str(value))
    if obj and isinstance(obj[0], (int, float)):
        return [[float(x) for x in obj]]
    series: List[List[float]] = []
    for item in obj:
        if isinstance(item, (int, float)):
            return [[float(x) for x in obj]]
        series.append([float(x) for x in item])
    return series


def format_raw_value_text(value: Any, max_chars: Optional[int] = None) -> tuple[str, bool]:
    """Exact official Text formatting on raw CSV `value` (before series normalize).

    Returns (text, truncated).
    """
    obj = value if isinstance(value, list) else ast.literal_eval(str(value))
    if len(obj) > 10:
        text = f"Given Time Series: {obj}"
    else:
        text = "\n".join(f"Given Time Series {i + 1}: {val}" for i, val in enumerate(obj))
    truncated = False
    if max_chars is not None and len(text) > max_chars:
        text = text[: max_chars - 20] + "\n...[truncated]..."
        truncated = True
    return text, truncated


def format_series_text(series: List[List[float]], max_chars: Optional[int] = None) -> str:
    """Best-effort formatting from normalized series.

    Prefer `format_raw_value_text` for MMTS fidelity: flat univariate vs ``[[...]]``
    become identical after `_parse_series`, so raw formatting is required there.
    """
    if len(series) == 1:
        text, _ = format_raw_value_text(series[0], max_chars=max_chars)
        return text
    text, _ = format_raw_value_text(series, max_chars=max_chars)
    return text


def infer_series_roles(subset: SubsetName, source_file: str, n_series: int) -> Dict[str, Any]:
    """Structured query/candidate/alignment roles for MMTS subsets."""
    roles: Dict[str, Any] = {
        "n_series": n_series,
        "query_series_index": 1 if n_series >= 1 else None,
        "candidate_series_indices": [],
        "align_direction": None,
        "option_to_series": {},
    }
    src = source_file.replace("\\", "/")
    if subset == SubsetName.MATCH and n_series >= 2:
        # TS1 = query; TS2..TSN map to options A..
        roles["query_series_index"] = 1
        roles["candidate_series_indices"] = list(range(2, n_series + 1))
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for i, sid in enumerate(roles["candidate_series_indices"]):
            if i < len(letters):
                roles["option_to_series"][letters[i]] = sid
    elif subset == SubsetName.ALIGN:
        if "caption2ts" in src:
            roles["align_direction"] = "caption2ts"
            roles["query_series_index"] = None  # query is text in question
            roles["candidate_series_indices"] = list(range(1, n_series + 1))
            letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            for i, sid in enumerate(roles["candidate_series_indices"]):
                if i < len(letters):
                    roles["option_to_series"][letters[i]] = sid
        else:
            roles["align_direction"] = "ts2caption"
            roles["query_series_index"] = 1
            roles["candidate_series_indices"] = []
    elif n_series >= 2:
        roles["candidate_series_indices"] = list(range(1, n_series + 1))
    return roles


def extract_focus_intervals(question: str) -> List[List[int]]:
    """Best-effort parse of index windows mentioned in the question."""
    q = question or ""
    patterns = [
        r"indices?\s+(\d+)\s*[-–—to]+\s*(\d+)",
        r"index\s+(\d+)\s*[-–—to]+\s*index\s+(\d+)",
        r"from\s+index\s+(\d+)\s+to\s+index\s+(\d+)",
        r"between\s+indices?\s+(\d+)\s+and\s+(\d+)",
        r"segment\s+from\s+index\s+(\d+)[-–—]\s*(\d+)",
    ]
    out: List[List[int]] = []
    for pat in patterns:
        for m in re.finditer(pat, q, flags=re.IGNORECASE):
            a, b = int(m.group(1)), int(m.group(2))
            if b < a:
                a, b = b, a
            pair = [a, b]
            if pair not in out:
                out.append(pair)
    return out


def infer_question_type(qa_type: str, option: Any, answer: Any) -> str:
    qa = str(qa_type or "").lower()
    if option is None or (isinstance(option, float) and pd.isna(option)) or str(option).strip() == "":
        ans = str(answer)
        if re.fullmatch(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", ans.strip()) or "numerical" in qa:
            return "numerical"
    if "numerical" in qa:
        return "numerical"
    return "choice"


def fingerprint_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


class MMTSBenchAdapter:
    def __init__(self, raw_dir: str | Path, schema_version: str = "1.0"):
        self.raw_dir = Path(raw_dir)
        self.schema_version = schema_version

    def iter_raw_rows(self, subsets: Optional[Sequence[str]] = None) -> Iterable[Dict[str, Any]]:
        selected = [SubsetName(s) for s in subsets] if subsets else list(SubsetName)
        for subset in selected:
            for rel in SUBSET_FILES[subset]:
                path = self.raw_dir / rel
                if not path.exists():
                    raise FileNotFoundError(path)
                fp = fingerprint_file(path)
                df = pd.read_csv(path)
                for idx, row in df.iterrows():
                    yield {
                        "subset": subset,
                        "source_file": str(path.relative_to(self.raw_dir)),
                        "row_index": int(idx),
                        "row": row.to_dict(),
                        "file_fingerprint": fp,
                    }

    def row_to_sample(self, payload: Dict[str, Any], max_series_text_chars: Optional[int] = 8000) -> MMTSSample:
        row = payload["row"]
        series = _parse_series(row.get("value"))
        option = row.get("option")
        if isinstance(option, float) and pd.isna(option):
            option = None
        answer = str(row.get("answer"))
        qa_type = str(row.get("qa_type", ""))
        sample_id = f"{payload['subset'].value}:{Path(payload['source_file']).stem}:{payload['row_index']}"
        series_text, truncated = format_raw_value_text(row.get("value"), max_chars=max_series_text_chars)
        roles = infer_series_roles(payload["subset"], payload["source_file"], len(series))
        focus = extract_focus_intervals(str(row.get("question", "")))
        return MMTSSample(
            sample_id=sample_id,
            source_file=payload["source_file"],
            row_index=payload["row_index"],
            subset=payload["subset"],
            num=row.get("num"),
            qa_type=qa_type,
            question_type=infer_question_type(qa_type, option, answer),
            local_overall=str(row.get("local_overall", "")),
            task_type=row.get("task_type"),
            question=str(row.get("question", "")),
            option=None if option is None else str(option),
            answer=answer,
            domain=None if pd.isna(row.get("domain")) else str(row.get("domain")),
            freq=None if pd.isna(row.get("freq")) else str(row.get("freq")),
            is_univariate=None if pd.isna(row.get("is_univariate")) else bool(row.get("is_univariate")),
            stationarity=row.get("stationarity"),
            series=series,
            series_text=series_text,
            metadata={
                "file_fingerprint": payload.get("file_fingerprint"),
                "schema_version": self.schema_version,
                "ts_id": row.get("ts_id"),
                "n_series": len(series),
                "series_lengths": [len(s) for s in series],
                "series_truncated": truncated,
                "max_series_text_chars": max_series_text_chars,
                "focus_intervals": focus,
                "index_base": 0,
                **roles,
            },
        )

    def build_processed(self, out_dir: str | Path, subsets: Optional[Sequence[str]] = None) -> Path:
        """Write lightweight index only (no series) to avoid OOM."""
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        index_rows: List[Dict[str, Any]] = []
        fingerprints: Dict[str, str] = {}
        for payload in self.iter_raw_rows(subsets):
            row = payload["row"]
            option = row.get("option")
            if isinstance(option, float) and pd.isna(option):
                option = None
            answer = str(row.get("answer"))
            qa_type = str(row.get("qa_type", ""))
            sample_id = f"{payload['subset'].value}:{Path(payload['source_file']).stem}:{payload['row_index']}"
            index_rows.append(
                {
                    "sample_id": sample_id,
                    "source_file": payload["source_file"],
                    "row_index": payload["row_index"],
                    "subset": payload["subset"].value,
                    "num": row.get("num"),
                    "qa_type": qa_type,
                    "question_type": infer_question_type(qa_type, option, answer),
                    "local_overall": str(row.get("local_overall", "")),
                    "task_type": row.get("task_type"),
                    "domain": None if pd.isna(row.get("domain")) else str(row.get("domain")),
                    "answer": answer,
                }
            )
            fingerprints[payload["source_file"]] = payload["file_fingerprint"]
        manifest = {
            "schema_version": self.schema_version,
            "n_samples": len(index_rows),
            "source_fingerprints": fingerprints,
            "subsets": sorted({s["subset"] for s in index_rows}),
            "storage": "index_plus_raw_lazy",
        }
        (out / "index.jsonl").write_text(
            "\n".join(json.dumps(s, ensure_ascii=False) for s in index_rows) + "\n",
            encoding="utf-8",
        )
        (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        counts: Dict[str, int] = {}
        for s in index_rows:
            counts[s["subset"]] = counts.get(s["subset"], 0) + 1
        (out / "counts.json").write_text(json.dumps(counts, indent=2), encoding="utf-8")
        # keep compatibility stub
        (out / "samples.jsonl").write_text(
            "# deprecated: use index.jsonl + lazy raw loading\n",
            encoding="utf-8",
        )
        return out


class MMTSBenchDataset:
    """Lazy dataset: index in memory, series loaded from raw CSV on demand."""

    def __init__(
        self,
        processed_dir: str | Path,
        raw_dir: Optional[str | Path] = None,
        max_series_text_chars: Optional[int] = 8000,
    ):
        self.processed_dir = Path(processed_dir)
        self.raw_dir = Path(raw_dir) if raw_dir else self.processed_dir.parent.parent / "raw" / "mmts-bench"
        self.adapter = MMTSBenchAdapter(self.raw_dir)
        self.max_series_text_chars = max_series_text_chars
        self.index: List[Dict[str, Any]] = []
        index_path = self.processed_dir / "index.jsonl"
        if not index_path.exists():
            raise FileNotFoundError(f"Processed index not found: {index_path}. Run preprocess.")
        with index_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    self.index.append(json.loads(line))
        self._csv_cache: Dict[str, pd.DataFrame] = {}

    def _load_csv(self, source_file: str) -> pd.DataFrame:
        if source_file not in self._csv_cache:
            if len(self._csv_cache) >= 1:
                self._csv_cache.clear()
            self._csv_cache[source_file] = pd.read_csv(self.raw_dir / source_file)
        return self._csv_cache[source_file]

    def get(self, meta: Dict[str, Any]) -> MMTSSample:
        df = self._load_csv(meta["source_file"])
        row = df.iloc[int(meta["row_index"])].to_dict()
        payload = {
            "subset": SubsetName(meta["subset"]),
            "source_file": meta["source_file"],
            "row_index": int(meta["row_index"]),
            "row": row,
        }
        return self.adapter.row_to_sample(payload, max_series_text_chars=self.max_series_text_chars)

    def filter(
        self,
        subsets: Optional[Sequence[str]] = None,
        sample_ids: Optional[Sequence[str]] = None,
        limit: Optional[int] = None,
        question_type: Optional[str] = None,
        stratified: bool = False,
    ) -> List[MMTSSample]:
        rows = self.index
        if subsets:
            subset_set = set(subsets)
            rows = [s for s in rows if s["subset"] in subset_set]
        if sample_ids:
            id_set = set(sample_ids)
            rows = [s for s in rows if s["sample_id"] in id_set]
        if question_type:
            rows = [s for s in rows if s.get("question_type") == question_type]
        if limit is not None:
            if stratified:
                from collections import defaultdict

                buckets: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
                for s in rows:
                    buckets[s["subset"]].append(s)
                keys = sorted(buckets.keys())
                if not keys:
                    return []
                per = max(1, limit // len(keys))
                selected: List[Dict[str, Any]] = []
                for k in keys:
                    selected.extend(buckets[k][:per])
                rows = selected[:limit]
            else:
                rows = rows[:limit]
        return [self.get(r) for r in rows]

    def __len__(self) -> int:
        return len(self.index)
