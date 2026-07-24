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

### Phase 1: Infrastructure COMPLETE
- [x] **Project guidelines** - CLAUDE.md and PLAN.md initialized
- [x] **Pathlib refactoring** - Refactored `os.path` calls to `pathlib.Path` (`__main__.py`, `engine.py`, `parser.py`)
- [x] **Type safety** - Added type hints across core modules (`engine.py`, `parser.py`, `rule_base.py`, `reporter.py`, `config.py`, `__main__.py`); no `Any` used, opaque AST typed as `object`
- [x] **Type-safe `LintContext`** - `parser.py` now returns a frozen `LintContext` dataclass (file path, content, lines, language, ast, parse_error) instead of a raw `dict`; all 21 existing rules updated to attribute access

### Phase 2: Enhancement COMPLETE
- [x] **AST-based rule checking** - Added `AstRule` in `rule_base.py`, wrapping `hdlConvertorAst`'s own `HdlAstVisitor` (no new dispatcher needed). Ported `rule_entity_naming.py` (VHDL-001) and `rule_logic_type.py` (SV-001) off regex onto it, verified against a real `hdlConvertor` build in `.venv`. Remaining 19 rules still regex-based (unchanged, separate future work). See `docs/superpowers/specs/2026-07-09-ast-based-rule-checking-design.md`.
- [x] **Standard Rules Library** - Added 10 new `AstRule`-based rules: VER-002 through VER-006 (Verilog) and SV-002 through SV-007 (SystemVerilog) - parameter ALL_CAPS naming, clk/rst port ordering, reset active-low naming, blocking-assignment-in-clocked-block, and combinational-sensitivity-list checks, each verified against the real parser (`HdlOp(fn=ASSIGN)` vs `HdlStmAssign` for blocking/non-blocking; `HdlStmProcess.sensitivity` shapes for clocked/`@*`/`always_comb`/explicit-list). No signal/port prefix rule added - no such convention is idiomatic in Verilog/SystemVerilog. Added `guidelines/verilog_guideline.md` and `guidelines/systemverilog_guideline.md` rule tables to match VHDL's. See `docs/superpowers/specs/2026-07-10-standard-rules-library-design.md`.
- [x] **Configuration File** - `Config.load()` now reads `disabled_rules` from `.pyhdl-lint.toml` (wins if present) or `pyproject.toml`'s `[tool.pyhdl_lint]` table, searched in the cwd; malformed TOML degrades to an empty config with a warning rather than crashing. Bumped `requires-python` to `>=3.11` for stdlib `tomllib`. Naming-prefix config deferred - no rule reads a config-driven prefix yet. See `docs/superpowers/specs/2026-07-09-configuration-file-loading-design.md`.
- [x] **Test suite** - Added `pytest` as a `[project.optional-dependencies] test` extra. 55 tests: per-rule fires/silent cases with exact line/column assertions for all 18 remaining regex-based VHDL rules (`tests/test_vhdl_rules.py`) and VER-001 (`tests/test_verilog_rules.py`), using a fake `LintContext` (`tests/helpers.py`) that bypasses the real parser since `BaseRule` subclasses only read raw text; a smoke test (`tests/test_smoke.py`) runs the real `hdlConvertor`-backed `Engine` end to end and pins exact violation/rule counts. Found and fixed a real bug while writing tests: `rule_safe_fsm_attr.py`'s state-signal detection false-matched its own `attribute fsm_safe_state OF x : SIGNAL IS ...;` line as a second bogus signal declaration. See `docs/superpowers/specs/2026-07-09-test-suite-design.md`.
- [x] **VHDL guideline completeness** - Split VHDL-008/VHDL-013 out of their host classes (`rule_process_suffix.py`, `rule_fsm_redundant_else.py`) into their own files, fixing the one-rule-per-file violation flagged by the earlier audit. Implemented the 3 rules that audit found missing: VHDL-023 (port category comments, text-based - comments aren't in the AST at all), VHDL-024 (reset naming reflects synchronicity, `AstRule` - correlates entity port naming against process sensitivity-list usage across the whole architecture; VHDL's entity/architecture are separate top-level AST siblings, not nested like Verilog's combined module), VHDL-025 (clocked process sensitivity limited to clk/reset, `AstRule` - VHDL's `rising_edge(clk)` parses as a generic `HdlOp(fn=INDEX)` function call, not a dedicated edge op like Verilog's `posedge`). VHDL: 19 -> 24 rules. See `docs/superpowers/specs/2026-07-10-vhdl-completeness-design.md`.

### Phase 3: Real-World Usability IN PROGRESS
- [x] **Multi-file / directory linting** - `pyhdl-lint <path>` now accepts a directory, recursively discovering `.vhd`/`.vhdl`/`.v`/`.sv` files (non-HDL files silently skipped), caching one `Engine` per language encountered, and printing a `Reporter.report_summary()` (files checked, total violations) after all per-file reports - only for the directory path, so single-file output is unchanged. `main()` now returns an exit code instead of calling `sys.exit()` internally (testable in-process; also the correct shape for a `[project.scripts]` entry point). See `docs/superpowers/specs/2026-07-10-multi-file-linting-design.md`.
- [ ] **CI test/lint gate** - `.github/workflows/release.yml` currently publishes to PyPI on every push to `main` with no test or lint step beforehand; add a CI workflow (pytest, mypy, ruff) that must pass before the release workflow runs, once the Phase 2 test suite exists to gate on
- [ ] **Exclude directories during recursive scan** - directory linting's `rglob` currently walks everything, including `.git/`, `build/`, or vendored IP directories that may contain HDL files that shouldn't be linted; add a skip-list (dot-directories, common build dirs) or an `--exclude` glob option
- [ ] **`--quiet`/`-q` CLI flag** - `Reporter` already supports a `quiet` mode but nothing in the CLI exposes it
- [x] **`--format json` output mode** - Added `--format {text,json}` to `__main__.py` via `argparse` (replacing manual `sys.argv` indexing - justified now that there are 2 independent flags). `text` (default) is byte-for-byte unchanged; `json` prints a single JSON array of violations for a single-file target, for machine consumption.
- [x] **VSCode extension split into its own repo** - originally built as `editors/vscode/` in this repo; split out to [pyhdl-lint-vscode](https://github.com/monkey265/pyhdl-lint-vscode) since editor integration is a separate concern from the CLI linter. Consumes `--format json` above. That repo's own history covers a real bug hit along the way: a symlink-installed extension gets silently pruned by VSCode's extension scanner on every restart (confirmed via `sharedprocess.log`) - fixed by packaging with `vsce`/`npm` and installing via `code --install-extension` instead.
- [ ] **Column-indexing inconsistency** - discovered while building the extension: `AstRule`-based violations report `position.start_column` from `hdlConvertor`, which is 1-indexed; regex-based `BaseRule` violations use Python's `.find()`, which is 0-indexed. Same tool, two different column conventions depending on which rule fired. Not fixed - would mean auditing every rule file's column semantics, out of scope for "build the extension"; the extension currently passes columns through as-is (worst case a squiggle lands one character off, never the wrong line)
