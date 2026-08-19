"""Workflow executor: resolve $ref bindings and run ordered tool steps."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union

from ts_agent.schemas.models import ExecutedStep, InvocationCall, InvocationPlan, ToolWorkflow, WorkflowStep
from ts_agent.tools.call_normalizer import fingerprint
from ts_agent.tools.registry import ToolRegistry, ToolResult

_REF_RE = re.compile(r"^\$step(\d+)\.(.+)$")
_TOOL_REF_RE = re.compile(r"^\$([a-zA-Z_][a-zA-Z0-9_]*)\.(.+)$")

# Series selectors that identify which series to run on (filled by S4 literals).
_SERIES_SELECTOR_KEYS = frozenset(
    {
        "series",
        "series_index",
        "series_index_1",
        "series_index_2",
        "series_1",
        "series_2",
        "series1",
        "series2",
        "query_series_index",
        "long_series_index",
        "ref_series_index",
        "candidate_series_indices",
    }
)

# Args that tools can usually omit; drop when $ref path is missing instead of failing the step.
_OPTIONAL_ARG_KEYS = frozenset(
    {
        "period",
        "start",
        "end",
        "window",
        "window_size",
        "lag",
        "max_lag",
        "n_breakpoints",
        "threshold",
    }
)

_OMIT = object()


def _is_ref(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("$")


def _ref_is_mergeable(value: str, *, current_step: int, workflow_tools: Set[str]) -> bool:
    """Return False for hallucinated / self-referential bindings that can never resolve."""
    text = value.strip()
    m = _REF_RE.match(text)
    if m:
        step_n = int(m.group(1))
        # Self or future-step refs must not be injected as inputs for this step.
        if step_n >= current_step:
            return False
        return True
    m2 = _TOOL_REF_RE.match(text)
    if m2:
        tool_name = m2.group(1)
        # "$tool.series" is a common hallucination; only real prior tool names are valid.
        if tool_name not in workflow_tools:
            return False
        return True
    return False


def _has_concrete_series_selector(args: Dict[str, Any]) -> bool:
    for key in _SERIES_SELECTOR_KEYS:
        if key not in args:
            continue
        val = args[key]
        if val is None or _is_ref(val):
            continue
        if isinstance(val, list) and all(_is_ref(x) for x in val):
            continue
        return True
    return False


def merge_step_args(
    call_args: Optional[Dict[str, Any]],
    input_binding: Optional[Dict[str, Any]],
    *,
    current_step: int,
    workflow_tools: Set[str],
) -> Dict[str, Any]:
    """Merge S4 call args with S3 input_binding.

    Call args win on key conflicts. Invalid / self-referential bindings are dropped.
    If S4 already provided a concrete series selector, do not inject series $refs from S3.
    """
    raw: Dict[str, Any] = dict(call_args or {})
    concrete_series = _has_concrete_series_selector(raw)
    for key, val in (input_binding or {}).items():
        if key in raw:
            continue
        if _is_ref(val):
            if not _ref_is_mergeable(str(val), current_step=current_step, workflow_tools=workflow_tools):
                continue
            if concrete_series and key in _SERIES_SELECTOR_KEYS:
                continue
        raw[key] = val

    # If a concrete series_index (etc.) is present, drop competing series $refs that
    # would fail resolve_args even though the selector is already usable.
    if _has_concrete_series_selector(raw):
        for key in list(raw.keys()):
            if key in _SERIES_SELECTOR_KEYS and _is_ref(raw[key]):
                del raw[key]
    return raw


def match_invocation(
    step_n: int,
    tool_name: str,
    calls_by_step: Dict[int, InvocationCall],
    calls_by_tool: Dict[str, InvocationCall],
) -> Optional[InvocationCall]:
    """Bind S4 call args only when tool identity matches the workflow step.

    S4 often invents a different step/tool sequence than S3. Matching by step number
    alone would poison e.g. hurst_exponent with stl_strength's period=$step1.dominant_period.
    """
    by_step = calls_by_step.get(step_n)
    if by_step is not None and str(by_step.tool) == tool_name:
        return by_step
    by_tool = calls_by_tool.get(tool_name)
    if by_tool is not None:
        return by_tool
    return None


def _lookup_path(data: Any, path: str) -> Any:
    """Resolve dotted path; also search first series item when field is nested under series[]."""
    if data is None:
        raise KeyError(f"empty data for path {path!r}")
    # Direct top-level
    cur: Any = data
    parts = path.split(".")
    ok = True
    for part in parts:
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
            continue
        m = re.fullmatch(r"(\w+)\[(\d+)\]", part)
        if m and isinstance(cur, dict):
            key, idx = m.group(1), int(m.group(2))
            seq = cur.get(key)
            if isinstance(seq, (list, tuple)) and 0 <= idx < len(seq):
                cur = seq[idx]
                continue
        ok = False
        break
    if ok:
        return cur
    # Flatten: series[0].field or first series item
    series = data.get("series") if isinstance(data, dict) else None
    if isinstance(series, list) and series:
        first = series[0]
        if isinstance(first, dict) and path in first:
            return first[path]
        # try nested path on first item
        cur = first
        for part in parts:
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                raise KeyError(f"path {path!r} not found in tool result")
        return cur
    # Flat fields on root matching last segment
    if isinstance(data, dict) and path in data:
        return data[path]
    raise KeyError(f"path {path!r} not found in tool result")


def resolve_arg_value(
    value: Any,
    step_results: Dict[int, ExecutedStep],
    tool_to_step: Dict[str, int],
    *,
    soft_omit: bool = False,
) -> Any:
    """Resolve a single argument value; leave non-ref values unchanged.

    When soft_omit=True and the ref path is missing / invalid metadata-style $,
    return the sentinel _OMIT instead of raising.
    """
    if isinstance(value, list):
        out_list = []
        for item in value:
            resolved = resolve_arg_value(item, step_results, tool_to_step, soft_omit=soft_omit)
            if resolved is _OMIT:
                continue
            out_list.append(resolved)
        return out_list if out_list else _OMIT
    if isinstance(value, dict):
        out_dict: Dict[str, Any] = {}
        for k, v in value.items():
            resolved = resolve_arg_value(v, step_results, tool_to_step, soft_omit=soft_omit)
            if resolved is _OMIT:
                continue
            out_dict[k] = resolved
        return out_dict

    if not isinstance(value, str) or not value.startswith("$"):
        return value

    text = value.strip()
    m = _REF_RE.match(text)
    if m:
        step_n = int(m.group(1))
        field = m.group(2)
        if step_n not in step_results:
            if soft_omit:
                return _OMIT
            raise ValueError(f"unresolved reference {value!r}: step {step_n} not executed")
        prior = step_results[step_n]
        if not prior.success:
            if soft_omit:
                return _OMIT
            raise ValueError(f"unresolved reference {value!r}: step {step_n} failed ({prior.error})")
        try:
            return _lookup_path(prior.data, field)
        except KeyError:
            if soft_omit:
                return _OMIT
            raise
    m2 = _TOOL_REF_RE.match(text)
    if m2:
        tool_name = m2.group(1)
        field = m2.group(2)
        if tool_name not in tool_to_step:
            if soft_omit:
                return _OMIT
            raise ValueError(f"unresolved reference {value!r}: tool {tool_name} not in prior steps")
        return resolve_arg_value(
            f"$step{tool_to_step[tool_name]}.{field}",
            step_results,
            tool_to_step,
            soft_omit=soft_omit,
        )
    # Metadata-style hallucinations: $candidate_series_indices[1], $query_series_index, etc.
    if soft_omit:
        return _OMIT
    raise ValueError(f"invalid reference syntax {value!r}; expected $stepN.field or $tool.field")


def resolve_args(
    args: Dict[str, Any],
    step_results: Dict[int, ExecutedStep],
    tool_to_step: Dict[str, int],
) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in (args or {}).items():
        if v is None:
            continue  # omit nulls
        soft = k in _OPTIONAL_ARG_KEYS or k in _SERIES_SELECTOR_KEYS
        try:
            resolved = resolve_arg_value(v, step_results, tool_to_step, soft_omit=soft)
        except (ValueError, KeyError):
            if soft:
                continue
            raise
        if resolved is _OMIT:
            continue
        out[k] = resolved
    return out


class WorkflowExecutor:
    """Execute a ToolWorkflow with InvocationPlan, resolving $ref dependencies."""

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute(
        self,
        workflow: Union[ToolWorkflow, List[WorkflowStep], None],
        calls: Union[InvocationPlan, List[InvocationCall], None],
        series: List[List[float]],
        allowed_roles: List[str],
        executor_id: str,
    ) -> List[ExecutedStep]:
        steps = self._normalize_workflow(workflow)
        call_list = self._normalize_calls(calls)
        if not steps and not call_list:
            return []

        # Prefer workflow order; if only calls provided, order by step.
        if not steps and call_list:
            steps = [
                WorkflowStep(step=c.step, tool=c.tool, output_key=c.tool, input_binding={})
                for c in sorted(call_list, key=lambda x: x.step)
            ]

        calls_by_step = {c.step: c for c in call_list}
        # Also index by tool if step missing
        calls_by_tool = {c.tool: c for c in call_list}

        allowed = {s.name for s in self.registry.list_for_roles(allowed_roles)}
        step_results: Dict[int, ExecutedStep] = {}
        tool_to_step: Dict[str, int] = {}
        executed: List[ExecutedStep] = []
        workflow_tools = {str(s.tool) for s in steps}

        ordered = sorted(steps, key=lambda s: s.step)
        for wf_step in ordered:
            step_n = int(wf_step.step)
            tool_name = str(wf_step.tool)
            call_id = f"{executor_id}:step{step_n}"

            if tool_name not in allowed:
                step = ExecutedStep(
                    call_id=call_id,
                    step=step_n,
                    tool_name=tool_name,
                    arguments={},
                    resolved_arguments={},
                    success=False,
                    data={},
                    error=f"Tool not allowed for roles {allowed_roles}",
                )
                step_results[step_n] = step
                executed.append(step)
                continue

            inv = match_invocation(step_n, tool_name, calls_by_step, calls_by_tool)
            # Merge S3 bindings into S4 args; drop hallucinated $tool.series / self-refs.
            raw_args = merge_step_args(
                inv.args if inv is not None else {},
                wf_step.input_binding,
                current_step=step_n,
                workflow_tools=workflow_tools,
            )

            try:
                resolved = resolve_args(raw_args, step_results, tool_to_step)
            except (ValueError, KeyError) as e:
                step = ExecutedStep(
                    call_id=call_id,
                    step=step_n,
                    tool_name=tool_name,
                    arguments=raw_args,
                    resolved_arguments={},
                    success=False,
                    data={},
                    error=str(e),
                    args_fingerprint="",
                )
                step_results[step_n] = step
                executed.append(step)
                continue

            result: ToolResult = self.registry.run(tool_name, resolved, series)
            fp = fingerprint(tool_name, resolved) if result.success else ""
            step = ExecutedStep(
                call_id=call_id,
                step=step_n,
                tool_name=tool_name,
                arguments=raw_args,
                resolved_arguments=resolved,
                success=result.success,
                data=result.data if result.success else {},
                error=result.error,
                args_fingerprint=fp,
            )
            step_results[step_n] = step
            tool_to_step[tool_name] = step_n
            executed.append(step)

        return executed

    @staticmethod
    def _normalize_workflow(workflow: Union[ToolWorkflow, List[WorkflowStep], None]) -> List[WorkflowStep]:
        if workflow is None:
            return []
        if isinstance(workflow, ToolWorkflow):
            return list(workflow.workflow or [])
        return list(workflow)

    @staticmethod
    def _normalize_calls(calls: Union[InvocationPlan, List[InvocationCall], None]) -> List[InvocationCall]:
        if calls is None:
            return []
        if isinstance(calls, InvocationPlan):
            return list(calls.calls or [])
        return list(calls)
