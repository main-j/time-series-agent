from __future__ import annotations

import json
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ts_agent.core.utils import DiskCache, stable_hash


@dataclass
class LLMResponse:
    text: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_sec: float = 0.0
    raw: Dict[str, Any] = field(default_factory=dict)


class LLMProvider(ABC):
    def __init__(self):
        self.call_count = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.call_log: List[Dict[str, Any]] = []
        self.record_io: bool = False

    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], **kwargs: Any) -> LLMResponse:
        raise NotImplementedError

    def reset_stats(self) -> None:
        self.call_count = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.call_log = []

    def _maybe_record(
        self,
        messages: List[Dict[str, str]],
        resp: LLMResponse,
        *,
        call_tag: str = "",
        cached: bool = False,
    ) -> None:
        if not self.record_io:
            return
        self.call_log.append(
            {
                "call_index": len(self.call_log) + 1,
                "call_tag": call_tag or "unknown",
                "cached": cached,
                "messages": messages,
                "response_text": resp.text,
                "prompt_tokens": resp.prompt_tokens,
                "completion_tokens": resp.completion_tokens,
                "latency_sec": resp.latency_sec,
                "raw": resp.raw,
            }
        )


class MockLLMProvider(LLMProvider):
    """Deterministic mock used for pipeline smoke tests without GPU."""

    def generate(self, messages: List[Dict[str, str]], **kwargs: Any) -> LLMResponse:
        self.call_count += 1
        joined = "\n".join(m.get("content", "") for m in messages)
        role_hint = joined.lower()
        t0 = time.time()
        has_tool_results = "<tool_results>" in joined and "(none)" not in joined.split("<tool_results>")[-1][:80]
        call_tag = str(kwargs.get("call_tag", "mock"))

        if "agentplan" in role_hint or ("execution plan" in role_hint and "planner" in role_hint):
            text = self._plan(joined)
        elif ":s1s2:" in call_tag or "evidencecapabilityplan" in role_hint or "evidence planning + capability" in role_hint:
            text = self._stage_s1s2(joined, call_tag)
        elif ":s3:" in call_tag or "toolworkflow" in role_hint or "tool workflow planning" in role_hint:
            text = self._stage_s3(joined, call_tag)
        elif ":s4:" in call_tag or "invocationplan" in role_hint or "stage 4: tool invocation" in role_hint:
            text = self._stage_s4(joined, call_tag)
        elif ":s5:" in call_tag and "homogeneous" in call_tag:
            text = self._stage_homo_s5(joined, call_tag)
        elif ":s5:" in call_tag and "heterogeneous" in call_tag:
            text = self._stage_hetero_s5(joined, call_tag)
        elif "scaleobservation" in role_hint or "-scale homogeneous" in role_hint or "short-scale" in role_hint or "medium-scale" in role_hint or "long-scale" in role_hint:
            text = self._scale(joined, has_tool_results)
        elif "taskevidence" in role_hint or "heterogeneous task agent" in role_hint:
            text = self._task(joined, has_tool_results)
        elif "finalanswer" in role_hint or "integration agent" in role_hint:
            text = self._final(joined)
        else:
            text = (
                "<thinking_process>\nMock baseline reasoning.\n</thinking_process>\n"
                "<final_answer>\nA\n</final_answer>"
            )
        latency = time.time() - t0
        prompt_tokens = max(1, len(joined) // 4)
        completion_tokens = max(1, len(text) // 4)
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        resp = LLMResponse(
            text=text,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_sec=latency,
            raw={"provider": "mock"},
        )
        self._maybe_record(messages, resp, call_tag=call_tag)
        return resp

    def _stage_s1s2(self, joined: str, call_tag: str) -> str:
        is_hetero = "heterogeneous" in call_tag or "heterogeneous" in joined.lower()
        if is_hetero and "<temporal_profile>" in joined:
            # Prefer no-tool when profile already present (smoke path)
            return json.dumps(
                {
                    "reasoning": "Mock: use temporal profile; no new tools.",
                    "evidence_plan": {
                        "objective": "reconcile profile",
                        "claims_to_support": [{"claim": "profile sufficient", "required_evidence": ["upstream stats"]}],
                    },
                    "capability_selection": {
                        "selected_tools": [],
                        "no_tool_decision": {
                            "skip_tools": True,
                            "reason": "Mock temporal profile already has evidence",
                            "evidence_sources": [{"type": "upstream_observation", "ref": "medium:step1", "field": "stats"}],
                        },
                    },
                }
            )
        tool = "describe_series"
        if "medium" in call_tag:
            tool = "fft_period"
        elif "long" in call_tag:
            tool = "adf_stationarity"
        elif "matching" in call_tag:
            tool = "pairwise_distance"
        return json.dumps(
            {
                "reasoning": "Mock evidence+capability plan.",
                "evidence_plan": {
                    "objective": "gather evidence",
                    "claims_to_support": [{"claim": "basic structure", "required_evidence": ["stats"]}],
                    "analysis_scope": {},
                },
                "capability_selection": {
                    "selected_tools": [{"tool": tool, "reason": "mock", "supports_evidence": ["stats"]}],
                    "no_tool_decision": None,
                },
            }
        )

    def _stage_s3(self, joined: str, call_tag: str) -> str:
        tools = re.findall(r'"tool":\s*"([a-z_]+)"', joined)
        # Prefer selected_tools section tools
        selected = []
        for m in re.finditer(r'"selected_tools"\s*:\s*\[(.*?)\]', joined, flags=re.S):
            selected = re.findall(r'"tool":\s*"([a-z_]+)"', m.group(1))
            break
        names = selected or tools[:2] or ["describe_series"]
        # dedupe preserving order
        seen = []
        for n in names:
            if n not in seen and n not in {"string"}:
                seen.append(n)
        if not seen:
            seen = ["describe_series"]
        workflow = [
            {"step": i + 1, "tool": name, "output_key": name, "input_binding": {}}
            for i, name in enumerate(seen[:3])
        ]
        return json.dumps({"reasoning": "Mock workflow.", "workflow": workflow})

    def _stage_s4(self, joined: str, call_tag: str) -> str:
        steps = re.findall(r'"step":\s*(\d+).*?"tool":\s*"([a-z_]+)"', joined, flags=re.S)
        if not steps:
            tools = re.findall(r'"tool":\s*"([a-z_]+)"', joined)
            steps = [(str(i + 1), t) for i, t in enumerate(tools[:3])]
        calls = []
        for step, tool in steps:
            args: Dict[str, Any] = {}
            if tool != "describe_series":
                args["series_index"] = 1
            if tool == "pairwise_distance":
                args = {"method": "euclidean"}
            if tool == "cross_series_compare":
                args = {"series_index_1": 1, "series_index_2": 2}
            calls.append({"step": int(step), "tool": tool, "args": args})
        if not calls:
            calls = [{"step": 1, "tool": "describe_series", "args": {}}]
        return json.dumps({"reasoning": "Mock invocation.", "calls": calls})

    def _stage_homo_s5(self, joined: str, call_tag: str) -> str:
        scale = "short"
        for s in ("short", "medium", "long"):
            if f":{s}:" in call_tag or f"scale={s}" in joined.lower():
                scale = s
        call_ids = re.findall(r'"call_id":\s*"([^"]+)"', joined)
        return json.dumps(
            {
                "reasoning": "Mock homo S5 integration.",
                "scale": scale,
                "observations": ["Mock observation after staged tools."],
                "evidence_intervals": [],
                "confidence": 0.55,
                "tool_calls": [],
                "structured_observations": [
                    {
                        "claim": "structure observed",
                        "evidence": [
                            {
                                "type": "stats",
                                "value": True,
                                "call_id": call_ids[0] if call_ids else None,
                                "provenance": "tool" if call_ids else "unresolved",
                            }
                        ],
                        "confidence": "tool_supported" if call_ids else "unresolved",
                    }
                ],
                "coverage": {"stats": "tool_supported" if call_ids else "unresolved"},
                "unresolved_claims": [],
            }
        )

    def _stage_hetero_s5(self, joined: str, call_tag: str) -> str:
        role = "structure"
        m = re.search(r"role=([a-z_]+)", joined.lower())
        if m:
            role = m.group(1)
        for r in ("matching", "alignment", "reasoning", "structure"):
            if f":{r}:" in call_tag:
                role = r
        prefs = re.findall(r'"candidate_preference":\s*"([A-D])"', joined)
        pref = prefs[-1] if prefs else "A"
        cites = re.findall(r'"call_id":\s*"([^"]+)"', joined)
        return json.dumps(
            {
                "reasoning": "Mock hetero S5 integration.",
                "role": role,
                "hypothesis": "mock",
                "evidence": ["Mock evidence"],
                "candidate_preference": pref,
                "confidence": 0.6,
                "tool_calls": [],
                "cited_tool_call_ids": cites[:3],
                "executed_tools": [],
                "tool_summaries": [],
                "reasoning_claims": [],
                "coverage": {},
                "unresolved_claims": [],
            }
        )

    def _plan(self, joined: str) -> str:
        text = joined.lower()
        roles = ["structure"]
        if any(k in text for k in ["match", "similar", "candidate sequence", "reverse", "smooth"]):
            roles = ["matching"]
        elif any(k in text for k in ["caption", "description", "corresponds to the data"]):
            roles = ["alignment"]
        elif any(k in text for k in ["causal", "inductive", "deductive", "counterfactual", "analog"]):
            roles = ["reasoning", "structure"]
        else:
            roles = ["structure", "reasoning"]
        return json.dumps(
            {
                "reasoning": "Mock planner routes by keywords.",
                "capability": roles[0],
                "scope": "local" if "local_overall=local" in text else "overall",
                "univariate": True,
                "scales": ["short", "medium", "long"],
                "heterogeneous_agents": roles,
                "notes": "mock",
            }
        )

    def _scale(self, joined: str, has_tool_results: bool) -> str:
        scale = "short"
        if "medium-scale" in joined.lower() or 'scale": "medium"' in joined.lower() or "scale=medium" in joined.lower():
            scale = "medium"
        if "long-scale" in joined.lower() or "for the long scale" in joined.lower():
            scale = "long"
        # detect from prompt "Produce ... {scale} scale"
        m = re.search(r"for the (short|medium|long) scale", joined.lower())
        if m:
            scale = m.group(1)
        tool_calls = [] if has_tool_results else [{"name": "describe_series", "arguments": {}}]
        if scale == "medium" and not has_tool_results:
            tool_calls = [{"name": "fft_period", "arguments": {}}]
        if scale == "long" and not has_tool_results:
            tool_calls = [{"name": "adf_stationarity", "arguments": {}}]
        obs = ["Mock observation after tools." ] if has_tool_results else ["Need tool evidence."]
        return json.dumps(
            {
                "reasoning": "Mock scale analysis.",
                "scale": scale,
                "observations": obs,
                "evidence_intervals": [],
                "confidence": 0.55,
                "tool_calls": tool_calls,
                "tool_summaries": [],
            }
        )

    def _task(self, joined: str, has_tool_results: bool) -> str:
        role = "structure"
        if "role=matching" in joined.lower() or "role\": \"matching\"" in joined.lower():
            role = "matching"
        elif "role=alignment" in joined.lower():
            role = "alignment"
        elif "role=reasoning" in joined.lower():
            role = "reasoning"
        m = re.search(r"role=([a-z_]+)", joined.lower())
        if m:
            role = m.group(1)
        tool_calls = []
        if not has_tool_results:
            if role == "matching":
                tool_calls = [{"name": "pairwise_distance", "arguments": {"method": "euclidean"}}]
            else:
                tool_calls = [{"name": "describe_series", "arguments": {}}]
        pref = "A"
        if "nearest" in joined and "series_index" in joined:
            mm = re.search(r'"series_index":\s*(\d+)', joined)
            if mm:
                idx = int(mm.group(1))
                # series_index 2 => option A in Match templates (Time Series 2)
                pref = chr(ord("A") + max(0, idx - 2))
        return json.dumps(
            {
                "reasoning": "Mock task evidence.",
                "role": role,
                "evidence": ["Mock evidence from tools" if has_tool_results else "Awaiting tools"],
                "candidate_preference": pref,
                "confidence": 0.6 if has_tool_results else 0.4,
                "tool_calls": tool_calls,
                "tool_summaries": [],
            }
        )

    def _final(self, joined: str) -> str:
        prefs = re.findall(r'"candidate_preference":\s*"([A-D])"', joined)
        answer = prefs[-1] if prefs else "A"
        return json.dumps(
            {
                "reasoning": "Mock integration uses latest candidate preference.",
                "answer": answer,
                "explanation": "Aggregated mock evidence",
                "confidence": 0.55,
                "conflicts": [],
                "cited_evidence": prefs[-3:],
            }
        )


class LocalHFProvider(LLMProvider):
    def __init__(
        self,
        model_path: str,
        dtype: str = "bfloat16",
        device_map: str = "auto",
        max_new_tokens: int = 1024,
        temperature: float = 1.0,
        top_p: float = 0.9,
        seed: int = 42,
        offline: bool = True,
        cache_dir: Optional[str] = None,
    ):
        super().__init__()
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.torch = torch
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.seed = seed
        self.cache = DiskCache(Path(cache_dir)) if cache_dir else None

        path = Path(model_path)
        if not path.exists():
            raise FileNotFoundError(f"Local model path not found: {model_path}")
        if not (path / "config.json").exists():
            raise FileNotFoundError(f"Incomplete model: missing {path / 'config.json'}")
        weight_files = list(path.glob("*.safetensors")) + list(path.glob("pytorch_model*.bin"))
        if not weight_files:
            raise FileNotFoundError(f"Incomplete model: no weight files under {path}")

        if offline:
            import os

            os.environ["TRANSFORMERS_OFFLINE"] = "1"
            os.environ["HF_HUB_OFFLINE"] = "1"

        torch_dtype = {
            "bfloat16": torch.bfloat16,
            "float16": torch.float16,
            "float32": torch.float32,
        }.get(dtype, torch.bfloat16)

        self.tokenizer = AutoTokenizer.from_pretrained(str(path), trust_remote_code=True, local_files_only=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            str(path),
            torch_dtype=torch_dtype,
            device_map=device_map,
            trust_remote_code=True,
            local_files_only=True,
        )
        self.model.eval()

    def generate(self, messages: List[Dict[str, str]], **kwargs: Any) -> LLMResponse:
        cache_key = None
        if self.cache is not None:
            cache_key = stable_hash(
                {
                    "messages": messages,
                    "max_new_tokens": kwargs.get("max_new_tokens", self.max_new_tokens),
                    "temperature": kwargs.get("temperature", self.temperature),
                    "top_p": kwargs.get("top_p", self.top_p),
                    "seed": kwargs.get("seed", self.seed),
                }
            )
            hit = self.cache.get(cache_key)
            if hit is not None:
                self.call_count += 1
                self.total_prompt_tokens += hit.get("prompt_tokens", 0)
                self.total_completion_tokens += hit.get("completion_tokens", 0)
                resp = LLMResponse(**hit)
                self._maybe_record(
                    messages, resp, call_tag=str(kwargs.get("call_tag", "local_hf")), cached=True
                )
                return resp

        self.call_count += 1
        self.torch.manual_seed(kwargs.get("seed", self.seed))
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt")
        # device_map=auto models may not expose a single `.device`
        try:
            device = next(self.model.parameters()).device
        except Exception:
            device = self.torch.device("cuda" if self.torch.cuda.is_available() else "cpu")
        inputs = {k: v.to(device) for k, v in inputs.items()}
        t0 = time.time()
        with self.torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=kwargs.get("max_new_tokens", self.max_new_tokens),
                do_sample=True,
                temperature=kwargs.get("temperature", self.temperature),
                top_p=kwargs.get("top_p", self.top_p),
                pad_token_id=self.tokenizer.eos_token_id,
            )
        latency = time.time() - t0
        generated = output[0][inputs["input_ids"].shape[-1] :]
        text = self.tokenizer.decode(generated, skip_special_tokens=True)
        prompt_tokens = int(inputs["input_ids"].shape[-1])
        completion_tokens = int(generated.shape[-1])
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        resp = LLMResponse(
            text=text,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_sec=latency,
            raw={"provider": "local_hf"},
        )
        if self.cache is not None and cache_key is not None:
            self.cache.set(
                cache_key,
                {
                    "text": resp.text,
                    "prompt_tokens": resp.prompt_tokens,
                    "completion_tokens": resp.completion_tokens,
                    "latency_sec": resp.latency_sec,
                    "raw": resp.raw,
                },
            )
        self._maybe_record(messages, resp, call_tag=str(kwargs.get("call_tag", "local_hf")))
        return resp


def build_provider(cfg: Dict[str, Any]) -> LLMProvider:
    exp = cfg.get("experiment", {})
    use_mock = exp.get("use_mock_llm", "auto")
    if use_mock is True:
        return MockLLMProvider()
    if use_mock == "auto":
        try:
            import torch

            cuda_ok = torch.cuda.is_available()
        except Exception:
            cuda_ok = False
        if not cuda_ok:
            return MockLLMProvider()
    model_cfg = cfg["model"]
    return LocalHFProvider(
        model_path=model_cfg["local_path"],
        dtype=model_cfg.get("dtype", "bfloat16"),
        device_map=model_cfg.get("device_map", "auto"),
        max_new_tokens=model_cfg.get("max_new_tokens", 1024),
        temperature=model_cfg.get("temperature", 1.0),
        top_p=model_cfg.get("top_p", 0.9),
        seed=model_cfg.get("seed", 42),
        offline=model_cfg.get("offline", True),
        cache_dir=exp.get("cache_dir"),
    )
