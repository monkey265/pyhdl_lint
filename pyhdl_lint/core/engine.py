import importlib.util
import inspect
from pathlib import Path
from typing import List, Optional

from pyhdl_lint.core.rule_base import BaseRule, Violation
from pyhdl_lint.utils.config import Config

class Engine:
    def __init__(self) -> None:
        self.rules: List[BaseRule] = []

    def load_rules(self, rules_dir: Path) -> None:
        """
        Dynamically load rules from a directory.
        """
        if not rules_dir.exists():
            return

        for file_path in rules_dir.glob("*.py"):
            if file_path.name == "__init__.py":
                continue

            spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for _, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, BaseRule)
                    and obj.__module__ == module.__name__
                ):
                    self.rules.append(obj())

    def run(self, file_path: Path, language: str, config: Optional[Config] = None) -> List[Violation]:
        """
        Run all loaded rules against a file.
        """
        from pyhdl_lint.core.parser import Parser
        parser = Parser(language)
        context = parser.get_context(file_path)

        all_violations: List[Violation] = []
        for rule in self.rules:
            if config and not config.is_rule_enabled(rule.id):
                continue

            violations = rule.check(context)
            if violations:
                all_violations.extend(violations)

        return all_violations
