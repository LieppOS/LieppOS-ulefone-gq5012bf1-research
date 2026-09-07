# AW36515 hardware contract (GQ5012BF1)

Everything below is proved from the stock `aw36515.ko` binary, the stock
device tree, and read-only snapshots already committed to this repository.
Nothing is carried over from the AW36518 phase without independent proof.

## Part and bus

| property | value | proof |
|---|---|---|
| chip | Awinic AW36515, dual-channel flash/torch LED driver | `MODULE_DESCRIPTION`, register interface, two independent LED channels |
| I²C address | `0x63` | DT `reg = <0x63>`; live device name `6-0063` |
| I²C controller | `/soc/i2c@11e01000` (alias `i2c6`) | DT; `aliases { i2c6 = "/soc/i2c@11e01000" }` |
| live adapter number | **6** | `/sys/bus/i2c/devices/6-0063` bound to driver `aw36515` |
| compatible | `mediatek,aw36515` | `.rodata+0x48` of_device_id; live modalias `of:Naw36515T(null)Cmediatek,aw36515` |
| regmap | 8-bit register, 8-bit value, `max_register = 0xFF` | `aw36515_regmap` at `.rodata+0x1d8` (byte-identical to the AW36518 sibling's config) |
| channels | 2 (`LED0`, `LED1`) | per-LED enable bits, current registers, ctrl handlers, sub-devices |
| regulators | none requested | no `regulator_*` import |
| clocks | none requested | no `clk_*` import |
| interrupts | none requested | no `request_irq`/`devm_request_*_irq` import; faults are polled through register `0x0A` |
| GPIO | one, `flash-externel` | `of_get_named_gpio_flags`, `devm_gpio_request_one`, `gpio_to_desc`, `gpiod_set_raw_value` |
| runtime PM | enabled, but **no** system-sleep or runtime callbacks | `pm_runtime_enable`/`__pm_runtime_disable`/`__pm_runtime_set_status` are imported; `i2c_driver.driver.pm` carries no relocation and there are no `suspend`/`resume` symbols |

## External strobe GPIO

| property | value | proof |
|---|---|---|
| DT property | `flash-externel = <0x89 0x74 0x00>` | stock DTB `aw36515@63` |
| controller | phandle `0x89` (the SoC pin controller) | DTB |
| pin | **116** (`0x74`) | DTB |
| flags | 0 (active high) | DTB |
| request | `devm_gpio_request_one(dev, gpio, GPIOF_OUT_INIT_LOW, "flash_externel")` | `aw36515_probe+0x124` with the string at `.rodata.str1.1+0x106` |
| validity gate | `gpio > 0` and `gpio < 512`; an out-of-range GPIO makes probe return `-1` | `cmp w0,#1 / b.lt` then `cmp w0,#0x1ff / b.hi` → `mov w0,#-1` |
| stored at | `flash->flash_externel_gpio`, struct offset `+0x560` | `str w22,[x19,#0x560]` |
| driven low | at the start of `aw36515_init()` (first `set_driver(1)`) and in `aw36515_uninit()` (last `set_driver(0)`) | `aw36515_set_driver+0x40` and `+0x148` |
| driven high | by `V4L2_CID_FLASH_STROBE` — **unconditionally**, even when the power-throttling path suppressed the LED enable | `aw36515_set_ctrl+0x35c` reached from both the enabled and the `flashlight_pt_is_low()` arms |
| never driven low | by `V4L2_CID_FLASH_STROBE_STOP` | `STROBE_STOP` contains no GPIO access; only `set_driver(0)` lowers it |

The last two rows are a genuine vendor asymmetry and are reproduced as-is.

## Dual-channel architecture

This is the defining difference from the single-channel AW36518/AW36518_V2
siblings.

| aspect | behaviour | proof |
|---|---|---|
| enable | per channel: mask `0x01` for LED0, `0x02` for LED1 | `aw36515_set_ctrl` selects the mask on `led_no` in every enable path |
| simultaneous operation | **allowed** — nothing serialises the channels; each enable is a read-modify-write of one bit | both bits live in register `0x01` and are set/cleared independently |
| flash current | independent registers `0x03` (LED0) / `0x04` (LED1), full 8-bit code | `aw36515_set_ctrl+0x2ac/+0x2ec` |
| torch current | independent registers `0x05` (LED0) / `0x06` (LED1), full 8-bit code | `aw36515_torch_brt_ctrl+0xb4/+0xbc` |
| mode | **shared**: register `0x01` bits `[3:2]` for both channels | every mode write uses mask `0x0C` with no `led_no` dependence |
| timeout | **shared**: register `0x08` mask `0x0F` | `aw36515_set_ctrl` timeout case ignores `led_no` |
| strobe source | **shared**: register `0x01` mask `0x2C` | same |
| external strobe GPIO | **shared** (chip-wide) | one GPIO field in the struct |
| V4L2 controls | one `v4l2_ctrl_handler` + one `v4l2_subdev` + one `v4l2_ctrl_ops` per channel | `ctrls_led[2]` at `+0x50` (stride 224), `subdev_led[2]` at `+0x210` (stride 328), `aw36515_led_ctrl_ops[2]` at `.rodata+0x388` (stride 32) |
| MediaTek flashlight ids | one per channel, `channel = 0` and `channel = 1` | `flash_dev_id[2]` at `+0x4c8` (stride 52) |
| fault reporting | one shared status register `0x0A`; LED0 short = bit5, LED1 short = bit4, both map to `V4L2_FLASH_FAULT_SHORT_CIRCUIT` | `aw36515_led0_get_ctrl` / `aw36515_led1_get_ctrl` (identical bodies) |
| per-channel protection | **none beyond the shared fault register**; there is no cross-channel interlock, no per-channel current cap and no per-channel timeout | exhaustive read of every register write in the module |
| thermal clamp | applied to **both** channels, LED0 first then LED1 | `aw36515_cooling_set_cur_state` calls `aw36515_torch_brt_ctrl` twice |

## Recovered struct layout

`devm_kzalloc(&client->dev, 0x568 /* 1384 */, GFP_KERNEL)`:

| offset | member | evidence |
|---|---|---|
| `+0x000` | `struct device *dev` | `stp x21,x22,[x19]`; later `[dev + 0x2e8]` = `of_node` |
| `+0x008` | `struct aw36515_platform_data *pdata` | second half of the same `stp`; indexed as `pdata + led*4` in `init_controls` |
| `+0x010` | `struct regmap *regmap` | `str x0,[x19,#0x10]` after `__devm_regmap_init_i2c` |
| `+0x018` | `struct mutex lock` | `__mutex_init(flash+0x18, "&flash->lock", &__key)` |
| `+0x048` | `enum v4l2_flash_led_mode led_mode` | read/written by every mode path |
| `+0x050` | `struct v4l2_ctrl_handler ctrls_led[2]` (stride 224) | `to_aw36515_flash` offsets `-0x38` / `-0x118`; `remove` frees `+0x50` and `+0x130` |
| `+0x210` | `struct v4l2_subdev subdev_led[2]` (stride 328) | `umaddl x24, led, #0x148, flash`; `remove` unregisters `+0x210` and `+0x358` |
| `+0x4a0` | `struct device_node *dnode[2]` | `add x26, flash + led*8, #0x4a0` in the `reg == led_no` branch |
| `+0x4b0` | **24 bytes never accessed** | gap between `dnode[]` and `flash_dev_id[]`; reproduced as `void *vendor_reserved[3]` |
| `+0x4c8` | `struct flashlight_device_id flash_dev_id[2]` (stride 52) | `type/ct/part` writes at `+0x4c8/+0x4cc/+0x4d0`, name at `+0x4d4`, channel/decouple at `+0x4f4`; second element at `+0x4fc` |
| `+0x530` | `struct thermal_cooling_device *cdev` | stored after `thermal_of_cooling_device_register` |
| `+0x538` | `int need_cooler` | set to 1/0 by `cooling_set_cur_state`, tested by both brightness paths |
| `+0x540` | `unsigned long max_state` = 5 | `mov w8,#5; str x8,[x19,#0x540]` in probe; returned by `cooling_get_max_state` |
| `+0x548` | `unsigned long target_state` | returned by `cooling_get_cur_state` |
| `+0x550` | `unsigned long target_current` = 2000560 at probe | `str x9,[x19,#0x550]` |
| `+0x558` | `unsigned long ori_current` = 500780 at probe | `str x10,[x19,#0x558]` |
| `+0x560` | `int flash_externel_gpio` | GPIO store/load |
| `0x568` | total size | `devm_kmalloc(dev, #0x568, 0xdc0)` |

The 24-byte gap is the **same vendor-struct feature already proved for
AW36518/AW36518_V2** (there it sits between `dnode[1]` and `flash_dev_id[1]`).
Its members are unrecoverable — no stock instruction touches the range — so it
is reproduced as an explicitly unused reserved array rather than invented
fields.

## Platform data defaults

When the device has no platform data (which is the case on this board), probe
allocates 20 bytes and fills them with:

| field | value | unit | proof |
|---|---|---|---|
| `max_flash_timeout` | 1600 | ms | `mov x8,#0x640` |
| `max_flash_brt[0]`, `max_flash_brt[1]` | 2000560 | µA | packed `0x1e86b0` written twice |
| `max_torch_brt[0]`, `max_torch_brt[1]` | 500780 | µA | packed `0x7a42c` written twice |

## Reset / init sequence

1. `probe`: `regmap_read(0x00)` — chip ID, **value discarded, not logged, no gate**.
2. `probe`: `regmap_read(0x07)`; on failure probe returns **0** (success) without resetting.
3. `probe`: `msleep(10)`.
4. `probe`: two `printk` records (`"%s:%d: do software reset0 reg0x07=0x%02x"` at line 1047, `"…reset1 write data:0x%02x to reg 0x07"` at line 1049).
5. `probe`: `regmap_write(0x07, val | BIT(7))` — software reset.
6. First `set_driver(1)` (`aw36515_init`): GPIO low → timeout `0x08 = 0x0A` (400 ms) → mode `0x01[3:2] = 0` → `0x05 &= ~0x80` → `0x03 &= ~0x80` → `regmap_read(0x0A)` to clear latched faults.

There is **no retry loop and no delay** anywhere else in the driver; the only
sleeps are the probe `msleep(10)` and the `msleep(arg.dur)` inside
`flashlight_strobe_store`.
