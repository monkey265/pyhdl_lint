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
1. Create a new `.py` file in the appropriate `rules/` directory.
2. Define a class that inherits from `pyhdl_lint.core.rule_base.BaseRule`.
3. Implement the `check(context)` method.

Example:
```python
from pyhdl_lint.core.rule_base import BaseRule, Violation

class MyNewRule(BaseRule):
    def __init__(self):
        super().__init__(id="RULE-001", description="My custom rule")

    def check(self, context):
        # Your logic here
        return []
```

## Usage
```bash
python -m pyhdl_lint <path_to_hdl_file>
```
