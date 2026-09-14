# GQ5012BF1 — extcon-mtk-usb DT contract (Phase 6)

Static/offline. **No DT was altered.** Every property below was confirmed to
exist as a literal in the stock `.ko` and in the reconstruction, by exact-line
string match against both ELFs.

## 1. Node

```
compatible = "mediatek,extcon-usb";
```

Stock module aliases (from `.modinfo`):

```
of:N*T*Cmediatek,extcon-usb
of:N*T*Cmediatek,extcon-usbC*
```

The `of_device_id` table is 400 bytes in both images = 2 × 200-byte
`struct of_device_id` (one match + sentinel), consistent with the two aliases.

## 2. Property / string verification

count = exact whole-line matches in each ELF's string pool.

| property | stock | recon | role |
|---|---|---|---|
| `mediatek,extcon-usb` | 2 | 2 | compatible + `of_find_compatible_node()` lookup |
| `mediatek,bypss-typec-sink` | 1 | 1 | **misspelling is stock; preserved verbatim** |
| `mediatek,u2` | 1 | 1 | gates the procfs node |
| `vbus-supply` | 1 | 1 | presence check before regulator get |
| `usb-otg-vbus` | 1 | 1 | MT6375 regulator name |
| `vbus-voltage` | 1 | 1 | 5250000 uV |
| `vbus-current` | 1 | 1 | 1800000 uA |
| `vbus-limit-current` | 1 | 1 | 500000 uA |
| `tcpc` | 1 | 1 | TCPC phandle/name property |
| `type_c_port0` | 1 | 1 | required value for the procfs node |
| `otg_gpio_select` | 1 | 1 | GPIO 37 |
| `uvc_switch_gpio` | 1 | 1 | GPIO 55 |
| `uvc_vbus_gpio` | 1 | 1 | GPIO 152 |
| `charger` / `primary_chg` | 1 / 1 | 1 / 1 | power-supply phandle + by-name fallback |
| `extcon_usb` | 1 | 1 | workqueue name |

## 3. GPIO contract

| GPIO | DT property | acquisition | owner behaviour |
|---|---|---|---|
| 28 | `id-gpios` | `devm_gpiod_get(dev, "id", ...)` + `gpiod_to_irq()` | accessory-detect input, ID IRQ |
| 37 | `otg_gpio_select` | `of_get_named_gpio_flags()` → `gpio_to_desc()` | Type-C OTG / source-VBUS companion |
| 55 | `uvc_switch_gpio` | `of_get_named_gpio_flags()` → `gpio_to_desc()` | UVC/USB path switch |
| 152 | `uvc_vbus_gpio` | `of_get_named_gpio_flags()` → `gpio_to_desc()` | accessory VBUS/power switch |

**Why two different GPIO APIs** (PROVEN by the import census): the three YFT
property names use underscores (`otg_gpio_select`, `uvc_switch_gpio`,
`uvc_vbus_gpio`), which the gpiod consumer API cannot match — it only probes
`<con-id>-gpios` / `<con-id>-gpio`. The vendor therefore reads them raw with
`of_get_named_gpio_flags()` and converts with `gpio_to_desc()`. This is exactly
consistent with the stock import set, where `devm_gpiod_get` appears **once**
(the `id` pin) while `gpio_to_desc` / `gpio_request` / `gpiod_*_raw_value`
recur.

GPIO 37 is **not** the uSmart accessory GPIO 152. They are distinct lines with
distinct owners and are not conflated anywhere in the reconstruction.

## 4. Regulator contract

```
vbus-supply        = <&usb_otg_vbus>       (MT6375)
vbus-voltage       = 5250000 uV
vbus-current       = 1800000 uA
vbus-limit-current =  500000 uA
```

Enable path requests voltage then current then `regulator_enable()`; disable
path calls `regulator_disable()`. `vbus_limit_cur` = 1 requests 500000 uA and
0 restores 1800000 uA, only while VBUS is active.

## 5. Graph

The extcon endpoint links to the normal ssusb/MTU3 role-switch topology
(`usb_role_switch_get()` / `usb_role_switch_set_role()` in the import set).
There is exactly **one** USB fabric (USB0 / MTU3 / xHCI / USB2 PHY). No second
USB controller is implied or implemented, and the historical
`11211000.usb1/mode` path has no live DT controller backing and is **not**
implemented as real hardware.
