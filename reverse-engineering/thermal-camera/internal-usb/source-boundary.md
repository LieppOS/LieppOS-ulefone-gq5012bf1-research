# Source boundary

| part | source | state |
|---|---|---|
| rails GPIO 149/191/192, boot I2C ID, `tiny2c_usb_mode`, `sensor_id`, sets `yft_usb_flag` | `yft_tiny2c_usb.ko` — ODM-only, reconstructed (`../fm78100/source/yft_tiny2c_usb.c`) | DONE in FM78100-COMPANION (11/12 byte-identical, probe behaviour-identical) |
| `tiny2c_mode` → role, flag gates, uSmart GPIO 28/55/152, OTG GPIO 37 | `extcon-mtk-usb.ko` — MTK ALPS + YFT patch (`../../usb/reconstruction/exact-source/extcon-mtk-usb.c`) | DONE (22/22 byte-identical) in EXTCON-MTK-USB |
| `yft_usb_flag` definition, BC1.2 PHY-switch skip, PD requeue | `mt6375-charger.ko` — ALPS + YFT deltas (private tree commit c1eef8d, 78/78 exact) | DONE in power-charging |
| role switch, host controller, PHY | `mtu3.ko`, `xhci-mtk-hcd-v2.ko`, `phy-mtk-xsphy.ko` | DONE in USB kernel stack |
| initial bind | GKI built-in `uvcvideo` (generic) | generic |
| usbfs | GKI `drivers/usb/core/devio.c` (generic) | generic |
| power/role writers | M170infisens / M170infDlp `GPIOUtils`, FactoryMode `InfirayEcoTest`, `services.jar` AMS cleanup | proprietary Java, decompiled |
| device ownership, stream, vendor control | `libAC020sdk.so`, `libusbuvccamera020.so` (bundled libusb/libuvc fork), `libircmd020.so` | proprietary native; documented at binary boundary in AC020-UVC |
| radiometry / processing | `libadvir*`, `libcommonsdk`, MNN, fusion libs | THERMOVUE-T2 (out of scope) |

No source in this scope is unreconstructed: every kernel part is already byte-level
closed in its owning component; userspace is proprietary and bounded by AC020-UVC.
