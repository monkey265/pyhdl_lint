from hdlConvertorAst.hdlAst import HdlIdDef, HdlOp, HdlValueId

from pyhdl_lint.core.rule_base import AstRule

def _type_mentions_reg(type_expr: object) -> bool:
    if isinstance(type_expr, HdlValueId):
        return type_expr.val == "reg"
    if isinstance(type_expr, str):
        return type_expr == "reg"
    if isinstance(type_expr, HdlOp):
        return any(_type_mentions_reg(op) for op in type_expr.ops)
    return False

class LogicTypeRule(AstRule):
    def __init__(self) -> None:
        super().__init__(
            id="SV-001",
            description="Use 'logic' instead of 'reg' in SystemVerilog."
        )

    def visit_HdlIdDef(self, o: HdlIdDef) -> HdlIdDef:
        if _type_mentions_reg(o.type):
            self.add_violation(o, "Prefer 'logic' over 'reg' in SystemVerilog.")
        return super().visit_HdlIdDef(o)
