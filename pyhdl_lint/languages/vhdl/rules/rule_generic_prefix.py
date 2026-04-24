import re
from pyhdl_lint.core.rule_base import BaseRule, Violation, Severity

class GenericPrefixRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="VHDL-006", 
            description="Generics should have prefix 'g_'.",
            severity=Severity.WARNING
        )

    def check(self, context):
        violations = []
        # Simplified: look for names inside generic() block or just general generic definitions
        # This regex is very loose but covers the generic map/generic part
        pattern = re.compile(r'\b(\w+)\s*:\s*\w+\s*(?:;|\)|:=)', re.IGNORECASE)
        
        inside_generic = False
        lines = context["lines"]
        for i, line in enumerate(lines):
            code_line = line.split('--')[0].strip().upper()
            if "GENERIC" in code_line and "(" in code_line:
                inside_generic = True
                continue
            
            if inside_generic:
                if ")" in code_line and ";" in code_line:
                    inside_generic = False
                
                # Check for names
                match = re.search(r'\b(\w+)\s*:', line.split('--')[0])
                if match:
                    name = match.group(1)
                    if not name.startswith("g_"):
                        violations.append(
                            Violation(
                                self.id, 
                                i + 1, 
                                line.find(name), 
                                f"Generic '{name}' should have prefix 'g_'.",
                                self.severity
                            )
                        )
        return violations
