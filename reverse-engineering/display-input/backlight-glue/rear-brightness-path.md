# Rear display (CO5300) brightness path

```
MiniScreen app -> services VirtualDisplay -> ITinylcd HIDL -> tinylcd.default.so
  -> ioctl / sysfs tiny_lcd_backlight_control | tiny_lcd_bl_enable
  -> spi_tiny_co5300_lcd.ko: backlight_step = value
  -> next frame write: if (backlight_step != current_backlight_level) send DCS 0x51 <step & 0xff>, then 0x2C
```

(CO5300 closure, `../rear-display-input/co5300/protocol.md`)

## Backlight GPIO

- The driver reads `tiny_lcd,backlight_gpio` (`of_get_named_gpio`), requests it
  as `bl_ctrl_gpio` and drives it low only if `gpio_is_valid()`.
- **The live DT `tiny_lcd` node (spi0@11010000) has no
  `tiny_lcd,backlight_gpio` property.** It has `dc-ctrl-gpio` (190),
  `en-1v8-gpio` (118), `en-2v8-gpio` (29), `reset-gpio` (154) and `te_gpio` (31).
  So `bl_ctrl_gpio` is `-ENOENT`, the request is skipped, and no GPIO exists.
  This corrects "requested at probe but never used". In the source the request
  is dead code; on this board there is no backlight GPIO at all.

## Other controllers

- No other module references the CO5300 or a rear LED class device. No LED
  class device named `lcd-backlight1` exists, even though
  init.mt6878.rc/hwcomposer/lights HAL carry the generic MTK second-panel paths
  `/sys/class/leds/lcd-backlight1/*`.
- `hynitron.ko` exports only touch power/gesture control, not brightness.
- Rear brightness is therefore exclusively the CO5300 DCS 0x51 8-bit value,
  sent lazily in-band with frames. There is no PWM, LED class, thermal cooler
  or battery throttle.
