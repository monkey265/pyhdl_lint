from abc import ABC, abstractmethod
from enum import Enum

class Severity(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"

class BaseRule(ABC):
    def __init__(self, id, description, severity=Severity.ERROR):
        self.id = id
        self.description = description
        self.severity = severity

    @abstractmethod
    def check(self, context):
        pass

class Violation:
    def __init__(self, rule_id, line, column, message, severity=Severity.ERROR):
        self.rule_id = rule_id
        self.line = line
        self.column = column
        self.message = message
        self.severity = severity

    def __str__(self):
        sev_str = f"[{self.severity.value}] " if self.severity != Severity.ERROR else ""
        return f"{sev_str}[{self.rule_id}] Line {self.line}, Col {self.column}: {self.message}"
