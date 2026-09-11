# Hynitron controller identity

## PROVEN FITTED ON GQ5012BF1

The fitted rear-touch controller is **Hynitron CST820**, stock chip-type ID
`0x00b7` (183), product-line 800. This is not inferred from the firmware name:
stock `hyn_ts_data_init` writes configured chip type `0xb7` before detection,
the live DT binds this one configured instance at I2C0/0x15, and the stock chip
table maps `0xb7` to the CST8xx/800 family at normal address 0x15. Public
Hynitron ID tables independently name 0xb7 CST820.

The live snapshot proves the device was bound (`/sys/bus/i2c/devices/0-0015`,
IRQ 56, input `hyn_ts`). No captured boot log contains the six running ID bytes,
so running firmware/module/project numeric values remain read-on-probe values,
not invented constants.

## SUPPORTED BY DRIVER

Relevant embedded-image selection accepts:

| chip type | silicon | project | module | image |
|---:|---|---:|---:|---|
| `0xb5` | CST816T | 0 | 4 | CST816T image |
| `0xb6` | CST816D | 0 | 4 | CST816D image |
| `0xb7` | CST820 | 0 | wildcard `0xff` | same CST816D-family image |

The generic `hynitron_chip_type_grp` also recognizes legacy CST1xx/2xx/3xx/
6xx/7xx/8xx/9xx IDs. Those are framework support, not evidence that another
part is fitted.

## Runtime identity fields

Probe normally reads six bytes from register `0xa6` first. Stock stores byte 1
as project ID, byte 2 as module ID, byte 3 as running firmware version and byte
4 as checksum and formats them into `second_touch_fw_version`. Only when this
normal read fails does fallback detection reset, write `0xaa` to 16-bit register
`0xa001`, and poll `0xa003` for `0x55` up to ten times before restoring address
0x15 and resetting out of ROM mode. It does not read an invented `0xa7` chip-ID
register. Probe fails only if both normal information and fallback detection
fail; the later informational re-read is non-fatal.
