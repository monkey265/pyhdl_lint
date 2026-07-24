"""Tests for the __main__ CLI entry point, including multi-file/directory linting."""
import json
from pathlib import Path

import pytest

from pyhdl_lint import __main__ as cli


def run_cli(monkeypatch: pytest.MonkeyPatch, *args: str) -> int:
    monkeypatch.setattr("sys.argv", ["pyhdl-lint", *args])
    return cli.main()


def test_no_args_returns_usage_error(monkeypatch: pytest.MonkeyPatch) -> None:
    assert run_cli(monkeypatch) == 1


def test_nonexistent_path_returns_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    assert run_cli(monkeypatch, str(tmp_path / "missing.vhd")) == 1


def test_single_file_unsupported_extension_errors(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    bad = tmp_path / "notes.txt"
    bad.write_text("hello\n")
    assert run_cli(monkeypatch, str(bad)) == 1


def test_single_clean_file_returns_zero(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    vhd = tmp_path / "clean.vhd"
    vhd.write_text("ENTITY my_entity IS\nEND ENTITY my_entity;\n")
    assert run_cli(monkeypatch, str(vhd)) == 0


def test_single_violating_file_returns_one(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    vhd = tmp_path / "bad.vhd"
    vhd.write_text("ENTITY MY_ENTITY IS\nEND ENTITY MY_ENTITY;\n")
    assert run_cli(monkeypatch, str(vhd)) == 1


def test_empty_directory_returns_zero(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    assert run_cli(monkeypatch, str(tmp_path)) == 0


def test_directory_with_no_hdl_files_returns_zero(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("not hdl\n")
    assert run_cli(monkeypatch, str(tmp_path)) == 0


def test_directory_recursive_mixed_language_aggregates_violations(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "bad.vhd").write_text("entity MY_ENTITY is\nend entity MY_ENTITY;\n")
    (tmp_path / "bad.sv").write_text("module m;\n  reg r;\nendmodule\n")
    (tmp_path / "clean.v").write_text("module good_name (input clk);\nendmodule\n")
    (tmp_path / "notes.txt").write_text("ignored\n")

    exit_code = run_cli(monkeypatch, str(tmp_path))

    assert exit_code == 1
    out = capsys.readouterr().out
    assert "Files checked: 3" in out
    assert "Total violations:" in out


def test_directory_all_clean_returns_zero(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "clean.vhd").write_text("ENTITY my_entity IS\nEND ENTITY my_entity;\n")
    (tmp_path / "clean.v").write_text("module good_name (input clk);\nendmodule\n")
    assert run_cli(monkeypatch, str(tmp_path)) == 0


def test_format_json_prints_only_a_json_array(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    vhd = tmp_path / "bad.vhd"
    vhd.write_text("ENTITY MY_ENTITY IS\nEND ENTITY MY_ENTITY;\n")

    exit_code = run_cli(monkeypatch, str(vhd), "--format", "json")

    assert exit_code == 1
    out = capsys.readouterr().out
    violations = json.loads(out)
    assert isinstance(violations, list)
    assert len(violations) == 1
    assert violations[0]["rule_id"] == "VHDL-001"
    assert violations[0]["line"] == 1
    assert violations[0]["severity"] == "ERROR"
    assert "MY_ENTITY" in violations[0]["message"]


def test_format_json_clean_file_returns_empty_array(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    vhd = tmp_path / "clean.vhd"
    vhd.write_text("ENTITY my_entity IS\nEND ENTITY my_entity;\n")

    exit_code = run_cli(monkeypatch, str(vhd), "--format", "json")

    assert exit_code == 0
    assert json.loads(capsys.readouterr().out) == []
