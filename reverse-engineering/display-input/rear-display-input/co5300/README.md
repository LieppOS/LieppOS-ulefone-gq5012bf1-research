# CO5300 rear display: `spi_tiny_co5300_lcd`

**Status: DONE (static).** Source is reconstructed; 24/25 functions are
byte-identical to the shipped module and the one residual is characterized
below. No runtime validation was performed (offline only).

## Identity

| item | value |
|---|---|
| module | `vendor_dlkm/lib/modules/spi_tiny_co5300_lcd.ko` |
| SHA-256 | `39eecad8254c2fc69f9c8d52902b443b3adc64c79c4c6a529af19b4b1f2a9742` |
| compiler | Android clang 17.0.2 (r487747c, build 10087095) |
| driver name | `spi_tiny_lcd_co5300`; OF `hxytech, spi_tiny_lcd` (literal space) |
| depends | `yft_devinfo,hynitron` |
| panel | CO5300-class AMOLED DDIC with GRAM, 340×340 RGB565; ID `DA=0x33`, `DB=0x11/0x10` |
| bus | MT6989-IP SPI @0x11010000, CS0, mode 3, 52 MHz writes / 1 MHz reads, DT max 60 MHz |
| GPIOs | reset 154, 1V8 118, 2V8 29, DC 190, TE 31 (falling-edge IRQ), bl (requested, unused) |
| ADC | IIO `tiny_lcd_adc`, 451..999 mV accepted |
| userspace | `/dev/tiny_lcd_miscdev` (0666), 11 ioctls, five driver sysfs attributes |

The `SSD1317 … QG-9696TSWXG04` description and `alias=spi:SSD1317` are stale
metadata (`MODULE_DESCRIPTION`/`MODULE_ALIAS`), not the fitted panel.

## Documents

- `protocol.md`: SPI framing, init stream, ID rule, runtime commands
- `command-table.tsv`: every opcode, with board-proven behavior vs generic meaning
- `update-path.md`: frame geometry, TE path, locking, defects
- `power-sequence.md`: probe, suspend, resume, AOD, backlight, init/exit
- `../integration.md`: coupling with Hynitron (CO5300 owns touch power)
- `../userspace/service-map.md`: HAL/service/framework boundary
- `source/`: reconstruction (publishable; excludes the stock splash bitmap)
- `parity/`: explicit-operand parity tables

## Parity (A = shipped stock module, B = `source/` rebuilt)

Build: CI-12901745 GKI, clang r487747c, `LTO=none`, isolated `M=` build, with
provider CRCs from the real Hynitron build and the stock yft_devinfo `__kcrctab`.

| axis | result |
|---|---|
| functions | 25/25 present, **25/25 size-equal, 24/25 byte-identical** |
| KCFI type IDs | 25/25 equal |
| relocations | 24/25 functions identical; `.text` 1473/1474 entries, all other sections equal |
| data objects | 64/64 present, **64/64 section+size equal, 63/64 bytes equal** (`srcversion` only) |
| imports | 58/58 name+CRC equal; `__versions` order equal |
| exports | 0 / 0 |
| `.modinfo` | 10/11 identical; `srcversion` differs (MD4 of original source text) |
| section sizes | `.text` 14580, `.rodata` 1944, `.data` 231672, `.bss` 231624, `.rodata.str1.1` 7508, `.init.text` 372, `.exit.text` 64, `__versions` 3712, `.modinfo` 434: all equal |
| clean reproducibility (B1 vs B2, two clean builds) | all loadable sections byte-equal |

The stock layout and sizes matter because the following facts are recovered
from them and are reproduced exactly:

- **`__LINE__`.** Each log passes `__func__` and `__LINE__`. All 112 original
  line numbers (97…1414) are recovered from immediates and pinned with `#line`.
- **`g_data` SRA split.** The static aggregate is split into `g_data.0..13`.
  Fields 9 and 12 are written but never read, which gives exactly stock's
  numbering gaps.
- **`push_table`.** The MediaTek `push_table(table, count)` helper is inlined
  into `initial_co5300()`. That is why stock reloads `count` per iteration and
  emits two local-bounds traps.
