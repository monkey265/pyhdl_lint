from hdlConvertorAst.hdlAst import HdlAll, HdlOp, HdlOpType, HdlStmProcess

from pyhdl_lint.core.rule_base import AstRule, Severity

CLOCK_EDGE_OPS = (HdlOpType.RISING, HdlOpType.FALLING)

class CombinationalSensitivityRule(AstRule):
    def __init__(self) -> None:
        super().__init__(
            id="VER-006",
            description="Combinational blocks should use '@*' instead of an explicit sensitivity list.",
            severity=Severity.WARNING,
        )

    def visit_HdlStmProcess(self, o: HdlStmProcess) -> HdlStmProcess:
        sensitivity = o.sensitivity or []
        is_clocked = any(isinstance(s, HdlOp) and s.fn in CLOCK_EDGE_OPS for s in sensitivity)
        is_all = any(s is HdlAll for s in sensitivity)
        if sensitivity and not is_clocked and not is_all:
            self.add_violation(o, "Combinational block should use '@*' instead of an explicit sensitivity list.")
        return super().visit_HdlStmProcess(o)
