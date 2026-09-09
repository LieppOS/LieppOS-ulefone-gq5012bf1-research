# SC8571 mandatory RED

## Frozen input

Best donor: LineageOS/OnePlus SM8550 OPLUS
`oplus_sc8571_master.c`, SHA256
`7b56d7cca64a12d32552f9464bb606ce0b08041ef9d938cab0b9a4206db8224b`.
The frozen file under `workspace/phase4-sc8571/source-search/` was not edited.

## Build-before-change result

An unmodified copy of the donor C/header was submitted as an external module to
the exact workspace target `//common:kernel_aarch64`:

```text
//lieppos/sc8571-red-donor:sc8571_red_donor
RED_BUILD_RC=1
fatal error: '../oplus_vooc.h' file not found
```

This is the required honest RED: the candidate is inseparable from the OPLUS
charger/PPS framework (`oplus_vooc.h`, `oplus_gauge.h`, `oplus_charger.h`,
`oplus_pps.h`) and cannot be compiled as the Ulefone MediaTek module. Adding
stubs would create a fake framework and was not done. Raw log:
`workspace/phase4-sc8571/raw/red-donor-build.log`.

## Stock versus donor

| surface | stock ELF | frozen OPLUS donor | RED conclusion |
|---|---|---|---|
| function set | 34 ELF functions | 44 detected C definitions | 3 shared names only; not a source match |
| framework | MediaTek `charger_class` | OPLUS PPS/VOOC/gauge/track | incompatible |
| provider import | `charger_device_register` CRC `0x36325d38` | absent | stock boundary must be reconstructed |
| IC transport | regmap + 58 `struct reg_field` entries (1,160-byte table) | raw `i2c_smbus_*` + private mutex | architecture differs |
| role model | one OF-matched driver, role data `{master,slave}` | separate master/slave A/slave B units | architecture differs |
| charger operations | 648-byte `charger_ops`, 14 function pointers | OPLUS exported helper API | callback surface differs |
| DT | stock reads 40 required scalar properties plus required IRQ and optional charger name | donor parse is effectively empty; OPLUS GPIO property elsewhere | differs |
| ADC | stock table-driven 5-channel charger callback | donor direct dedicated register readers | semantics donor-only until stock-confirmed |
| IRQ | stock threaded IRQ reads a stock status register and notifies power supply | OPLUS UCP/PPS disconnect and tracking path | differs |
| initialization | stock 20-entry DT-backed reg-field write sequence plus reset/delay | hard-coded OPLUS SC/bypass configuration | differs |
| watchdog/mode | stock fields recovered from its own table/code | donor policy-specific literal writes | no default may be copied |
| strings | stock SouthChip/MediaTek logs and `primary_dvchg`/`secondary_dvchg` | OPLUS PPS/error-upload strings | differs |
| data tables | regmap config, 145 fields, ADC scale/accuracy, charger ops | macro header and direct calls | register naming only |

## Proven reconstruction rule

Every post-RED implementation decision must trace to one of:

1. stock symbol/relocation-aware disassembly;
2. stock `.rodata`/`.data`/`.bss` contents;
3. stock DT/DTBO;
4. the exact charger-class provider source/type graph;
5. a committed read-only runtime capture.

The OPLUS donor can confirm a silicon field name only after stock evidence has
already fixed its register, mask, and transformation. It supplies no Ulefone
policy defaults.
