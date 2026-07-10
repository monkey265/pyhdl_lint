# Implementation Status

| Rule | Rule Code | Implemented |
| --- | --- | --- |
| Use `logic` instead of `reg` | SV-001 | [x] |
| Module name should not start with `mod_` | SV-002 | [x] |
| Parameters should be ALL_CAPS | SV-003 | [x] |
| Port ordering (Clk, Rst) | SV-004 | [x] |
| Reset active low naming (`_n`) | SV-005 | [x] |
| No blocking assignment (`=`) in a clocked block | SV-006 | [x] |
| Combinational block should use `always_comb`/`@*`, not an explicit sensitivity list | SV-007 | [x] |

No signal/port prefix convention is enforced (unlike VHDL's `s_`/`v_`) - no such
convention is idiomatic in SystemVerilog, so none is invented. See
`docs/superpowers/specs/2026-07-10-standard-rules-library-design.md` for the design
rationale and verified AST facts behind SV-002 through SV-007.
