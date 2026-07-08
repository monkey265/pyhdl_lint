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

## Installation

This linter relies on the `hdlConvertor` parser engine, which compiles a C++ extension using ANTLR4. 

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
pyhdl-lint <path_to_hdl_file>
```
