# External USB-C physical/logical path

```text
USB-C receptacle (BM65_SUB_V1.2 daughterboard)
  CC1/CC2 ───────────────→ MT6375 TCPC (`type_c_port0`): attach, orientation, DR/PR, PD
  VBUS ──────────────────↔ MT6375 charger (sink) / `usb-otg-vbus` boost (source)
  SBU1/SBU2 ─────────────→ MT6375 ADC water detection only
  D+/D− ─→ board route selected by GPIO55
             GPIO55=0 (probe/default; external gadget works) → USB-C external pair
             GPIO55=1 → uSmart accessory pair
           → XS-PHY `usb2-phy0@11f40000` (only child/port)
           → MTU3 `11201000.usb0`, dr_mode=otg, role switch
               DEVICE → UDC `11201000.usb0` / configfs gadget
               HOST   → dynamic xHCI child `11200000.xhci0` / usb1 port 1
               NONE   → data IP off
```

The internal Tiny2-C module reaches the same U2 fabric by board routing tied to its own
power/control path; no thermal mux GPIO is exposed. See `thermal-interaction.md`.

## Negative capability proof

| item | proof | verdict |
|---|---|---|
| USB3 device port | MTU3 IPPC hardware: `usb3-drd: 0`, device U3 count 0, trunk 0x1008 "U2 IP" | absent |
| USB3 host port | xHCI Supported-Protocol: `USB3 root hub has no ports`; only usb1, one U2 port | absent |
| U3 PHY | DT has only `usb2-phy0`; no U3 register window/efuse; disabled FPGA test PHY is unrelated | absent |
| SS orientation mux/redriver | template `typec-mux-switch` has no downstream mux/redriver driver/device | absent |
| DP Alt Mode | no DP TX/PHY and no lane mux; template TCPC DP declarations cannot reach hardware | nonfunctional |
| passive analog audio | no FSA4480-class switch, codec route or SBU audio path | unsupported |
| second external controller | no live `11211000.usb1`; its init chmod is dead; only MTU3 11201000 exists | absent |
| Thunderbolt/PCIe/SuperSpeed video | no U3/DP/PCIe tunneling fabric at the receptacle | impossible |

D+/D− are orientation-independent, so CC polarity is reported to Type-C class but needs
no USB2 data mux. Digital USB Audio Class devices remain supported as ordinary USB2 host
devices; that is distinct from passive analog Type-C audio.
