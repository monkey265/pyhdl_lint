"""Regression tests for the regex-based VHDL rules (VHDL-002 through VHDL-025, excluding VHDL-001).

VHDL-001 is AST-based and tested against the real parser in test_ast_rules.py.
VHDL-024/VHDL-025 are also AST-based (need real HdlModuleDec/HdlStmProcess
correlation) and are tested against the real parser in test_vhdl_ast_rules.py.
"""
import pytest

from pyhdl_lint.languages.vhdl.rules.rule_comb_sensitivity import CombinatorialSensitivityRule
from pyhdl_lint.languages.vhdl.rules.rule_forbidden_libraries import ForbiddenLibrariesRule
from pyhdl_lint.languages.vhdl.rules.rule_fsm_default_assign import FsmDefaultAssignmentRule
from pyhdl_lint.languages.vhdl.rules.rule_fsm_redundant_else import FsmRedundantElseRule
from pyhdl_lint.languages.vhdl.rules.rule_fsm_transitions import FsmStateChangeRule
from pyhdl_lint.languages.vhdl.rules.rule_generic_prefix import GenericPrefixRule
from pyhdl_lint.languages.vhdl.rules.rule_integer_range import IntegerRangeRule
from pyhdl_lint.languages.vhdl.rules.rule_keyword_case import KeywordCaseRule
from pyhdl_lint.languages.vhdl.rules.rule_latch_prevention import LatchPreventionRule
from pyhdl_lint.languages.vhdl.rules.rule_library_work import LibraryWorkRule
from pyhdl_lint.languages.vhdl.rules.rule_port_comments import PortCommentsRule
from pyhdl_lint.languages.vhdl.rules.rule_port_ordering import PortOrderingRule
from pyhdl_lint.languages.vhdl.rules.rule_process_naming import ProcessNamingRule
from pyhdl_lint.languages.vhdl.rules.rule_process_suffix import ProcessSuffixRule
from pyhdl_lint.languages.vhdl.rules.rule_reset_active_low import ResetActiveLowRule
from pyhdl_lint.languages.vhdl.rules.rule_safe_fsm_attr import SafeFsmAttributeRule
from pyhdl_lint.languages.vhdl.rules.rule_sig_var_case import SignalVariableCaseRule
from pyhdl_lint.languages.vhdl.rules.rule_signal_prefix import SignalPrefixRule
from pyhdl_lint.languages.vhdl.rules.rule_statement_naming import StatementNamingRule
from pyhdl_lint.languages.vhdl.rules.rule_std_case import StdFunctionCaseRule
from pyhdl_lint.languages.vhdl.rules.rule_variable_prefix import VariablePrefixRule
from tests.helpers import make_context

# (case id, rule class, content, expected line, expected column, message substring)
FIRES_CASES = [
    ("VHDL-002", KeywordCaseRule, "begin\n", 1, 0, "begin"),
    ("VHDL-003", SignalVariableCaseRule, "signal My_Sig : std_logic;\n", 1, 7, "My_Sig"),
    ("VHDL-004", SignalPrefixRule, "signal bad_name : std_logic;\n", 1, 7, "bad_name"),
    ("VHDL-005", VariablePrefixRule, "variable bad_var : integer;\n", 1, 9, "bad_var"),
    ("VHDL-006", GenericPrefixRule, "generic (\n    bad_gen : integer := 10\n);\n", 2, 4, "bad_gen"),
    ("VHDL-007", ProcessNamingRule, "process(clk)\n", 1, 0, "must have a label"),
    ("VHDL-008", ProcessSuffixRule, "bad_name: process(clk)\n", 1, 0, "should end with '_proc'"),
    ("VHDL-009", LibraryWorkRule, "library work;\n", 1, 8, "work"),
    ("VHDL-010", StatementNamingRule, "if foo = '1' then\n", 1, 0, "should have a label"),
    ("VHDL-011", StdFunctionCaseRule, "x <= rising_edge(clk);\n", 1, 5, "rising_edge"),
    ("VHDL-012", FsmStateChangeRule, "if rising_edge(data) then\n", 1, 3, "data"),
    (
        "VHDL-013",
        FsmRedundantElseRule,
        "case state is\nwhen idle =>\nelse\nnext_state <= idle;\nend case;\n",
        3,
        0,
        "IDLE",
    ),
    (
        "VHDL-015",
        FsmDefaultAssignmentRule,
        "fsm_proc: process(state)\ncase state is\nend process;\n",
        2,
        0,
        "FSM detected",
    ),
    ("VHDL-016", ForbiddenLibrariesRule, "use ieee.std_logic_unsigned.all;\n", 1, 9, "std_logic_unsigned"),
    ("VHDL-017", IntegerRangeRule, "signal s_count : integer;\n", 1, 7, "s_count"),
    ("VHDL-018", CombinatorialSensitivityRule, "process(a)\nend process;\n", 1, 0, "Combinatorial process"),
    (
        "VHDL-019-first",
        PortOrderingRule,
        "port (\n    data_in : in std_logic;\n    rst     : in std_logic\n);\n",
        2,
        4,
        "clock signal",
    ),
    ("VHDL-020", ResetActiveLowRule, "reset : in std_logic;\n", 1, 0, "active low"),
    (
        "VHDL-021",
        LatchPreventionRule,
        "process(a)\nif a = '1' then\nend if;\nend process;\n",
        2,
        0,
        "missing ELSE branch",
    ),
    ("VHDL-022", SafeFsmAttributeRule, "signal state1 : integer;\n", 1, 7, "state1"),
    (
        "VHDL-023",
        PortCommentsRule,
        "port (\n    clk : in std_logic\n);\n",
        1,
        0,
        "categories",
    ),
]

