import re
from pyhdl_lint.core.rule_base import BaseRule, Violation, Severity

class CombinatorialSensitivityRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="VHDL-018", 
            description="Combinatorial processes should use 'PROCESS(ALL)' in VHDL-2008.",
            severity=Severity.WARNING
        )

    def check(self, context):
        violations = []
        lines = context["lines"]
        
        inside_process = False
        is_clocked = False
        process_line_idx = -1
        sensitivity_list = ""
        
        for i, line in enumerate(lines):
            code_line = line.split('--')[0].strip()
            low_line = code_line.lower()
            
            # Start of process
            match = re.search(r'\bprocess\b\s*\(([^)]+)\)', low_line)
            if match:
                inside_process = True
                is_clocked = False
                process_line_idx = i
                sensitivity_list = match.group(1).strip()
                continue
                
            if inside_process:
                if "rising_edge" in low_line or "falling_edge" in low_line or "'event" in low_line:
                    is_clocked = True
                
                if "end process" in low_line:
                    if not is_clocked and sensitivity_list.upper() != "ALL":
                        violations.append(
                            Violation(
                                self.id, 
                                process_line_idx + 1, 
                                lines[process_line_idx].lower().find("process"), 
                                "Combinatorial process detected: Recommended to use 'PROCESS(ALL)' for VHDL-2008 compliance and robustness.",
                                self.severity
                            )
                        )
                    inside_process = False
                    
        return violations
