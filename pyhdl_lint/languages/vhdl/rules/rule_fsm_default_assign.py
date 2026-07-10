import re
from pyhdl_lint.core.rule_base import BaseRule, Violation, Severity

class FsmDefaultAssignmentRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="VHDL-015", 
            description="FSM outputs should have default assignments at the top of the process.",
            severity=Severity.WARNING
        )

    def check(self, context):
        violations = []
        lines = context.lines
        
        inside_fsm_process = False
        saw_assignment = False
        
        for i, line in enumerate(lines):
            code_line = line.split('--')[0].strip()
            low_line = code_line.lower()
            
            # Identify FSM process (very heuristic)
            if "process" in low_line and ("state" in low_line or "fsm" in low_line):
                inside_fsm_process = True
                saw_assignment = False
                continue
                
            if inside_fsm_process:
                if "end process" in low_line:
                    inside_fsm_process = False
                    continue
                
                # Check for assignment
                if "<=" in code_line:
                    saw_assignment = True
                
                # If we see a CASE before any assignment
                if "case" in low_line and "state" in low_line:
                    if not saw_assignment:
                        violations.append(
                            Violation(
                                self.id, 
                                i + 1, 
                                line.lower().find("case"), 
                                "FSM detected: Recommended to use default assignments for outputs at the top of the process.",
                                self.severity
                            )
                        )
                    # Reset for the next branch or just stop checking for this process
                    # Actually, once we hit the case, we've missed the "top"
                    inside_fsm_process = False 
                    
        return violations
