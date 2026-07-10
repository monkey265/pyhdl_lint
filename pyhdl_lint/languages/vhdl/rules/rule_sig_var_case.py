import re
from pyhdl_lint.core.rule_base import BaseRule, Violation, Severity

class SignalVariableCaseRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="VHDL-003", 
            description="Signals and variables must be lowercase.",
            severity=Severity.ERROR
        )

    def check(self, context):
        violations = []
        content = context.content
        
        # Regex to find signal and variable declarations
        # Matches: signal/variable <name> :
        pattern = re.compile(r'\b(signal|variable)\s+(\w+)\s*:', re.IGNORECASE)
        
        lines = context.lines
        for i, line in enumerate(lines):
            # Strip comments
            code_line = line.split('--')[0]
            matches = pattern.finditer(code_line)
            for match in matches:
                name = match.group(2)
                if not name.islower():
                    violations.append(
                        Violation(
                            self.id, 
                            i + 1, 
                            match.start(2), 
                            f"Name '{name}' must be lowercase.",
                            self.severity
                        )
                    )
        return violations
