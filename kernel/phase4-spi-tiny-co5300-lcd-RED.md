# CO5300 mandatory RED

## Baseline

Result: **NO_PUBLIC_DONOR_FOUND / empty-source RED**.

No plausible public source contains the stock function names, miscdevice,
11-request ioctl ABI, YFT registry calls, Hynitron coordination, MTK pinctrl
states or SSD1317 ID logic. Generic CO5300 and SSD1317 sources are not an
unchanged-build donor, so no behavioral source was edited or compiled before
this RED was recorded.

## Stock-versus-empty mismatch

| Dimension | Frozen stock | Empty/public baseline |
|---|---|---|
| functions | 25 named functions | 0 |
| imports | 58 exact MODVERSION edges | 0 |
| exports | 0 | 0 |
| identity | `spi_tiny_co5300_lcd`, SSD1317 metadata | absent |
| compatible | `hxytech, spi_tiny_lcd` (metadata underscore alias quirk) | absent |
| SPI | SPI0 CS0, 60 MHz DT; stock sets mode 0, 8 bpw | absent |
| GPIO/pinctrl | five DT GPIOs plus eight named pinctrl states | absent |
| controller | `DA=33`, `DB=10/11`; 44-entry init table | absent |
| misc/UAPI | `tiny_lcd_miscdev`, 11 ioctls | absent |
| frame path | 96x96x2, user pointer, 18,432-byte copy/SPI write | absent |
| providers | 2 rebuilt-Hynitron + 2 stock-yft_devinfo edges | absent |
| PM | userspace/ioctl-owned power state, no PM callback | absent |

This is the immutable RED reference. Reconstruction begins from relocation-aware
stock disassembly, DT, the 32/64-bit stock HAL, frozen provider ABIs and exact
command-table bytes—not from a generic donor.
