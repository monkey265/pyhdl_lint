import re
from pyhdl_lint.core.rule_base import BaseRule, Violation, Severity

class ProcessNamingRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="VHDL-007",
            description="Process must be named.",
            severity=Severity.ERROR
        )

    def check(self, context):
        violations = []
        lines = context.lines

        # Pattern to find process starts, avoiding "end process"
        # Matches: [label:] PROCESS, but NOT END PROCESS
        process_pattern = re.compile(r'(\w+\s*:)?\s*\bPROCESS\b', re.IGNORECASE)

        for i, line in enumerate(lines):
            code_line = line.split('--')[0].strip()
            if code_line.upper().startswith("END"):
                continue

            match = process_pattern.search(code_line)
            if match:
                label = match.group(1)
                if not label:
                    violations.append(
                        Violation(
                            self.id,
                            i + 1,
                            match.start(),
                            "Process must have a label.",
                            Severity.ERROR
                        )
                    )
        return violations
