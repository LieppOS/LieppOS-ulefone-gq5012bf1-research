# uSmart accessory power path

## Proven software contract

`mtk_usb_extcon_detect_cable` controls uSmart power only with raw
`gpio_set_value(GPIO152, inserted)`. The DT name is `uvc_vbus_gpio`; the output is
initialized LOW and goes HIGH before GPIO55 is switched to uSmart. Removal drives it LOW
before returning the route to external Type-C.

No regulator API, MT6375 operation, GPIO37 operation, current-limit request, voltage
request, delay or power-good check occurs in the GPIO28 insertion/removal path.

## Boundary

| question | result |
|---|---|
| is GPIO152 the accessory power gate? | yes, exact software contract |
| nominal function | USB VBUS/accessory power enable (DT/driver naming and USB-camera role) |
| exact rail source and voltage | board-only/unknown; do not infer from `vbus-supply` |
| current limit, inrush, short protection | unknown; no uSmart API |
| MT6375 `usb-otg-vbus` | separate external Type-C SOURCE_VBUS path, fixed 5.25 V/1.8 A |
| GPIO37 | Type-C source companion only |
| SC851x | no DT/software edge; unrelated |
| reverse charge into phone | no stock support found |
| `reverse_charging_level` | dead SELinux path; no driver attribute |

The `/extcon-usb` node has a `vbus-supply` phandle to MT6375 because the same driver also
handles external Type-C source VBUS. That phandle does **not** prove MT6375 supplies
uSmart: the ID worker never calls `mtk_usb_extcon_set_vbus`. Earlier canonical reports
that drew MT6375 directly upstream of GPIO152 are retracted.

Driver shutdown disables only the Type-C regulator/GPIO37. It does not explicitly clear
GPIO152 or GPIO55; physical shutdown/reset eventually removes power, but no uSmart
shutdown transaction exists in the driver.
