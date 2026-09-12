# Phase 4 `spi_tiny_co5300_lcd` DT and provider contract

## Live stock DT binding

The enabled child is on the MT6989 SPI controller at physical
`0x11010000`, chip select 0, with `spi-max-frequency = <60000000>` and the
literal compatible string:

```text
hxytech, spi_tiny_lcd
```

The embedded space is intentional and produces stock aliases
`of:N*T*Chxytech,_spi_tiny_lcd` and `...C*`.

Properties consumed by the module:

| Property | Resolved GPIO |
|---|---:|
| `tiny_lcd,reset-gpio` | 154 |
| `tiny_lcd,en-1v8-gpio` | 118 |
| `tiny_lcd,en-2v8-gpio` | 29 |
| `tiny_lcd,dc-ctrl-gpio` | 190 |
| `tiny_lcd,backlight_gpio` | requested but not driven after probe |
| `tiny_lcd,te_gpio` | 31 |

The node also supplies the named IIO channel `tiny_lcd_adc` and these exact
pinctrl state names:

- `stl_spi1_mo_as_spi1_mo`
- `stl_spi1_mo_as_gpio`
- `stl_spi1_mi_as_spi1_mi`
- `stl_spi1_mi_as_gpio`
- `stl_spi1_clk_as_spi1_clk`
- `stl_spi1_clk_as_gpio`
- `stl_spi1_cs_as_spi1_cs`
- `stl_spi1_cs_as_gpio`

No DT modification is required or permitted for reconstruction.

## External providers

The module exports no symbols. It imports four vendor symbols.

| Symbol | CRC | Prototype | Provider policy |
|---|---:|---|---|
| `tiny_tp_gesture_contorl` | `0x4e4b7919` | `void (int)` | rebuilt Hynitron `Module.symvers` |
| `tiny_tp_power_contorl` | `0xfcc94fc7` | `void (int)` | rebuilt Hynitron `Module.symvers` |
| `yft_tinylcd_device_add` | `0x9c6d85d0` | `int (struct spi_driver *, int)` | stock `yft_devinfo` ABI witness |
| `yft_set_tinylcd_device_used` | `0x25e94db4` | `int (char *, int)` | stock `yft_devinfo` ABI witness |

YFT CRCs were read directly from the stock provider's `__kcrctab`; the witness
is `workspace/phase4-spi-tiny-co5300-lcd/oracle/stock-yft-devinfo.symvers`.
Hynitron's witness is its real source-built output, frozen at
`workspace/phase4-spi-tiny-co5300-lcd/oracle/hynitron-rebuilt.Module.symvers`.
There is no CRC patching, handwritten `__versions`, fake provider object, ELF
editing, or modpost-warning bypass.
