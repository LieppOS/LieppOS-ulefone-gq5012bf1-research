# WL2868 chip/variant contract

## Stock code

Both public dispatchers recognize state chip byte `0x01` as the WL2864C helper family and `0x82` as the WL2868C helper family; any other byte returns -1. The helper families differ in voltage tables/divisor and enable bit-7 behavior.

However, successful stock probe unconditionally writes `0x82` to the state byte. It does not transfer register 0x00 and does not parse `id_reg`, `id_val`, `id_reg_2868c`, or `id_val_2868c`. Consequently, under stock's normal lifecycle the WL2864C branch is present but unreachable unless memory is changed outside this module.

## Board evidence

The frozen merged DT node at I2C 11, declared address 0x29, contains:

- `id_reg = <0x00>`
- `id_val = <0x01>`
- `id_reg_2868c = <0x00>`
- `id_val_2868c = <0x82>`

The device is bound live as `11-0029` to driver `wl2864c`, and the stock module is loaded. This is strong board-intent evidence for the WL2868C path, consistent with probe's hardcoded 0x82. It is **not** an observed physical register read. The exact physical die therefore remains `WL2868C-intended / not independently read from hardware`, which is the strongest claim permitted by the frozen evidence.

## Variant differences

| Behavior | state ID 0x01 (WL2864C helper) | state ID 0x82 (WL2868C helper) |
|---|---|---|
| channels/registers | seven; 0x03–0x09 | seven; 0x03–0x09 |
| LDO1–2 encoding | `(value/100 - 6000)/125` | `(value/100 - 4960)/80` |
| LDO3–7 encoding | `(value/100 - 12000)/125` | `(value/100 - 15040)/80` |
| enable low bits | bit `ldo-1` | bit `ldo-1` |
| enable bit 7 | preserved exactly as read | OR 0x80 when the entire post-RMW byte is nonzero; write 0 only when that byte is zero |
| default writes | none in probe | none in probe |
| probe chip name/log | no ID-specific name | chip byte logged numerically after hardcoding 0x82 |

No channel-count or VOUT-register-address difference exists.
