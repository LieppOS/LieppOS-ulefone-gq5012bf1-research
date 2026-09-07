# Phase 4 — `leds_rgb_aw2013` hardware contract (GQ5012BF1 / Armor 29 Pro Thermal)

Everything below is recovered from the stock binary plus the stock device tree
plus read-only stock userspace/init/sepolicy.  Nothing is inferred from the chip
name alone.

## 1. Device identity

| item | value | evidence |
| --- | --- | --- |
| chip | Awinic AW2013, 3-channel constant-current RGB LED driver | chip-ID register `0x00` must read `0x33`, `.text+0x758 cmp w2,#0x33` |
| bus | I2C bus 11, controller `i2c@11d71000` (`mediatek,mt6989-i2c`) | live `/sys/bus/i2c/devices/11-0045` |
| address | 0x45 (7-bit) | DT `reg = <0x45>`, live `11-0045` |
| regmap | 8-bit register, 8-bit value, `max_register = 0x77` | `aw2013_regmap_config` at `.rodata+0x190`, bytes byte-identical to upstream |
| driver name | `leds-rgb-aw2013` | `.data+0x38` → `.rodata.str1.1+0xba` |
| module | `leds_rgb_aw2013`, vendor_boot ramdisk, `modules.load` line 179 | see stock oracle |

## 2. Power / enable path — **GPIO, not a regulator**

Upstream `leds-aw2013.c` powers the chip from a `vcc` regulator
(`devm_regulator_get` / `regulator_enable` / `regulator_disable`).  **The stock
GQ5012BF1 module imports none of those symbols.**  Instead:

```
of_get_named_gpio(np, "aw2013-pwd-gpio", 0)   -> GPIO 188 (mt6878 pinctrl)
gpio_to_desc(188)                             -> must be non-NULL
gpio_is_valid(188)                            -> informational printk only
gpio_request(188, "aw2013-pwd-gpio")
gpio_direction_output(188, 1)                 -> chip enabled (active high)
gpio_get_value(188)                           -> logged
   ... probe then repeats:
gpio_get_value(188)                           -> logged as "aw2013_probe -1"
gpio_direction_output(188, 1)                 -> re-asserted, return ignored
gpio_get_value(188)                           -> logged as "aw2013_probe -2"
```

Consequences that matter for a replacement kernel:

* the PWD/enable line is **latched high in probe and never lowered** — there is
  no `gpio_free()`, no release on `remove`, no PM callback that touches it;
* the GPIO is requested with the same string used for the DT property;
* on any GPIO failure the driver sets the global `aw2013_pwd_gpio = -1`, prints
  `" yft_parse_dts get gpio fail. aw2013_pwd_gpio"` and fails probe with
  **`-ENODEV`** (`.text+0x970 mov w27,#-0x13`).

Regulator/rail conclusion: **no regulator is consumed by this driver.**  Any
LDO feeding the AW2013 on this board is either always-on or owned elsewhere.

## 3. Channel map and electrical limits

| channel | DT node | `reg` | colour | `led-max-microamp` | `imax` code | full-scale current | `led-fixed-brightness` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | `aw@0` | 0 | red | 5000 µA | 1 | 5 mA | 64 (0x40) |
| 1 | `aw@1` | 1 | green | 5000 µA | 1 | 5 mA | 64 (0x40) |
| 2 | `aw@2` | 2 | blue | 5000 µA | 1 | 5 mA | 128 (0x80) |

`imax = min_t(u32, microamp / 5000, 3)` and is written into
`LCFG[n][1:0]` (mask `0x03`).  AW2013 `IMAX` encoding is 0 = 0 mA-ish/lowest,
1 = 5 mA, 2 = 10 mA, 3 = 15 mA; all three channels therefore run at the **5 mA**
step.  This is an indicator-class current, not an illumination-class current.

## 4. Brightness semantics — the Ulefone override

The single most important behavioural delta from upstream:

```c
num = led->num;
if (brightness)                       /* any non-zero request */
        brightness = led->fixed_brightness;   /* <-- clamp to the DT value */
regmap_write(regmap, AW2013_REG_PWM(num), brightness);
```

