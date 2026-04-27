library work; -- ERROR: VHDL-009
use ieee.std_logic_unsigned.all; -- ERROR: VHDL-016

entity TEST_ENTITY is -- ERROR: VHDL-001 (should be lowercase)
    generic (
        g_timeout : integer := 10 -- OK
    );
    port (
        data_in : in std_logic; -- WARNING: VHDL-019 (should be clk)
        clk     : in std_logic; -- WARNING: VHDL-019 (should be rst)
        reset   : in std_logic  -- WARNING: VHDL-020 (active low _n)
    );
end entity;

architecture rtl of TEST_ENTITY is
    signal My_Signal : std_logic; -- ERROR: VHDL-003 (lowercase), WARNING: VHDL-004 (s_)
    signal s_count   : integer;   -- WARNING: VHDL-017 (no range)
    signal s_state   : integer range 0 to 3; -- WARNING: VHDL-022 (no safe attr)
    variable v_good  : integer;   -- OK
    variable bad_var : integer;   -- WARNING: VHDL-005 (v_)
begin
    comb_proc: process(s_good) -- WARNING: VHDL-018 (should be ALL), ERROR: VHDL-021 (latch)
    begin
        if s_good = 1 then
            My_Signal <= '1';
        end if; -- Missing ELSE
    end process;

    fsm_proc: process(clk) -- WARNING: VHDL-015 (no default assign)
    begin
        if rising_edge(clk) then
            case current_state is
                when IDLE =>
                    if start = '1' then
                        next_state <= RUN;
                    end if;
                when others => null;
            end case;
        end if;
    end process;
end architecture;
