from abc import ABC, abstractmethod

class BaseRule(ABC):
    def __init__(self, id, description):
        self.id = id
        self.description = description

    @abstractmethod
    def check(self, context):
        """
        Perform the linting check.
        :param context: A dictionary or object containing the file content, 
                       tokens, or AST to be checked.
        :return: A list of violations.
        """
        pass

class Violation:
    def __init__(self, rule_id, line, column, message):
        self.rule_id = rule_id
        self.line = line
        self.column = column
        self.message = message

    def __str__(self):
        return f"[{self.rule_id}] Line {self.line}, Col {self.column}: {self.message}"