(`.text+0x254 cbz w20, …` / `.text+0x258 ldr w20,[cdev+0x1b0]`)

So the driver is effectively **binary per channel**:

* userspace writing *any* value 1…255 to `/sys/class/leds/red/brightness`
  results in PWM register `0x34` being programmed with **64**, not with the
  requested value;
* writing 0 turns the channel off (PWM = 0, `LCTR` bit cleared, `LCFG.MD`
  cleared).

`max_brightness` is left at the LED-class default 255, so userspace still sees a
0…255 range; only the *effect* is quantised.  Colour mixing is therefore limited
to the 7 non-black combinations of (red 64, green 64, blue 128).

## 5. Chip enable/disable policy

The chip is only powered up (register-wise) while at least one channel has a
non-zero `cdev.brightness`:

* `aw2013_chip_in_use()` scans `leds[0..num_leds-1].cdev.brightness`;
* if in use and `!chip->enabled` → `chip->enabled = true`, `GCR = 0x01`, then
  re-program every channel's `LCFG` IMAX;
* if no longer in use → `GCR = 0x00`, `chip->enabled = false`.

Note the Ulefone build sets `chip->enabled = true` **before** the `GCR` write
(`.text+0x324 strb w8,[x22,#0x584]` precedes `.text+0x328 bl regmap_write`), and
`aw2013_chip_disable()` no longer has a regulator step, so it cannot fail.

## 6. Blink / breathing

Hardware blink is used (the LED-class `timer` trigger calls `blink_set`).  The
math is byte-for-byte upstream:

```
off = min(5, ilog2((*delay_off - 1) / 130) + 1)   -> LEDT1(n) = T4
on  = min(7, ilog2((*delay_on  - 1) / 130) + 1)   -> LEDT0(n) = T2
*delay_off = BIT(off) * 130 ms
*delay_on  = BIT(on)  * 130 ms
```

* time step **130 ms**; achievable on-times 130·2^0…130·2^7 (130 ms…16.64 s),
  off-times 130·2^0…130·2^5 (130 ms…4.16 s);
* both delays zero → defaults to 500/500 ms (1 Hz) before quantisation;
* `delay_on == 0` → LED forced off via `brightness_set(0)`;
* `delay_off == 0` → `LCFG.MD` cleared (steady on, blinking disabled);
* rise/fall (`LCFG.FI`/`FO`, `LEDT0.T1`, `LEDT1.T3`, `LEDT2`) are **never
  written** — there is no breathing-ramp programming in this driver, so
  "breathing" in the UI is produced by fade-free hardware blinking only.

## 7. Reset / init sequence (exact order from `aw2013_probe`)

1. `devm_kzalloc(&client->dev, 0x588, GFP_KERNEL|__GFP_ZERO)` — `sizeof(struct aw2013)` is **1416**.
2. `yft_aw2013_parse_dts()` — GPIO 188 requested and driven high (see §2).
3. Two extra `gpio_get_value` / `gpio_direction_output(1)` / `gpio_get_value`
   rounds with the `"aw2013_probe -1"` / `"aw2013_probe -2"` printks.
4. `mutex_init(&chip->mutex)` (lockdep name `"&chip->mutex"`), then `mutex_lock`.
5. `chip->client = client`, `i2c_set_clientdata(client, chip)`.
6. `devm_regmap_init_i2c(client, &aw2013_regmap_config)`.
7. `regmap_read(RSTR /*0x00*/)` → must equal **0x33**, else `-ENODEV`.
8. `aw2013_probe_dt()`:
   * count available children, require `1 <= count <= 3`, else `-EINVAL`;
   * **`regmap_write(RSTR, 0x55)` — software reset** (this is the only reset);
   * per child: parse `reg`, `led-max-microamp`, `led-fixed-brightness`;
     install `brightness_set_blocking` and `blink_set`; `devm_led_classdev_register_ext`.
   * `chip->num_leds = i`.
