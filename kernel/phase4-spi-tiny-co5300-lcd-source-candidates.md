# CO5300 / tiny rear display source candidates

## Result

`NO_PUBLIC_DONOR_FOUND`; project classification remains **NO_USEFUL_SOURCE**.
The stock object is a YFT/Ulefone SPI misc driver despite its filename: its
metadata says `SSD1317` and its probe accepts controller ID command responses
`DA=0x33`, `DB=0x10/0x11`. Public CO5300 drivers are therefore not provenance
for this implementation.

## Bounded exact-identifier search

The following identifiers were searched verbatim locally, with GitHub/web and
`grep.app`: `spi_tiny_co5300_lcd`, `spi-tiny-co5300-lcd`, `spi_tiny_lcd`,
`hxytech, spi_tiny_lcd`, `hxytech,_spi_tiny_lcd`, `tiny_lcd_miscdev`,
`TINY_LCM_IOC_POWER_AOD`, `TINY_LCM_IOC_TP_GESTURE_ENABLE`,
`yft_tinylcd_device_add`, `yft_set_tinylcd_device_used`,
`tiny_tp_gesture_contorl`, `tiny_tp_power_contorl`, `tiny_lcd_get_sensor_id`,
`spi_lcd_change_backlight`, `QG-9696TSWXG04`, `SSD1317`, and `CO5300`.
NothingOSS, MediaTek BSP mirrors, Motorola, MiCode, OnePlus, OPPO/realme,
Transsion, Sony, Ulefone/YFT mirrors, GitHub and Gitee were included in the
bounded search. No exact driver source or ioctl header was found.

| Candidate | Classification | Evidence |
|---|---|---|
| Espressif `esp_lcd_co5300` | `SAME_CONTROLLER_DIFFERENT_BOARD` only for filename-level CO5300 research | Different controller protocol, resolution and framework; no SSD1317/YFT/misc/ioctl identifiers. |
| Zephyr `display_co5300.c` | `SAME_CONTROLLER_DIFFERENT_BOARD` | Generic CO5300 display API; no stock identifiers or command/UAPI match. |
| Infineon CO5300 middleware | `SAME_CONTROLLER_DIFFERENT_BOARD` | Non-Linux generic implementation and different panel topology. |
| Public SSD1317/u8g2-style drivers and SSD1317 datasheet material | `STRUCTURAL_DONOR_ONLY` | Confirms SSD1317 command-family meanings but not the 44-entry stock table, MTK pinctrl/GPIO sequence, misc UAPI or YFT/Hynitron edges. |
| Stock ELF + stock 32/64-bit TinyLCD HAL | clean-room authority | Only artifacts matching all unique identifiers and ioctl values. |

No classification upgrade is inferred from generic command-name overlap.
