"""Regression tests for the AST-based VHDL rules VHDL-024/VHDL-025, against the real hdlConvertor parser."""
from pathlib import Path

from pyhdl_lint.core.parser import Parser
from pyhdl_lint.languages.vhdl.rules.rule_clocked_sensitivity import ClockedProcessSensitivityRule
from pyhdl_lint.languages.vhdl.rules.rule_reset_synchronicity import ResetSynchronicityRule

ASYNC_GOOD = """\
library ieee;
use ieee.std_logic_1164.all;

entity probe is
    port (
        clk      : in std_logic;
        areset_n : in std_logic;
        q        : out std_logic
    );
end entity;

architecture rtl of probe is
begin
    async_proc: process(clk, areset_n)
    begin
        if areset_n = '0' then
            q <= '0';
        elsif rising_edge(clk) then
            q <= '1';
        end if;
    end process;
end architecture;
"""

SYNC_NAMED_ASYNC_BAD = """\
library ieee;
use ieee.std_logic_1164.all;

entity probe is
    port (
        clk   : in std_logic;
        rst_n : in std_logic;
        q     : out std_logic
    );
end entity;

architecture rtl of probe is
begin
    async_proc: process(clk, rst_n)
    begin
        if rst_n = '0' then
            q <= '0';
        elsif rising_edge(clk) then
            q <= '1';
        end if;
    end process;
end architecture;
"""

SYNC_GOOD = """\
library ieee;
use ieee.std_logic_1164.all;

entity probe is
    port (
        clk   : in std_logic;
        rst_n : in std_logic;
        q     : out std_logic
    );
end entity;

architecture rtl of probe is
begin
    sync_proc: process(clk)
    begin
        if rising_edge(clk) then
            if rst_n = '0' then
                q <= '0';
            else
                q <= '1';
            end if;
        end if;
    end process;
end architecture;
"""

CLOCKED_EXTRA_SIGNAL_BAD = """\
library ieee;
use ieee.std_logic_1164.all;

entity probe is
    port (
        clk  : in std_logic;
        data : in std_logic;
        q    : out std_logic
    );
end entity;

architecture rtl of probe is
begin
    bad_proc: process(clk, data)
    begin
        if rising_edge(clk) then
            q <= data;
        end if;
    end process;
end architecture;
"""

CLOCKED_CLEAN = """\
library ieee;
use ieee.std_logic_1164.all;

entity probe is
    port (
        clk : in std_logic;
        rst : in std_logic;
        q   : out std_logic
    );
end entity;

architecture rtl of probe is
begin
    good_proc: process(clk, rst)
    begin
        if rising_edge(clk) then
            q <= rst;
        end if;
    end process;
end architecture;
"""


def check(tmp_path: Path, rule_cls, content: str):
    vhd = tmp_path / "case.vhd"
    vhd.write_text(content)
    return rule_cls().check(Parser("vhdl").get_context(vhd))


def test_reset_synchronicity_silent_on_correct_async_naming(tmp_path: Path) -> None:
    assert check(tmp_path, ResetSynchronicityRule, ASYNC_GOOD) == []


def test_reset_synchronicity_flags_async_usage_named_as_sync(tmp_path: Path) -> None:
    violations = check(tmp_path, ResetSynchronicityRule, SYNC_NAMED_ASYNC_BAD)
    assert len(violations) == 1
    assert "rst_n" in violations[0].message


def test_reset_synchronicity_silent_on_correct_sync_naming(tmp_path: Path) -> None:
    assert check(tmp_path, ResetSynchronicityRule, SYNC_GOOD) == []


def test_clocked_sensitivity_flags_extra_signal(tmp_path: Path) -> None:
    violations = check(tmp_path, ClockedProcessSensitivityRule, CLOCKED_EXTRA_SIGNAL_BAD)
    assert len(violations) == 1
    assert "data" in violations[0].message


def test_clocked_sensitivity_silent_on_clk_and_reset_only(tmp_path: Path) -> None:
    assert check(tmp_path, ClockedProcessSensitivityRule, CLOCKED_CLEAN) == []
