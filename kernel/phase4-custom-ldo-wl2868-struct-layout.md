# WL2868 private-state layout

## Proven object

Stock has one local `.bss` object, `wl2864c_data`, of exactly **112 bytes (0x70)**. It is static storage; probe performs no allocation and imports no mutex API. At probe entry stock stores the `i2c_client *` at offset 0 and zeros every other byte through 0x6f.

| Offset | Size | Proven semantic | Evidence |
|---:|---:|---|---|
| `0x00` | 8 | `struct i2c_client *client` | probe `stp x0,xzr,[base]`; every raw-I2C path loads this pointer, then client `addr` at +2 and adapter at +0x18 |
| `0x08..0x2f` | 40 | **UNKNOWN / zeroed storage** | zeroed by probe; no stock load/store relocation addresses this range |
| `0x30` | 8 | reset GPIO descriptor | probe stores result of `devm_gpiod_get(dev,"reset",GPIOD_OUT_HIGH)`; later set/pulse/put loads use this offset |
| `0x38` | 8 | optional VIN1 GPIO descriptor | probe stores result of `devm_gpiod_get(dev,"vin1",GPIOD_OUT_HIGH)`; success path sets and puts it |
| `0x40` | 4 | VIN2 integer GPIO number | `wl2864c_vin2_power` loads a 32-bit value, passes it to `gpio_to_desc`, then calls `gpiod_set_raw_value` |
| `0x44` | 1 | chip dispatch byte | probe stores `0x82`; both public dispatchers load one byte; success log loads one byte |
| `0x45..0x67` | 35 | **UNKNOWN / zeroed storage** | zeroed by probe; no stock load/store relocation addresses this range |
| `0x68` | 4 | misc read-register cursor | open stores zero; llseek loads/stores a 32-bit cursor; read snapshots it as the first register |
| `0x6c` | 1 | probe-ready flag | successful probe stores 1; remove stores 0; open rejects when zero |
| `0x6d..0x6f` | 3 | **UNKNOWN / padding** | zeroed; never otherwise accessed |

## Negative findings

There is no separately allocated private structure, `devm_kzalloc`, `kmalloc` in probe, `i2c_set_clientdata`, device-pointer field, mutex, register cache, channel-state array, enable cache, or miscdevice embedded in this object. The miscdevice is a separate 80-byte `.data` object. The 112-byte size and all accessed offsets are exact; the two unknown ranges are deliberately not assigned invented semantics.

The reconstruction uses explicit unknown byte ranges and compile-time `sizeof`/`offsetof` assertions for every proven field.
