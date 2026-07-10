import re
from pyhdl_lint.core.rule_base import BaseRule, Violation, Severity

VHDL_KEYWORDS = [
    "abs", "access", "after", "alias", "all", "and", "architecture", "array",
    "assert", "attribute", "begin", "block", "body", "buffer", "bus", "case",
    "component", "configuration", "constant", "disconnect", "downto", "else",
    "elsif", "end", "entity", "exit", "file", "for", "function", "generate",
    "generic", "group", "guarded", "if", "impure", "in", "inertial", "inout",
    "is", "label", "library", "linkage", "literal", "loop", "map", "mod",
    "nand", "new", "next", "nor", "not", "null", "of", "on", "open", "or",
    "others", "out", "package", "port", "postponed", "procedure", "process",
    "pure", "range", "record", "register", "reject", "rem", "report", "return",
    "rol", "ror", "select", "severity", "shared", "signal", "sla", "sll",
    "sra", "srl", "subtype", "then", "to", "transport", "type", "unaffected",
    "units", "until", "use", "variable", "wait", "when", "while", "with", "xnor", "xor"
]

class KeywordCaseRule(BaseRule):
    def __init__(self):
        super().__init__(
            id="VHDL-002", 
            description="Keywords must be in ALL CAPS.",
            severity=Severity.ERROR
        )

    def check(self, context):
        violations = []
        lines = context.lines
        
        # Simple regex to find words (not inside strings or comments)
        # Note: This is a simplified version. A real parser would be better.
        for i, line in enumerate(lines):
            # Strip comments
            code_line = line.split('--')[0]
            if not code_line:
                continue
                
            # Find words
            words = re.findall(r'\b\w+\b', code_line)
            for word in words:
                if word.lower() in VHDL_KEYWORDS:
                    if word != word.upper():
                        violations.append(
                            Violation(
                                self.id, 
                                i + 1, 
                                line.find(word), 
                                f"Keyword '{word}' must be ALL CAPS.",
                                self.severity
                            )
                        )
        return violations
