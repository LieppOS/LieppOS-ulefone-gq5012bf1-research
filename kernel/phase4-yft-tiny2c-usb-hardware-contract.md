# yft_tiny2c_usb physical hardware contract

## Signals directly controlled

| stock field | MT6878 GPIO | DT flags | direction | polarity | final probe state | runtime 0/1 | role |
|---|---:|---:|---|---|---:|---|---|
| `gpio_1v8` | 192 | 0 | not configured by module | raw high enables | 0 | raw low/high | thermal module 1.8-V enable |
| `gpio_3v3` | 191 | 0 | not configured by module | raw high enables | 0 | raw low/high | thermal module 3.3-V enable |
| `gpio_5v` | no DT GPIO | n/a | n/a | n/a | no physical output proven | generic code handles value | compiled optional 5-V enable slot only |
| `gpio_io3v3` | 149 | 0 | not configured by module | raw high enables | 0 | raw low/high | thermal module 3.3-V I/O enable |

The driver uses `gpio_request`, `gpio_to_desc`, and `gpiod_set_raw_value`; it never calls a
GPIO direction API. Direction therefore comes from boot firmware/pinctrl/default GPIO state
outside this module. Raw, not logical, APIs prove that DT active-low semantics would be
ignored. The three stock flags are zero and userspace/driver logs identify 1 as power-on,
therefore the three populated enables are active-high.

## Probe and runtime topology

```text
MT6878 GPIO 192 (1V8 enable) ─┐
MT6878 GPIO 191 (3V3 enable) ─┼─> internal thermal-imaging module power domains
MT6878 GPIO 149 (IO3V3 enable)┘
                                      │
MT6878 I2C8, GPIO141/142, addr 0x3c ─> module power/ID endpoint (chip ID registers 0/1)
                                      │
separate extcon/USB1 + MT6375 path ──> internal USB/UVC data and USB VBUS routing
```

The last edge is corroborated by stock userspace coordinating two independent sysfs nodes;
it is not a direct call or DT phandle from this module.

## Required questions

1. **What does `tiny2c` mean?** In stock software it is the YFT/InfiRay internal thermal
   module family/path name. It labels the module power/ID endpoint and paired USB routing
   mode; it is not an I2C controller name and does not imply a public TinyWire protocol.
2. **Built-in thermal camera?** Yes. Exact stock binding, the thermal FactoryMode tests,
   ThermoVue package, AC020/UVC libraries, and coordinated sysfs writes identify this as the
   built-in thermal-imaging path.
3. **Shares USB1?** Stock userspace powers this module and then selects
   `/sys/class/yft_extcon/tiny2c_mode`; that separate extcon driver operates the board USB1
   host/route. Thus the thermal data path uses the board's secondary/internal USB path.
4. **Shares Type-C resources?** It shares MT6375 charger USB-PHY/DPDM attach machinery only
   through `yft_usb_flag`; it has no Type-C/TCPC imports or phandles. Physical lane identity
   beyond the proven USB1/extcon route is not asserted.
5. **Touches uSmart?** It does not control uSmart GPIOs, VBUS, detection, or accessories.
   The broader board design reuses the secondary USB/extcon infrastructure; see the separate
   uSmart contract.
6. **Supplies VBUS?** No direct VBUS source. The stock platform node has no 5-V GPIO and the
   module has no regulator/OTG call. MT6375 `usb-otg-vbus` is controlled by extcon/USB logic.
7. **Only selects/isolates an internal USB camera?** It powers three populated low-voltage
   rails and sets a charger BC1.2-exclusion flag. Actual USB role/mux/VBUS selection is done
   by `extcon-mtk-usb`, not by this module.
