# CO5300 rear panel: power, reset and lifecycle (board-proven)

GPIOs come from DT and are resolved live: reset 154, 1V8 enable 118, 2V8 enable
29, DC 190, TE 31, plus `tiny_lcd,backlight_gpio`. The driver-internal names are
`g_data.1`=reset, `.2`=dc, `.3`=1V8, `.4`=2V8, `.5`=bl, `.6`=te.

## Probe (`spi_probe`)

1. Log the OF node name and `max_speed_hz`; set `g_data.spi`; allocate 4 KiB
   tx/rx buffers (tx failure → "kmalloc error"). Set mode 3 / 8 bpw.
2. `stl_parse_dt()` reads six GPIOs. In order (reset, 1V8, 2V8, DC, bl, TE) it
   requests `tl_reset_gpio`, `tl_en_1v8_gpio`, `tl_en_2v8_gpio`, `dc_ctrl_gpio`
   and `bl_ctrl_gpio`, each driven **low**, and `te_gpio` as an input. It then
   gets pinctrl and looks up eight states, selecting the four
   `stl_spi1_*_as_spi1_*` states. **Its return value is ignored**: probe
   continues even if GPIO or pinctrl setup failed.
3. Power-up: 5 ms, 1V8 high, 10 ms, 2V8 high, 10 ms, reset high, 15 ms, reset
   low, 30 ms, reset high, 120 ms.
4. ADC `tiny_lcd_adc` → mV; panel ID reads 0xDA/0xDB. Probe passes only if
   ID1 = 0x33 and the ADC is 451..999 mV.
5. Map the TE GPIO to an IRQ and request it falling-edge, as `tiny_lcd_te`.
6. Replay the 44-record init table, set `backlight_step = 255`, send the splash
   frame and log its duration, then wait 100 ms.
7. Init the TE delayed work; create five driver attributes (failure is only
   logged); register the misc device (failure is only logged).
8. Set `power_on = frame_send_enable = frame_send_end = 1`; call
   `yft_set_tinylcd_device_used("spi_tiny_lcd_co5300", 1)`; log
   `YFT_DEVICE  tinylcd = 1`.

## Suspend (`tiny_lcd_power_enable_func(0)`): ioctl POWER_DISABLE, sysfs 0

This runs only if `power_on == 1`:

1. TE IRQ `disable_irq()` once (tracked by `pre_irq_en`).
2. `backlight_step = current_backlight_level = 0`.
3. `28`, 20 ms, `10`, 220 ms.
4. Reset low, 20 ms, 2V8 low, 20 ms, 1V8 low, 20 ms.
5. SPI pins (MO/MI/CLK/CS) switch to their GPIO pinctrl states, and
   `power_on = 0`.

## Resume (`tiny_lcd_power_enable_func(≠0)`): ioctl POWER_ENABLE, sysfs ≠0

- If already `power_on == 1`, it only sets `frame_send_end = 1` and logs
  `aod 38`. This is the AOD → normal transition and does no re-init.
- Otherwise the SPI pinctrl states are selected, then: 20 ms, 1V8 high, 20 ms,
  2V8 high, 20 ms, reset high, 15 ms, low, 30 ms, high, 120 ms. The full init
  table follows, then `power_on = 1`, `frame_send_end = 1`, and the TE IRQ is
  re-enabled.

## AOD (`TINY_LCM_IOC_POWER_AOD`)

Rear touch is powered down (`tiny_tp_power_contorl(0)`), then
`tiny_lcd_aod_suspend()` runs, which only waits 10 ms. Finally
`frame_send_end = 0`, so subsequent frame writes go out immediately instead of
waiting for TE. **The panel stays powered.** The ioctl does not turn the panel
on.

## Backlight

`BL_ENABLE` and `BL_DISABLE` do **not** touch power or GPIOs.
`tiny_lcd_bl_enable_func()` only logs "Ignore operation". The ioctls toggle
`frame_send_enable`, and `BL_ENABLE` also sets the frame status to 1. Brightness
is purely controller-side (`51`) and is applied lazily on the next frame. The
sysfs `tiny_lcd_bl_enable` / `tiny_lcd_backlight_control` both just set
`backlight_step`.

## Remove / exit

`spi_remove` only deregisters the misc device. Attributes, IRQ, GPIOs, buffers
and work stay alive (stock leak). Module init calls
`yft_tinylcd_device_add(&driver, 0)` first, then the MediaTek `get_boot_mode()`
(`/chosen` → `/chosen@0` → `atag,boot`). Boot modes 1, 5, 6, 8 and 9 skip
`spi_register_driver` and return 0. A registration failure logs, calls
`driver_unregister` and returns the error.
