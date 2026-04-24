import os

class Config:
    def __init__(self, config_dict=None):
        self.settings = config_dict or {}

    @classmethod
    def load(cls, path=None):
        # Placeholder for loading from pyproject.toml or .pyhdl-lint.toml
        # For now, return default empty config
        return cls()

    def is_rule_enabled(self, rule_id):
        # Rules are enabled by default unless explicitly disabled
        disabled_rules = self.settings.get("disabled_rules", [])
        return rule_id not in disabled_rules
