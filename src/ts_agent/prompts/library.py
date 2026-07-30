from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ts_agent.core.utils import load_yaml


class PromptLibrary:
    def __init__(self, prompt_dir: str | Path):
        self.prompt_dir = Path(prompt_dir)
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, name: str) -> Dict[str, Any]:
        if name not in self._cache:
            path = self.prompt_dir / f"{name}.yaml"
            if not path.exists():
                raise FileNotFoundError(path)
            self._cache[name] = load_yaml(path)
        return self._cache[name]

    def render(self, name: str, **kwargs: Any) -> Dict[str, str]:
        tpl = self.get(name)
        system = tpl["system"].format(**kwargs)
        user = tpl["user"].format(**kwargs)
        return {"system": system, "user": user, "version": tpl.get("version", "unknown"), "name": name}

    def versions(self) -> Dict[str, str]:
        versions = {}
        for path in sorted(self.prompt_dir.glob("*.yaml")):
            data = load_yaml(path)
            versions[path.stem] = data.get("version", "unknown")
        return versions
