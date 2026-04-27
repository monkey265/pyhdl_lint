import re
from pyhdl_lint.core.rule_base import BaseRule, Violation, Severity

class ResetActiveLowRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="VHDL-020", 
            description="Reset signals should be active low (suffix '_n').",
            severity=Severity.WARNING
        )

    def check(self, context):
        violations = []
        # Matches: (signal|variable|port) <name> : ...
        # Simplified: look for any name containing rst or reset
        pattern = re.compile(r'\b(\w+)\b', re.IGNORECASE)
        
        lines = context["lines"]
        for i, line in enumerate(lines):
            code_line = line.split('--')[0]
            # Exclude comments
            words = pattern.findall(code_line)
            for word in words:
                low_word = word.lower()
                if ("rst" in low_word or "reset" in low_word) and not low_word.endswith("_n"):
                    # Avoid flagging keywords or types
                    if low_word in ["reset", "rst"]: # Only flag if it's the full name or part of it
                         violations.append(
                            Violation(
                                self.id, 
                                i + 1, 
                                line.find(word), 
                                f"Reset signal '{word}' should be active low and end with '_n'.",
                                self.severity
                            )
                        )
        return violations
