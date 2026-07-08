# pyhdl_lint (Python HDL Linter) Plan - Modular HDL Linter

`pyhdl_lint` is a **command-line tool for modular linting of HDL files** (VHDL, Verilog, SystemVerilog). It provides a dynamic rules loading system and unified AST checking via `hdlConvertor`.

## Goals

- **Modular Architecture** - Rules are fully isolated in independent modules
- **Dynamic Loading** - Simply drop a `.py` rule file into a language's `rules/` directory to enable it
- **Multi-language Support** - Linting capabilities for VHDL, Verilog, and SystemVerilog
- **AST-based Analysis** - Use `hdlConvertor`'s universal AST for robust linting checks
- **Professional UX** - Concise, clear, and informative CLI warnings/errors with no emoji noise
- **Type Safety** - Fully annotated codebase to facilitate reliability and clean development

## Non-Goals

- Formatting code files (handled by external formatters)
- Full syntax compilation or logic synthesis (rely on actual compiler tools)
- Interactive GUI (keep the interface terminal/CLI focused)

---

## High-Level Architecture

**pyhdl_lint Workflow**:

1. **CLI Execution**: User invokes `pyhdl-lint <file_path>`
2. **Language Mapping**: Map file extension to target language (VHDL, Verilog, SystemVerilog)
3. **Rule Loading**: Dynamically load rule classes from the appropriate language's rules directory
4. **Parsing**: Use `hdlConvertor` to parse the HDL source file into a unified AST
5. **Linting Engine**: Execute each loaded rule against the AST context, checking enabled status
6. **Reporting**: Print out formatted violation list (file, line, column, severity, description) and exit with code `1` if violations are found

**User Workflow**:
```bash
# Install linter
pip install -e .

# Run linter on a file
pyhdl-lint tests/vhdl_test_guidelines.vhd
```

---

## CLI Architecture

`pyhdl_lint` follows a **simple, single-entry CLI command structure**:

### Command
- **`pyhdl-lint <file_path>`** - Lint target HDL source file and report findings

### Design Principles
- **Extensibility** - Rule engine is open to extension via new dynamically loaded modules
- **Boring & Stable** - Rely on the standard library where possible, avoiding heavy dependencies
- **Strict Verification** - Check rule validity before execution to prevent runtime crashes

---

## HDL Integration Model

### Supported Dialects (via hdlConvertor)
- **VHDL**: 2008 dialect (via `PyHdlLanguageEnum.VHDL_2008`)
- **Verilog**: 2005 dialect (via `PyHdlLanguageEnum.VERILOG_2005`)
- **SystemVerilog**: 2017 dialect (via `PyHdlLanguageEnum.SYSTEM_VERILOG_2017`)

### Input Mapping
- `.vhd`, `.vhdl` ➔ VHDL
- `.v` ➔ Verilog
- `.sv` ➔ SystemVerilog

---

## Configuration Model (Type-Safe)

`pyhdl_lint` uses a **type-safe configuration class**:

```python
class Config:
    """Type-safe configuration loader and validator."""
    def __init__(self, config_dict: Optional[dict] = None) -> None:
        self.settings: dict = config_dict or {}

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "Config":
        """Load configuration from pyproject.toml or local files."""
        ...

    def is_rule_enabled(self, rule_id: str) -> bool:
        """Check if a specific rule ID is enabled."""
        ...
```

### Professional Standards
- **No hardcoded paths** - Always use system-agnostic relative paths or `pathlib.Path`
- **Type safety** - Full type annotations, avoiding dynamic types where possible
- **Boring output** - Clear text outputs without emojis or unnecessarily complex formats

---

## Current Architecture Status

### Working Well
- **Dynamic rule discovery** - Automatically finds and loads classes inheriting from `BaseRule`
- **AST Parsing** - Successfully converts target files into AST structures using `hdlConvertor`
- **Clean output format** - Easy-to-read list of linting errors/warnings

### Recently Modernized
- **CLAUDE.md / PLAN.md** - Introduced project standards and architecture roadmap
- **Packaging** - Modern `pyproject.toml` configuration

### Future Enhancements
- **Pathlib Migration** - Refactor all remaining `os.path` usages to `pathlib.Path`
- **Type-safe Context** - Replace dict-based context with a typed dataclass or Pydantic model
- **Linter Rule Library** - Build out standard rule packages for VHDL/Verilog/SystemVerilog
- **Configuration loading** - Complete configuration parsing from `pyproject.toml`

---

## Implementation Architecture

### Module Organization
```
pyhdl_lint/
├── __init__.py
├── __main__.py          # Main entrypoint, reads CLI args & runs engine
├── core/                # Core linting logic
│   ├── __init__.py
│   ├── engine.py        # Rule execution and dynamic module loading
│   ├── parser.py        # hdlConvertor parser wrapper
│   ├── reporter.py      # Violation printing & terminal outputs
│   └── rule_base.py     # Severity, BaseRule, and Violation class definitions
├── utils/               # Shared utilities
│   ├── __init__.py
│   └── config.py        # Config loader
└── languages/           # Language rulesets
    ├── vhdl/rules/
    ├── verilog/rules/
    └── systemverilog/rules/
```

---

## Quality Standards

### Code Quality (Professional Standards)
- **Type Safety** - Avoid the `Any` type completely, use concrete type hints
- **Error Handling** - Informative error outputs, especially for parser failures
- **Formatting** - Consistent formatting verified with `ruff` and `mypy`

### Success Criteria
- **Extensible checks** - Creating a new rule is as simple as adding a file with a `BaseRule` subclass
- **Reliability** - Will not crash on syntax errors, reporting them gracefully instead
- **Clean Exit Status** - Exits with non-zero code on violation, allowing easy CI/CD integration

---

## Modernization Status

### Phase 1: Infrastructure IN PROGRESS
- [x] **Project guidelines** - CLAUDE.md and PLAN.md initialized
- [ ] **Pathlib refactoring** - Refactor `os.path` calls to `pathlib.Path`
- [ ] **Type safety** - Enforce zero `Any` types across core modules

### Phase 2: Enhancement (Future)
- [ ] **Standard Rules Library** - Basic rule suite for VHDL/Verilog/SystemVerilog
- [ ] **Configuration File** - Fully support `pyproject.toml` tool configuration section
- [ ] **Test suite** - Implement pytest checks using sample HDL files in `/tests`
