# SH366003 hardware contract

## Explicit identity

```text
CHIP = Sino Wealth SH366003 (stock compatible and driver identity); silicon subrevision not separately exposed
I2C_BUS = 9
I2C_ADDRESS = 0x55
DEVICE_ID_REGISTER = SBS Control/ManufacturerAccess register 0x00, subcommand 0x0001
DEVICE_ID_VALUE = 0x0603
FW_VERSION = two-byte response returned by MAC command 0x40d9; exact live bytes were not captured
AFI_VERSION = 0x8cd3 expected by the embedded image final verification (MAC command 0x0046)
BATTERY_PROFILE_VERSION = 0x5a93 (MAC command 0x004d; SBS date encoding 2025-04-19)
```

## Evidence

- DT and live binding: `sh,sh366003`, `/soc/i2c@11c24000/sh366003@55`, `9-0055`.
- Probe sends control subcommand `0x0001`, waits 10 ms, reads register `0x00`, and rejects a result other than `0x0603`.
- The stock AFI stream ends by writing MAC command `0x0046`, waiting 1,500 ms, then comparing raw 0x3e response bytes with `46 00 d3 8c`; the value is little-endian `0x8cd3`.
- Automatic update acceptance requires command `0x004d == 0x5a93` and FCC greater than 3,500 mAh. `0x5a93` decodes through the stock date formula to 2025-04-19.
- Probe obtains two bytes from MAC command `0x40d9`, NUL-terminates them, and formats `fuelgauge_fw_version` as `Vno:0x%02x-%s(%02d%02d)\n`.

No separate silicon-revision or ROM-version read was identified. `SH366003-7300`, `MTK7300`, and `LION` occur in stock constants/strings, but do not prove a distinct silicon revision.
