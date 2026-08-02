from pathlib import Path

from ts_agent.core.llm import MockLLMProvider
from ts_agent.data.mmts import MMTSBenchAdapter, MMTSBenchDataset
from ts_agent.pipelines.experiment import ExperimentPipeline


RAW = Path("/root/autodl-tmp/time-series-agent/data/raw/mmts-bench")
PROC = Path("/root/autodl-tmp/time-series-agent/data/processed/mmts-bench")
PROMPTS = Path("/root/autodl-tmp/time-series-agent/prompts")


def test_adapter_and_pipeline_smoke():
    adapter = MMTSBenchAdapter(RAW)
    adapter.build_processed(PROC)
    ds = MMTSBenchDataset(PROC, raw_dir=RAW)
    assert len(ds) > 1000
    sample = ds.filter(limit=1)[0]
    pipe = ExperimentPipeline(MockLLMProvider(), str(PROMPTS), max_tool_rounds=2)
    base = pipe.run_baseline(sample)
    arch = pipe.run_architecture(sample)
    assert base.experiment == "baseline"
    assert arch.experiment == "architecture"
    assert arch.model_calls >= 1