SILENT_CASES = [
    ("VHDL-002", KeywordCaseRule, "BEGIN\n"),
    ("VHDL-003", SignalVariableCaseRule, "signal my_sig : std_logic;\n"),
    ("VHDL-004", SignalPrefixRule, "signal s_good : std_logic;\n"),
    ("VHDL-005", VariablePrefixRule, "variable v_good : integer;\n"),
    ("VHDL-006", GenericPrefixRule, "generic (\n    g_good : integer := 10\n);\n"),
    ("VHDL-007", ProcessNamingRule, "main_proc: process(clk)\n"),
    ("VHDL-008", ProcessSuffixRule, "main_proc: process(clk)\n"),
    ("VHDL-009", LibraryWorkRule, "library ieee;\n"),
    ("VHDL-010", StatementNamingRule, "check_lbl: if foo = '1' then\n"),
    ("VHDL-011", StdFunctionCaseRule, "x <= RISING_EDGE(clk);\n"),
    (
        "VHDL-012",
        FsmStateChangeRule,
        "if rising_edge(clk) then\nend if;\ncase state is\nwhen idle =>\nwhen others =>\nend case;\n",
    ),
    (
        "VHDL-013",
        FsmRedundantElseRule,
        "if rising_edge(clk) then\nend if;\ncase state is\nwhen idle =>\nwhen others =>\nend case;\n",
    ),
    (
        "VHDL-015",
        FsmDefaultAssignmentRule,
        "fsm_proc: process(state)\nout <= '0';\ncase state is\nend process;\n",
    ),
    ("VHDL-016", ForbiddenLibrariesRule, "use ieee.numeric_std.all;\n"),
    ("VHDL-017", IntegerRangeRule, "signal s_count : integer range 0 to 15;\n"),
    ("VHDL-018", CombinatorialSensitivityRule, "process(all)\nend process;\n"),
    (
        "VHDL-019",
        PortOrderingRule,
        "port (\n    clk   : in std_logic;\n    rst_n : in std_logic\n);\n",
    ),
    ("VHDL-020", ResetActiveLowRule, "rst_n : in std_logic;\n"),
    (
        "VHDL-021",
        LatchPreventionRule,
        "process(a)\nif a = '1' then\nelse\nend if;\nend process;\n",
    ),
    (
        "VHDL-022",
        SafeFsmAttributeRule,
        'signal state1 : integer;\nattribute fsm_safe_state of state1 : signal is "default_state";\n',
    ),
    (
        "VHDL-023",
        PortCommentsRule,
        "port (\n    -- Inputs\n    clk : in std_logic\n);\n",
    ),
]


@pytest.mark.parametrize("case_id,rule_cls,content,line,column,message", FIRES_CASES, ids=[c[0] for c in FIRES_CASES])
def test_rule_fires(case_id, rule_cls, content, line, column, message) -> None:
    violations = rule_cls().check(make_context(content))
    assert len(violations) == 1
    assert violations[0].line == line
    assert violations[0].column == column
    assert message in violations[0].message


@pytest.mark.parametrize("case_id,rule_cls,content", SILENT_CASES, ids=[c[0] for c in SILENT_CASES])
def test_rule_silent(case_id, rule_cls, content) -> None:
    assert rule_cls().check(make_context(content)) == []
