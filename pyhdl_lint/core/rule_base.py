from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional

from hdlConvertorAst.to.hdl_ast_visitor import HdlAstVisitor

class Severity(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"

@dataclass(frozen=True)
class LintContext:
    """Type-safe context passed to every rule's check() call."""
    file_path: Path
    content: str
    lines: List[str]
    language: str
    ast: Optional[object]
    parse_error: Optional[str]

class BaseRule(ABC):
    def __init__(self, id: str, description: str, severity: Severity = Severity.ERROR) -> None:
        self.id = id
        self.description = description
        self.severity = severity

    @abstractmethod
    def check(self, context: LintContext) -> List["Violation"]:
        pass

class AstRule(BaseRule, HdlAstVisitor):
    """Base class for rules that traverse the hdlConvertor AST instead of raw text."""

    def __init__(self, id: str, description: str, severity: Severity = Severity.ERROR) -> None:
        BaseRule.__init__(self, id, description, severity)
        HdlAstVisitor.__init__(self)
        self._violations: List["Violation"] = []

    def add_violation(self, node: object, message: str) -> None:
        position = getattr(node, "position", None)
        line = position.start_line if position is not None else 0
        column = position.start_column if position is not None else 0
        self._violations.append(Violation(self.id, line, column, message, self.severity))

    def check(self, context: LintContext) -> List["Violation"]:
        self._violations = []
        if context.ast is not None:
            self.visit_HdlContext(context.ast)
        return self._violations

class Violation:
    def __init__(
        self,
        rule_id: str,
        line: int,
        column: int,
        message: str,
        severity: Severity = Severity.ERROR,
    ) -> None:
        self.rule_id = rule_id
        self.line = line
        self.column = column
        self.message = message
        self.severity = severity

    def __str__(self) -> str:
        sev_str = f"[{self.severity.value}] " if self.severity != Severity.ERROR else ""
        return f"{sev_str}[{self.rule_id}] Line {self.line}, Col {self.column}: {self.message}"
