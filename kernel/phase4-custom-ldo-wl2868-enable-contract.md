# WL2868 enable contract

Public ABI: `int will_ldo_en(int ldo_num, int enable)`.

## Common behavior

- Valid channel range: 1–7. Invalid values log and helper returns 0; no I2C occurs.
- Register: exactly `0x0e`.
- Read with a two-message raw transfer. On negative read result, both helper variants log and return `-ENODEV` (-19), not the underlying errno.
- Bit map: channel N is bit N-1 (`1,2,4,8,0x10,0x20,0x40`).
- `enable == 0` clears that bit. **Any nonzero value** sets it.
- No register cache exists; every valid call is read-modify-write.

## Variant-specific write value and returns

| Channel | Bit | WL2864C (ID 0x01) | WL2868C (ID 0x82) |
|---:|---:|---|---|
| 1 | 0x01 | preserve all other read bits | same low-bit change; then global-bit rule |
| 2 | 0x02 | preserve all other read bits | same |
| 3 | 0x04 | preserve all other read bits | same |
| 4 | 0x08 | preserve all other read bits | same |
| 5 | 0x10 | preserve all other read bits | same |
| 6 | 0x20 | preserve all other read bits | same |
| 7 | 0x40 | preserve all other read bits | same |

WL2868C bit 7 semantics are exact: after changing the selected low bit, write 0 only when the **entire intermediate byte** is zero; otherwise write `(result | 0x80)`. This normally sets bit 7 whenever any output is enabled. A read value containing bit 7 can keep the intermediate byte nonzero even after the final low output bit is cleared, so stock can write `0x80`; do not simplify the rule to “clear bit 7 when all low bits are clear.” WL2864C does not force bit 7 and preserves the read byte except for the selected bit.

On write failure WL2864C returns the raw negative I2C result; on successful write it returns the original `enable` integer. WL2868C returns the raw negative write result or 0 on success. These helper returns are not visible to the normal consumer: the exported `will_ldo_en` dispatcher discards them and returns 0 for either supported chip byte, or -1 for an unsupported chip byte.

Stock custom_ldo/imgsensor uses enable values exactly 1 and 0, after voltage programming for set and after reprogramming the same voltage for unset.
