import re
from pyhdl_lint.core.rule_base import BaseRule, Violation, Severity

class PortOrderingRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="VHDL-019", 
            description="Clock should be the first port, and Reset should be the second.",
            severity=Severity.WARNING
        )

    def check(self, context):
        violations = []
        lines = context["lines"]
        
        inside_port = False
        port_index = 0
        
        for i, line in enumerate(lines):
            code_line = line.split('--')[0].strip()
            low_line = code_line.lower()
            
            if "port" in low_line and "(" in low_line:
                inside_port = True
                port_index = 0
                continue
                
            if inside_port:
                if ")" in low_line and ";" in low_line:
                    inside_port = False
                    continue
                
                # Identify a port definition
                match = re.search(r'\b(\w+)\s*:', code_line)
                if match:
                    port_name = match.group(1).lower()
                    port_index += 1
                    
                    if port_index == 1:
                        if not any(x in port_name for x in ["clk", "clock"]):
                            violations.append(
                                Violation(
                                    self.id, 
                                    i + 1, 
                                    line.find(match.group(1)), 
                                    f"First port '{match.group(1)}' should be the clock signal.",
                                    self.severity
                                )
                            )
                    elif port_index == 2:
                        if not any(x in port_name for x in ["rst", "reset"]):
                            violations.append(
                                Violation(
                                    self.id, 
                                    i + 1, 
                                    line.find(match.group(1)), 
                                    f"Second port '{match.group(1)}' should be the reset signal.",
                                    self.severity
                                )
                            )
        return violations
