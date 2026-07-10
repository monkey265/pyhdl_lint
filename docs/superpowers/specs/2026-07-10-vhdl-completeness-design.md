# VHDL Rule Completeness: VHDL-023/024/025 + VHDL-008/013 split

## Problem

`guidelines/vhdl_guideline.md`'s own rule table has 3 rows marked `[ ]` unimplemented
(VHDL-023 port category comments, VHDL-024 reset synchronicity naming, VHDL-025
clocked-process sensitivity restricted to clk/reset), found during an earlier audit.
Separately, VHDL-008 and VHDL-013 are emitted from inside `ProcessNamingRule`
(VHDL-007) and `FsmStateChangeRule` (VHDL-012) respectively rather than their own
files/classes — noted as a structural inconsistency in that same audit (can't disable
one without the other via `disabled_rules`; violates the project's stated
one-rule-per-file principle).

## Verified AST facts (real parser)

- **Comments are not in the AST at all.** `HdlIdDef.doc` is empty (`''`) even for a
  port with a real inline `-- comment` in the source. VHDL-023 must be text-based
  (`BaseRule`), not `AstRule` — there is nothing for an AST rule to inspect.
- **VHDL's `rising_edge(clk)` is a generic function call, not a dedicated edge op.**
  Unlike Verilog's `posedge clk` (which parses to `HdlOp(fn=RISING, ...)`), VHDL's
  `rising_edge(clk)` parses to `HdlOp(fn=HdlOpType.INDEX, ops=[HdlValueId('rising_edge'),
  HdlValueId('clk')])` — VHDL's array-indexing and function-call syntax are
  indistinguishable at this AST level. Detecting "is this process clocked" requires
  searching the process body for this `INDEX`-with-`rising_edge`/`falling_edge`-name
  shape, not looking for a `RISING`/`FALLING` op.
- **`HdlStmProcess.sensitivity` items are real `HdlValueId`s with `.val` names** (e.g.
  `[HdlValueId('clk'), HdlValueId('areset_n')]` for `PROCESS(clk, areset_n)`) — but
  **carry no position** (`.position is None` for every sensitivity item, verified).
  Violations anchored on a sensitivity item must fall back to the enclosing process's
  position (same pattern already used for VER-005/SV-006's blocking-assignment rule).
- Entity ports (`HdlModuleDec.ports`, same `HdlIdDef` type) **do** carry real
  positions, confirmed identically to the Verilog/SystemVerilog work.

## Design

### 1. Split VHDL-008/VHDL-013 (pure extraction, no logic change)

- `pyhdl_lint/languages/vhdl/rules/rule_process_suffix.py` — new `ProcessSuffixRule`
  (VHDL-008), containing exactly the `_proc`-suffix check currently inside
  `ProcessNamingRule.check()`. `ProcessNamingRule` keeps only the label-required check.
- `pyhdl_lint/languages/vhdl/rules/rule_fsm_redundant_else.py` — new
  `FsmRedundantElseRule` (VHDL-013), containing exactly the redundant-ELSE check
  currently inside `FsmStateChangeRule.check()`. `FsmStateChangeRule` keeps only the
  rising-edge-on-clocks-only check.
- No detection-logic changes; this only moves code so each ID is independently
  enable/disable-able and the dynamic loader reports 21 rule objects for VHDL instead
  of 19.

### 2. VHDL-023 — port category comments (`BaseRule`, text-based)

Reuses `rule_port_ordering.py`'s `inside_port` line-scanning pattern. While inside a
`PORT ( ... );` block, track whether any line (comment-only or trailing) contains a
`--` comment. If the block closes having seen zero comments, flag once at the `PORT (`
line: `"Port list should have comments indicating signal categories (e.g. -- Inputs, -- Outputs)."`

### 3. VHDL-024 — reset naming reflects synchronicity (`AstRule`)

Override `visit_HdlModuleDef`. First pass over `o.objs`: for every `HdlStmProcess`,
collect `s.val.lower()` for each `HdlValueId` in `o.sensitivity` into an
`async_signals` set (this is VHDL's async-reset idiom — `PROCESS(clk, areset_n)`).
Then, for each port in `o.dec.ports` whose name contains `rst`/`reset`: compare
`name.lower().startswith("a")` against `name.lower() in async_signals`; flag a
mismatch in either direction (named-async-but-never-used-async, or
used-async-but-not-named-async), anchored on the port (real position available).

### 4. VHDL-025 — clocked process sensitivity limited to clk/reset (`AstRule`)

Override `visit_HdlStmProcess`. A small recursive helper `_contains_clock_edge_call`
walks `HdlStmBlock`/`HdlStmIf`/`HdlOp` looking for the `INDEX`-op-with-
`rising_edge`/`falling_edge`-name shape described above. If found (process is
clocked), flag every sensitivity-list signal whose name doesn't contain
`clk`/`clock`/`rst`/`reset`, anchored on the enclosing process (sensitivity items have
no position of their own).

## Testing

Extend `tests/test_vhdl_rules.py` (fake-`LintContext`) for VHDL-023 (text-based, no
real parser needed) and the post-split `VHDL-008`/`VHDL-013` (same fake-context
pattern, now testing the new standalone classes instead of the ones they were
extracted from). VHDL-024/025 need `tests/test_ast_rules.py`-style real-parser tests
(added there or a new `tests/test_vhdl_ast_rules.py`) since they're `AstRule`s.
Update `tests/test_smoke.py`'s VHDL rule-count assertion (19 → 21).

## Out of scope

- No change to any other existing VHDL rule.
- No change to VHDL-020 (still just checks the `_n` suffix; VHDL-024 is additive, not
  a replacement).
