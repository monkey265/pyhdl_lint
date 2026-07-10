from hdlConvertorAst.hdlAst import HdlModuleDec

from pyhdl_lint.core.rule_base import AstRule

class ModuleNameRule(AstRule):
    def __init__(self) -> None:
        super().__init__(
            id="SV-002",
            description="Module name should not start with 'mod_'.",
        )

    def visit_HdlModuleDec(self, o: HdlModuleDec) -> HdlModuleDec:
        if o.name.startswith("mod_"):
            self.add_violation(o, f"Module name '{o.name}' should not start with 'mod_'.")
        return super().visit_HdlModuleDec(o)
