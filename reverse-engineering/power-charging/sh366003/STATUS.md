# SH366003-FUEL-GAUGE — STATUS (2026-10-07)

**DONE (static, named scope: `sh366003_fg.ko` kernel driver and its hardware/DT/profile/psy contract).**

`sh366003_fg.ko`: 39/39 functions present and same size, **38/39 byte-identical**; the 39th
(`sh_fg_probe`) differs only by a proven register-allocation permutation (11/809 instructions,
x22↔x25 + two swapped independent `adrp/add` pairs); 42/42 data objects, 194+829 strings,
35/35 imports, 36/36 modversion CRCs, 0/0 exports, KCFI 28/28, 1513 relocations
(1509 identical + 4 order-only addend swaps), `.modinfo`/vermagic identical, B1 == B2.
Remaining differences: R1 register allocation, `.note.gnu.build-id`, DWARF (stripped in stock).

Literal source is not recovered (no public template); the source is a binary-equivalent
reconstruction (`source-lineage.md`).

| closure item | state |
|---|---|
| hardware identity / bus / address / IRQ / topology | PROVEN (`hardware-topology.md`) |
| DT contract | PROVEN; child `clock-frequency` unconsumed (corrected) |
| register map | 36 rows, all from the exact rebuild |
| profile / calibration ownership | compiled AFI → gauge data flash; calibration/learned data only in gauge |
| power_supply + sysfs interface | PROVEN (`power-supply-interface.tsv`) |
| charging boundary | measurement only; reads `primary_chg` ONLINE |
| YFT-DEVINFO dependency | bounded exactly by CRC + call-site bytes (`yft-devinfo-boundary.md`) |
| firmware/NVM | gauge-internal ROM firmware not accessible/not touched; AFI = data-flash program; no file loader |

Runtime validation only (not RE blockers): SOC/voltage/current/temperature accuracy vs reference,
FCC aging, low-SOC behaviour, AFI programming path on a unit whose profile ≠ 0x5A93
(DO_NOT_RUNTIME_TEST without a recovery plan), actual i2c-9 SCL rate (static: 100 kHz).
