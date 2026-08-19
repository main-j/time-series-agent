from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


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


class HomoAssignment(BaseModel):
    """Planner-issued evidence contract for one homogeneous scale agent."""

    scale: ScaleName
    objective: str = ""
    required_measurements: List[str] = Field(default_factory=list)
    validation_requirements: List[str] = Field(default_factory=list)
    target_series: List[int] = Field(default_factory=list)
    focus_intervals: List[List[int]] = Field(default_factory=list)


class HeteroAssignment(BaseModel):
    """Planner-issued evidence contract for one heterogeneous role agent."""

    role: HeterogeneousRole
    objective: str = ""
    required_measurements: List[str] = Field(default_factory=list)
    validation_requirements: List[str] = Field(default_factory=list)
    target_series: List[int] = Field(default_factory=list)
    focus_intervals: List[List[int]] = Field(default_factory=list)


class AgentPlan(BaseModel):
    reasoning: str
    task_summary: str = ""
    target_output: str = ""
    answer_type: Literal["choice", "numerical", "binary", "unknown"] = "unknown"
    capability: str = "unknown"
    scope: Literal["local", "overall", "unknown"] = "unknown"
    univariate: Optional[bool] = None
    homo_assignments: List[HomoAssignment] = Field(default_factory=list)
    hetero_assignments: List[HeteroAssignment] = Field(default_factory=list)
    # Derived for pipeline compatibility; runtime fills these from assignments.
    scales: List[ScaleName] = Field(default_factory=list)
    heterogeneous_agents: List[HeterogeneousRole] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)
    notes: str = ""

    @model_validator(mode="after")
    def _sync_derived_lists(self) -> "AgentPlan":
        if self.homo_assignments:
            self.scales = list(dict.fromkeys(item.scale for item in self.homo_assignments))
        if self.hetero_assignments:
            self.heterogeneous_agents = list(
                dict.fromkeys(item.role for item in self.hetero_assignments)
            )
        return self


class ToolCallRequest(BaseModel):
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


# ---- Five-stage Tool Agent intermediate schemas ----


class ClaimSpec(BaseModel):
    """One claim that the agent must support or falsify with evidence."""

    claim: str
    required_evidence: List[str] = Field(default_factory=list)


class EvidencePlan(BaseModel):
    """S1: what claims need what measurable evidence (not tool names)."""

    objective: str = ""
    claims_to_support: List[ClaimSpec] = Field(default_factory=list)
    analysis_scope: Dict[str, Any] = Field(default_factory=dict)
    validation_needs: List[str] = Field(default_factory=list)


class EvidenceSourceRef(BaseModel):
    """Pointer to upstream evidence when skipping tools."""

    type: str = "upstream_observation"
    ref: str = ""
    field: str = ""


class NoToolDecision(BaseModel):
    """Required when selected_tools is empty."""

    skip_tools: bool = True
    reason: str = ""
    evidence_sources: List[EvidenceSourceRef] = Field(default_factory=list)


class SelectedTool(BaseModel):
    tool: str
    reason: str = ""
    supports_evidence: List[str] = Field(default_factory=list)


class CapabilitySelection(BaseModel):
    """S2: tools chosen by capability matching against required_evidence."""

    selected_tools: List[SelectedTool] = Field(default_factory=list)
    no_tool_decision: Optional[NoToolDecision] = None


class EvidenceCapabilityPlan(BaseModel):
    """S1+S2 merged LLM output."""

    evidence_plan: EvidencePlan = Field(default_factory=EvidencePlan)
    capability_selection: CapabilitySelection = Field(default_factory=CapabilitySelection)
    reasoning: str = ""


class WorkflowStep(BaseModel):
    step: int
    tool: str
    output_key: str = ""
    input_binding: Dict[str, Any] = Field(default_factory=dict)


class ToolWorkflow(BaseModel):
    """S3: ordered analysis pipeline with dependency bindings."""

    workflow: List[WorkflowStep] = Field(default_factory=list)
    reasoning: str = ""


class InvocationCall(BaseModel):
    step: int
    tool: str
    args: Dict[str, Any] = Field(default_factory=dict)


class InvocationPlan(BaseModel):
    """S4 LLM output: static args + $ref placeholders for Runtime."""

    calls: List[InvocationCall] = Field(default_factory=list)
    reasoning: str = ""


class EvidenceItem(BaseModel):
    type: str
    value: Any = None
    source_tool: Optional[str] = None
    call_id: Optional[str] = None
    provenance: Literal["tool", "upstream", "context", "unresolved"] = "tool"
    ref: Optional[str] = None
    series_index: Optional[int] = None
    args_fingerprint: Optional[str] = None


class ClaimObservation(BaseModel):
    claim: str
    evidence: List[EvidenceItem] = Field(default_factory=list)
    confidence: Literal["tool_supported", "context_supported", "unresolved", "qualified"] = "unresolved"
    maps_to_measurement: Optional[str] = None


class ExecutedStep(BaseModel):
    """System-owned record of one workflow step execution."""

    call_id: str
    step: int
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    resolved_arguments: Dict[str, Any] = Field(default_factory=dict)
    success: bool
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    args_fingerprint: str = ""


