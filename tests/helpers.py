from pathlib import Path

from pyhdl_lint.core.rule_base import LintContext


def make_context(content: str, language: str = "vhdl") -> LintContext:
    """Build a LintContext for regex-based BaseRule tests, bypassing the real parser."""
    return LintContext(
        file_path=Path(f"<test>.{language}"),
        content=content,
        lines=content.splitlines(),
        language=language,
        ast=None,
        parse_error=None,
    )
