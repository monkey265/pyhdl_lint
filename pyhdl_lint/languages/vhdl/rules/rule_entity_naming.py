from pyhdl_lint.core.rule_base import BaseRule, Violation

class EntityNameRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="VHDL-001", 
            description="Entity name should be in uppercase."
        )

    def check(self, context):
        violations = []
        content = context["content"]
        lines = content.splitlines()

        for i, line in enumerate(lines):
            stripped_line = line.strip().lower()
            if stripped_line.startswith("entity "):
                parts = line.strip().split()
                if len(parts) > 1:
                    entity_name = parts[1]
                    # Check if it's actually a name (not followed by ;)
                    if entity_name.endswith(";"):
                        entity_name = entity_name[:-1]
                    
                    if not entity_name.isupper():
                        violations.append(
                            Violation(
                                self.id, 
                                i + 1, 
                                line.find(entity_name), 
                                f"Entity name '{entity_name}' should be uppercase."
                            )
                        )
        return violations