class ScaleObservation(BaseModel):
    reasoning: str
    scale: ScaleName
    observations: List[str] = Field(default_factory=list)
    evidence_intervals: List[str] = Field(default_factory=list)
    confidence: float = 0.5
    tool_calls: List[ToolCallRequest] = Field(default_factory=list)
    tool_summaries: List[str] = Field(default_factory=list)
    # Five-stage artifacts
    evidence_plan: Optional[EvidencePlan] = None
    capability_selection: Optional[CapabilitySelection] = None
    workflow: Optional[ToolWorkflow] = None
    structured_observations: List[ClaimObservation] = Field(default_factory=list)
    coverage: Dict[str, str] = Field(default_factory=dict)
    unresolved_claims: List[str] = Field(default_factory=list)
    executed_steps: List[ExecutedStep] = Field(default_factory=list)
    skipped_stages: List[str] = Field(default_factory=list)


class TemporalProfile(BaseModel):
    short: Optional[ScaleObservation] = None
    medium: Optional[ScaleObservation] = None
    long: Optional[ScaleObservation] = None
    conflicts: List[str] = Field(default_factory=list)
    summary: str = ""
    structured_by_scale: Dict[str, List[ClaimObservation]] = Field(default_factory=dict)


class ExecutedToolEvidence(BaseModel):
    """System-owned record of one tool execution; never trust model-authored copies."""

    call_id: str
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    success: bool
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    executor_role: HeterogeneousRole


class TaskEvidence(BaseModel):
    reasoning: str
    role: HeterogeneousRole
    evidence: List[str] = Field(default_factory=list)
    candidate_preference: Optional[str] = None
    confidence: float = 0.5
    tool_calls: List[ToolCallRequest] = Field(default_factory=list)
    cited_tool_call_ids: List[str] = Field(default_factory=list)
    executed_tools: List[ExecutedToolEvidence] = Field(default_factory=list)
    tool_summaries: List[str] = Field(default_factory=list)
    # Five-stage artifacts
    evidence_plan: Optional[EvidencePlan] = None
    capability_selection: Optional[CapabilitySelection] = None
    workflow: Optional[ToolWorkflow] = None
    reasoning_claims: List[ClaimObservation] = Field(default_factory=list)
    coverage: Dict[str, str] = Field(default_factory=dict)
    unresolved_claims: List[str] = Field(default_factory=list)
    executed_steps: List[ExecutedStep] = Field(default_factory=list)
    skipped_stages: List[str] = Field(default_factory=list)
    hypothesis: str = ""


class DecisionTrace(BaseModel):
    """LLM-authored comparison trace for threshold/label questions (not code-side binning)."""

    metric: Optional[str] = None
    observed_value: Any = None
    intervals_from_question: List[str] = Field(default_factory=list)
    matched_label: Optional[str] = None
    matched_letter: Optional[str] = None


class FinalAnswer(BaseModel):
    reasoning: str
    answer: str
    explanation: str = ""
    confidence: float = 0.5
    conflicts: List[str] = Field(default_factory=list)
    cited_evidence: List[str] = Field(default_factory=list)
    decision_trace: Optional[DecisionTrace] = None

    @field_validator("answer", mode="before")
    @classmethod
    def _coerce_answer(cls, value: Any) -> str:
        if isinstance(value, bool) or value is None:
            raise ValueError("answer must be a choice letter or numeric value")
        if isinstance(value, (str, int, float)):
            return str(value)
        raise ValueError("answer must be a string or number")


# ---- Integration four-layer view (projection; does not replace upstream artifacts) ----


class PlannerIntent(BaseModel):
    goal: str = ""
    question_type: str = "unknown"
    required_output: str = ""
    success_criteria: List[str] = Field(default_factory=list)
    assignments_brief: List[Dict[str, Any]] = Field(default_factory=list)


class PerceptionStateItem(BaseModel):
    series_index: Optional[int] = None
    type: str = ""
    value: Any = None
    trusted: bool = False


class ScalePerceptionSlice(BaseModel):
    states: List[PerceptionStateItem] = Field(default_factory=list)
    coverage: Dict[str, str] = Field(default_factory=dict)
    summary: str = ""


class HomoPerceptionView(BaseModel):
    by_scale: Dict[str, ScalePerceptionSlice] = Field(default_factory=dict)
    conflicts: List[str] = Field(default_factory=list)
    summary: str = ""


class HeterRoleReasoning(BaseModel):
    role: str = ""
    hypothesis: str = ""
    reasoning_chain: List[str] = Field(default_factory=list)
    candidate_preference: Optional[str] = None
    confidence: float = 0.5
    grounded: bool = False
    grounded_in: List[str] = Field(default_factory=list)
    uncertainty: str = ""


class HeterReasoningView(BaseModel):
    roles: List[HeterRoleReasoning] = Field(default_factory=list)


class ExecutionMetadata(BaseModel):
    option_mapping: Dict[str, Any] = Field(default_factory=dict)
    verified_preference: Optional[str] = None
    verified: bool = False
    warnings: List[str] = Field(default_factory=list)


class IntegrationBundle(BaseModel):
    """Clean four-layer input for Integration LLM."""

    question: str = ""
    candidates: str = ""
    question_type: str = "choice"
    planner_intent: PlannerIntent = Field(default_factory=PlannerIntent)
    homo_perception: HomoPerceptionView = Field(default_factory=HomoPerceptionView)
    heter_reasoning: HeterReasoningView = Field(default_factory=HeterReasoningView)
    execution_metadata: ExecutionMetadata = Field(default_factory=ExecutionMetadata)
    question_rules_appendix: str = ""


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
