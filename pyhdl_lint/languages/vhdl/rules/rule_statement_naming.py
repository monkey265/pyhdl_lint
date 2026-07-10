import re
from pyhdl_lint.core.rule_base import BaseRule, Violation, Severity

class StatementNamingRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="VHDL-010", 
            description="IF/FOR/WHILE statements should be named.",
            severity=Severity.WARNING
        )

    def check(self, context):
        violations = []
        lines = context.lines
        
        # Pattern to find IF/FOR/WHILE starts
        # Matches: [label:] (IF|FOR|WHILE)
        pattern = re.compile(r'(\w+\s*:)?\s*\b(IF|FOR|WHILE)\b', re.IGNORECASE)
        
        for i, line in enumerate(lines):
            code_line = line.split('--')[0].strip()
            # Avoid matching END IF, END LOOP etc.
            if code_line.upper().startswith("END"):
                continue
            if code_line.upper().startswith("ELSIF"):
                continue
                
            match = pattern.search(code_line)
            if match:
                label = match.group(1)
                statement_type = match.group(2)
                if not label:
                    violations.append(
                        Violation(
                            self.id, 
                            i + 1, 
                            line.lower().find(statement_type.lower()), 
                            f"{statement_type.upper()} statement should have a label.",
                            self.severity
                        )
                    )
        return violations
