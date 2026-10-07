# uSmart power boundary: SC851x and MT6375 excluded

**Corrected 2026-10-07.** Canonical power contract: [`power-path.md`](power-path.md).

## Proven uSmart operation

```text
GPIO28 LOW/HIGH
  → extcon-mtk-usb ID work
  → GPIO152 HIGH/LOW (uSmart accessory power gate)
```

The ID worker performs raw GPIO operations only. It does not call the driver's
`mtk_usb_extcon_set_vbus`, regulator APIs, GPIO37 or charger APIs.

## SC851x

`sc851x_charger.ko` has no regulator, extcon, USB, TCPC, MT6375, power-supply, charger
class or uSmart symbol edge; DT has no phandle between SC851x and `/extcon-usb`; its only
GPIO is IRQ and its only sysfs surface is raw `registers`. Classification:
**PROVEN_UNRELATED** to uSmart detection, route and software-controlled power.

## MT6375

The `/extcon-usb` `vbus-supply` resolves to MT6375 `usb-otg-vbus`, and the same extcon
driver uses it with GPIO37 for external Type-C SOURCE_VBUS (5.25 V / 1.8 A). That shared
driver ownership previously led to an over-broad claim that MT6375 sourced uSmart. The
uSmart insertion path never calls the regulator operation, so no such source edge is
proven. GPIO152 may control a board load switch/boost, but its upstream rail, voltage,
current and part are board-only unknowns.

No stock software support was found for charging the phone through uSmart or for the dead
`reverse_charging_level` label.
