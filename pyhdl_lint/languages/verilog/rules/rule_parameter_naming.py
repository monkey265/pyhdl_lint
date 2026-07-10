from hdlConvertorAst.hdlAst import HdlModuleDec

from pyhdl_lint.core.rule_base import AstRule, Severity

class ParameterNamingRule(AstRule):
    def __init__(self) -> None:
        super().__init__(
            id="VER-002",
            description="Parameters should be ALL_CAPS.",
            severity=Severity.WARNING,
        )

    def visit_HdlModuleDec(self, o: HdlModuleDec) -> HdlModuleDec:
        for param in o.params:
            if param.name != param.name.upper():
                self.add_violation(param, f"Parameter '{param.name}' should be ALL_CAPS.")
        return super().visit_HdlModuleDec(o)
