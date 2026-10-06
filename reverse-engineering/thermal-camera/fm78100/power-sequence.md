# Thermal power / ID / USB sequence (static, stock)

All steps below are read from stock binaries (byte-identical rebuild for `yft_tiny2c_usb.ko`,
exact rebuild for `extcon-mtk-usb.ko`) and decompiled stock APKs. Timestamps come from the
existing controlled capture `usb-research/evidence/thermal-camera-enumeration-log.txt`.

## 1. Boot (once) — presence/ID read at 8-003c

`yft_tiny2c_usb` is loaded from vendor_dlkm `modules.load` line 195.

1. `tiny2c_usb_probe()` (platform `/yft_tiny2c_usb`): `kmalloc(20)`; parse+request GPIOs in
   order 1v8 (192), 3v3 (191), 5v (absent → negative, skipped), io3v3 (149).
2. `tiny2c_usb_power_init(1)`: raw-high in order **io3v3 149 → [5v] → 3v3 191 → 1v8 192**,
   no delay between rails.
3. `i2c_register_driver(tiny2c_usb_i2c_driver)` → synchronous `tiny2c_usb_i2c_probe(8-003c)`:
   `msleep(400)` (module boot), then up to 3 × `tiny2c_usb_read_chipid()`
   (each = up to 5 × [read reg 0x0000, read reg 0x0001]), `mdelay(10)` after each
   non-`0x4c59` result. `0x4c59` → success; any other nonzero → success; 0 → `-1`.
4. `tiny2c_usb_power_init(0)`: all rails low (same order). **The module is unpowered after
   boot.** `yft_usb_flag` is not touched during probe.
5. Create `tiny2c_usb_mode` (0644) and `sensor_id` (0444); init.yft.rc chmods both 0666.

Quirk: if `i2c_register_driver` fails the function returns before step 4, leaving rails high.

## 2. Thermal start (app)

`GPIOUtils.powerUpControl()` (M170infisens `com.energy.tc2c`, M170infDlp `com.energy.tc2c.sop`;
FactoryMode `InfirayEcoTest` writes the same two nodes):

| t (capture) | step | owner | effect |
|---|---|---|---|
| 23.942 | write `1` → `/sys/devices/platform/yft_tiny2c_usb/tiny2c_usb_mode` | yft_tiny2c_usb | GPIO 149 → [5v] → 191 → 192 high, then `yft_usb_flag = 1` (charger BC1.2 + extcon Type-C/ID role events ignored) |
| 23.943 | write `1` → `/sys/class/yft_extcon/tiny2c_mode` | extcon-mtk-usb | `queue_delayed_work(extcon_wq, update_role, 0)` → NONE→HOST: `extcon_set_state_sync(EXTCON_USB_HOST,1)` + `usb_role_switch_set_role(HOST)` |
| 23.953 | xHCI root hub `usb1` registered | MTU3/xhci-mtk | host mode up |
| 24.676 | `usb 1-1: new high-speed USB device number 2 using xhci-mtk` | module | ≈0.73 s after rails on (module ASIC boot) |
| 24.866 | `3474:4321`, Mfr "Thermal Cam Co.,Ltd", Product "Camera", Serial "202206223"; `Found UVC 1.10 device Camera` | GKI uvcvideo (built-in) | generic UVC binds first |
| later | app gets permission via `USBMonitor`, libusb `detach_kernel_driver` + claim → both interfaces show `driver=usbfs` | libusbuvccamera020 | userspace streaming + vendor control |

No I2C traffic to 0x3c happens at thermal start. No GPIO 55/152/28/37 change happens.
No explicit delay exists in either kernel store; the apps poll `USBMonitor` for attach.

## 3. Thermal stop

`GPIOUtils.powerDownControl()` / FactoryMode `onDestroy`, and `services.jar`
ActivityManager crash cleanup when `com.energy.tc2c`, `com.energy.tc2c.sop` or
`com.energy.ac020` dies:

1. App stops the stream and closes libusb (FactoryMode unregisters `USBMonitor` first).
2. write `0` → `tiny2c_usb_mode`: rails low (149 → [5v] → 191 → 192), then `yft_usb_flag = 0`.
   The device disappears from the bus here (power loss = disconnect).
3. write `0` → `tiny2c_mode`: role work HOST→NONE (`EXTCON_USB_HOST=0`, role switch NONE).

Note the stock order drops the rails *before* leaving host mode; there is no settle delay.

## 4. Mode node semantics

| input to `tiny2c_usb_mode` | rails | `yft_usb_flag` |
|---|---|---|
| `1` | on | 1 (after rails) |
| `0` or unparsable | off | 0 (after rails) |
| other integer | unchanged ("fail: %d") | unchanged |

`tiny2c_mode` store: `1` → HOST, anything else → NONE; its show always prints `0`
(`yft_tiny2c_status` is never assigned in stock).

## 5. What is not in the chain

- GPIO 152 (`uvc_vbus_gpio`) and GPIO 55 (`uvc_switch_gpio`): uSmart accessory only (ID pin 28).
- MT6375 OTG VBUS / `otg_gpio_select` 37: Type-C source path only.
- No reset GPIO, no regulator API, no pinctrl, no clock for the module.
