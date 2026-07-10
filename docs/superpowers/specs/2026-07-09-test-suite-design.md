# Test Suite (PLAN.md Phase 2, part 1 of 2)

## Problem

No automated test harness exists. `tests/test_ast_rules.py` and `tests/test_config.py`
are ad-hoc assert-based scripts (added during the AST-rule-checking and config-loading
work) that only cover VHDL-001, SV-001, and `Config.load()`. The other 19 rule classes
(covering 21 rule IDs, since VHDL-008/VHDL-013 are emitted from inside other classes)
have zero test coverage. `pytest` isn't installed anywhere.

## Decisions

- **pytest as an optional dependency** — `[project.optional-dependencies] test = ["pytest"]`
  in `pyproject.toml`, not a base runtime dependency (end users linting HDL don't need it).
- **Fake `LintContext` for regex-based rules, real parser only for `AstRule` rules** —
  `BaseRule` subclasses only read `context.content`/`context.lines`, so a hand-built
  `LintContext` with `ast=None` is sufficient and avoids needing `hdlConvertor` for 19 of
  21 rule IDs. `AstRule` rules (VHDL-001, SV-001) need `context.ast` to be a real parsed
  tree — those keep using `Parser(...).get_context(...)` against real fixture files, as
  `test_ast_rules.py` already does.
- **`vhdl_test_guidelines.vhd`'s inline `-- ERROR: VHDL-XXX` annotations are not parsed
  into a generic oracle.** They're incomplete (VHDL-002 keyword-case fires ~40 times,
  none annotated), and building a parser for them is new infra beyond what's asked.
  Instead: targeted per-rule tests with small inline snippets (matching the existing
  `test_ast_rules.py` pattern), plus one smoke test asserting the full real run against
  that fixture produces a fixed violation count (regression guard, not a golden oracle).
- **Drop the `if __name__ == "__main__":` runner blocks** from the two existing ad-hoc
  test files now that pytest is the standard way to run tests — no reason to maintain
  two runners for the same assertions.

## Design

### `pyproject.toml`
```toml
[project.optional-dependencies]
test = ["pytest"]
```

### `tests/helpers.py`
```python
from pathlib import Path
from pyhdl_lint.core.rule_base import LintContext

def make_context(content: str, language: str = "vhdl") -> LintContext:
    return LintContext(
        file_path=Path(f"<test>.{language}"),
        content=content,
        lines=content.splitlines(),
        language=language,
        ast=None,
        parse_error=None,
    )
```

### `tests/test_vhdl_rules.py`

`pytest.mark.parametrize`-driven: one "fires on bad input, with correct line/column"
case and one "silent on clean input" case per remaining VHDL `BaseRule` (VHDL-002
through VHDL-022, excluding VHDL-001 which is AST-tested elsewhere). VHDL-008 and
VHDL-013 get extra assertions on `ProcessNamingRule`/`FsmStateChangeRule` (the classes
that actually emit them) rather than being treated as separate rules.

### `tests/test_verilog_rules.py`

Same pattern, one entry for `VER-001` (`ModuleNamingRule`).

### `tests/test_smoke.py`

Uses the real installed parser (`.venv` already has `hdlConvertor`) to run the full
`Engine` against `tests/vhdl_test_guidelines.vhd`, `tests/test_file.v`,
`tests/test_file.sv`, asserting the exact violation counts already verified live
(73 / 1 / 1) and that `Engine.load_rules` discovers exactly 19 / 1 / 1 rule objects per
language — a regression guard against both rule-logic drift and loader bugs (like the
`AstRule`-leaking-into-the-loader bug hit and fixed during the AST rule work).

### Cleanup

Remove the `if __name__ == "__main__":` blocks from `tests/test_ast_rules.py` and
`tests/test_config.py`.

## Out of scope

- No comment-annotation parser for `vhdl_test_guidelines.vhd`.
- No CI wiring (that's Phase 3's "CI test/lint gate" item).
- No new rules — this only tests what already exists.
