import re
from pyhdl_lint.core.rule_base import BaseRule, Violation, Severity

class VariablePrefixRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="VHDL-005", 
            description="Variables should have prefix 'v_'.",
            severity=Severity.WARNING
        )

    def check(self, context):
        violations = []
        pattern = re.compile(r'\bvariable\s+(\w+)\s*:', re.IGNORECASE)
        
        lines = context["lines"]
        for i, line in enumerate(lines):
            code_line = line.split('--')[0]
            matches = pattern.finditer(code_line)
            for match in matches:
                name = match.group(1)
                if not name.startswith("v_"):
                    violations.append(
                        Violation(
                            self.id, 
                            i + 1, 
                            match.start(1), 
                            f"Variable '{name}' should have prefix 'v_'.",
                            self.severity
                        )
                    )
        return violations
