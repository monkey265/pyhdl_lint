import re
from pyhdl_lint.core.rule_base import BaseRule, Violation, Severity

class ProcessSuffixRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="VHDL-008",
            description="Process name should end in '_proc'.",
            severity=Severity.WARNING
        )

    def check(self, context):
        violations = []
        lines = context.lines

        # Pattern to find labeled process starts, avoiding "end process"
        process_pattern = re.compile(r'(\w+\s*:)?\s*\bPROCESS\b', re.IGNORECASE)

        for i, line in enumerate(lines):
            code_line = line.split('--')[0].strip()
            if code_line.upper().startswith("END"):
                continue

            match = process_pattern.search(code_line)
            if match:
                label = match.group(1)
                if label:
                    name = label.strip().replace(':', '').strip()
                    if not name.endswith("_proc"):
                        violations.append(
                            Violation(
                                self.id,
                                i + 1,
                                line.find(name),
                                f"Process name '{name}' should end with '_proc'.",
                                self.severity
                            )
                        )
        return violations
