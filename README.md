# pyhdl_lint

A modular HDL linter for VHDL, Verilog, and SystemVerilog.

## Features
- **Modular Architecture**: Rules are isolated in separate files.
- **Dynamic Loading**: Just add a `.py` file to a language's `rules/` directory to add a new rule.
- **Multi-language Support**: VHDL, Verilog, and SystemVerilog.

## Project Structure
- `pyhdl_lint/core/`: Contains the engine and base classes.
- `pyhdl_lint/languages/`: Contains language-specific rules.
    - `vhdl/rules/`: Add VHDL rules here.
    - `verilog/rules/`: Add Verilog rules here.
    - `systemverilog/rules/`: Add SystemVerilog rules here.

## How to add a rule

There are two base classes to build a rule on, depending on what the rule needs to inspect.

### AST-based rule (recommended)

Inherit from `pyhdl_lint.core.rule_base.AstRule` and override the `visit_<NodeType>`
method(s) for the AST node types you care about (from `hdlConvertorAst.hdlAst`, e.g.
`HdlModuleDec`, `HdlIdDef`, `HdlStmIf`). This traverses the real parsed AST instead of
raw text, so it won't false-positive on comments/string literals and handles multi-line
statements correctly. Call `self.add_violation(node, message)` to report a violation
(line/column are read from the node's own position), and call `super().visit_<NodeType>(node)`
to keep traversing into that node's children.

```python
from hdlConvertorAst.hdlAst import HdlModuleDec

from pyhdl_lint.core.rule_base import AstRule

class MyNewRule(AstRule):
    def __init__(self) -> None:
        super().__init__(id="RULE-001", description="My custom rule")

    def visit_HdlModuleDec(self, o: HdlModuleDec) -> HdlModuleDec:
        if "bad_pattern" in o.name:
            self.add_violation(o, f"Entity '{o.name}' matches a forbidden pattern.")
        return super().visit_HdlModuleDec(o)
```

See `pyhdl_lint/languages/vhdl/rules/rule_entity_naming.py` and
`pyhdl_lint/languages/systemverilog/rules/rule_logic_type.py` for real examples.

### Text-based rule

For checks that genuinely only care about raw source text (rare), inherit from
`pyhdl_lint.core.rule_base.BaseRule` directly and implement `check(context)`, using
`context.content`/`context.lines`.

```python
from pyhdl_lint.core.rule_base import BaseRule, Violation

class MyNewRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(id="RULE-001", description="My custom rule")

    def check(self, context):
        # Your logic here
        return []
```

Either way: drop the file into the appropriate `rules/` directory and it's picked up automatically.

## Installation

This linter relies on the `hdlConvertor` parser engine, which compiles a C++ extension using ANTLR4, and requires Python 3.11 or newer.

### 1. Install System Dependencies

You must install Java, the ANTLR4 build tools, and the C++ runtime development packages:

**On Debian/Ubuntu:**
```bash
sudo apt update
sudo apt install default-jre antlr4 libstringtemplate4-java libantlr4-runtime-dev
```

### 2. Install Linter & Python Dependencies

You can install the linter and compile its dependencies in editable mode using `pip` or `uv`:

```bash
# Using pip
pip install -e .

# Or using uv (much faster)
uv pip install -e .
```

This will install the `pyhdl-lint` command in your environment.

## Usage
```bash
# Lint a single file
pyhdl-lint <path_to_hdl_file>

# Lint every .vhd/.vhdl/.v/.sv file under a directory, recursively
pyhdl-lint <path_to_directory>

# Machine-readable output (used by https://github.com/monkey265/pyhdl-lint-vscode)
pyhdl-lint <path_to_hdl_file> --format json
```

## Editor Integration

A personal-use VSCode extension that lints on save lives in a separate repo:
[pyhdl-lint-vscode](https://github.com/monkey265/pyhdl-lint-vscode). It depends on
this repo's `.venv` being built (see Installation above) and consumes the
`--format json` output shown above.

## Configuration

Rules can be disabled via a config file, checked for in the current working directory
(the directory you run `pyhdl-lint` from):

1. `.pyhdl-lint.toml` — wins outright if present
2. `pyproject.toml`'s `[tool.pyhdl_lint]` table

If neither is found (or the file fails to parse), every rule runs by default.

`.pyhdl-lint.toml`:
```toml
disabled_rules = ["VHDL-002", "SV-001"]
```

or `pyproject.toml`:
```toml
[tool.pyhdl_lint]
disabled_rules = ["VHDL-002", "SV-001"]
```

Requires Python 3.11+ (uses the stdlib `tomllib`).
