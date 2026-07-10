from pyhdl_lint.core.rule_base import BaseRule, Violation

class ModuleNameRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="VER-001", 
            description="Module name should not start with 'mod_'."
        )

    def check(self, context):
        violations = []
        lines = context.lines

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("module "):
                parts = stripped.split()
                if len(parts) > 1:
                    module_name = parts[1].split('(')[0].split(';')[0].strip()
                    if module_name.startswith("mod_"):
                        violations.append(
                            Violation(
                                self.id, 
                                i + 1, 
                                line.find(module_name), 
                                f"Module name '{module_name}' should not start with 'mod_'."
                            )
                        )
        return violations
