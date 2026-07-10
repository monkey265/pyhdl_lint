# Standard Rules Library (PLAN.md Phase 2, part 2 of 2)

## Problem

VHDL has 19 rules; Verilog and SystemVerilog each have exactly 1
(`rule_module_naming.py` / `rule_logic_type.py`). PLAN.md asks for naming convention
rules (ports, signals, modules, parameter prefixes) and design safety rules (blocking
vs. non-blocking assignments, sensitivity list checks) ported to both languages. No
`verilog_guideline.md`/`systemverilog_guideline.md` exists, so exact conventions
weren't predefined and were decided during brainstorming (see Decisions).

## Decisions

- **Duplicate small rule files across `languages/verilog/rules/` and
  `languages/systemverilog/rules/`** rather than building a shared base module. The
  architecture has zero cross-language sharing today; introducing one for ~10 small
  rules would be a new abstraction not otherwise needed.
- **No signal/port prefix convention invented.** VHDL's `s_`/`v_` Hungarian-style
  prefixes aren't idiomatic in Verilog/SV shops, and no house convention exists to
  encode. "Signal naming" from PLAN.md's wording is left uncovered rather than
  inventing an arbitrary rule.
- **Parameters: `ALL_CAPS`, not a prefix.** Substitutes for VHDL's `g_` prefix
  convention with the actual near-universal Verilog/SV idiom.
- **Clk/rst port discipline ported from VHDL** (VHDL-019/020 equivalents) since it's a
  hardware-design concern independent of language.
- **All 10 new rules are `AstRule`-based**, not regex `BaseRule` (even though the
  existing `VER-001` is regex-based) — per README's stated preference for new rules,
  and because every fact below was independently verified against the real installed
  `hdlConvertor` parser rather than assumed.

## Verified AST facts (real parser, not guessed)

- Verilog module header info (`.params`, `.ports`) lives at `HdlModuleDef.dec`, not a
  standalone top-level `HdlModuleDec` (Verilog's `module ... endmodule` combines
  declaration and body in one construct, unlike VHDL's separate `entity`/`architecture`).
  Each `HdlIdDef` port/param carries its own accurate `.position` — no precision loss
  like VHDL-001 had with plain-`str` names.
- Blocking assignment (`x = y;`) parses to `HdlOp(fn=HdlOpType.ASSIGN, ops=[dst, src])`
  appearing directly in a statement list. Non-blocking (`x <= y;`) parses to
  `HdlStmAssign(is_blocking=False, dst=..., src=...)`. (`HdlStmAssign.is_blocking` is
  `False` even for non-blocking assignments in this parser version — it does not
  reliably distinguish blocking/non-blocking; the *class* used (`HdlOp` vs
  `HdlStmAssign`) is the actual signal.)
- `HdlStmProcess.sensitivity`:
  - Clocked (`always @(posedge clk)` / SV `always_ff @(posedge clk)`): a list
    containing `HdlOp(fn=HdlOpType.RISING or FALLING, ops=[<clock HdlValueId>])`.
  - Verilog combinational (`always @*`): `[HdlAll]` — `HdlAll` appears as the class
    object itself (not an instance; per its docstring it must never be instantiated),
    so detection must use `is HdlAll`, not `isinstance`.
  - SystemVerilog `always_comb`: `sensitivity is None` (different from Verilog's `@*`).
  - Explicit list (`always @(a, b)`): a list of `HdlValueId`s.

## Design

### Naming rules (`visit_HdlModuleDec`)

- **SV-002** (`rule_module_naming.py`, mirrors VER-001): flag `o.name.startswith("mod_")`.
- **VER-002/SV-003** (`rule_parameter_naming.py`): for each `p` in `o.params`, flag if
  `p.name != p.name.upper()`.
- **VER-003/SV-004** (`rule_port_ordering.py`): for `o.ports`, flag index 0 if it doesn't
  contain `clk`/`clock`; flag index 1 if it doesn't contain `rst`/`reset`. Mirrors
  VHDL-019 exactly, AST-based instead of regex.
- **VER-004/SV-005** (`rule_reset_active_low.py`): for each port whose name contains
  `rst`/`reset`, flag if it doesn't end with `_n`. Mirrors VHDL-020.

### Design safety rules (`visit_HdlStmProcess` + `visit_HdlOp`)

- **VER-005/SV-006** (`rule_blocking_assignment.py`): track "inside a clocked process"
  via a save/restore instance flag set in an overridden `visit_HdlStmProcess` (clocked
  = sensitivity contains an `HdlOp` with `fn in (RISING, FALLING)`); in an overridden
  `visit_HdlOp`, flag `fn == ASSIGN` while that flag is set.
- **VER-006/SV-007** (`rule_comb_sensitivity.py`): in `visit_HdlStmProcess`, flag when
  `sensitivity` is a non-empty list that is neither clocked nor `[HdlAll]` (Verilog) —
  the SV variant additionally treats `sensitivity is None` (`always_comb`) as clean.

All violations report `line`/`column` from the flagged node's own `.position`
(ports/params/HdlOp all carry accurate real positions, unlike VHDL-001's degraded case).

## Verification

Extend `tests/test_vhdl_rules.py`-style fake-`LintContext` testing where possible, but
since these are `AstRule`s, they need a real `context.ast` — tests use the real
`Parser("verilog"/"systemverilog").get_context(...)` against small `tmp_path` fixture
files, matching `tests/test_ast_rules.py`'s existing pattern. New
`tests/test_verilog_ast_rules.py` and `tests/test_systemverilog_ast_rules.py` (fires +
silent case per rule), plus updated `tests/test_smoke.py` rule-count assertions (now 7
Verilog rules, 8 SystemVerilog rules) and a live full-fixture violation-count check.

## Out of scope

- No signal/port prefix rule (no real convention to enforce).
- No shared cross-language rule base module.
- No changes to the 19 existing VHDL rules or `VER-001`/`SV-001`.
