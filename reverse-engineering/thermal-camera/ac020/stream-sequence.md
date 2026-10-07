# Stream start / stop (static; stock M170infisens, dual-fusion mode)

Power/role steps are already closed (FM78100-COMPANION `power-sequence.md`, USB stack);
timestamps from the controlled capture `usb-research/evidence/thermal-camera-enumeration-log.txt`.

## Start

| # | step | component | wire effect |
|---|---|---|---|
| 1 | `GPIOUtils.powerUpControl()`: write `1` → `/sys/devices/platform/yft_tiny2c_usb/tiny2c_usb_mode` | yft_tiny2c_usb | GPIO 149 → 191 → 192 high, `yft_usb_flag=1` (t=23.942) |
| 2 | write `1` → `/sys/class/yft_extcon/tiny2c_mode` | extcon-mtk-usb | role NONE→HOST, xHCI root hub up (23.953) |
| 3 | module ASIC boots from its flash | module | HS enumeration 3474:4321 at 24.676–24.866 (≈0.73 s after rails); GET_DESCRIPTORs; SET_CONFIGURATION 1; `uvcvideo` binds |
| 4 | `StartPreviewTask`: sleep 500 ms, then poll `USBMonitorManager.isDeviceConnected()` every 50 ms (≤ 9 s) | app | Android permission / `UsbManager.openDevice` → fd |
| 5 | `initHandleEngine(ctrlBlock)` → `native_init_handle_engine` (DriverType 5): video handle (`iruvc_camera_handle_create`), control handle (`iruvc_usb_handle_create`, polling 2000 ms), `ircmd_create_handle`, DFU handle | libAC020sdk | `iruvc_usb_device_open`: libusb wraps the fd, reads descriptors, detaches `uvcvideo`, claims if0/if1 (`driver=usbfs`), libuvc `uvc_open` scans VC/VS descriptors and submits the interrupt transfer on 0x83 |
| 6 | `onSuccess`: `IrcmdEngineTaskHelper.mirrorAndFlipStatusSet()` | libircmd020 | vdcmd `basic_mirror_and_flip_status_set` (0x10/0x10/0x43) — OUT 0x20 + status 0x22 |
| 7 | `handleDualCalFileRead()` | libAC020sdk `adv_file_read` | `adv_cfg_file_open/read/close` (module 0x08) — read of the module-resident fusion calibration file |
| 8 | `TempCompensation.getNucTData()`; `SystemClock.sleep(100)` | app / vdcmd reads as needed | – |
| 9 | `startPreview()` → `IrcamEngine.startVideoStream()` → `native_video_stream_start` → video handle start → `UVCCamera::setPreviewSize(256, 386, 25, 25, mode 1, 1.0)` | libusbuvccamera020 | VS_PROBE SET_CUR/GET_CUR(/MIN/MAX) + VS_COMMIT for format 1 / frame 2 / interval 400000 |
| 10 | `UVCCamera::startPreview` → `uvc_start_streaming_bandwidth` | libusbuvccamera020 | SET_INTERFACE if1 alt 1; iso URBs on 0x81 |
| 11 | frames → `iruvc` frame callback → `IrcamEngine` → `mIrFrameCallback` | app | 197 632 B per frame @25 Hz; split image / info / temperature (`frame-format.md`) |
| 12 | runtime commands (user/automatic) | libircmd020 | FFC (`basic_ffc_update`), auto-FFC, gain switch, sun-detect, shutter-tab, … (`vendor-opcodes.tsv`) |
| 13 | visible camera (fusion) | Camera2 | unrelated to USB |

No vendor "preview start" command is sent: streaming is controlled solely by UVC
probe/commit + alternate setting. `basic_preview_stop`/`thermometry_preview_start`
exist in the library but have no stock caller.

## Stop (`StopPreviewTask`)

| # | step | wire effect |
|---|---|---|
| 1 | `stopPreview()` → `IrcamEngine.stopVideoStream()` → `uvc_stop_streaming` | iso URBs cancelled (DISCARDURB), SET_INTERFACE if1 alt 0 |
| 2 | wait (20 ms steps; app-kill path waits 3 s) | – |
| 3 | `GPIOUtils.powerDownControl()`: `tiny2c_usb_mode` 0 | rails off → device disappears (disconnect) |
| 4 | `tiny2c_mode` 0 | role HOST→NONE |
| crash | `services.jar` ActivityManager writes 0 to both nodes when `com.energy.tc2c`/`.sop`/`com.energy.ac020` dies | same as 3–4 |

Not performed live (static reconstruction only).
