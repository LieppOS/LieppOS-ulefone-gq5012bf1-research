# yft_tiny2c_usb device-tree contract

## Platform node consumed by the module

Exact live-DT path: `/yft_tiny2c_usb`

| property | raw stock value | decoded | consumed? |
|---|---|---|---|
| `name` | `yft_tiny2c_usb\0` | node name | kernel core only |
| `compatible` | `mediatek,yft_tiny2c_usb\0` | platform OF match | **yes** |
| `phandle` | `<0x1d1>` | node handle | no |
| `tiny2c_usb_vdd_1v8` | `<0x89 0xc0 0>` | MT6878 GPIO 192, flags 0 | **yes** |
| `tiny2c_usb_vdd_3v3` | `<0x89 0xbf 0>` | MT6878 GPIO 191, flags 0 | **yes** |
| `tiny2c_usb_vddio_3v3` | `<0x89 0x95 0>` | MT6878 GPIO 149, flags 0 | **yes** |
| `status` | absent | enabled by default | core behavior |
| `tiny2c_usb_vdd_5v` | **absent** | no board GPIO supplied | queried by stock code but not present |

Phandle `0x89` resolves to `/soc/pinctrl`, compatible
`mediatek,mt6878-pinctrl`, `#gpio-cells=<2>`. All three present flags cells are zero.
The stock code asks for the four properties above in 1v8, 3v3, 5v, io3v3 order and reuses
a single `enum of_gpio_flags` slot. It never tests or applies the flags and drives raw GPIO
values, so no logical active-low translation occurs.

## I2C child consumed by the module's dynamically registered I2C driver

Exact live-DT path: `/soc/i2c@11e03000/fm78100@0x3c`

| property | stock value | consumed? |
|---|---|---|
| `name` | `fm78100` | kernel core only |
| `compatible` | `mediatek,tiny2c_usb` | **yes**, I2C OF match |
| `reg` | `<0x3c>` | **yes**, I2C core creates address 0x3c client |
| `status` | `okay` | yes, core population |

The same I2C driver also has ID `tiny2c_usb-sensor`. Parent
`/soc/i2c@11e03000` reports `scl-gpio-id=<141>` and `sda-gpio-id=<142>`; those bus pins
belong to the I2C controller and are not requested or switched by this module.

## Present but not consumed / absent

The target nodes contain no pinctrl properties or states, USB-controller phandle, extcon
phandle, charger phandle, regulator supply, clock, PHY, role-switch, ID/detect GPIO,
interrupt, debounce, reset GPIO, camera-mode GPIO, or YFT scalar/string setting. The parent
I2C controller has clocks/interrupt/registers, consumed by the controller driver rather than
`yft_tiny2c_usb`.

The `extcon-usb` DT node and MT6375 `usb-otg-vbus` regulator are separate consumers/providers.
Their existence must not be rewritten as a phandle relation in this module's node.
