# BC1.2 / charger-detection boundary

Only USB integration is covered; charge-current/voltage algorithms are not.

```text
sink VBUS / Type-C attach
  → mt6375-charger bc12_work
    → wait for MTU3 `cdp-block` to clear (≤250 × 100 ms while still attached)
    → phy_set_mode_ext(usb2-phy, PHY_MODE_USB_DEVICE, PHY_MODE_BC11_SET)
    → MT6375 BC1.2 engine
    → classify PORT_STAT
    → BC11_CLR (restore D+/D− to USB) and power_supply_changed
    → extcon psy_detector (only when yft_usb_flag=0 and current role NONE)
```

| classification | power-supply type exposed | extcon result | data consequence |
|---|---|---|---|
| SDP | `POWER_SUPPLY_TYPE_USB`, USB_TYPE_SDP | DEVICE | gadget can enumerate |
| CDP | `POWER_SUPPLY_TYPE_USB_CDP`, USB_TYPE_CDP | DEVICE | gadget can enumerate |
| DCP / Apple / Samsung | `POWER_SUPPLY_TYPE_USB_DCP`, USB_TYPE_DCP | no DEVICE | charging only |
| unknown TA | `POWER_SUPPLY_TYPE_USB`, USB_TYPE_DCP | DEVICE (stock checks TYPE, not USB_TYPE) | attempts gadget; normally no host data |
| no info / unknown status | no report/change until resolved | no new role | none |
| PD/PPS ready sink | driver forces TYPE/USB_TYPE to USB_CDP | DEVICE if role NONE | PD power and USB data remain separately negotiated |
| detach | attach NONE, type USB + USB_TYPE_UNKNOWN; BC1.2 disabled/PHY restored | Type-C detach queues NONE | gadget disconnect |
| ADVMETA boot | forces SDP without BC1.2 | DEVICE path can be selected | factory behavior |

While internal thermal power sets `yft_usb_flag=1`, `mt6375_chg_set_usbsw` returns without
putting D+/D− into BC1.2 mode, the extcon psy worker returns, and PD-ready requeues
`bc12_work`. This prevents charger detection from stealing the PHY during thermal USB.
SOURCE_VBUS handling is independent.
