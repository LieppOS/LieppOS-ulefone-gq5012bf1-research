# Phase 4 — `leds_rgb_aw2013` userspace / Lights HAL contract (GQ5012BF1)

## 1. LED class names — these are hard ABI

The driver passes `init_data.fwnode = of_fwnode_handle(child)` to
`devm_led_classdev_register_ext()`.  Each child carries `label = "red"` /
`"green"` / `"blue"`, so the LED core names the class devices:

```
/sys/class/leds/red      <- aw@0, reg = 0
/sys/class/leds/green    <- aw@1, reg = 1
/sys/class/leds/blue     <- aw@2, reg = 2
```

physically at
`/sys/devices/platform/soc/11d71000.i2c/i2c-11/11-0045/leds/{red,green,blue}`.

These three names are **the only** `red`/`green`/`blue` LED class devices on the
device: the only other LED providers are `mtk-leds`
(`compatible = "mediatek,disp-leds"`, single child `label = "lcd-backlight"`),
`leds-ln2403.ko`, `leds-mtk*.ko` and the `aw_vibrator` haptic class device.
Renaming them would silently break every consumer listed below.

## 2. Sysfs surface actually used

All attributes come from the LED class core — the driver creates **no** custom
sysfs files (no `device_create_file`, no `attribute_group` in the binary).

| attribute | provider | used by |
| --- | --- | --- |
| `brightness` | LED core → `brightness_set_blocking` = `aw2013_brightness_set` | Lights HAL, FactoryMode, init |
| `max_brightness` | LED core (255) | Lights HAL |
| `trigger` | LED core (`CONFIG_LEDS_TRIGGERS`) | Lights HAL writes `timer` / `none` |
| `delay_on`, `delay_off` | `ledtrig-timer`, which calls `blink_set` = `aw2013_blink_set` | Lights HAL |

## 3. Android Lights HAL relationship

`/vendor/etc/vintf/manifest/lights-mtk-default.xml`:

```xml
<hal format="aidl">
    <name>android.hardware.light</name>
    <version>2</version>
    <fqname>ILights/default</fqname>
</hal>
```

`/vendor/etc/init/lights-mtk-default.rc`:

```
service vendor.light-default /vendor/bin/hw/android.hardware.lights-service.mediatek
    class hal
    user system
    group system
    shutdown critical
```

started from `init.mt6878.rc` immediately after the `red/green/blue` `chown`s.

Strings extracted from that binary (read-only):

```
/sys/class/leds/red/brightness      /sys/class/leds/red/trigger
/sys/class/leds/red/delay_on        /sys/class/leds/red/delay_off
/sys/class/leds/green/brightness    /sys/class/leds/green/trigger
/sys/class/leds/green/delay_on      /sys/class/leds/green/delay_off
/sys/class/leds/blue/brightness     /sys/class/leds/blue/trigger
/sys/class/leds/blue/delay_on       /sys/class/leds/blue/delay_off
timer            none
blink_red        blink_green        blink_blue
"blink_red, level=%d, onMS=%d, offMS=%d"
"RED_DELAY_OFF_FILE doesn't exist or cannot write!!"
"GREEN_DELAY_OFF_FILE doesn't exist or cannot write!!"
"BLUE_DELAY_OFF_FILE doesn't exist or cannot write!!"
```

This is the stock MediaTek `lights` implementation: for a blinking request it
writes `trigger=timer`, then `delay_on`/`delay_off`, then `brightness`; for a
steady request it writes `trigger=none` and `brightness`.  The HAL logs an error
if the `delay_off` node is missing — i.e. **the HAL requires `blink_set` to be
implemented** (otherwise the timer trigger would not create `delay_*`).  The
reconstruction keeps `led->cdev.blink_set = aw2013_blink_set`, so `delay_on` /
`delay_off` exist.

`system_server`'s `LightsService` talks only to this HAL; it never touches sysfs
directly.  The HAL is what maps `LightType::NOTIFICATIONS`, `BATTERY` and
`ATTENTION` onto the three colour channels.

## 4. init / ueventd ownership and permissions

