# Rear display ↔ rear touch coupling

## Why `spi_tiny_co5300_lcd` depends on `hynitron`

`depends=yft_devinfo,hynitron` exists because the display module imports two
Hynitron exports. **The display module owns the rear-touch power and wake
sequencing.** Hynitron has no PM callbacks, display notifier, `fb`/DRM notifier
or panel link of its own. Its `hyn_suspend`/`hyn_resume` logic exists only
inlined inside the exported `tiny_tp_power_contorl()`.

There is nothing in the reverse direction: Hynitron imports nothing from the
display module. Neither module shares GPIOs, regulators or orientation data
with the other.

## Cross-module symbol map

| symbol | provider | consumer | CRC | KCFI | meaning |
|---|---|---|---|---|---|
| `tiny_tp_power_contorl(int)` | hynitron | spi_tiny_co5300_lcd | `0xfcc94fc7` | `0x019c0cac` | rear-touch suspend (0) / resume (≠0) |
| `tiny_tp_gesture_contorl(int)` | hynitron | spi_tiny_co5300_lcd | `0x4e4b7919` | `0x019c0cac` | arm (≠0) / disarm (0) wake-gesture mode for the next suspend |
| `yft_tinylcd_device_add(struct spi_driver*, int)` | yft_devinfo | spi_tiny_co5300_lcd | `0x9c6d85d0` | n/a | registry entry at module init (used = 0) |
| `yft_set_tinylcd_device_used(char*, int)` | yft_devinfo | spi_tiny_co5300_lcd | `0x25e94db4` | n/a | marks `spi_tiny_lcd_co5300` used after a good probe |
| `yft_touchpanel_device_add` etc. | yft_devinfo | hynitron | (see hynitron parity) | n/a | rear-touch registry (separate from TinyLCD) |

## Call sites in the display module (byte-exact)

| caller (CO5300) | sequence |
|---|---|
| ioctl `POWER_ENABLE` 0x6b37 | panel resume (or AOD→normal), **then** `tiny_tp_power_contorl(1)` |
| ioctl `POWER_DISABLE` 0x6b38 | `tiny_tp_power_contorl(0)` **first**, then panel suspend |
| ioctl `POWER_AOD` 0x6b40 | `tiny_tp_power_contorl(0)`, 10 ms, `frame_send_end = 0` (panel stays on) |
| ioctl `TP_GESTURE_ENABLE` 0x6b3e | `tiny_tp_gesture_contorl(1)`; if not (`power_on == 1 && frame_send_end`): `tiny_tp_power_contorl(1)` then `(0)` ("force tp reset"), re-entering suspend in gesture mode |
| ioctl `TP_GESTURE_DISABLE` 0x6b3f | `tiny_tp_gesture_contorl(0)` |
| sysfs `tiny_lcd_tp_control` | `tiny_tp_power_contorl(value != 0)` |

## Provider semantics (stock `hynitron.ko`, disassembled)

`tiny_tp_gesture_contorl(en)` logs `en !!!`/`disen !!!` and sets the global
`tiny_tpgesture_status` to 1 or 0. If the device is absent it logs "data
pointor is null" and does nothing.

`tiny_tp_power_contorl(0)` (inlined `hyn_suspend`) proceeds only if not
already suspended:

1. `suspended = 1`.
2. `hyn_reset_proc(10)`.
3. If `tiny_tpgesture_status == 1`, `hyn_gesture_suspend()` (wake-gesture
   mode, IRQ kept armed). Otherwise `disable_irq_nosync()` once and
   `hyn_enter_deep_sleep()`.

`tiny_tp_power_contorl(≠0)` (inlined `hyn_resume`) proceeds only if suspended:

1. `suspended = 0`.
2. `hyn_reset_proc(40)`.
3. `hyn_release_all_finger()`, which reports `BTN_TOUCH 0`, `SYN_MT_REPORT`
   and `SYN_REPORT`.
4. Clear the gesture-active flag.
5. If gesture mode is set, `hyn_gesture_resume()`. Otherwise re-enable the IRQ
   if it was disabled.

## Lifecycle as seen from the rear screen

1. **Rear screen on.** HAL `set_power(1)` → `POWER_ENABLE`: the panel powers
   up and re-inits, then touch resumes.
2. **Rear screen off.** `set_power(0)` → `POWER_DISABLE`: touch suspends (deep
   sleep or gesture), then the panel goes down.
3. **AOD.** `POWER_AOD`: touch is suspended while the panel stays lit, and
   frames are pushed immediately rather than TE-paced.
4. **Wake gesture.** `start_gesture(1)` → `TP_GESTURE_ENABLE`: gesture mode is
   armed. If the panel is not in normal-on state, touch is cycled so it
   re-suspends into gesture mode.

The touch IRQ and gesture key reporting are entirely Hynitron's. The framework
consumes the `hyn_ts` input device and maps it onto the mini-screen display.
