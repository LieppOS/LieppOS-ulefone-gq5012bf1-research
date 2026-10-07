# Userspace hardware/control path

```
M170infisens (com.energy.tc2c)                      M170infDlp (com.energy.tc2c.sop)          FactoryMode
 StartPreviewTask → GPIOUtils.powerUpControl()       same + FirmwareUpgradeManager             InfirayEcoTest
 USBMonitor(UsbManager) → UsbControlBlock (fd, bus, dev, VID/PID)
 IrcamEngine.Builder().setDriverType(USB_DUAL_NATIVE_CAM)            (USB)                     (USB)
   └ libAC020sdk.so  native_init_handle_engine
        ├ ir_video_handle_create   (libircam.so)  ─ iruvc_camera_handle_create  (libusbuvccamera020.so)   ← stream
        ├ ir_control_handle_create (libircam.so)  ─ iruvc_usb_handle_create     (libAC020sdk.so)          ← control
        │      callbacks: read=iruvc_usb_data_read  write=iruvc_usb_data_write
        │                 write_wo_status=iruvc_data_write_without_read_return_status
        │                 open/close=iruvc_usb_device_open/close (libusbuvccamera020)
        ├ ircmd_create_handle (libircmd020.so)  ← vdcmd framing, CRC16, chunking ≤0x800, polling time
        └ irdfu_handle_create (DFU/upgrade, libAC020sdk)
   IrcmdEngine (Java) → libircmd020 JNI → adv_*/basic_* → standard/short/long_cmd_* → callbacks above
   frame callback → IrcamEngine → app (image / info / temperature split)
```

| binary | sha256 (arm64) | role | USB/V4L2 interface | device node | key imports |
|---|---|---|---|---|---|
| `libusbuvccamera020.so` | `d3e36b336ef65535a52e71dea926bd1e5b6db9207e8fe8a4c29e1a6c59dbefe8` (M170*), `fb94d993b4dbb0cbf2c315b870aac9674ca8d4413d5c93d6bc38627faddcfa2f` (FactoryMode) | bundled libusb 1.0 (android_usbfs) + libuvc fork; `iruvc_camera_*` stream API, `iruvc_usb_device_open/close` | usbfs ioctls; UVC probe/commit; iso + interrupt URBs | `/dev/bus/usb/BBB/DDD` (fd from UsbManager; `/proc/bus/usb` fallback string) | `ioctl`, `libusb_*` internal |
| `libAC020sdk.so` | `4af60e8e941729e87c5c8f572e1f89e2a8f2bf09b1ea9655fd9a1a4298bbc9d3` (M170*), `332764f014cb4f26566fddcea4e3cd055c48ac024247f9f929a7377b33f29869` (FactoryMode) | JNI engine, handle wiring, **vdcmd USB transport** (`iruvc_control_cmd`, `iruvc_usb_data_*`), DFU/upgrade, auto-gain, file read/write | `libusb_control_transfer` (vendor 0x41/0xC1 and DFU class) | same fd | `libusb_control_transfer`, `ircmd_*`, `iruvc_*` |
| `libircmd020.so` | `682fe2a84121b46e53b5237e80fe1d9743624baf3f27e50827e67e8f95d36157` (M170*), `0aa7d5c751379281e6f6e8bfb88bb4b0eed2031b30072c1ccad7034dd3d281ad` (FactoryMode) | command layer: frame headers, CRC16, chunking, ~440 `adv_*`/`basic_*` commands | none directly (callbacks) | – | libc only |
| `libircam.so` | `fe0cf15c29e436ec4ea418f61696ca605255ffa74173e3c928129efdc3e4ddb8` | 0x60-byte control/video handle containers | none | – | libc |
| `libdualcommon.so` | `9f81f2cde0e6b484c8c7832aa4afb77083dbf69eb2f95d9a9fa296a22b8d5b2b` | IR+VL frame pipeline for USB_DUAL_NATIVE_CAM (no USB imports; uses the video handle) | none | – | – |
| `libdualuvccamera020.so`, `libomniircamera020.so` | `851069983240ab1125b09f6f65ec8171c7477f8f42efd8bb1d05f14519d61d8b`, `b489995edd24dc3c43026a384fd3a28ed87c003779a69b58b9a50afe45c976e7` | transports for DriverType USB_DUAL(3) / USB_OMNI(10) | – | – | **not used** by stock (only types 0 and 5 are built) |
| `libadvir*`, `libcommonsdk`, `libmnnmodel`, `libcolormapping`, fusion libs | – | image/radiometry/SR processing | none | – | out of scope |

ABI: devices are arm64; the APKs also carry armeabi-v7a copies (different hashes, same
roles); the 64-bit set is the one loaded.

The thermal module is never accessed through a HAL, daemon, binder service, V4L2 or the
Android camera framework (`../userspace/service-map.md`).
