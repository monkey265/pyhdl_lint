from hdlConvertorAst.hdlAst import HdlOp, HdlOpType, HdlStmBlock, HdlStmIf, HdlStmProcess, HdlValueId

from pyhdl_lint.core.rule_base import AstRule, Severity

CLOCK_EDGE_FUNCTIONS = ("rising_edge", "falling_edge")

def _contains_clock_edge_call(node: object) -> bool:
    if node is None:
        return False
    if isinstance(node, HdlOp):
        if node.fn == HdlOpType.INDEX and node.ops and isinstance(node.ops[0], HdlValueId) and node.ops[0].val.lower() in CLOCK_EDGE_FUNCTIONS:
            return True
        return any(_contains_clock_edge_call(op) for op in node.ops)
    if isinstance(node, HdlStmIf):
        if _contains_clock_edge_call(node.cond) or _contains_clock_edge_call(node.if_true) or _contains_clock_edge_call(node.if_false):
            return True
        return any(_contains_clock_edge_call(c) or _contains_clock_edge_call(s) for c, s in node.elifs)
    if isinstance(node, HdlStmBlock):
        return any(_contains_clock_edge_call(s) for s in node.body)
    return False

class ClockedProcessSensitivityRule(AstRule):
    def __init__(self) -> None:
        super().__init__(
            id="VHDL-025",
            description="Clocked process sensitivity should be limited to clock and reset signals.",
            severity=Severity.WARNING,
        )

    def visit_HdlStmProcess(self, o: HdlStmProcess) -> HdlStmProcess:
        if _contains_clock_edge_call(o.body):
            for s in (o.sensitivity or []):
                if isinstance(s, HdlValueId):
                    name = s.val.lower()
                    if not any(x in name for x in ("clk", "clock", "rst", "reset")):
                        self.add_violation(
                            o,
                            f"Clocked process sensitivity should be limited to clock and reset signals; found unexpected signal '{s.val}'.",
                        )
        return super().visit_HdlStmProcess(o)
