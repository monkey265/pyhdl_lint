"""Self-check for Config.load() TOML file discovery and precedence."""
from pathlib import Path

from pyhdl_lint.utils.config import Config


def test_load_returns_empty_config_when_no_file_present(tmp_path: Path) -> None:
    config = Config.load(tmp_path)
    assert config.is_rule_enabled("VHDL-001")


def test_load_reads_dedicated_pyhdl_lint_toml(tmp_path: Path) -> None:
    (tmp_path / ".pyhdl-lint.toml").write_text('disabled_rules = ["VHDL-001"]\n')
    config = Config.load(tmp_path)
    assert not config.is_rule_enabled("VHDL-001")
    assert config.is_rule_enabled("VHDL-002")


def test_load_reads_pyproject_tool_section(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[tool.pyhdl_lint]\ndisabled_rules = ["SV-001"]\n'
    )
    config = Config.load(tmp_path)
    assert not config.is_rule_enabled("SV-001")


def test_dedicated_file_wins_over_pyproject(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[tool.pyhdl_lint]\ndisabled_rules = ["SV-001"]\n'
    )
    (tmp_path / ".pyhdl-lint.toml").write_text('disabled_rules = ["VHDL-001"]\n')
    config = Config.load(tmp_path)
    assert not config.is_rule_enabled("VHDL-001")
    assert config.is_rule_enabled("SV-001")


def test_malformed_toml_degrades_to_empty_config(tmp_path: Path) -> None:
    (tmp_path / ".pyhdl-lint.toml").write_text("this is not valid toml [[[")
    config = Config.load(tmp_path)
    assert config.is_rule_enabled("VHDL-001")
