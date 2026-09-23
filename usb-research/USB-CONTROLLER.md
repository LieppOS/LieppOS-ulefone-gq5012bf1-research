# USB controller identity

## `11201000.usb0`

Classification: **PROVEN**.

`11201000.usb0` is the only operational MediaTek MTU3 dual-role controller instantiated by the effective GQ5012BF1 stock DT.

| Field | Value |
|---|---|
| DT path | `/soc/usb0@11201000` |
| compatible | `mediatek,mtu3` |
| platform driver | `mtu3` |
| stock module | `mtu3.ko` |
| MAC registers | `0x11201000`, size `0x2e00` |
| IPPC registers | `0x11203e00`, size `0x100` |
| device IRQ | GIC SPI 384, level high |
| mode | `otg` |
| maximum speed | `high-speed` |
| PHY reference | USB2 child at `11f40000`, argument `PHY_TYPE_USB2`/`3` |
| role-switch | yes; graph endpoint to `/extcon-usb` |
| host child | `/soc/usb0@11201000/xhci0@11200000` |

Evidence: `USB-DEVICE-TREE.md`, `evidence/stock-usb-dt-nodes.txt`, `evidence/live-usb-dt-nodes.txt`, `evidence/stock-platform-bindings.txt`.

## Host child

`11200000.xhci0` is the xHCI host portion of the same dual-role fabric:

| Field | Value |
|---|---|
| compatible | `mediatek,mtk-xhci` |
| platform driver while active | `xhci-mtk` |
| stock module | `xhci-mtk-hcd-v2.ko` |
| registers | `0x11200000`, size `0x1000` |
| IRQ | GIC SPI 385, level high |
| status | `okay` |
| USB offload reference | `/soc/usb-offload` points to this child |

The child is unbound during external gadget mode. It binds dynamically for host mode. In the thermal-camera test it created one 480-Mbit/s root hub (`usb1`, serial `11200000.xhci0`) and enumerated the camera directly at port 1.

## Role-specific use

```text
External gadget / ADB:
11201000.usb0 -> mtu3 UDC -> external Type-C D+/D− -> host, 480 Mbit/s

Internal thermal camera:
11201000.usb0 -> 11200000.xhci0 -> internal route -> 3474:4321, 480 Mbit/s

External OTG:
11201000.usb0 -> 11200000.xhci0 -> external Type-C D+/D−
```

The first two paths are runtime-proven. The external OTG path is proven by DT/driver/extcon contracts and existing stock functionality; an independent live peripheral descriptor capture was not performed in this session.

## Controller/port count

The merged stock DT and live platform bus contain:

- one MTU3 instance at `11201000`;
- one xHCI child at `11200000`;
- one production USB2 PHY port;
- no live `11211000.usb1` controller;
- no SuperSpeed companion root hub during active xHCI runtime.

Old userspace chmod paths under `11211000.usb1` are dead inherited configuration. They do not create hardware or a platform device.

## USB3 interpretation

The module description calls MTU3 a “USB3 DRD Controller Driver” because the driver family supports USB3-capable MediaTek designs. On this instance:

- DT maximum is High-Speed;
- only a USB2 PHY is referenced;
- UDC maximum is High-Speed;
- xHCI creates only a 480-Mbit/s root hub.

Therefore the **configured controller path is USB2-only**, regardless of the generic driver name.
