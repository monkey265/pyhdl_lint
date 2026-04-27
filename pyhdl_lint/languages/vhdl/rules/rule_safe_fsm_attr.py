import re
from pyhdl_lint.core.rule_base import BaseRule, Violation, Severity

class SafeFsmAttributeRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="VHDL-022", 
            description="Recommended to use 'fsm_safe_state' attribute for FSM state signals.",
            severity=Severity.WARNING
        )

    def check(self, context):
        violations = []
        lines = context["lines"]
        
        state_signals = []
        safe_state_attributes = []
        
        for i, line in enumerate(lines):
            code_line = line.split('--')[0].strip()
            low_line = code_line.lower()
            
            # Find signals that look like state signals
            if "signal" in low_line and "state" in low_line and ":" in low_line:
                match = re.search(r'\bsignal\s+(\w+)\b', low_line)
                if match:
                    state_signals.append((i + 1, match.group(1)))
            
            # Find safe state attributes
            if "attribute fsm_safe_state" in low_line and "of" in low_line:
                match = re.search(r'\bof\s+(\w+)\b', low_line)
                if match:
                    safe_state_attributes.append(match.group(1).lower())
                    
        for line_num, name in state_signals:
            if name.lower() not in safe_state_attributes:
                violations.append(
                    Violation(
                        self.id, 
                        line_num, 
                        lines[line_num-1].lower().find(name.lower()), 
                        f"State signal '{name}' is missing 'fsm_safe_state' attribute for high-reliability recovery logic.",
                        self.severity
                    )
                )
                
        return violations
