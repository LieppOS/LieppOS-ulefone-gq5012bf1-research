# YFT/Ulefone deltas: rear display + rear touch

There is no public donor for the CO5300 module. "Donor behavior" below means
the generic idiom the code is built from: Linux `spidev.c`, the MediaTek panel
`push_table`/`log_store` helpers, and the Hynitron reference driver. Confidence
is **proven** wherever the stock bytes are reproduced.

| # | area | generic/donor behavior | GQ5012BF1 stock behavior | evidence | reconstruction | confidence |
|---|---|---|---|---|---|---|
| 1 | display↔touch coupling | touch drivers own their PM via notifiers | Hynitron exports `tiny_tp_power_contorl`/`tiny_tp_gesture_contorl`; the TinyLCD ioctls drive them; Hynitron has no notifier | CO5300 relocs + Hynitron disasm | `../integration.md`; CO5300 source | proven |
| 2 | rear panel transport | spidev char device | spidev sync helpers (`spidev_sync*`) wrapped with a D/C GPIO, a `vmalloc` copy per transfer, mode 3, 52 MHz / 1 MHz | byte-identical write_cmd/write_data/read_data | CO5300 source | proven |
| 3 | panel init | MediaTek `push_table(LCM_setting_table)` | 44-record CO5300 table, page-unlock sequence, `3A 55`, `35 00`, `53 20`, `63 FF`, sleep-out/display-on 60 ms | identical power_enable_func/probe | `init_setting.inc` | proven (bytes); generic meanings inferred |
| 4 | panel ID gate | none | `DA==0x33` + ADC 451..999 mV; `DB` selects `tiny_lcm_number` 1/2 | probe disasm | source | proven |
| 5 | GPIO setup | FocalTech `fts_gpio_configure` request/direction/unwind idiom | six GPIOs with `tl_*`/`*_ctrl_gpio` labels, all outputs low; result ignored by probe | stl_parse_dt inlined bytes | source | proven |
| 6 | SPI pin parking | none | four pinctrl pairs; SPI pins become GPIO on suspend and SPI on resume | probe/power bytes | source | proven |
| 7 | frame path | fbdev/DRM | misc ioctl, `gImage_logo` 340×340 RGB565, TE-paced delayed work or immediate (AOD); width 320 window | ioctl/te_work bytes | source | proven |
| 8 | backlight | GPIO/PWM backlight | DCS 0x51 lazily on next frame; BL_ENABLE/DISABLE only gate frame sending ("Ignore operation") | ioctl bytes | source | proven |
| 9 | AOD | n/a | `POWER_AOD`: touch off, panel stays on, frames sent immediately | ioctl bytes | source | proven |
| 10 | boot-mode gating | n/a | MediaTek `log_store` `get_boot_mode()`; modes 1/5/6/8/9 skip driver registration | init_module bytes | source | proven |
| 11 | YFT registry | n/a | `yft_tinylcd_device_add(drv, 0)` at init; `yft_set_tinylcd_device_used("spi_tiny_lcd_co5300", 1)` after probe | imports/CRCs | source | proven |
| 12 | metadata | SSD1317 96×96 OLED driver | description/alias left as SSD1317 (stale) | `.modinfo` | source | proven |
| 13 | rear-touch geometry | DT-driven | 340×340, 1 contact, protocol A; no transforms | DT + input contract | prior Hynitron contracts | proven |
| 14 | rear-touch chip config | multi-chip table | config chip type `0xb7` (CST820); CST816D-family image for 0xb7 | Hynitron data/disasm | prior recon (semantic) | proven (semantics) |
| 15 | userspace | n/a | `vendor.yft.hardware.tinylcd@1.0` HIDL + `tinylcd.default.so`; framework `MiniScreenDisplay`; `ro.yft_support_tinylcd=1` | strings/rc/vintf | `userspace/service-map.md` | proven (interfaces); app internals not claimed |

## Stock defects preserved (not fixed) by the reconstruction

- `buf_lock` is never initialized (zero `.bss` mutex).
- `vmalloc` failure in the 1-byte and frame writers continues into `memcpy(NULL, …)`.
- `spi_remove` leaks the IRQ, GPIOs, buffers, attributes and work.
- The 32-bit HAL ioctl encodings are not translated in `compat_ioctl`.
- `spidev_sync_read_data` transmits `{cmd, <next stack byte>}`.
- `stl_parse_dt` failures are ignored by probe.
