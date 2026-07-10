from hdlConvertorAst.hdlAst import HdlModuleDec

from pyhdl_lint.core.rule_base import AstRule, Severity

class ResetActiveLowRule(AstRule):
    def __init__(self) -> None:
        super().__init__(
            id="SV-005",
            description="Reset signals should be active low (suffix '_n').",
            severity=Severity.WARNING,
        )

    def visit_HdlModuleDec(self, o: HdlModuleDec) -> HdlModuleDec:
        for port in o.ports:
            low_name = port.name.lower()
            if ("rst" in low_name or "reset" in low_name) and not low_name.endswith("_n"):
                self.add_violation(port, f"Reset signal '{port.name}' should be active low and end with '_n'.")
        return super().visit_HdlModuleDec(o)
