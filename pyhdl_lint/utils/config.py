import tomllib
from pathlib import Path
from typing import Dict, List, Optional

class Config:
    def __init__(self, config_dict: Optional[Dict[str, List[str]]] = None) -> None:
        self.settings: Dict[str, List[str]] = config_dict or {}

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "Config":
        """
        Load config from .pyhdl-lint.toml (wins if present) or pyproject.toml's
        [tool.pyhdl_lint] table, searched in `path` (defaults to cwd).
        """
        search_dir = path if path is not None else Path.cwd()
        dedicated = search_dir / ".pyhdl-lint.toml"
        pyproject = search_dir / "pyproject.toml"

        for candidate, extract in (
            (dedicated, lambda d: d),
            (pyproject, lambda d: d.get("tool", {}).get("pyhdl_lint", {})),
        ):
            if not candidate.is_file():
                continue
            try:
                data = tomllib.loads(candidate.read_text(encoding="utf-8"))
            except tomllib.TOMLDecodeError as e:
                print(f"Warning: could not parse {candidate}: {e}")
                return cls()
            return cls(extract(data))

        return cls()

    def is_rule_enabled(self, rule_id: str) -> bool:
        # Rules are enabled by default unless explicitly disabled
        disabled_rules = self.settings.get("disabled_rules", [])
        return rule_id not in disabled_rules
