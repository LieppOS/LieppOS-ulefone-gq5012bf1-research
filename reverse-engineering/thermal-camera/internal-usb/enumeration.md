# Enumeration (runtime)

| step | detail | evidence |
|---|---|---|
| connect | ~0.73 s after rails on (module boots from flash); HS chirp on root port 1 | capture 23.942 → 24.676 |
| enumerate | addr 2, `3474:4321`, bcdDevice 2.00, strings 1/2/3, config 1 (descriptor tree: AC020-UVC `usb-descriptors.md`) | capture 24.866 |
| kernel bind | built-in `uvcvideo` (`Found UVC 1.10 device Camera`), creates its V4L2 node — unused by stock | capture 24.868 |
| framework | `UsbHostManager` attach, `USB_DEVICE_ATTACHED` broadcast; `USB_BOOST audio_boost_work` reacts to the new device (generic MTK boost, not thermal-specific) | capture 24.865 / 26.371 |
| app discovery | `USBMonitor` (UVCCamera library) — `USB_DEVICE_ATTACHED` receiver + device-list poll every 2 s; **no VID/PID filter** in M170infisens (`USBMonitor(ctx, false, listener)`, empty filter list → every device); `onAttach` → `requestPermission` → `onConnect(ctrlBlock)` sets `mUSBDeviceConnected` | decompiled `USBMonitor`, `USBMonitorManager` |
| app wait | `StartPreviewTask`: `sleep(500)` then poll `isDeviceConnected()` every 50 ms for ≤ 9 s; not connected → return without opening (state stays not-OPEN) | `StartPreviewTask` |
| retries | none in kernel or `StartPreviewTask`; app-level recovery: 25 s first-frame `startRestartTimer` → `DEVICE_RESTART` dialog; 3 s `startFrameDataCheck` after stream start → stop + start preview again | `Tiny2CDualFusionProxy`, `UvcNativeCamDualFusionPreviewManager` |
| claim | `uvc_open`: `libusb_set_auto_detach_kernel_driver(1)` → `libusb_claim_interface(0)` = usbfs `DISCONNECT_CLAIM` (detach uvcvideo + claim; fallback string "disconnect-and-claim failed"); VS interface 1 claimed when streaming starts | `libusbuvccamera020.so` |
| result | both `1-1:1.0` and `1-1:1.1` show `driver=usbfs`; `1-1:1.1` at alt 1 while streaming | capture active.txt |
