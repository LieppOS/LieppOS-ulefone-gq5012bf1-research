# RT5133 — init / runtime / shutdown sequence

Source: ALPS `drivers/regulator/rt5133-regulator.c` @ `5e415e059253`
(blob `047d4b2a20e4`), which rebuilds to the stock `rt5133-regulator.ko`
byte-for-byte except the build-id — so this is the stock behaviour, not a model of it.

## What actually happens on GQ5012BF1 (every stock boot)

| # | step | hardware effect |
|---|---|---|
| 1 | `extdev_io_class.ko` loads (vendor_boot `modules.load` #122): creates class `extdev_io` | none |
| 2 | `rt5133-regulator.ko` loads (#123); `i2c_register_driver` matches `5-0018` | none |
| 3 | `dev_info "rt5133_probe start(1.0.2_MTK)"`; `devm_kzalloc` priv; `crc8_populate_msb(tbl, 0x07)` | none |
| 4 | `devm_gpiod_get_optional(dev, "enable", GPIOD_OUT_HIGH)` | **GPIO1 → output high** |
| 5 | `devm_regmap_init(&rt5133_regmap_bus, 8/8-bit, max 0x3F, no cache)` | none |
| 6 | `devm_extdev_io_device_register()` → `/sys/class/extdev_io/RT5133.5-0018/{reg,size,data,type,lock}` | none |
| 7 | `rt5133_validate_vendor_info()`: `regmap_read(0x00)` → SMBus block read, 2 bytes, at 0x18 | **the only I2C transaction; fails** |
| 8 | `dev_err "Failed to check vendor info [%d]"`; return error | devres unwind: extdev node removed, GPIO1 descriptor freed (level stays high) |

No delay is executed (the `udelay(2)` belongs to step 10 below). No register is
ever written on this board.

## Full probe path (reference board / if a chip answered)

| # | call | registers / effect |
|---|---|---|
| 1–6 | as above | |
| 7 | validate | R `0x00`; `val & 0xF0`: `0x70` → RT5133 table, `0x80` → RT5133A table |
| 8 | (bug) unknown nibble | `priv->cdata` stays `NULL`, `IS_ERR(NULL)` is false → NULL dereference in step 11 |
| 9 | `rt5133_chip_reset` | W `0x06 = 0xB1` |
| 10 | | `udelay(2)` |
| 11 | `devm_regulator_register` ×9 (BASE, LDO1..8) | each runs `rt5133_of_parse_cb` first |
| 11a | BASE of_parse | RMW `0x19` bit7 ← `oc-shutdown-all` (0), bit6 ← `pgb-shutdown-all` (0) |
| 11b | LDOn of_parse | RMW `0x20+4(n-1)`: bit5 ← `oc-ptsel` (1), bit4 ← `pgb-ptsel` (1), bits1:0 ← `soft-start-time-sel` (1; default 1, clamp 3) |
| 11c | regulator core constraints (GKI 6.1 `of_regulator.c`/`core.c`) | every LDO has min and max → `apply_uV = true` → `machine_constraints_voltage()` reads VSEL and rewrites `0x21+4(n-1)[7:5]` only if the current setting lies outside [min,max] (LDO1: forced to idx 3 = 2.80 V). `regulator-active-discharge;` is **valueless** in the DT, but 6.1 reads it with `of_property_read_u32()` → `-EOVERFLOW` → constraint unset → `CTRL3` bit2 is **never written** |
| 12 | `devm_gpiochip_add_data` | 3 GPOs, base −1, label `5-0018`; no direction input op |
| 13 | `rt5133_enable_interrupts` | bulk W `0x10..0x12 = FF FF FF` (clear), bulk W `0x16..0x18 = 00 00 00` (unmask all) |
| 14 | `devm_request_threaded_irq(i2c->irq, NULL, handler, IRQF_ONESHOT)` | EINT19 falling |
| 15 | `i2c_set_clientdata` | |

Error unwind is entirely devres-based; there is no explicit rollback of
register writes (a failure after step 9 leaves the chip reset and partly configured).

## Runtime

* Enable/disable: regulator core → `0x20+4(n-1)` bit7 (LDOs), `0x09` bit1 inverted (BASE).
* Voltage: `0x21+4(n-1)` bits7:5 table index.
* GPO: `0x0B` bits (7-n)|(3-n); `get()` returns a cached software flag, not hardware.
* `module_param dbg_log_en` (0644) enables per-access `rt_dbg` logging.
* Debug raw I/O: `extdev_io` sysfs `reg/size/data` (0644) → `regmap_bulk_{read,write}`.

## Suspend / resume / shutdown

None. No `dev_pm_ops`, no `.shutdown`. `wakeup-source` in DT is not consumed.

## Remove

`rt5133_remove()` calls `extdev_io_device_unregister(priv->extdev)`, but the
extdev was registered with `devm_extdev_io_device_register()`, whose devres
release calls `extdev_io_device_unregister()` again → double
`device_unregister()` + double `kfree(data_buffer)`. Latent stock bug, reachable
only by unbinding a successfully probed device; unreachable on GQ5012BF1.
Preserved in source (parity first).
