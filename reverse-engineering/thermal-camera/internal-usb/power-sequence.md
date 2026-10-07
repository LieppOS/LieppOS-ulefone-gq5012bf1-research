# Power / detection / role sequence

Owner per step; code facts from the byte-exact rebuilds (`../fm78100/source/yft_tiny2c_usb.c`
11/12 + probe behaviour-identical; `../../usb/reconstruction/exact-source/extcon-mtk-usb.c`
22/22); timing from the stock capture `usb-research/evidence/thermal-camera-enumeration-log.txt`.

## BOOT (once) — presence/ID detection

| # | step | values / delays | owner |
|---|---|---|---|
| B1 | `yft_tiny2c_usb.ko` loads (vendor_dlkm `modules.load` line 195; depends `mt6375-charger` for `yft_usb_flag`) | – | init |
| B2 | `tiny2c_usb_probe`: parse DT GPIOs 192 (1v8), 191 (3v3), 5v (absent), 149 (io3v3); request each | parse failure → probe returns −1, no sysfs | yft_tiny2c_usb |
| B3 | `tiny2c_usb_power_init(1)`: `gpio_set_value` io3v3 149 = 1 → [5v] → 3v3 191 = 1 → 1v8 192 = 1 | no delay between rails | yft_tiny2c_usb |
| B4 | `i2c_add_driver` → synchronous `tiny2c_usb_i2c_probe(8-003c)`: `msleep(400)`, up to 3 × `read_chipid` (each ≤5 × read reg 0x0000, reg 0x0001), `mdelay(10)` after a non-0x4c59 result; 0x4c59 or any nonzero → OK; 0 → I2C probe −1 | `chip_id` cached | yft_tiny2c_usb (FM78100-COMPANION) |
| B5 | `tiny2c_usb_power_init(0)`: same order, all 0 → **module unpowered after boot** | `yft_usb_flag` untouched (0) | yft_tiny2c_usb |
| B6 | create `tiny2c_usb_mode` (0644) and `sensor_id` (0444); init.yft.rc chmods both 0666 | – | yft_tiny2c_usb / init |

`extcon-mtk-usb` (vendor ramdisk) has already set GPIO 55/152/37 as outputs = 0 and
created `/sys/class/yft_extcon/tiny2c_mode` and `uvc_insert_status`. No USB enumeration of
the module happens at boot (role is not HOST, and rails are off after B5).

## RUNTIME — thermal start (M170infisens `StartPreviewTask`, MODE_DUAL_FUSION)

| t (capture, s) | step | owner | effect |
|---|---|---|---|
| – | `startRestartTimer()` (25 s first-frame watchdog) | app | – |
| 23.942 | `GPIOUtils.powerUpControl()` → write "1\n" to `/sys/devices/platform/yft_tiny2c_usb/tiny2c_usb_mode` | yft_tiny2c_usb | GPIO 149 → [5v] → 191 → 192 = 1, **then** `yft_usb_flag = 1` |
| 23.943 | write "1\n" to `/sys/class/yft_extcon/tiny2c_mode` | extcon-mtk-usb | `mtk_usb_extcon_set_role(HOST)` → `extcon_wq` → `update_role`: (NONE or DEVICE)→HOST, `EXTCON_USB_HOST` = 1, `usb_role_switch_set_role(usb0, HOST)` |
| 23.953 | MTU3 registers xHCI → root hub `usb1` | mtu3 / xhci-mtk | host up 11 ms after the role write |
| 24.676 | `usb 1-1: new high-speed USB device number 2` | module | **0.734 s after rails on** (module ASIC boot from flash) |
| 24.866–24.868 | descriptors, `3474:4321`, `Found UVC 1.10 device Camera` | usbcore / built-in uvcvideo | uvcvideo binds both interfaces |
| 24.865 | `UsbHostManager: USB device attached` | framework | `USB_DEVICE_ATTACHED` broadcast |
| ≥ 24.4 | app: `SystemClock.sleep(500)`, then polls `USBMonitorManager.isDeviceConnected()` every 50 ms, ≤ 9 s | app | `USBMonitor` (attach broadcast + 2 s device-list poll) → `requestPermission` → `openDevice` → `onConnect(ctrlBlock)` |
| later | `initHandleEngine(ctrlBlock)` → userspace claim (`userspace-path.md`) | libAC020sdk / libusbuvccamera020 | uvcvideo detached; both interfaces `driver=usbfs` |

No delay exists in either kernel store; the only waits are the app's (500 ms + poll).
The two sysfs writes are independent (no lock, not atomic).

## RUNTIME — thermal stop (`StopPreviewTask`)

| # | step | owner | effect |
|---|---|---|---|
| S1 | `stopPreview()` → `IrcamEngine.stopVideoStream()` | libusbuvccamera020 | iso URBs cancelled, VS alt 0 |
| S2 | wait (20 ms steps; 200 ms MNN teardown; app-kill path 3 s) | app | – |
| S3 | `GPIOUtils.powerDownControl()`: "0" → `tiny2c_usb_mode` | yft_tiny2c_usb | GPIO 149 → [5v] → 191 → 192 = 0, **then** `yft_usb_flag = 0`; the module loses power → USB disconnect (`USB_DEVICE_DETACHED`, usbfs handles closed) |
| S4 | "0" → `tiny2c_mode` | extcon-mtk-usb | role HOST→NONE: `EXTCON_USB_HOST` = 0, role switch NONE → xHCI unregistered (`11200000.xhci0 driver=` empty) |
| S5 | `SystemClock.sleep(3000)` | app | – |

Stock drops the rails before leaving host mode (no settle delay). Interfaces are released
by the libusb close in the stop/teardown path or implicitly when the device disappears.

## Crash / kill cleanup

`services.jar` `ActivityManagerService.handleAppDiedLocked`: when process
`com.energy.tc2c`, `com.energy.tc2c.sop` or `com.energy.ac020` dies → writes "0" to
`tiny2c_usb_mode`, then "0" to `tiny2c_mode` (same as S3–S4). `com.yft.factorymode`
is **not** in the list.
