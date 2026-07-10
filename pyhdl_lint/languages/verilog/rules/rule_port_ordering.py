from hdlConvertorAst.hdlAst import HdlModuleDec

from pyhdl_lint.core.rule_base import AstRule, Severity

class PortOrderingRule(AstRule):
    def __init__(self) -> None:
        super().__init__(
            id="VER-003",
            description="Clock should be the first port, and Reset should be the second.",
            severity=Severity.WARNING,
        )

    def visit_HdlModuleDec(self, o: HdlModuleDec) -> HdlModuleDec:
        if len(o.ports) > 0:
            first = o.ports[0]
            if not any(x in first.name.lower() for x in ("clk", "clock")):
                self.add_violation(first, f"First port '{first.name}' should be the clock signal.")
        if len(o.ports) > 1:
            second = o.ports[1]
            if not any(x in second.name.lower() for x in ("rst", "reset")):
                self.add_violation(second, f"Second port '{second.name}' should be the reset signal.")
        return super().visit_HdlModuleDec(o)
