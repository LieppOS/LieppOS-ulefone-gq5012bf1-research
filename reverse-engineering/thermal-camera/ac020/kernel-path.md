# Kernel path

**NO DEVICE-SPECIFIC AC020 / THERMAL-UVC KERNEL DRIVER EXISTS.** Parity: N/A.

| step | what happens | evidence |
|---|---|---|
| power + host role | `yft_tiny2c_usb.ko` (rails 149/191/192; DONE in FM78100-COMPANION) and `extcon-mtk-usb` `tiny2c_mode` → HOST (USB kernel stack DONE) | closed components |
| enumeration | xHCI `11200000.xhci0` root port `1-1`, high-speed, device 3474:4321 | S |
| first bind | GKI built-in `uvcvideo` (`CONFIG_USB_VIDEO_CLASS=y`) logs `Found UVC 1.10 device Camera (3474:4321)` and would create `/dev/videoN` | S, boot Image string |
| userspace takeover | app opens `/dev/bus/usb/001/NNN` through `UsbManager` (fd); bundled libusb (`android_usbfs` backend) issues `USBDEVFS_DISCONNECT`/`DISCONNECT_CLAIM` + `CLAIMINTERFACE` for if0 and if1 → both interfaces show `driver=usbfs` during the session | S (`driver=usbfs` on 1-1:1.0 and 1-1:1.1), ioctl census of `libusbuvccamera020.so` |
| data | usbfs `SUBMITURB` (iso 0x81, interrupt 0x83), `REAPURBNDELAY`, `DISCARDURB`, `CONTROL`/`SUBMITURB` control for EP0, `SETINTERFACE`, `RELEASEINTERFACE`, `CLEAR_HALT`, `RESET`, `GET_CAPABILITIES`, `GETDRIVER` | ioctl constants in `libusbuvccamera020.so` |
| teardown | rails off → device disconnect; `tiny2c_mode` 0 → role NONE | power-sequence (FM78100) |

Searched: all `.ko` in vendor_boot, vendor_dlkm, system_dlkm, odm_dlkm and the GKI image —
no module matches `usb:v3474p4321*` or UVC class aliases other than built-in `uvcvideo`;
no ODM UVC/V4L2 driver; `yft_tiny2c_usb.ko` touches GPIO + I2C only.

## V4L2

Not on the stock path. `uvcvideo` creates a V4L2 node at enumeration, but no stock
component opens it: the AC020 SDK uses usbfs, the UVCCamera `Const.VIDEO_DEVICE_NODE =
"/dev/video0"` string in M170infisens is unreferenced, and the Android camera framework
is used only for the **visible** fusion camera (Camera2, 1440×1080@25). So: no V4L2
format enumeration, no VIDIOC_STREAMON, no V4L2 controls, no mmap buffers for the thermal
module in stock. (`libjni_deviceAsWebcam.so` = Android webcam gadget, unrelated.)
