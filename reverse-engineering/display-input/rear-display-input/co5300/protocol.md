# CO5300 rear panel: SPI command protocol

Source of truth: shipped `vendor_dlkm/lib/modules/spi_tiny_co5300_lcd.ko`
(SHA-256 `39eecad8…9742`). The rebuild is byte-identical in every function that
touches this protocol. Full opcode list: `command-table.tsv`.

## Physical framing (board-proven)

- 4-wire SPI with separate D/C GPIO (GPIO 190). **DC low = command**, **DC high
  = parameter/pixel data**. DC is driven through `gpio_direction_output()` before
  every transfer.
- `spi->mode = SPI_MODE_3`, `bits_per_word = 8`. These are set directly on the
  `spi_device` in probe; `spi_setup()` is never called.
- Each transfer's `speed_hz` is 52 MHz for commands, parameters and pixels, and
  1 MHz for ID reads. The DT `spi-max-frequency` is 60 MHz.
- **Command**: one 1-byte `spi_transfer` (DC low).
- **Parameter**: one 1-byte `spi_transfer` per byte (DC high). There is no
  burst for multi-byte parameters.
- **Register read**: DC low, one 2-byte full-duplex transfer `{cmd, <stack byte>}`.
  The result is `rx[1]`. Stock TX byte 1 is whatever follows `cmd` on the stack
  (the tx pointer is `&cmd` with `len = 2`). This is harmless for 0xDA/0xDB.
- Every 1-byte write is copied into a fresh `vmalloc(1)` buffer and freed after
  the transfer. **Stock bug:** if `vmalloc` fails, it logs
  `vmalloc error! (spidev_sync_write,98) error=12` and then `memcpy`s into NULL.

## Initialization stream (probe and every resume)

The stream comes from `push_table(init_setting, 44)`, inlined into
`initial_co5300()`. It contains 44 records `{u32 cmd; u8 count; u8 params[23]}`.
`cmd == 0xFFFC` is a delay pseudo-record (`mdelay(count)`).

Sequence (generic meanings are inference, see `command-table.tsv`):

1. Manufacturer pages: `FE 20; F4 5A; F5 59`, which unlocks (inferred).
2. Vendor registers on pages 0x40/0x90/0x40/0x70/0xE0, replayed verbatim.
3. `FE 20; F4 A5; F5 A5` locks again; `FE 00` returns to the user page.
4. `C4 80` (SPI-mode control), `3A 55` (RGB565), `35 00` (TE on, V-blank),
   `53 20` (brightness block on), `63 FF` (HBM brightness).
5. `2A 0000 0153`, `2B 0000 0153`: a full 340×340 window.
6. `11` (sleep out), 60 ms, `29` (display on), 60 ms, `2C` (memory write).

Board-proven facts: exact bytes, order, delays, that the table runs at probe
after IRQ registration and at every resume after the reset pulse, and that
`3A 55` pairs with the RGB565 frame sizes the driver sends.

Inferred (generic DCS/CO5300): the names of 0x11/0x29/0x2C/0x3A/0x35/0x53/0x51,
and the "unlock/lock" reading of F4/F5 and FE paging. The manufacturer-page
register meanings are not public and are not claimed.

## Identity (board-proven acceptance rule)

`0xDA` must read `0x33`; this read is retried up to three times until it is
nonzero. `0xDB` selects the panel variant: `0x11` → `tiny_lcm_number = 1` and
`0x10` → `2`, with other values leaving it unchanged. Probe additionally
requires the `tiny_lcd_adc` IIO channel to read 451..999 mV. A failure releases
all GPIOs and the RX buffer and returns -1. An `EPROBE_DEFER` from the ADC also
ends as -1, so stock never defers.

The module description `SSD1317 … QG-9696TSWXG04` and `alias=spi:SSD1317` are
stale metadata copied from an SSD1317 96×96 OLED driver. The executable
protocol is a CO5300-class AMOLED DDIC with internal GRAM (window + RAMWR).

## Runtime commands

- Brightness: `51 <backlight_step & 0xff>` then `2C`. These are sent *only*
  inside the next frame write, and only if `backlight_step` changed since the
  last send (`current_backlight_level != backlight_step`). There is no
  backlight GPIO activity: `bl_ctrl_gpio` is requested low in probe and never
  touched again.
- Window: `2A/2B` + `2C`, sent only when the frame width changes (`pre_framesize`).
- Suspend: `28`, 20 ms, `10`, 220 ms.

There is no MADCTL (0x36), inversion, gamma, scroll or rotation command. Panel
orientation is the controller's power-on default plus the vendor-page settings.
