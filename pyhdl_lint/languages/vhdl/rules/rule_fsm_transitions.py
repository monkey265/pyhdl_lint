import re
from pyhdl_lint.core.rule_base import BaseRule, Violation, Severity

class FsmStateChangeRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="VHDL-012", 
            description="FSM state change rules: rising_edge usage and transition IFs.",
            severity=Severity.ERROR
        )

    def check(self, context):
        violations = []
        lines = context["lines"]
        
        # Rule 1: rising_edge only on clocks
        # Matches rising_edge(<signal>)
        rising_edge_pattern = re.compile(r'rising_edge\s*\(\s*(\w+)\s*\)', re.IGNORECASE)
        
        # Rule 2: else in IF transitions (simplified detection)
        # Matches IF ... THEN followed by ELSE (within some context)
        # We'll check for ELSE lines that follow an IF line
        
        inside_case = False
        current_state_label = None
        for i, line in enumerate(lines):
            code_line = line.split('--')[0].strip()
            
            # Rule 1 check: rising_edge
            matches = rising_edge_pattern.finditer(code_line)
            for match in matches:
                signal_name = match.group(1).lower()
                if "clk" not in signal_name and "clock" not in signal_name:
                    violations.append(
                        Violation(
                            "VHDL-012", 
                            i + 1, 
                            line.find(match.group(0)), 
                            f"rising_edge() should only be used on clock signals, not '{signal_name}'.",
                            Severity.ERROR
                        )
                    )
            
            # Rule 2 check: No redundant else in transitions
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
                    # Or just check if the current line or next line has the assignment
                    found_redundant = False
                    for j in range(i + 1, min(i + 4, len(lines))):
                        next_line = lines[j].split('--')[0].lower()
                        if current_state_label and f"next_state" in next_line and f"<= {current_state_label}" in next_line:
                            found_redundant = True
                            break
                    
                    if found_redundant:
                        violations.append(
                            Violation(
                                "VHDL-013", 
                                i + 1, 
                                line.upper().find("ELSE"), 
                                f"Redundant ELSE branch: next_state is already {current_state_label.upper()} by default.",
                                Severity.WARNING
                            )
                        )
                    
        return violations
