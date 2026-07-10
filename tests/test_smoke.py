"""Regression guard: runs the real Engine (real hdlConvertor parser) end to end."""
from pathlib import Path

from pyhdl_lint.core.engine import Engine
from pyhdl_lint.utils.config import Config

FIXTURES_DIR = Path(__file__).parent
RULES_DIR = FIXTURES_DIR.parent / "pyhdl_lint" / "languages"


def test_vhdl_rule_count() -> None:
    engine = Engine()
    engine.load_rules(RULES_DIR / "vhdl" / "rules")
    assert len(engine.rules) == 24


def test_verilog_rule_count() -> None:
    engine = Engine()
    engine.load_rules(RULES_DIR / "verilog" / "rules")
    assert len(engine.rules) == 6


def test_systemverilog_rule_count() -> None:
    engine = Engine()
    engine.load_rules(RULES_DIR / "systemverilog" / "rules")
    assert len(engine.rules) == 7


def test_vhdl_guidelines_fixture_violation_count() -> None:
    engine = Engine()
    engine.load_rules(RULES_DIR / "vhdl" / "rules")
    violations = engine.run(FIXTURES_DIR / "vhdl_test_guidelines.vhd", "vhdl", config=Config.load(FIXTURES_DIR))
    assert len(violations) == 73


def test_verilog_fixture_violation_count() -> None:
    engine = Engine()
    engine.load_rules(RULES_DIR / "verilog" / "rules")
    violations = engine.run(FIXTURES_DIR / "test_file.v", "verilog", config=Config.load(FIXTURES_DIR))
    assert len(violations) == 1


def test_systemverilog_fixture_violation_count() -> None:
    engine = Engine()
    engine.load_rules(RULES_DIR / "systemverilog" / "rules")
    violations = engine.run(FIXTURES_DIR / "test_file.sv", "systemverilog", config=Config.load(FIXTURES_DIR))
    assert len(violations) == 1
