from pyhdl_lint.languages.verilog.rules.rule_module_naming import ModuleNameRule
from tests.helpers import make_context


def test_module_naming_flags_mod_prefix() -> None:
    violations = ModuleNameRule().check(make_context("module mod_bad (input clk);\n", "verilog"))
    assert len(violations) == 1
    assert violations[0].line == 1
    assert violations[0].column == 7
    assert "mod_bad" in violations[0].message


def test_module_naming_silent_on_clean_name() -> None:
    context = make_context("module good_name (input clk);\n", "verilog")
    assert ModuleNameRule().check(context) == []
