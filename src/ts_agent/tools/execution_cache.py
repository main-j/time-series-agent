"""Per-sample tool execution cache keyed by normalized fingerprints."""
from __future__ import annotations

from typing import Dict, Optional

from ts_agent.tools.call_normalizer import call_identity
from ts_agent.tools.registry import ToolRegistry, ToolResult


class ToolExecutionCache:
    def __init__(self) -> None:
        self._store: Dict[str, ToolResult] = {}
        self.hits = 0
        self.misses = 0

    def get(self, fingerprint: str) -> Optional[ToolResult]:
        return self._store.get(fingerprint)

    def put(self, fingerprint: str, result: ToolResult) -> None:
        self._store[fingerprint] = result

    def run(
        self,
        registry: ToolRegistry,
        name: str,
        arguments: Dict,
        series,
    ) -> ToolResult:
        fp, source_id, canon_args = call_identity(name, arguments)
        cached = self.get(fp)
        if cached is not None:
            self.hits += 1
            return cached
        self.misses += 1
        result = registry.run(name, canon_args, series)
        if result.success:
            data = dict(result.data or {})
            data.setdefault("evidence_source_id", source_id)
            data.setdefault("call_fingerprint", fp)
            result = ToolResult(
                name=result.name,
                success=result.success,
                data=data,
                error=result.error,
            )
        self.put(fp, result)
        return result
