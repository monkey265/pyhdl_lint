import re
from pyhdl_lint.core.rule_base import BaseRule, Violation, Severity

STD_FUNCTIONS = [
    "rising_edge", "falling_edge", "to_integer", "to_unsigned", "to_signed",
    "std_logic_vector", "unsigned", "signed", "resize", "std_match",
    "shift_left", "shift_right", "rotate_left", "rotate_right",
    "ieee", "std_logic_1164", "numeric_std", "std_logic_arith", "std_logic_unsigned"
]

class StdFunctionCaseRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="VHDL-011", 
            description="STD and provided functions/types should be ALL CAPS.",
            severity=Severity.WARNING
        )

    def check(self, context):
        violations = []
        lines = context.lines
        
        for i, line in enumerate(lines):
            code_line = line.split('--')[0]
            words = re.findall(r'\b\w+\b', code_line)
            for word in words:
                if word.lower() in STD_FUNCTIONS:
                    if word != word.upper():
                        violations.append(
                            Violation(
                                self.id, 
                                i + 1, 
                                line.find(word), 
                                f"STD entity '{word}' should be ALL CAPS.",
                                self.severity
                            )
                        )
        return violations
