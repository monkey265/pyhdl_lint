"""Regression tests for the AST-based SystemVerilog rules (SV-002 through SV-007), against the real hdlConvertor parser."""
from pathlib import Path

from pyhdl_lint.core.parser import Parser
from pyhdl_lint.languages.systemverilog.rules.rule_blocking_assignment import BlockingAssignmentRule
from pyhdl_lint.languages.systemverilog.rules.rule_comb_sensitivity import CombinationalSensitivityRule
from pyhdl_lint.languages.systemverilog.rules.rule_module_naming import ModuleNameRule
from pyhdl_lint.languages.systemverilog.rules.rule_parameter_naming import ParameterNamingRule
from pyhdl_lint.languages.systemverilog.rules.rule_port_ordering import PortOrderingRule
from pyhdl_lint.languages.systemverilog.rules.rule_reset_active_low import ResetActiveLowRule


def check(tmp_path: Path, rule_cls, content: str):
    sv = tmp_path / "case.sv"
    sv.write_text(content)
    return rule_cls().check(Parser("systemverilog").get_context(sv))


def test_module_naming_flags_mod_prefix(tmp_path: Path) -> None:
    violations = check(tmp_path, ModuleNameRule, "module mod_bad (input logic clk);\nendmodule\n")
    assert len(violations) == 1
    assert "mod_bad" in violations[0].message


def test_module_naming_silent_on_clean_name(tmp_path: Path) -> None:
    assert check(tmp_path, ModuleNameRule, "module good_name (input logic clk);\nendmodule\n") == []


def test_parameter_naming_flags_lowercase(tmp_path: Path) -> None:
    content = "module m #(parameter int bad_param = 4) (input logic clk);\nendmodule\n"
    violations = check(tmp_path, ParameterNamingRule, content)
    assert len(violations) == 1
    assert "bad_param" in violations[0].message


def test_parameter_naming_silent_on_all_caps(tmp_path: Path) -> None:
    content = "module m #(parameter int WIDTH = 4) (input logic clk);\nendmodule\n"
    assert check(tmp_path, ParameterNamingRule, content) == []


def test_port_ordering_flags_wrong_order(tmp_path: Path) -> None:
    content = "module m (input logic data_in, input logic clk);\nendmodule\n"
    violations = check(tmp_path, PortOrderingRule, content)
    assert len(violations) == 2


def test_port_ordering_silent_on_clk_rst(tmp_path: Path) -> None:
    content = "module m (input logic clk, input logic rst);\nendmodule\n"
    assert check(tmp_path, PortOrderingRule, content) == []


def test_reset_active_low_flags_missing_suffix(tmp_path: Path) -> None:
    content = "module m (input logic clk, input logic reset);\nendmodule\n"
    violations = check(tmp_path, ResetActiveLowRule, content)
    assert len(violations) == 1
    assert "reset" in violations[0].message


def test_reset_active_low_silent_on_n_suffix(tmp_path: Path) -> None:
    content = "module m (input logic clk, input logic rst_n);\nendmodule\n"
    assert check(tmp_path, ResetActiveLowRule, content) == []


def test_blocking_assignment_flags_equals_in_clocked_block(tmp_path: Path) -> None:
    content = "module m (input logic clk); logic y; always_ff @(posedge clk) begin y = 1; end\nendmodule\n"
    violations = check(tmp_path, BlockingAssignmentRule, content)
    assert len(violations) == 1


def test_blocking_assignment_silent_on_nonblocking(tmp_path: Path) -> None:
    content = "module m (input logic clk); logic y; always_ff @(posedge clk) begin y <= 1; end\nendmodule\n"
    assert check(tmp_path, BlockingAssignmentRule, content) == []


def test_comb_sensitivity_flags_explicit_list(tmp_path: Path) -> None:
    content = "module m (input logic a, input logic b); logic y; always @(a, b) begin y = a; end\nendmodule\n"
    violations = check(tmp_path, CombinationalSensitivityRule, content)
    assert len(violations) == 1


def test_comb_sensitivity_silent_on_always_comb(tmp_path: Path) -> None:
    content = "module m (input logic a, input logic b); logic y; always_comb begin y = a; end\nendmodule\n"
    assert check(tmp_path, CombinationalSensitivityRule, content) == []
