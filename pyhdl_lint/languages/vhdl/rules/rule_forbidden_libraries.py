import re
from pyhdl_lint.core.rule_base import BaseRule, Violation, Severity

class ForbiddenLibrariesRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="VHDL-016", 
            description="Use 'numeric_std' instead of the non-standard 'std_logic_unsigned' or 'std_logic_arith'.",
            severity=Severity.ERROR
        )

    def check(self, context):
        violations = []
        # Matches: use ieee.std_logic_unsigned.all; or library std_logic_unsigned;
        pattern = re.compile(r'\b(std_logic_unsigned|std_logic_arith)\b', re.IGNORECASE)
        
        lines = context.lines
        for i, line in enumerate(lines):
            code_line = line.split('--')[0]
            if pattern.search(code_line):
                violations.append(
                    Violation(
                        self.id, 
                        i + 1, 
                        line.lower().find(pattern.search(code_line).group(0).lower()), 
                        f"Non-standard library '{pattern.search(code_line).group(0)}' is forbidden. Use 'numeric_std' instead.",
                        self.severity
                    )
                )
        return violations
