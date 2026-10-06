# thermal-camera — STATUS

| component | status | summary |
|---|---|---|
| FM78100-COMPANION (8-003c) | **DONE (static)** | identity resolved (module ASIC I2C slave, FM78100 retracted); full I2C map (2 reads); role = boot ID; power/USB sequence; `yft_tiny2c_usb.ko` 11/12 functions byte-identical, data/ABI/strings exact, B1==B2 |
| AC020-UVC | PARTIAL | identity PROVEN at fw/software level (Tiny2-C 256×192; 640×512 native retracted); USB/UVC descriptor map (stock capture + same-identity public descriptor); kernel = GKI uvcvideo + usbfs, no custom driver; OEM vdcmd header table extracted (250/257 call sites). Open: per-command selector sequence / payload layouts inside `libusbuvccamera020.so`, and an on-unit frame-descriptor read |
| THERMOVUE-T2 transport boundary | mapped (see `ac020/uvc-path.md`) | open transport = UVC/usbfs + vdcmd; proprietary = radiometry/processing libs + MNN SR |
