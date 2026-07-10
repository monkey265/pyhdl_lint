import re
from pyhdl_lint.core.rule_base import BaseRule, Violation, Severity

class LatchPreventionRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="VHDL-021", 
            description="Combinatorial processes must avoid latches (every IF needs an ELSE).",
            severity=Severity.ERROR
        )

    def check(self, context):
        violations = []
        lines = context.lines
        
        inside_comb_process = False
        if_stack = [] # Store line numbers of IFs
        
        for i, line in enumerate(lines):
            code_line = line.split('--')[0].strip()
            low_line = code_line.lower()
            
            # Start of process
            if "process" in low_line and "(" in low_line:
                # We assume any process without rising_edge is combinatorial 
                # (This is checked at the end of the process block usually, but let's be simpler)
                # Actually, let's just check all processes and if we see rising_edge, we skip it.
                inside_comb_process = True
                is_clocked = False
                if_stack = []
                continue
                
            if inside_comb_process:
                if "rising_edge" in low_line or "falling_edge" in low_line or "'event" in low_line:
                    is_clocked = True
                
                if "if " in low_line and " then" in low_line:
                    if_stack.append(i + 1)
                
                if "else" in low_line:
                    if if_stack:
                        if_stack.pop() # This IF has an ELSE (or ELSIF)
                
                if "end if" in low_line:
                    if if_stack:
                        start_line = if_stack.pop()
                        if not is_clocked:
                            violations.append(
                                Violation(
                                    self.id, 
                                    start_line, 
                                    lines[start_line-1].lower().find("if"), 
                                    "Combinatorial IF statement missing ELSE branch (risk of latch).",
                                    self.severity
                                )
                            )
                
                if "end process" in low_line:
                    inside_comb_process = False
                    
        return violations
