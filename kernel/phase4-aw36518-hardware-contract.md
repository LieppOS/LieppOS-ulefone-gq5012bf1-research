# GQ5012BF1 — AW36518 hardware contract (Phase 2)

All statements below are taken from the stock module, the stock device tree, or
stock userspace.  Nothing is taken from a datasheet, and no flash/torch hardware
was operated during this phase.

## Fitted part and topology

| Item | Value | Evidence |
|---|---|---|
| Driver identity | Awinic AW36518 single-channel flash LED driver | `MODULE_DESCRIPTION`, `MODULE_AUTHOR "Alec <like@awinic.com>"` |
| Driver version string | `V1.0.0` | `.rodata.str1.1+0x178`, printed by `probe` |
| Bus | I²C, 7-bit address `0x63` | `aw36518@63` node, `reg = <0x63>` |
| I²C controller | `i2c@11e03000` (`mediatek,mt6989-i2c`), runtime adapter **8** → device `8-0063` | merged DTB + live `/sys/bus/i2c` snapshot |
| Register access | regmap-i2c, 8-bit address / 8-bit data, `max_register = 0xFF` | `aw36518_regmap` |
| Channels driven | exactly **one** (`aw36518_LED0`); every register path is gated by `if (led_no) return 0;` | `aw36518_torch_brt_ctrl` 0xf18, inlined `enable_ctrl` |
| Sub-device name | `aw36518-led0` (ABI, matched by flashlight core) | `.rodata.str1.1+0x33e`; `fl_enable()` in `flashlight.ko` |
| Sibling part on the same phone | `aw36518_v2` at `12-0063` (`i2c@11d72000`), plus `aw36515` (dual-channel) at another bus | DTB nodes, sibling modules |
| GPIO | one optional output, DT property `flash-externel`, label `flash_externel`, kept in `flash->flash_externel_gpio` | `of_get_named_gpio_flags` + `devm_gpio_request_one` at `probe+0x160…0x198` |
| IRQ | none — no `request_irq`/`devm_request_*irq` import | `phase4-aw36518-imports.tsv` |
| Regulators / clocks / pinctrl | none — no regulator or clk imports; `pinctrl/consumer.h` is included by the source family but unused | imports table |
| Thermal | registers a cooling device `flashlight_cooler` (`#cooling-cells = <2>` in DT) | `thermal_of_cooling_device_register` at `probe+0x51c` |
| Power management | runtime PM (`pm_runtime_enable`, `__pm_runtime_resume/idle` from V4L2 open/close) + system sleep via `pm_runtime_force_suspend/resume` | `aw36518_pm_ops` |

## Chip identification path

`probe` performs, in this exact order, after the flashlight and thermal
registrations:

1. `regmap_read(regmap, 0x00, &val)` → logged as `read chip id:%d`.
   **The value is never compared against anything**: there is no chip-ID gate,
   no `-ENODEV` path, and probe cannot fail because of it.
2. `pr` version banner `V1.0.0 aw36518_probe:986`.
3. `regmap_read(regmap, 0x07, &val)`; if it returns < 0, probe returns 0
   immediately (no reset, no error propagation).
4. `msleep(10)`.
5. `printk("… do software reset0 reg0x07=0x%02x")`, `val |= 0x80`,
   `printk("… do software reset1 write data:0x%02x to reg 0x07")`,
   `regmap_write(regmap, 0x07, val)`.

So the only hardware handshake in probe is a read of register 0x00 (logged
only) and a read-modify-write of bit 7 of register 0x07 (software reset).

## GPIO ("flash-externel") behaviour

| Site | Action |
|---|---|
| `probe` (inlined `aw36518_gpio_init`) | `of_get_named_gpio(np, "flash-externel", 0)`; if > 0 and `gpio_is_valid()`, `devm_gpio_request_one(dev, gpio, GPIOF_OUT_INIT_LOW, "flash_externel")`; failures return `-1` / the errno and abort probe. Always logs `wl2864c_i2c_probe vin1_enable_gpio:%d...` (vendor copy/paste label). |
| `aw36518_init` | drives the pin **low** before the register init sequence |
| `V4L2_CID_FLASH_STROBE` | drives the pin **high** after mode+enable, i.e. this is the external strobe/enable line |
| `aw36518_uninit` (last `flashlight_set_driver(0)`) and `aw36518_strobe_store` tail | drives the pin **low** |
| `aw36518_suspend` | drives the pin **low** |

The write is always `gpiod_set_raw_value(gpio_to_desc(gpio), state)`, i.e. raw
(polarity-agnostic) access.

On this board the `aw36518@63` node carries **no** `flash-externel` property
(only the `aw36515@63` node has `flash-externel = <0x89 0x74 0x00>`), so at
runtime the field stays 0 and the driver toggles GPIO 0 through
`gpio_to_desc(0)`.  That is stock behaviour and is reproduced exactly; it is a
vendor quirk, not a reconstruction artefact.

## Camera / sensor relationship

* The module registers a V4L2 sub-device (`MEDIA_ENT_F_FLASH`,
  `V4L2_SUBDEV_FL_HAS_DEVNODE`) named `aw36518-led0` and, in parallel, a
  MediaTek flashlight device through `flashlight_dev_register_by_device_id()`.
* `aw36518_subdev_init` walks the `flash` child nodes and only binds
  `sd->fwnode` when a child's `reg` equals the LED index (0).  The GQ5012BF1
  `aw36518@63/flash@0` node has `reg = <0x02>`, so **no fwnode is attached** and
  the sub-device is not linked into the composite media graph — unlike
  `aw36515@63`, whose children carry `port@0/port@1` endpoints wired to
  `mtk-composite-v4l2-1`.  Consequently the AW36518 path is reached through the
  MediaTek flashlight character device, not through V4L2 media links.

## Safety-relevant summary

* One LED channel; flash and torch share register 0x01 mode bits.
* Timeout is programmed to 400 ms at every driver init and can be changed only
  through `V4L2_CID_FLASH_TIMEOUT` (step 40 ms, register 0x08 bits 3:0).
* Current is programmed as a linear register code (see
  `phase4-aw36518-electrical-contract.md`); the thermal cooling device can only
  ever *lower* the torch current.
