import re
from pyhdl_lint.core.rule_base import BaseRule, Violation, Severity

class LibraryWorkRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="VHDL-009", 
            description="Created library must not be named 'work'.",
            severity=Severity.ERROR
        )

    def check(self, context):
        violations = []
        # Matches: library work;
        pattern = re.compile(r'\blibrary\s+work\b', re.IGNORECASE)
        
        lines = context["lines"]
        for i, line in enumerate(lines):
            code_line = line.split('--')[0]
            if pattern.search(code_line):
                violations.append(
                    Violation(
                        self.id, 
                        i + 1, 
                        line.lower().find("work"), 
                        "Library must not be named 'work'.",
                        self.severity
                    )
                )
        return violations
