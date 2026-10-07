# USB D+/D− routing

```text
Type-C receptacle USB2 pair ─┐
                              ├─ GPIO55-controlled board element ─→ usb2-phy0
uSmart connector USB2 pair ──┘                                  └→ MTU3 11201000
                                                                       └→ xHCI 11200000
```

| GPIO55 | selected software contract | evidence |
|---:|---|---|
| 0 | external Type-C/default route | output initialized LOW; normal external gadget/host works in that state |
| 1 | uSmart accessory route | `uvc_switch_gpio` is asserted on active-low accessory detection before HOST request |

The route element's silicon/part number and schematic nets are not present in DT or
binaries. That is non-blocking: software only needs the polarity and ordering.

There is one USB2 PHY/controller, no live `11211000.usb1`, and no simultaneous data
path. Changing MTU3 role does not change GPIO55; changing GPIO55 does not validate or
serialize the role. Therefore later Type-C, thermal or uSmart events can produce a
powered/routed device with the wrong USB role.

GPIO55 is not the internal thermal camera's rail or role control. The thermal module uses
GPIO149/191/192 and `tiny2c_*`; it merely competes for the common downstream USB fabric.
