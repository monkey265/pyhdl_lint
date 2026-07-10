"""Self-check for the AST-based rules (VHDL-001, SV-001) against the real hdlConvertor parser."""
from pathlib import Path

from pyhdl_lint.core.parser import Parser
from pyhdl_lint.languages.systemverilog.rules.rule_logic_type import LogicTypeRule
from pyhdl_lint.languages.vhdl.rules.rule_entity_naming import EntityNameRule

FIXTURES_DIR = Path(__file__).parent


def test_entity_naming_flags_uppercase_entity() -> None:
    context = Parser("vhdl").get_context(FIXTURES_DIR / "vhdl_test_guidelines.vhd")
    violations = EntityNameRule().check(context)
    assert len(violations) == 1
    assert violations[0].line == 4
    assert "TEST_ENTITY" in violations[0].message


def test_entity_naming_silent_on_lowercase_entity(tmp_path: Path) -> None:
    vhd = tmp_path / "clean.vhd"
    vhd.write_text("entity my_entity is\nend entity my_entity;\n")
    context = Parser("vhdl").get_context(vhd)
    assert EntityNameRule().check(context) == []


def test_logic_type_flags_reg(tmp_path: Path) -> None:
    sv = tmp_path / "reg.sv"
    sv.write_text("module m;\n  reg r;\nendmodule\n")
    context = Parser("systemverilog").get_context(sv)
    violations = LogicTypeRule().check(context)
    assert len(violations) == 1
    assert violations[0].line == 2


def test_logic_type_silent_on_logic_and_wire(tmp_path: Path) -> None:
    sv = tmp_path / "clean.sv"
    sv.write_text("module m;\n  logic l;\n  wire w;\nendmodule\n")
    context = Parser("systemverilog").get_context(sv)
    assert LogicTypeRule().check(context) == []
