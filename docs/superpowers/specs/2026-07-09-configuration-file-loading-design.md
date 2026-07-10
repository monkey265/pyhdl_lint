# Configuration File Loading (PLAN.md Phase 2)

## Problem

`Config.load()` in `pyhdl_lint/utils/config.py` is a placeholder that always returns
an empty config — no file is ever read. `Config.is_rule_enabled()` already reads
`self.settings.get("disabled_rules", [])`, so wiring up real loading closes the loop
for that one setting end-to-end.

## Decisions

- **Search location**: current working directory only. Matches how the CLI is
  actually invoked (`pyhdl-lint <file>`, run from the repo root). No directory-walking.
- **Precedence**: `.pyhdl-lint.toml` in cwd wins outright if present (no merging).
  Otherwise fall back to `pyproject.toml`'s `[tool.pyhdl_lint]` table in cwd. Neither
  found (or a parse error) → empty config, same as today (everything enabled).
- **Scope**: only `disabled_rules` is wired up. PLAN.md also mentions "custom naming
  prefixes" as a future config use case, but no rule currently reads a config-driven
  prefix — inventing that setting now would be scope beyond "load the config file".
- **Python floor**: `tomllib` is stdlib only from Python 3.11+; `pyproject.toml`
  currently declares `requires-python = ">=3.8"`. Bumping the floor to `>=3.11` was
  chosen over adding a `tomli` fallback dependency, since PLAN.md's own plan calls for
  `tomllib` specifically and nothing else in the codebase needs <3.11.

## Design

`pyproject.toml`: `requires-python = ">=3.11"`.

`pyhdl_lint/utils/config.py`:

```python
import tomllib
from pathlib import Path
from typing import Dict, List, Optional

class Config:
    def __init__(self, config_dict: Optional[Dict[str, List[str]]] = None) -> None:
        self.settings: Dict[str, List[str]] = config_dict or {}

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "Config":
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
        disabled_rules = self.settings.get("disabled_rules", [])
        return rule_id not in disabled_rules
```

`path` param semantics: the directory to search in (defaults to cwd), not a specific
file path — kept as-is from the existing signature, just given real meaning.

Malformed TOML degrades gracefully (warning + empty config) rather than crashing,
matching the project's existing "never crash on bad input" pattern (`parser.py`'s
`parse_error` handling).

## Verification

Real assert-based test (`tests/test_config.py`, same style as `tests/test_ast_rules.py`)
writing actual `.pyhdl-lint.toml` / `pyproject.toml` files into `tmp_path` and asserting
`Config.load(tmp_path)` returns the expected `disabled_rules`. No mocking needed —
`tomllib` is genuinely stdlib.

## Out of scope

- No directory-walking search.
- No naming-prefix config wiring into existing rules.
- No `tomli` fallback dependency; `requires-python` is bumped instead.
