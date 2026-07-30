from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class SubsetName(str, Enum):
    BASE = "Base"
    INWILD = "InWild"
    MATCH = "Match"
    ALIGN = "Align"


class ScaleName(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class HeterogeneousRole(str, Enum):
    STRUCTURE = "structure"
    REASONING = "reasoning"
    MATCHING = "matching"
    ALIGNMENT = "alignment"


class MMTSSample(BaseModel):
    sample_id: str
    source_file: str
    row_index: int
    subset: SubsetName
    num: Optional[Union[int, str]] = None
    qa_type: str = ""
    question_type: Literal["choice", "numerical"] = "choice"
    local_overall: str = ""
    task_type: Any = None
    question: str
    option: Optional[str] = None
    answer: str
    domain: Optional[str] = None
    freq: Optional[str] = None
    is_univariate: Optional[bool] = None
    stationarity: Optional[Any] = None
    series: List[List[float]]
    series_text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentPlan(BaseModel):
    reasoning: str
    capability: str
    scope: Literal["local", "overall", "unknown"] = "unknown"
    univariate: Optional[bool] = None
    scales: List[ScaleName] = Field(default_factory=lambda: [ScaleName.SHORT, ScaleName.MEDIUM, ScaleName.LONG])
    heterogeneous_agents: List[HeterogeneousRole] = Field(default_factory=list)
    notes: str = ""


class ToolCallRequest(BaseModel):
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class ScaleObservation(BaseModel):
    reasoning: str
    scale: ScaleName
    observations: List[str] = Field(default_factory=list)
    evidence_intervals: List[str] = Field(default_factory=list)
    confidence: float = 0.5
    tool_calls: List[ToolCallRequest] = Field(default_factory=list)
    tool_summaries: List[str] = Field(default_factory=list)


class TemporalProfile(BaseModel):
    short: Optional[ScaleObservation] = None
    medium: Optional[ScaleObservation] = None
    long: Optional[ScaleObservation] = None
    conflicts: List[str] = Field(default_factory=list)
    summary: str = ""


class TaskEvidence(BaseModel):
    reasoning: str
    role: HeterogeneousRole
    evidence: List[str] = Field(default_factory=list)
    candidate_preference: Optional[str] = None
    confidence: float = 0.5
    tool_calls: List[ToolCallRequest] = Field(default_factory=list)
    tool_summaries: List[str] = Field(default_factory=list)


class FinalAnswer(BaseModel):
    reasoning: str
    answer: str
    explanation: str = ""
    confidence: float = 0.5
    conflicts: List[str] = Field(default_factory=list)
    cited_evidence: List[str] = Field(default_factory=list)


class BaselineAnswer(BaseModel):
    reasoning: str = ""
    answer: str
    raw_text: str = ""


class RunTrace(BaseModel):
    sample_id: str
    experiment: str
    success: bool
    predicted_answer: str = ""
    ground_truth: str = ""
    question_type: str = "choice"
    latency_sec: float = 0.0
    model_calls: int = 0
    tool_calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    error: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
