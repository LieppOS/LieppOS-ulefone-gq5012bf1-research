# AC020-UVC — identity and kernel boundary

## Identity

| claim | class | evidence |
|---|---|---|
| "AC020" is the InfiRay/Raytron SDK/ASIC-family name used by the stock software (`libAC020sdk.so`, `com.energy.ac020library`, `libircmd020.so`, `libusbuvccamera020.so`, build tree `ANDROID_RS300_SDK`) — not a separate USB-bridge chip | PROVEN (naming) |
| the USB device, the UVC function and the I2C 8-003c slave are the same module ASIC | STRONGLY SUPPORTED (TC2-C pinout: one ASIC with USB2 + IIC slave; no hub/bridge on the bus: device sits on root port `1-1`) |
| module = Raytron/InfiRay **Tiny2-C (TC2-C)**, 256×192, 12 µm, 25 Hz | PROVEN at firmware/software level: `M170infDlp.apk!assets/RS300_TC2C_00.00.04.07_01.46_whole_package…zip` → `whole_package.json` `"device_name":"TINY2-C"`; M170infDlp `IR_SENSOR_WIDTH=256`, `IR_SENSOR_HEIGHT=386`, `IR_SENSOR_LINE_HEIGHT=2`, `IR_SENSOR_FPS=25`; FactoryMode 256×384 YUYV+temp |
| "640×512 / ThermoVue T2" | marketing **output** figure (Ulefone spec: "ThermoVue T2 … SharpenAI … 640 x 512"). The stock app runs `MImageUtils.ModelName.MNN_SR_TINY2C` super-resolution (`mIrData` → `mIrDataX2`) on the 256×192 stream. Native 640×512: **RETRACTED** |
| ASIC tag | `0x4c59` ("LY") read at 8-003c, consistent with Raytron's LY300 ASIC — STRONGLY SUPPORTED |

## USB identity (stock unit, PROVEN from `usb-research/evidence/thermal-camera-*`)

`3474:4321`, bcdDevice 2.00, Mfr "Thermal Cam Co.,Ltd", Product "Camera", Serial
"202206223" (a firmware constant — the identical string appears on unrelated public
units), class EF/02/01 (IAD), high-speed 480 Mbit/s on `1-1`, UVC 1.10. Interfaces:
`1-1:1.0` VideoControl (0E/01, 1 endpoint) and `1-1:1.1` VideoStreaming (0E/02,
alt 1 with 1 endpoint). See `usb-descriptors.md`.

## Kernel side

- **No custom driver.** No vendor/ODM module matches 3474:4321 or any UVC class.
- GKI `CONFIG_USB_VIDEO_CLASS=y` (built-in `uvcvideo`, confirmed by `"Found UVC %u.%02x device %s (%04x:%04x)"` in the boot Image) binds first: log line `Found UVC 1.10 device Camera (3474:4321)`.
- The stock apps then open `/dev/bus/usb/001/00N` via Android `UsbManager`/`USBMonitor`;
  bundled libusb detaches the kernel driver and claims both interfaces — the capture shows
  `driver=usbfs` on `1-1:1.0` and `1-1:1.1`. Streaming and all vendor control run in
  userspace over usbfs (isochronous + control transfers).
- No V4L2 node is used by stock (`VIDEO_DEVICE_NODE=/dev/video0` in M170infisens `Const`
  is unreferenced).

## Files

| file | content |
|---|---|
| `usb-descriptors.md` | descriptor map (stock capture + same-identity public descriptor) |
| `uvc-path.md` | module → USB → usbfs/libusb → SDK → app |
| `vendor-control.md` | UVC standard vs vendor control channel |
