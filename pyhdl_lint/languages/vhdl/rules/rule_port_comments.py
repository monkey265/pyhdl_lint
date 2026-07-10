from pyhdl_lint.core.rule_base import BaseRule, Violation, Severity

class PortCommentsRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="VHDL-023",
            description="Port list should have comments indicating signal categories.",
            severity=Severity.WARNING
        )

    def check(self, context):
        violations = []
        lines = context.lines

        inside_port = False
        port_start_line = -1
        has_comment = False

        for i, line in enumerate(lines):
            code_line = line.split('--')[0].strip()
            low_line = code_line.lower()

            if "port" in low_line and "(" in low_line:
                inside_port = True
                port_start_line = i
                has_comment = "--" in line
                continue

            if inside_port:
                if "--" in line:
                    has_comment = True
                if ")" in low_line and ";" in low_line:
                    inside_port = False
                    if not has_comment:
                        violations.append(
                            Violation(
                                self.id,
                                port_start_line + 1,
                                lines[port_start_line].lower().find("port"),
                                "Port list should have comments indicating signal categories (e.g. -- Inputs, -- Outputs).",
                                self.severity
                            )
                        )
        return violations
