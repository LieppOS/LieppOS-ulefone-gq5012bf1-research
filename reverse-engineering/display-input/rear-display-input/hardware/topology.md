# Rear display + rear touch hardware topology (GQ5012BF1)

Sources: stock merged DT and live-tree snapshot (earlier phase-4 DT contracts),
stock module disassembly, stock HAL strings. Generic CO5300 or Hynitron
datasheet values are not used.

```text
MT6878 SoC
├─ SPI (MT6989-IP, regs 0x11010000), CS0, mode 3, 8 bpw
│   └─ "hxytech, spi_tiny_lcd"  → spi_tiny_co5300_lcd
│        CO5300-class AMOLED DDIC with GRAM, 340×340 RGB565 (ID 0xDA=0x33, 0xDB=0x11|0x10)
│        reset GPIO154 · 1V8-en GPIO118 · 2V8-en GPIO29 · D/C GPIO190
│        TE GPIO31 → falling-edge IRQ "tiny_lcd_te" · bl_ctrl GPIO (requested low, unused)
│        IIO "tiny_lcd_adc" (panel-ID resistor, 451..999 mV)
│        pinctrl stl_spi1_{mo,mi,clk,cs}_as_{spi1_*,gpio} (SPI pins parked as GPIO when off)
└─ I2C0 (i2c@11c20000), 400 kHz, 7-bit 0x15
    └─ "hynitron,hyn_ts" → Hynitron CST820 (chip type 0xb7, CST8xx self-cap line) → hynitron.ko
         IRQ GPIO11 (EINT 11, falling; live Linux IRQ 56) · reset GPIO32 · VDD-en GPIO119
         max-touch-number 1 · display-coords 340×340 · input "hyn_ts" (MT protocol A)
```

| property | CO5300 rear panel | Hynitron rear touch |
|---|---|---|
| bus | SPI CS0, 52 MHz writes / 1 MHz reads (DT max 60 MHz) | I2C0 @0x11c20000, 400 kHz, 7-bit 0x15 |
| interrupt | TE, falling edge, frame pacing | touch IRQ, gesture-wake capable |
| power | two GPIO-switched rails (1V8 then 2V8), active-high | VDD enable GPIO119 (driven high at probe) |
| reset | GPIO154, high 15 ms → low 30 ms → high, 120 ms settle | GPIO32 via `hyn_reset_proc(ms)` (10 ms on suspend, 40 ms on resume/probe) |
| geometry | 340×340 (alternate 320×320 at offset 10,10) | 0..340 × 0..340 (`hynitron,display-coords = <340 340>`), 1 contact |
| backlight | controller-side DCS 0x51 only | n/a |
| orientation | no MADCTL; power-on default + vendor pages | no swap/invert/rotation properties in DT; driver flags `x_overturn`/`y_overturn`/`xy_exchange` default off |
| owner of power sequencing | spi_tiny_co5300_lcd | spi_tiny_co5300_lcd (via exports) |

The physical mounting orientation is not statically encoded anywhere in the
kernel modules. No rotation is applied in kernel space; any rotation belongs to
the framework's mini-screen display.
