import re
from pyhdl_lint.core.rule_base import BaseRule, Violation, Severity

class IntegerRangeRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="VHDL-017", 
            description="Integers used as counters or states should have a range limit.",
            severity=Severity.WARNING
        )

    def check(self, context):
        violations = []
        # Matches: signal <name> : integer; (without range)
        pattern = re.compile(r'\bsignal\s+(\w+)\s*:\s*integer\s*(?:;|\)|:=)', re.IGNORECASE)
        
        lines = context.lines
        for i, line in enumerate(lines):
            code_line = line.split('--')[0]
            match = pattern.search(code_line)
            if match:
                name = match.group(1)
                # Heuristic: only check if it looks like a counter or state
                if any(x in name.lower() for x in ["count", "cnt", "state", "index"]):
                    violations.append(
                        Violation(
                            self.id, 
                            i + 1, 
                            line.find(name), 
                            f"Integer signal '{name}' should have a range limit to prevent overflow and unintended hardware usage.",
                            self.severity
                        )
                    )
        return violations
