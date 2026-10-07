# Userspace ownership (integration view)

Detailed stack, hashes and protocol: AC020-UVC (`../ac020/userspace-path.md`,
`../ac020/vendor-control-protocol.tsv`). Only the device-ownership chain is listed here.

| step | component | call | kernel interface |
|---|---|---|---|
| power + role | `GPIOUtils` (M170infisens / M170infDlp), FactoryMode `InfirayEcoTest` | FileWriter "1"/"0" | sysfs `tiny2c_usb_mode`, `tiny2c_mode` |
| discovery / permission | `USBMonitor` → `UsbManager.requestPermission`, `openDevice` | `UsbDeviceConnection` fd, bus/dev numbers, raw descriptors | `/dev/bus/usb/001/NNN` (opened by system_server, fd passed) |
| handle | `IrcamEngine.Builder()…setDriverType(USB_DUAL_NATIVE_CAM)` (M170infDlp upgrade: `USB`) → `libAC020sdk` `native_init_handle_engine` | `iruvc_camera_handle_create`, `iruvc_usb_handle_create`, `ircmd_create_handle` | – |
| open / claim | `libusbuvccamera020` `iruvc_usb_device_open` → `UVCCamera::connect` → `uvc_get_device_with_fd(dup(fd))` → `uvc_open` | auto-detach + claim VC interface; interrupt EP 0x83 submitted | usbfs `DISCONNECT_CLAIM`, `SUBMITURB` |
| control | `libircmd020` → `libAC020sdk` `iruvc_usb_data_*` → `libusb_control_transfer` | EP0 vendor 0x41/0x20, 0xC1/0x22, 0xC1/0x21 | usbfs `CONTROL` |
| stream | `UVCCamera::setPreviewSize/startPreview` → probe/commit, claim VS if1, alt 1 | iso EP 0x81 → 256×386 frames → JNI frame callback → image / info / temperature split | usbfs `SETINTERFACE`, `SUBMITURB`/`REAPURBNDELAY` |
| close | `stopVideoStream` → alt 0; `uvc_close` → `uvc_release_if` + auto-detach 0; `libusb_close` | – | usbfs `RELEASEINTERFACE` |

No HAL, daemon, binder service, V4L2 node, `/dev/i2c-*`, ioctl to a vendor driver or
Android camera framework object is involved for the thermal module (the Camera2 user
in M170infisens is the visible fusion camera).