- **spidev structure.** The `spidev_sync()`/`spidev_sync_write()`/
  `spidev_sync_read()` helpers follow `drivers/spi/spidev.c`.
- **Header set.** `<linux/regulator/consumer.h>` brings the `__COUNTER__`-derived
  `__UNIQUE_ID_*` names to stock values (`author458` etc.). It is consistent
  with the stock header set; `<linux/suspend.h>` would give the same count.

### The one residual: `spidev_sync_write_multi_data` (864 = 864 bytes)

At the `g_data.spi == NULL` (`-ESHUTDOWN`) exit of the inlined `spidev_sync()`,
the rebuild jump-threads the constant -108 straight to the "SPI transfer timed
out" log, duplicating the `vfree()` call. The remaining two-way merge
`status ? status : m.actual_length` is then if-converted into `csel`. Stock keeps
one shared `vfree` + `tbnz` merge and a branch for the `actual_length` load.

Same size, same calls, same loads/stores, same behavior on all three paths
(spi NULL / error / success). Eight source variants were tested: the 5.x and
6.x spidev shapes, int vs ssize_t, an early return, a returning caller, and
explicit casts. All produce the identical delta. The source trigger of stock's
non-threading is therefore not identified. It is an optimizer CFG choice with
no semantic effect.

## Corrections to the earlier (2026-09-25) behavioral contract

The earlier `kernel/phase4-spi-tiny-co5300-lcd-*` notes and the source in
`lieppos/spi-tiny-co5300-lcd-recon/` were semantic reconstructions; that source
reached 6/25 size-equal and 4/25 byte-identical. Byte-level recovery overturns
these claims:

| earlier claim | stock (proven) |
|---|---|
| `BL_ENABLE` calls power-on(2); `BL_DISABLE` powers off | both only log "Ignore operation" and toggle `frame_send_enable`; `BL_ENABLE` also sets status 1 |
| `POWER_ENABLE`/`POWER_DISABLE` affect the panel only | also call `tiny_tp_power_contorl(1)` after power-on, and `(0)` before power-off |
| `POWER_AOD` powers on then sets `frame_send_end = 0` | powers rear **touch off**, waits 10 ms, sets `frame_send_end = 0`; panel power untouched |
| `TP_GESTURE_ENABLE`: power(1), 10 ms, gesture(1) | gesture(1); then, unless (`power_on == 1 && frame_send_end`), power(1) then power(0) ("force tp reset") |
| brightness re-sent when the frame pointer changes | re-sent when `backlight_step != current_backlight_level` |
| immediate WRITE_FRAME leaves status 3 | immediate send sets status **1** |
| TE ISR gated on panel-power flag | gated on `frame_send_enable` |
| probe fails on any GPIO/pinctrl error | `stl_parse_dt()` result ignored; only ID/ADC/IRQ failures abort |
| probe power-up 20/20/20 ms | probe uses 5/10/10 ms rail delays (resume uses 20/20/20) |
| `/chosen@0` read first | `/chosen` first, then `/chosen@0` (MediaTek `log_store` helper) |
| sysfs stores clamp to 0/1, write_frame only for value 1 | power/bl/tp stores parse straight into the globals without clamp; write_frame sends for any value |
| GPIO labels `tiny_lcd_*` | `tl_reset_gpio`, `tl_en_1v8_gpio`, `tl_en_2v8_gpio`, `dc_ctrl_gpio`, `bl_ctrl_gpio`, `te_gpio` |
| `DEFINE_MUTEX(buf_lock)` | zero-filled, never-initialized mutex in `.bss` (stock defect) |
| SPI id table `SSD1317` | no `spi_device_id` table; `MODULE_ALIAS("spi:SSD1317")` |

## Firmware/asset boundary

There is no controller firmware. The only opaque blob is the 231200-byte splash
`gImage_logo` (stock `.data`, SHA-256 `c1a917c5…61cf`). It is not
redistributed; extract it from the stock `.data` section to build. The
44-record init table is configuration and is included.
