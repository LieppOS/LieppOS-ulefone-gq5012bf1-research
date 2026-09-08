# GQ5012BF1 SC851x hardware contract

## Required resolution

```text
DT_ADDRESS = 0x69
LIVE_ADDRESS = 0x69 (Linux device 6-0069)
DRIVER_EXPECTED_ADDRESS = 0x69 (I2C core instantiates from DT reg)
DISCREPANCY_RESOLVED = YES
EXPLANATION = The node directory/name is sc851x-charger@6f, but its authoritative
              big-endian reg cell is 00 00 00 69. The parent i2c@11e01000 is
              exposed as bus 6 and the bound live device is 6-0069. @6f is a
              stale unit-address suffix only; the driver contains no hard-coded
              slave address and uses the i2c_client created at 0x69.
```

## Evidence chain

| layer | evidence |
|---|---|
| live DT path | `/sys/firmware/devicetree/base/soc/i2c@11e01000/sc851x-charger@6f` |
| live DT `compatible` | bytes decode to `sc,sc8510\0` |
| live DT `reg` | bytes `00 00 00 69` = `0x69` |
| parent | `i2c@11e01000`, `mediatek,mt6989-i2c` |
| Linux enumeration | `/sys/bus/i2c/devices/6-0069` |
| binding | `/sys/bus/i2c/drivers/sc851x` and `/sys/module/sc851x_charger` |
| IRQ | live thread `[irq/57-sc851x-irq]` |
| binary behavior | `devm_regmap_init_i2c(client, ...)`; no constant I2C address in probe/read/write paths |

Device-tree unit-address text is a naming convention and should normally match
`reg`, but it is not the value used to instantiate the I2C client. This board's
suffix is malformed/stale and should not be propagated as an electrical address.

## Board DT configuration

- selected family member: **SC8510** (`sc,sc8510`)
- IRQ specifier: GPIO controller phandle 137, line 12, flags 2
- required scalar configuration properties: 35/35 present
- `audio-en = 1`
- no supply phandle, regulator consumer, charger-class link, extcon link, USB
  controller link, or uSmart link in this node

Exact property-to-field mappings and raw values are in
`phase4-sc851x-register-fields.tsv`.

## Silicon role

SouthChip's public product page identifies SC8510 as a 99.5%-efficiency
switched-capacitor device for a 2S architecture: 10-A battery discharging in
forward 2:1 conversion, 4-A charging in reverse 1:2 conversion, plus a
load-switch function. It can preserve 1S-equivalent downstream power
architecture around a 2S pack.

This establishes the chip family purpose, not the board's exact schematic.
Static software evidence cannot prove which SC8510 power pins connect to which
GQ5012BF1 rails.

## Stock-driver role boundary

The stock module:

- resets and configures protection/timing/frequency/audio fields;
- reads/logs registers and three IRQ flag bytes;
- exposes a raw debug register file;
- clears `AUDIO_EN` at shutdown;
- does **not** register a charger, power supply, regulator, extcon or USB role;
- does **not** expose an intermodule enable/mode/direction API;
- does **not** write any of the 14 allocated-only fields.

Therefore it is a **hardware configuration/debug/IRQ shim**, not charging
policy. SC8571 is a separate sibling at `0x67` and its module depends on
`charger_class`; that framework distinction must remain explicit.

## Bounded unknowns

Without a board schematic, private full register datasheet, or prohibited live
electrical/register experimentation, this investigation does not claim:

- the schematic net names connected to V1X/V2X/VAC;
- how conversion enable/direction is selected outside this driver;
- whether an external enable pin or silicon reset default activates a path;
- the detailed electrical semantics of `AUDIO_EN` or `FAM_EN`;
- the precise physical loads behind the SC8510.
