library work; -- ERROR: VHDL-009

entity test_entity is -- ERROR: VHDL-001 (should be uppercase)
    generic (
        timeout : integer := 10 -- WARNING: VHDL-006 (should be g_timeout)
    );
end entity;

architecture rtl of test_entity is
    signal My_Signal : std_logic; -- ERROR: VHDL-003 (lowercase), WARNING: VHDL-004 (s_)
    variable v_good : integer;  -- OK
    variable bad_var : integer;  -- WARNING: VHDL-005 (v_)
begin
    process -- ERROR: VHDL-007 (no label)
    begin
        wait;
    end process;

    good_proc: process(clk) -- OK
    begin
    end process;

    bad_name: process(clk) -- WARNING: VHDL-008 (should be bad_name_proc)
    begin
    end process;
end architecture;
