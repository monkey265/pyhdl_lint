from pyhdl_lint.core.rule_base import BaseRule, Violation

class LogicTypeRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="SV-001", 
            description="Use 'logic' instead of 'reg' in SystemVerilog."
        )

    def check(self, context):
        violations = []
        lines = context["lines"]

        for i, line in enumerate(lines):
            if "reg " in line:
                violations.append(
                    Violation(
                        self.id, 
                        i + 1, 
                        line.find("reg "), 
                        "Prefer 'logic' over 'reg' in SystemVerilog."
                    )
                )
        return violations
