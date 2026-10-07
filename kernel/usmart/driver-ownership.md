# Driver/source ownership

| function | owner | status |
|---|---|---|
| GPIO28 acquisition/IRQ/work/boot sample | `extcon-mtk-usb.ko` | exact closed module/source |
| GPIO152 power and GPIO55 route outputs | `extcon-mtk-usb.ko` | exact closed module/source |
| `uvc_insert_status` | `extcon-mtk-usb.ko` | exact |
| HOST/NONE request, extcon and role work | `extcon-mtk-usb.ko` → role switch | exact; USB details already DONE |
| U2 PHY, MTU3, xHCI and usbcore | XS-PHY/MTU3/xHCI/GKI | already DONE |
| external Type-C CC/VBUS/BC1.2 | MT6375 TCPC/charger + extcon | separate, already DONE |
| internal thermal rails/flag | `yft_tiny2c_usb.ko` + MT6375-exported `yft_usb_flag` | separate, already DONE |
| uSmart camera stream/control | downloadable `com.endoscope.otgcamera` app and bundled libs | userspace; no dedicated kernel camera driver |
| app-install prompt | YftSystemUI | observer only |
| factory validation | FactoryMode | observer/launcher only |
| SC851x / reverse charge | none | excluded/dead |

There is no dedicated `usmart.ko`, HAL, daemon or binder service. All board glue is an ODM
addition inside exact `extcon-mtk-usb.ko`; no parity rebuild is needed. Stock code uses
legacy raw integer GPIO APIs for 55/152 and descriptor GPIO for 28.

Canonical exact source:
`reverse-engineering/usb/reconstruction/exact-source/extcon-mtk-usb.c`.
