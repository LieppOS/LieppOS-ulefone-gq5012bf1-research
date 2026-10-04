# AW36518 / AW36518-V2 flash drivers — parity closure

Live DT: three Awinic flash ICs at 0x63:
- `aw36515@63` on i2c@11e01000 (DONE elsewhere)
- `aw36518@63` on i2c@11e03000 (`mediatek,aw36518`)
- `aw36518_i2c13@63` on i2c@11d72000 (`mediatek,aw36518_v2`)

All three are `okay`.

| module | functions | data | imports (CRC) | modinfo | B1==B2 |
|---|---|---|---|---|---|
| aw36518.ko (`7dcf64a7…`) | 22/23 byte-identical, 23/23 size/KCFI | 32/32 | 47/47 | 9/9 | yes |
| aw36518_v2.ko (`c7faa3ba…`) | 22/23 byte-identical, 23/23 size/KCFI | 32/32 | 46/46 | 9/9 | yes |

These were 13/23 and 12/23 before this pass. Five source corrections, all
proven by the disassembly (`source/aw36518*/phase4-recon-to-exact.diff`):

1. `aw36518_gpio_set` logs a literal `pin(0)`. The stock passes `wzr`, not
   `flash_externel_gpio`.
2. The FLAG1 short-circuit test checks bit 5 and bit 4 in separate `if`s
   (fault decode semantics unchanged).
3. In probe, `aw36518_gpio_init()` is tested `< 0`.
4. `reg_show` declares `int i` first (register-allocation order).
5. Six `#line` anchors restore the stock `__LINE__` values: 932, 986, 991,
   993, 1023, 1033. V2 uses 930, 984, 988, 990, 1020, 1030.

The residual is identical in both modules: one instruction-scheduling
difference in probe, plus the `.data` order of three byte-identical objects
(see `README.md`). Hardware, register and thermal-cooler behaviour are as in
the Phase-4 contracts (`kernel/phase4-aw36518*`).
