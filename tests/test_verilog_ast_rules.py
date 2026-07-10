"""Regression tests for the AST-based Verilog rules (VER-002 through VER-006), against the real hdlConvertor parser."""
from pathlib import Path

import pytest

from pyhdl_lint.core.parser import Parser
from pyhdl_lint.languages.verilog.rules.rule_blocking_assignment import BlockingAssignmentRule
from pyhdl_lint.languages.verilog.rules.rule_comb_sensitivity import CombinationalSensitivityRule
from pyhdl_lint.languages.verilog.rules.rule_parameter_naming import ParameterNamingRule
from pyhdl_lint.languages.verilog.rules.rule_port_ordering import PortOrderingRule
from pyhdl_lint.languages.verilog.rules.rule_reset_active_low import ResetActiveLowRule


def check(tmp_path: Path, rule_cls, content: str):
    v = tmp_path / "case.v"
    v.write_text(content)
    return rule_cls().check(Parser("verilog").get_context(v))


def test_parameter_naming_flags_lowercase(tmp_path: Path) -> None:
    violations = check(tmp_path, ParameterNamingRule, "module m #(parameter bad_param = 4) (input clk);\nendmodule\n")
    assert len(violations) == 1
    assert "bad_param" in violations[0].message


def test_parameter_naming_silent_on_all_caps(tmp_path: Path) -> None:
    assert check(tmp_path, ParameterNamingRule, "module m #(parameter WIDTH = 4) (input clk);\nendmodule\n") == []


def test_port_ordering_flags_wrong_order(tmp_path: Path) -> None:
    violations = check(
        tmp_path, PortOrderingRule, "module m (input data_in, input clk);\nendmodule\n"
    )
    assert len(violations) == 2


def test_port_ordering_silent_on_clk_rst(tmp_path: Path) -> None:
    assert check(tmp_path, PortOrderingRule, "module m (input clk, input rst);\nendmodule\n") == []


def test_reset_active_low_flags_missing_suffix(tmp_path: Path) -> None:
    violations = check(tmp_path, ResetActiveLowRule, "module m (input clk, input reset);\nendmodule\n")
    assert len(violations) == 1
    assert "reset" in violations[0].message


def test_reset_active_low_silent_on_n_suffix(tmp_path: Path) -> None:
    assert check(tmp_path, ResetActiveLowRule, "module m (input clk, input rst_n);\nendmodule\n") == []


def test_blocking_assignment_flags_equals_in_clocked_block(tmp_path: Path) -> None:
    violations = check(
        tmp_path,
        BlockingAssignmentRule,
        "module m (input clk); reg y; always @(posedge clk) begin y = 1; end\nendmodule\n",
    )
    assert len(violations) == 1


def test_blocking_assignment_silent_on_nonblocking(tmp_path: Path) -> None:
    content = "module m (input clk); reg y; always @(posedge clk) begin y <= 1; end\nendmodule\n"
    assert check(tmp_path, BlockingAssignmentRule, content) == []


def test_comb_sensitivity_flags_explicit_list(tmp_path: Path) -> None:
    content = "module m (input a, input b); reg y; always @(a, b) begin y = a; end\nendmodule\n"
    violations = check(tmp_path, CombinationalSensitivityRule, content)
    assert len(violations) == 1


def test_comb_sensitivity_silent_on_star(tmp_path: Path) -> None:
    content = "module m (input a, input b); reg y; always @* begin y = a; end\nendmodule\n"
    assert check(tmp_path, CombinationalSensitivityRule, content) == []
