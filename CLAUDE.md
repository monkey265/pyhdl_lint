# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Principles: Simplicity & Type Safety

`pyhdl_lint` (Python HDL Linter) prioritizes **professional code standards** and **complete type safety**:

- **Type-first development**: Everything uses proper type hints - no `Any`, no dynamic typing
- **Professional standards**: No emojis in code, no hardcoded values, proper constants
- **CLI-focused**: Simple, reliable command-line interface for HDL linting
- **Cross-platform**: Support for Windows, macOS, and Linux environments

## Architecture Overview

`pyhdl_lint` is a **modular HDL linter for VHDL, Verilog, and SystemVerilog** utilizing the `hdlConvertor` parser engine:

**Core Functionality**:
- Dynamic rules loading from language-specific rules directories
- AST-based parsing and analysis using `hdlConvertor`
- Violation reporting with line/column numbers and severity levels
- Centralized type-safe configuration support

## Development Commands

### Installation
```bash
# Install package in development mode
pip install -e .

# Or using uv (much faster)
uv pip install -e .
```

### Running the Linter
```bash
# Lint an HDL file
pyhdl-lint <path_to_hdl_file>
```

### Testing & Quality
```bash
# Run tests
pytest

# Type checking, formatting, and linting
mypy .
ruff format .
ruff check .
```

## Code Quality Standards

### Type Safety Requirements
- **No Any types**: All functions and classes must have proper type hints
- **Type checking**: Must pass `mypy` type checking without errors
- **Pydantic / Type-safe models**: Use type-safe representations for config and rules

### Professional Code Standards
- **No emojis**: Keep code and output professional - avoid emojis in code, comments, or CLI output
- **No hardcoding**: Use constants, configura   tion classes, or environment variables
- **Proper error handling**: Consistent error patterns with informative messages
- **Cross-platform paths**: Use `pathlib.Path` for all file operations

## CLI Architecture

### Command Structure
```
pyhdl-lint <file_path>  # Main CLI entry point
```

### Core Modules
- **CLI Layer** (`pyhdl_lint/__main__.py`): Script entry point and rule orchestration
- **Engine** (`pyhdl_lint/core/engine.py`): Dynamic rule loader and execution engine
- **Parser** (`pyhdl_lint/core/parser.py`): AST generator using `hdlConvertor`
- **Reporter** (`pyhdl_lint/core/reporter.py`): Format and output violation reports
- **Rule Base** (`pyhdl_lint/core/rule_base.py`): `BaseRule`/`AstRule` base classes, `LintContext`, `Violation`
- **Configuration** (`pyhdl_lint/utils/config.py`): Loads `disabled_rules` from `.pyhdl-lint.toml` or `pyproject.toml`'s `[tool.pyhdl_lint]` table (cwd only, `.pyhdl-lint.toml` wins if both present); requires Python 3.11+ for stdlib `tomllib`

## Development Workflow - MANDATORY

### Task Documentation
- **ALWAYS create task file**: For ANY work request, immediately create `.claude/doc/tasks/[date]-[seq]-[task-name].md`
- **Update throughout**: Document progress, decisions, blockers in real-time
- **Include context**: Always pass current task file path to agents for context sharing

### Code Quality Workflow  
- **After completing ANY code changes**: Prompt user "Should I run the code-reviewer to check for quality issues?"
- **Never assume**: Don't run code-reviewer automatically without asking
- **Update task file**: Document review results and any issues found

### Agent Management
- **Use agents for all complex tasks**: Code reviews, documentation, analysis, implementation planning
- **Always provide task context**: Give agents the current task file path when applicable
- **Delegate, don't duplicate**: Use specialized agents instead of handling complex tasks directly

### Agent Context Management (Required)
- **Persist context in repo (important)**: Agents MUST save context under `.claude/doc/` to ensure continuity across runs.
  - Tasks: `.claude/doc/tasks/YYYY-MM-DD-SEQ-slug.md` (SEQ is a 3-digit daily sequence starting at `001`)
  - Decisions/ADR: `.claude/doc/adr/ADR-####-short-title.md`
  - General agent reports: `.claude/doc/agent-reports/YYYY-MM-DD-SEQ-agent-report.md`
- **Round-trip updates**: After each agent step, append a concise update to the active task file.

## Key Implementation Patterns

### Creating a New Linting Rule

Prefer `AstRule` (traverses the real `hdlConvertorAst` AST via `visit_<NodeType>`
overrides, no regex on raw text):

```python
from hdlConvertorAst.hdlAst import HdlModuleDec
from pyhdl_lint.core.rule_base import AstRule, Severity

class MyNewRule(AstRule):
    """Rule to check for specific naming conventions or styles."""

    def __init__(self) -> None:
        super().__init__(
            id="RULE-001",
            description="Short description of my custom rule",
            severity=Severity.WARNING
        )

    def visit_HdlModuleDec(self, o: HdlModuleDec) -> HdlModuleDec:
        if "bad_pattern" in o.name:
            self.add_violation(o, f"'{o.name}' matches a forbidden pattern.")
        return super().visit_HdlModuleDec(o)
```

Fall back to `BaseRule` directly (implementing `check(context: LintContext)` against
`context.content`/`context.lines`) only for checks that genuinely need raw text.
See `README.md` for the full guide and real examples in `pyhdl_lint/languages/`.

### Type-Safe File Operations
```python
from pathlib import Path
from typing import Optional

def read_hdl_file(file_path: Path) -> Optional[str]:
    """Read file content safely using pathlib."""
    if not file_path.exists() or not file_path.is_file():
        return None
    try:
        return file_path.read_text(encoding="utf-8")
    except OSError:
        return None
```

## SOLID Principles for Linting Tools
- **S**ingle Responsibility: Each rule class handles exactly one linting check
- **O**pen/Closed: Extensible for new languages and rules without modifying core engine
- **L**iskov Substitution: All custom rules must implement the `BaseRule` interface (directly, or via the `AstRule` base for AST-driven checks)
- **I**nterface Segregation: Rules receive a single, type-safe `LintContext`
- **D**ependency Inversion: High-level engine depends on the `BaseRule` abstraction, not concrete rule classes
