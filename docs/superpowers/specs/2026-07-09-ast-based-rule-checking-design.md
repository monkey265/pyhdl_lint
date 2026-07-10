# AST-Based Rule Checking (PLAN.md Phase 2)

## Problem

Most rules do line-by-line regex/string matching on `context.content`/`context.lines`
instead of using the `hdlConvertor` AST already available at `context.ast`. This
false-positives on comments/string literals and misses multi-line statements.
PLAN.md names `rule_entity_naming.py` and `rule_logic_type.py` as examples.

## Research findings

`hdlConvertor`'s AST node classes live in a separate transitive dependency,
`hdlConvertorAst` (package `hdlConvertorAst.hdlAst`), not `hdlConvertor.hdlAst`.
Confirmed from source (GitHub, via `gh search code` and `WebFetch` on raw source
files — `hdlConvertorAst` is not installed in this sandbox, so nothing below was
verified by actually running the parser):

- `HdlConvertor().parse(...)` returns a single `HdlContext`, whose `.objs` is a
  flat list of top-level `iHdlObj`s (`HdlModuleDef`, `HdlModuleDec`, `HdlLibrary`, ...).
- Every AST node (`iHdlObj` and subclasses, including leaf nodes like `HdlValueId`)
  carries a `.position` (`CodePosition`: `file_name`, `start_line`, `start_column`,
  `stop_line`, `stop_column`) — real line/col info, no need to re-derive it from text.
- `hdlConvertorAst.to.hdl_ast_visitor.HdlAstVisitor` is a ready-made traversal base
  class already shipped by the dependency: `visit_HdlContext` entry point,
  `visit_<ClassName>` per node type, with correct child recursion already implemented
  (e.g. `visit_HdlModuleDec` visits `.params`, `.ports`, `.objs`). No need to write a
  new dispatcher — subclass this instead (ponytail rung 5: already-installed dependency
  solves it).
- `HdlModuleDec.name` is the entity/module name as an `HdlValueId` (itself positioned).
- `HdlIdDef` covers ports/generics/signals/variables uniformly, distinguished by fields
  (`.direction`, `.is_const`, `.is_latched`, etc.), not by separate classes.
- For SystemVerilog `reg` vs `logic` vs `bit`: traced the C++ parser
  (`src/svConvertor/typeParser.cpp::visitInteger_vector_type`) — the literal keyword
  text is preserved via `mkWireT(ctx, HdlValueId(ctx->getText()), ...)`, i.e. embedded
  somewhere in the type expression tree as an `HdlValueId`. The *exact* nesting shape
  (bare `HdlValueId` vs wrapped in `HdlOp`) could not be confirmed without a live parse.
  `HdlIdDef.is_latched` does **not** correspond to `reg` — it corresponds to the SV
  `var` keyword instead (confirmed from `visitNet_or_var_data_type`), so it must not be
  used as the signal for this rule.

## Update: verified against a real install

`hdlConvertor`/`hdlConvertorAst` were successfully built via `uv pip install -e .`
into a local `.venv` (build tools `cmake`, `g++`, `antlr4`, `java` were already
present). This resolved the open questions above against the real parser output:

- `HdlModuleDec.name` / `HdlIdDef.name` are plain `str`, **not** `HdlValueId` as the
  source-reading guess assumed. Only the *enclosing* node (`HdlModuleDec`, `HdlIdDef`)
  carries a `.position` (`start_line`, `start_column`, `stop_line`, `stop_column`,
  `file_name`); there is no separate positioned name token. `.position.start_column`
  points at the start of the declaration keyword (e.g. `entity`), not at the name text
  itself — this is a minor, accepted precision loss vs. the old regex rule (which
  pointed at the name).
