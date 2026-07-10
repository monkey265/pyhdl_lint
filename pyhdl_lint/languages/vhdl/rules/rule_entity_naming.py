from hdlConvertorAst.hdlAst import HdlModuleDec

from pyhdl_lint.core.rule_base import AstRule

class EntityNameRule(AstRule):
    def __init__(self) -> None:
        super().__init__(
            id="VHDL-001",
            description="Entity name should be in lowercase."
        )

    def visit_HdlModuleDec(self, o: HdlModuleDec) -> HdlModuleDec:
        if not o.name.islower():
            self.add_violation(o, f"Entity name '{o.name}' should be lowercase.")
        return super().visit_HdlModuleDec(o)
