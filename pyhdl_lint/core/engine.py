import os
import importlib.util
import inspect
from pyhdl_lint.core.rule_base import BaseRule

class Engine:
    def __init__(self):
        self.rules = []

    def load_rules(self, rules_dir):
        """
        Dynamically load rules from a directory.
        """
        if not os.path.exists(rules_dir):
            return

        for filename in os.listdir(rules_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]
                file_path = os.path.join(rules_dir, filename)
                
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, BaseRule) and obj is not BaseRule:
                        self.rules.append(obj())

    def run(self, file_path, language, config=None):
        """
        Run all loaded rules against a file.
        """
        from pyhdl_lint.core.parser import Parser
        parser = Parser(language)
        context = parser.get_context(file_path)

        all_violations = []
        for rule in self.rules:
            if config and not config.is_rule_enabled(rule.id):
                continue
                
            violations = rule.check(context)
            if violations:
                all_violations.extend(violations)
        
        return all_violations