`/vendor/etc/init/hw/init.mt6878.rc`:

```
chown system system /sys/class/leds/red/brightness      (line 108)
chown system system /sys/class/leds/green/brightness    (line 109)
chown system system /sys/class/leds/blue/brightness     (line 110)
...
chown system system /sys/class/leds/red/trigger         (line 804)
chown system system /sys/class/leds/green/trigger       (line 805)
chown system system /sys/class/leds/blue/trigger        (line 806)
```

`/vendor/etc/init/hw/init.yft.rc` (Ulefone/YFT-specific, lines 28-33):

```
chmod 0666 /sys/class/leds/red/brightness
chown system system /sys/class/leds/red/brightness
chmod 0666 /sys/class/leds/green/brightness
chown system system /sys/class/leds/green/brightness
chmod 0666 /sys/class/leds/blue/brightness
chown system system /sys/class/leds/blue/brightness
```

Note `0666` — Ulefone deliberately opens these world-writable, which is what
lets the factory-test app drive them without the HAL.

`/vendor/etc/ueventd.rc` (lines 257-280) additionally grants `system:system 0664`
on `delay_on`, `delay_off` and on `tr1 tr2 tf1 tf2 ton toff` for all three
colours.  **`tr1/tr2/tf1/tf2/ton/toff` do not exist on this driver** — they are
the MediaTek `leds-mt65xx` breathing attributes and are dead rules here; the
same file also references a non-existent `/sys/devices/platform/leds-mt65xx/`
tree.  They are harmless leftovers and must not be taken as a requirement.

`/system/etc/init/hw/init.rc` lines 1200-1205 additionally chown
`red/device/grpfreq`, `red/device/grppwm`, `red/device/blink` — again legacy
`leds-mt65xx` nodes that do not exist with this driver.

## 5. Direct sysfs consumers (bypassing the HAL)

| consumer | paths |
| --- | --- |
| `/system/app/FactoryMode/FactoryMode.apk` (Ulefone factory test) | `/sys/class/leds/red/brightness`, `/sys/class/leds/green/brightness`, `/sys/class/leds/blue/brightness` |
| `vendor/bin/factory`, `vendor/bin/meta_tst` | `/sys/class/leds/...` (factory/META mode) |

FactoryMode writes raw brightness values.  Because of the
`led-fixed-brightness` clamp (see hardware contract §4) any non-zero value it
writes produces the same physical output — a red/green LED at PWM 64, blue at
PWM 128.  A replacement driver that honoured the requested brightness instead
would *not* break the apps but would change the observable light level, so the
clamp is reproduced exactly.

## 6. SELinux

`vendor_file_contexts` contains **no** rule for
`/sys/devices/platform/soc/11d71000.i2c/i2c-11/11-0045/...` — the LED nodes fall
through to the generic `sysfs` label, and access is governed by the DAC
permissions set in `init.yft.rc` / `ueventd.rc`.  Nothing in sepolicy therefore
pins the driver's device path, only the class names matter.

## 7. Kernel-side ABI summary

| ABI item | value | must not change |
| --- | --- | --- |
| module name | `leds_rgb_aw2013` | `modules.load` line 179, `modules.alias` |
| OF alias | `of:N*T*Cawinic,rgb,aw2013`, `…C*` | `modules.alias` 1289-1290 |
| i2c driver name | `leds-rgb-aw2013` | `/sys/bus/i2c/drivers/leds-rgb-aw2013` |
| LED class names | `red`, `green`, `blue` | Lights HAL, init.mt6878.rc, init.yft.rc, ueventd.rc, FactoryMode |
| `blink_set` present | yes | HAL requires `delay_on`/`delay_off` |
| exported symbols | none | nothing depends on this module |
| `.modinfo depends` | empty | `modules.dep` line 188 is `…/leds-rgb-aw2013.ko:` with nothing after the colon |

All of the above are reproduced byte-identically by the reconstruction
(`.rodata`, `.rodata.str1.1`, `.data` and the `.modinfo` name/alias/depends
records are byte-for-byte equal to stock).
