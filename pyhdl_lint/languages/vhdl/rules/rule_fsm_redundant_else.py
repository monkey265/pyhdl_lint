import re
from pyhdl_lint.core.rule_base import BaseRule, Violation, Severity

class FsmRedundantElseRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="VHDL-013",
            description="No redundant ELSE branch in FSM state transitions.",
            severity=Severity.WARNING
        )

    def check(self, context):
        violations = []
        lines = context.lines

        inside_case = False
        current_state_label = None
        for i, line in enumerate(lines):
            code_line = line.split('--')[0].strip()
            low_line = code_line.lower()

            if "case" in low_line and "state" in low_line:
                inside_case = True
                continue

            if inside_case:
                if "end case" in low_line:
                    inside_case = False
                    current_state_label = None
                    continue

                # Detect the state we are currently in
                when_match = re.search(r'when\s+(\w+)\s*=>', low_line)
                if when_match:
                    current_state_label = when_match.group(1)
                    continue

                # If we see an ELSE
                if code_line.upper().startswith("ELSE"):
                    # Check next few lines for next_state <= current_state_label
                    found_redundant = False
                    for j in range(i + 1, min(i + 4, len(lines))):
                        next_line = lines[j].split('--')[0].lower()
                        if current_state_label and "next_state" in next_line and f"<= {current_state_label}" in next_line:
                            found_redundant = True
                            break

                    if found_redundant:
                        violations.append(
                            Violation(
                                self.id,
                                i + 1,
                                line.upper().find("ELSE"),
                                f"Redundant ELSE branch: next_state is already {current_state_label.upper()} by default.",
                                self.severity
                            )
                        )
        return violations