- For SystemVerilog `reg`/`logic`/`wire`: confirmed via a real parse of a throwaway
  `.sv` file — `HdlIdDef.type` for `reg x;` is `HdlOp(fn='PARAMETRIZATION', ops=[HdlValueId('reg'), None, None])`;
  for `logic x;` it's the same shape with `ops=[HdlValueId('logic'), ...]`; for `wire x;`
  it's `HdlTypeAuto`. **Correction**: an earlier pass of this check misread `ops[0]` as a
  plain `str` because `iHdlObj.__repr__`/`pprint` renders `HdlValueId` as a bare quoted
  string, hiding the wrapper class. A direct `isinstance()`/`type()` check (not reading
  the debug repr) showed `ops[0]` is genuinely an `HdlValueId` instance — matching the
  original source-reading guess, not the repr-based "correction". Lesson: verify runtime
  shape with `isinstance`/`type()` directly, never by eyeballing a debug `__repr__`.
  `is_latched` is confirmed unrelated (`False` in all cases here, since none used SV's `var`).

Both `AstRule.add_violation` and the `_type_mentions_reg` helper handle `HdlValueId`
(checking `.val`) as the primary case, with a plain-`str` fallback kept defensively.

## Design

### 1. Generic `AstRule` base class — `pyhdl_lint/core/rule_base.py`

Wraps `HdlAstVisitor` rather than reimplementing traversal:

```python
class AstRule(BaseRule, HdlAstVisitor):
    def __init__(self, id: str, description: str, severity: Severity = Severity.ERROR) -> None:
        BaseRule.__init__(self, id, description, severity)
        HdlAstVisitor.__init__(self)
        self._violations: List[Violation] = []

    def add_violation(self, node: object, message: str) -> None:
        pos = getattr(node, "position", None)
        line = pos.start_line if pos is not None else 0
        column = pos.start_column if pos is not None else 0
        self._violations.append(Violation(self.id, line, column, message, self.severity))

    def check(self, context: LintContext) -> List[Violation]:
        self._violations = []
        if context.ast is not None:
            self.visit_HdlContext(context.ast)
        return self._violations
```

Rule authors override `visit_<NodeType>` methods, call `self.add_violation(node, msg)`,
and call `super().visit_<NodeType>(node)` to continue traversing children. No AST
(parse error) means no violations — matches the existing "never crash on syntax
errors" behavior of the regex-based rules.

### 2. `pyproject.toml`

Add `hdlConvertorAst` as an explicit direct dependency (currently only pulled in
transitively via `hdlConvertor`), since the code now imports it directly.

### 3. Port `rule_entity_naming.py` (VHDL-001) to `AstRule`

Override `visit_HdlModuleDec`; check `o.name.val.islower()`; `add_violation(o.name, ...)`
for line/col (the `HdlValueId` name node is itself positioned). Fully grounded — no
open questions.

### 4. Port `rule_logic_type.py` (SV-001) to `AstRule`

Override `visit_HdlIdDef`; recursively scan `o.type` for any `HdlValueId` with
`.val == "reg"` (robust to whatever exact wrapper `mkWireT` produces, rather than
assuming one specific shape); `add_violation(o, ...)` if found. **Explicitly marked
best-effort / unverified against a live parse** in a code comment — if the assumption
is wrong, the rule under-fires (misses violations) rather than crashing or
false-positiving, which is an acceptable failure mode.

### 5. Verification

`hdlConvertorAst` node classes are plain Python classes (no C++ build needed to
*construct* instances directly), so a `test_ast_rule.py` builds small fake
`HdlContext`/`HdlModuleDec`/`HdlIdDef` trees by hand and asserts both ported rules
fire on violating input and stay silent on clean input, plus that `AstRule.check`
returns `[]` when `context.ast is None`. This validates pyhdl_lint's own logic given
a known AST shape — it does not validate that hdlConvertor's real parser actually
produces that shape.

## Out of scope

- The other 19 existing regex-based rules are untouched.
- No change to `hdlConvertor` itself or attempt to install/build it in this environment.
- No new "Standard Rules Library" expansion (separate PLAN.md Phase 2 item).
