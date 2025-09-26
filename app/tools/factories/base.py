from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..registry import get_registry


@dataclass
class FactoryBase:
    """Abstract base class for tool factories providing common behavior.

    Subclasses must implement _default_paths, known_names and _create_tool.
    """

    desc_base: Optional[Path] = None
    register: bool = True
    registry: Optional[Any] = None
    strict: bool = True

    @abstractmethod
    def _default_paths(self) -> Tuple[Path, Path]:
        """Return a tuple of (primary_desc_path, shared_desc_path) specific to the factory."""
        raise NotImplementedError

    @abstractmethod
    def known_names(self) -> Sequence[str]:
        """Return the default list of tool names known to this factory."""
        raise NotImplementedError

    @abstractmethod
    def _create_tool(self, name: str) -> Any:
        """Create a single tool instance by name. May raise if creation fails."""
        raise NotImplementedError

    def _resolve_paths(self) -> Tuple[Path, Path]:
        """Resolve description paths, using provided desc_base or defaults from subclass."""
        primary, shared = self._default_paths()
        return (self.desc_base or primary), shared

    def validate(self, names: Optional[Sequence[str]] = None) -> Dict[str, List[str]]:
        """Validate that description files exist for the given names.

        Returns a dict with key 'missing_descriptions'. Subclasses may extend this.
        """
        desc_base, shared_base = self._resolve_paths()
        issues: Dict[str, List[str]] = {"missing_descriptions": []}
        target_names = list(names) if names is not None else list(self.known_names())
        for name in target_names:
            desc_file = desc_base / f"{name}.md"
            shared_file = shared_base / f"{name}.md"
            if not desc_file.exists() and not shared_file.exists():
                issues["missing_descriptions"].append(str(desc_file))
        return issues

    def create_tools(self, names: Optional[Sequence[str]] = None) -> List[Any]:
        """Create tools for the given names, optionally registering them.

        Subclasses provide creation via _create_tool.
        """
        selected = list(names) if names is not None else list(self.known_names())

        issues = self.validate(selected)
        if self.strict and issues.get("missing_descriptions"):
            raise FileNotFoundError(f"Missing description files: {issues}")

        tools: List[Any] = []
        registry_to_use = self.registry if self.registry is not None else (get_registry() if self.register else None)

        for name in selected:
            try:
                tool = self._create_tool(name)
            except Exception:
                continue
            tools.append(tool)
            if registry_to_use is not None:
                try:
                    registry_to_use.register_tool(tool)
                except Exception:
                    pass

        return tools
