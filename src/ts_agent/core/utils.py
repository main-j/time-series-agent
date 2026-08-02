from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def extract_json_object(text: str) -> Dict[str, Any]:
    """Extract and parse the first JSON object from model output."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError(f"No JSON object found in model output: {text[:300]}")
    candidate = match.group(0)
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        # common fixes: trailing commas
        fixed = re.sub(r",\s*([}\]])", r"\1", candidate)
        return json.loads(fixed)


def parse_model(text: str, model_cls: Type[T]) -> T:
    data = extract_json_object(text)
    return model_cls.model_validate(data)


def extract_final_answer_letter(text: str) -> Optional[str]:
    m = re.search(r"<final_answer>\s*([A-Za-z])\s*</final_answer>", text, re.I)
    if m:
        return m.group(1).upper()
    m = re.search(r"Final answer is\s*:\s*([A-Za-z])", text, re.I)
    if m:
        return m.group(1).upper()
    m = re.search(r"\b([A-D])\b\s*$", text.strip())
    if m:
        return m.group(1).upper()
    m = re.search(r"(?:answer|option)\s*[:=\-]?\s*([A-D])\b", text, re.I)
    if m:
        return m.group(1).upper()
    return None


def extract_numerical_answer(text: str) -> Optional[str]:
    m = re.search(r"<final_answer>\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*</final_answer>", text)
    if m:
        return m.group(1)
    m = re.search(r"Final answer is\s*:\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)", text, re.I)
    if m:
        return m.group(1)
    m = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", text)
    return m.group(0) if m else None


def stable_hash(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_yaml(path: Path) -> Dict[str, Any]:
    import yaml

    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


class DiskCache:
    def __init__(self, root: Path):
        self.root = ensure_dir(root)

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        path = self.root / f"{key}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def set(self, key: str, value: Dict[str, Any]) -> None:
        path = self.root / f"{key}.json"
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
