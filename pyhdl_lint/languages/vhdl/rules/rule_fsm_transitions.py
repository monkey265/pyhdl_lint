import re
from pyhdl_lint.core.rule_base import BaseRule, Violation, Severity

class FsmStateChangeRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="VHDL-012",
            description="rising_edge() should only be used on clock signals.",
            severity=Severity.ERROR
        )

    def check(self, context):
        violations = []
        lines = context.lines

        # Matches rising_edge(<signal>)
        rising_edge_pattern = re.compile(r'rising_edge\s*\(\s*(\w+)\s*\)', re.IGNORECASE)

        for i, line in enumerate(lines):
            code_line = line.split('--')[0].strip()

            matches = rising_edge_pattern.finditer(code_line)
            for match in matches:
                signal_name = match.group(1).lower()
                if "clk" not in signal_name and "clock" not in signal_name:
                    violations.append(
                        Violation(
                            self.id,
                            i + 1,
                            line.find(match.group(0)),
                            f"rising_edge() should only be used on clock signals, not '{signal_name}'.",
                            self.severity
                        )
                    )
        return violations