9. `mutex_unlock(&chip->mutex)`.
10. `gftk_leds = chip` (module-global publication).
11. `led_aw2103_control()` — the charging indicator (see §8).

Nothing is written to `GCR` or any channel register during probe: after the
`0x55` reset the chip is left disabled and dark, matching `default-state = "off"`.

## 8. What this LED physically is on the Armor 29 Pro Thermal

**It is the front notification / charging indicator RGB LED.**  Four independent
lines of evidence, none of which is "it is an AW2013 so it must be":

1. **Userspace role.**  Its three LED class devices are named `red`, `green`,
   `blue`, and the MediaTek Lights HAL binary
   `/vendor/bin/hw/android.hardware.lights-service.mediatek` opens exactly
   `/sys/class/leds/{red,green,blue}/{brightness,delay_on,delay_off,trigger}`
   and implements `blink_red/blink_green/blink_blue(level, onMS, offMS)`.  That
   is the Android notification/battery/attention light path.
2. **Charging behaviour built into the driver.**  `led_aw2103_control()` runs at
   the end of probe, reads the MediaTek boot mode from `/chosen` `atag,boot`,
   and *only* acts when boot mode is 8 (`KERNEL_POWER_OFF_CHARGING_BOOT`) or 9
   (`LOW_POWER_OFF_CHARGING_BOOT`).  It then queries the `3rd-gauge` power
   supply for `POWER_SUPPLY_PROP_CAPACITY` and lights one channel:

   | battery capacity | channel lit | colour |
   | --- | --- | --- |
   | ≥ 90 % | `leds[1]` | **green** |
   | ≤ 15 % | `leds[0]` | **red** |
   | 16…89 % | `leds[2]` | **blue** |

   This is a textbook off-mode-charging battery indicator; a decorative or
   camera light would not be wired to fuel-gauge capacity.
3. **It is not the decorative/rear light.**  Ulefone's decorative "marquee" /
   "dgled" lights are AW22xxx parts (`aw22xxx_led` sysfs, `yft_marquee_file` /
   `yft_dgled_device` sepolicy labels).  No `aw22*` device is bound on this
   device (`buses.txt` contains no AW22xxx), and no AW22xxx module ships in
   `vendor_dlkm` or the ramdisk — those sepolicy rules are carry-over from other
   Ulefone models.
4. **It is not camera/flash related.**  Camera flash on this board is
   `aw36515` / `aw36518` / `aw36518_v2` on I2C bus 6 @0x63 behind
   `flashlight.ko`; the camping light is `soc:gftk_camplight`; the night-vision
   light is `flashlight_core`.  All are separate, already-reconstructed drivers.

Additionally, `red`/`green`/`blue` LED class devices exist **only** here: the
only other LED providers on the device are `mtk-leds` (`lcd-backlight` only,
`compatible = "mediatek,disp-leds"`), `leds-mtk*.ko`, `leds-ln2403.ko`
(backlight) and `aw_vibrator` (haptics).

## 9. Runtime resources the driver does *not* use

Explicitly checked and absent from the stock binary:

* **no workqueue, no timer, no delayed work, no threaded IRQ, no IRQ at all**
  (no `INIT_WORK`, `queue_work`, `timer_setup`, `request_*irq` imports);
* **no suspend/resume/PM ops** — `aw2013_driver.driver.pm` is a zero field in
  `.data`, `.shutdown` is NULL;
* **no custom sysfs attributes** — no `device_create_file`, no `attribute_group`;
  every sysfs node comes from the LED class core;
* **no debugfs, no procfs, no misc device, no chrdev**;
* **no regulator, no clock, no pinctrl-state switching**;
* **no exported symbols** (no `__ksymtab` section), `depends=` empty;
* **no module parameters**.

Teardown is minimal: `aw2013_remove()` only calls the inlined
`aw2013_chip_disable()` (writes `GCR = 0` if enabled).  The LED class devices are
released by devm; the mutex is **not** destroyed and the enable GPIO is **not**
freed — reproduced faithfully.
