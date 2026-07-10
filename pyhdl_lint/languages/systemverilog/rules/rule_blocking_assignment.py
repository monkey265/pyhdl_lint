from typing import Optional

from hdlConvertorAst.hdlAst import HdlOp, HdlOpType, HdlStmProcess

from pyhdl_lint.core.rule_base import AstRule, Severity

CLOCK_EDGE_OPS = (HdlOpType.RISING, HdlOpType.FALLING)

class BlockingAssignmentRule(AstRule):
    def __init__(self) -> None:
        super().__init__(
            id="SV-006",
            description="Blocking assignment ('=') should not be used inside a clocked block.",
            severity=Severity.ERROR,
        )
        self._clocked_process: Optional[HdlStmProcess] = None

    def visit_HdlStmProcess(self, o: HdlStmProcess) -> HdlStmProcess:
        previous = self._clocked_process
        sensitivity = o.sensitivity or []
        is_clocked = any(isinstance(s, HdlOp) and s.fn in CLOCK_EDGE_OPS for s in sensitivity)
        self._clocked_process = o if is_clocked else None
        result = super().visit_HdlStmProcess(o)
        self._clocked_process = previous
        return result

    def visit_HdlOp(self, o: HdlOp) -> HdlOp:
        if self._clocked_process is not None and o.fn == HdlOpType.ASSIGN:
            # HdlOp nodes for blocking assignments carry no position in this parser;
            # fall back to the enclosing clocked process's position instead of (0, 0).
            anchor = o if o.position is not None else self._clocked_process
            self.add_violation(anchor, "Blocking assignment '=' should not be used inside a clocked block; use non-blocking '<=' instead.")
        return super().visit_HdlOp(o)
