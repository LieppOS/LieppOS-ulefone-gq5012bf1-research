# yft_tiny2c_usb GPIO / pinctrl contract

## Acquisition

Probe allocates a 20-byte zeroed structure, then calls `of_get_named_gpio_flags(np, name,
0, &flags)` in this exact order:

1. `tiny2c_usb_vdd_1v8` -> offset `0x00` -> GPIO 192
2. `tiny2c_usb_vdd_3v3` -> offset `0x04` -> GPIO 191
3. `tiny2c_usb_vdd_5v` -> offset `0x08` -> property absent on GQ5012BF1
4. `tiny2c_usb_vddio_3v3` -> offset `0x0c` -> GPIO 149

A single flags word at offset `0x10` is reused and never interpreted. Present DT flags are 0.
Each numerically valid GPIO (`(unsigned)gpio <= 511`) is requested. Labels are
`tiny2c_gpio_1v8`, `tiny2c_gpio_3v3`, `tiny2c_gpio_5v`, and
`tiny2c_gpio_io3v3`. There is no `gpio_free` path.

Request failures for 1v8, 3v3, or io3v3 abort with `-1`; a 5v request failure is logged but
probe continues. Missing/negative property values skip `gpio_request` through the unsigned
range test. A literal GPIO 0 is logged as unavailable but still requested.

## Direction, polarity and pinctrl

- Direction: **not set by this module**; no direction import/call exists.
- Drive API: `gpiod_set_raw_value(gpio_to_desc(gpio), value)`.
- Polarity translation: none; raw values ignore active-low metadata.
- Stock flags: zero for GPIO 192, 191 and 149.
- Proven electrical convention: raw 1 is application/driver `power on`, raw 0 is `power off`.
- Pinctrl states: none present in the target nodes and no pinctrl imports.

## Exact transition order

| trigger | operation order | delays | provider flag |
|---|---|---|---|
| platform probe pre-I2C | io3v3=1; 5v=1 only if stored value nonzero; 3v3=1; 1v8=1 | none in helper | unchanged (initial provider value 0) |
| platform probe post-I2C registration | io3v3=0; optional 5v=0; 3v3=0; 1v8=0 | none | unchanged |
| sysfs parsed value 1 | same raw-high order | none | set to 1 after GPIOs |
| sysfs parsed value 0 | same raw-low order | none | set to 0 after GPIOs |
| sysfs unparsable | parser result ignored; local remains 0, so power-off sequence | none | set to 0 |
| sysfs other integer | no GPIO operation | none | unchanged |

The generic 5v slot is nonzero for negative OF errors, so power/show helpers pass the invalid
number through `gpio_to_desc`; no physical GQ5012BF1 5-V GPIO is established by the stock DT.
This defect is preserved rather than silently replacing the slot with a regulator or new GPIO.
