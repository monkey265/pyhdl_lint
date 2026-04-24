import re
from pyhdl_lint.core.rule_base import BaseRule, Violation, Severity

class SignalPrefixRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="VHDL-004", 
            description="Signals should have prefix 's_'.",
            severity=Severity.WARNING
        )

    def check(self, context):
        violations = []
        pattern = re.compile(r'\bsignal\s+(\w+)\s*:', re.IGNORECASE)
        
        lines = context["lines"]
        for i, line in enumerate(lines):
            code_line = line.split('--')[0]
            matches = pattern.finditer(code_line)
            for match in matches:
                name = match.group(1)
                if not name.startswith("s_"):
                    violations.append(
                        Violation(
                            self.id, 
                            i + 1, 
                            match.start(1), 
                            f"Signal '{name}' should have prefix 's_'.",
                            self.severity
                        )
                    )
        return violations
