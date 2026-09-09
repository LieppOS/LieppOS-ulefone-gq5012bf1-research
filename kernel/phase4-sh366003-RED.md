# SH366003 mandatory RED

## Baseline

No plausible public donor was found, so the mandatory failing baseline is the absence of a source implementation:

`NO_PUBLIC_DONOR_FOUND`

The reconstruction therefore starts from an empty consumer and the stock ELF oracle. An unmodified generic SBS driver fails the contract and was not built as a false donor.

## Required stock delta

| Surface | Generic/empty baseline | Stock oracle requirement |
|---|---|---|
| Function set | absent | 36 named functions (39 ELF `STT_FUNC` entries including init/exit stubs/table artifacts) |
| I2C style | unspecified | SMBus word plus raw `i2c_transfer`; 0x3e/0x40 MAC and 0x00 control transports |
| Register map | unspecified | standard telemetry plus MAC 0x0041..0x40d9 and AFI writes through 0x3e/0x60 |
| power_supply | absent | `3rd-gauge`, Battery, exact 10-property list |
| Firmware/AFI | absent | embedded 2,142-byte `sinofs_afi_data`, 209-operation interpreter, version/update gate |
| Monitor | absent | first run 10 s, recurring 5 s, telemetry plus eight status reads and DAStatus1 |
| DT | absent | exact `sh,sh366003`, I2C 9 address 0x55; no driver-specific properties consumed |
| Calibration/profile | absent | exact embedded data-flash stream and checksums |
| Firmware version | absent | MAC command 0x40d9 plus exported YFT string |
| State | absent | 0x428-byte stock allocation with two delayed works, five mutexes, caches and update flags |
| PM | unspecified | no PM callbacks; remove is a no-op; shutdown logs only |
| YFT | absent | three exact stock-provider imports and CRCs |

This RED is fail-closed: ordinary telemetry alone cannot satisfy it. The AFI interpreter, version gate, update sequencing, class ABI, and YFT boundary are required reconstruction surfaces.
