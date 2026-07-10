# Implementation Status

| Rule | Rule Code | Implemented |
| --- | --- | --- |
| Module name should not start with `mod_` | VER-001 | [x] |
| Parameters should be ALL_CAPS | VER-002 | [x] |
| Port ordering (Clk, Rst) | VER-003 | [x] |
| Reset active low naming (`_n`) | VER-004 | [x] |
| No blocking assignment (`=`) in a clocked block | VER-005 | [x] |
| Combinational block should use `@*`, not an explicit sensitivity list | VER-006 | [x] |

No signal/port prefix convention is enforced (unlike VHDL's `s_`/`v_`) - no such
convention is idiomatic in Verilog, so none is invented. See
`docs/superpowers/specs/2026-07-10-standard-rules-library-design.md` for the design
rationale and verified AST facts behind VER-002 through VER-006.
