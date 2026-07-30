"""Validate Baseline group against plan + MMTS official Text requirements."""
from __future__ import annotations

import ast
import json
import random
from pathlib import Path

import pandas as pd
import pytest

from ts_agent.agents.roles import BaselineAgent
from ts_agent.core.llm import LLMProvider, LLMResponse, MockLLMProvider
from ts_agent.data.mmts import MMTSBenchDataset, _parse_series, format_raw_value_text
from ts_agent.pipelines.experiment import ExperimentPipeline
from ts_agent.prompts.library import PromptLibrary

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "prompts"


def _official_series_text(raw_value: str) -> str:
    value_list = ast.literal_eval(str(raw_value))
    if len(value_list) > 10:
        return f"Given Time Series: {value_list}"
    return "\n".join(f"Given Time Series {i + 1}: {val}" for i, val in enumerate(value_list))


class CaptureLLM(LLMProvider):
    def __init__(self, text: str):
        super().__init__()
        self.text = text
        self.messages = None

    def generate(self, messages, **kwargs):
        self.call_count += 1
        self.messages = messages
        return LLMResponse(text=self.text, raw={})


@pytest.fixture
def ds():
    return MMTSBenchDataset(
        ROOT / "data/processed/mmts-bench",
        raw_dir=ROOT / "data/raw/mmts-bench",
        max_series_text_chars=None,
    )


@pytest.fixture
def prompts():
    return PromptLibrary(str(PROMPTS))


def test_series_text_matches_official_on_random_mmts(ds):
    rng = random.Random(7)
    metas = rng.sample(ds.index, 20)
    mismatches = []
    for meta in metas:
        df = pd.read_csv(ROOT / "data/raw/mmts-bench" / meta["source_file"])
        raw = str(df.iloc[int(meta["row_index"])]["value"])
        official = _official_series_text(raw)
        ours = format_raw_value_text(raw, max_chars=None)
        if official != ours:
            mismatches.append(meta["sample_id"])
    assert mismatches == [], f"series format mismatches: {mismatches[:5]}"

    # Also verify dataset-loaded series_text matches official (no truncation).
    sample = ds.get(metas[0])
    df = pd.read_csv(ROOT / "data/raw/mmts-bench" / metas[0]["source_file"])
    raw = str(df.iloc[int(metas[0]["row_index"])]["value"])
    assert sample.series_text == _official_series_text(raw)


def test_baseline_prompt_and_single_shot_behavior(ds, prompts):
    sample = ds.get(ds.index[0])
    llm = CaptureLLM(
        "<thinking_process>\nanalysis\n</thinking_process>\n<final_answer>\nC\n</final_answer>"
    )
    pred, raw = BaselineAgent(llm, prompts).run(sample)
    sys_p, user_p = llm.messages[0]["content"], llm.messages[1]["content"]

    assert llm.call_count == 1
    assert pred == "C"
    assert "<question>" in user_p and "<timeseries>" in user_p and "<candidates>" in user_p
    assert "tool_catalog" not in user_p and "tool_results" not in user_p
    assert "temporal_profile" not in user_p.lower()
    assert "<final_answer>" in sys_p
    assert "Do not make up information" in sys_p or "not provided" in sys_p.lower()
    # choice instruction present
    assert "letter" in sys_p.lower() or "options" in sys_p.lower()


def test_baseline_numerical_parse(ds, prompts):
    numerical = None
    for meta in ds.index:
        s = ds.get(meta)
        if s.question_type == "numerical":
            numerical = s
            break
    assert numerical is not None
    llm = CaptureLLM("<thinking_process>x</thinking_process><final_answer>\n12.5\n</final_answer>")
    pred, _ = BaselineAgent(llm, prompts).run(numerical)
    assert pred == "12.5"


def test_baseline_pipeline_no_tools_on_stratified(ds):
    rng = random.Random(11)
    by = {}
    for m in ds.index:
        by.setdefault(m["subset"], []).append(m)
    metas = []
    for subset in ["Base", "InWild", "Match", "Align"]:
        metas.append(rng.choice(by[subset]))
    pipe = ExperimentPipeline(MockLLMProvider(), str(PROMPTS))
    for meta in metas:
        sample = ds.get(meta)
        # force choice-like mock success path: skip pure numerical for mock letter outputs
        if sample.question_type != "choice":
            continue
        tr = pipe.run_baseline(sample)
        assert tr.tool_calls == 0
        assert tr.model_calls == 1
        assert tr.success
        assert tr.predicted_answer
