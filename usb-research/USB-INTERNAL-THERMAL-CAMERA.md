# Internal thermal-camera USB path

> **2026-10-07:** integration closed in `reverse-engineering/thermal-camera/internal-usb/` (INTERNAL-THERMAL-USB DONE). That folder supersedes the GPIO 55/152, `tiny2c_mode` and FM78100 statements below; see its `stale-claims.md`. The runtime capture here remains the primary enumeration evidence.

## Verdict

The ThermoVue module is a normal **USB 2.0 High-Speed UVC 1.10 device** directly attached to root port 1 of `11200000.xhci0`, the host-controller child of `11201000.usb0`.

Classification: **PROVEN by controlled stock runtime enumeration**.

It is not attached through a second `11211000.usb1` controller, and no internal USB hub appears between the MT6878 host controller and the thermal module.

## Controlled stock-runtime evidence

The test was run only after confirming slot `_a`, `sys.boot_completed=1`, idle `tiny2c_mode=0`, and all thermal rail GPIOs off. The reproducible on-device procedure is `scripts/capture_internal_thermal_usb_device.sh`.

The stock `com.energy.tc2c` launcher was started, the device-local script waited while external ADB disappeared, captured sysfs and logs, returned Home, stopped the app, restored both stock mode controls to `0`, and verified the idle state. No partition, RPMB, calibration, NVRAM or persist write occurred.

Evidence:

- `evidence/thermal-camera-enumeration-log.txt` — selected stock kernel/framework enumeration lines;
- `evidence/thermal-camera-active-sysfs.txt` — active device, interfaces, speed and driver bindings;
- `evidence/thermal-camera-transition-sysfs.txt` — pre/active/Home/restored states;
- `scripts/capture_internal_thermal_usb_device.sh` — exact capture and cleanup procedure.

## Exact USB identity

| Field | Observed value | Classification |
|---|---|---|
| bus/port | `1-1` | PROVEN |
| root hub | `usb1`, serial `11200000.xhci0` | PROVEN |
| VID:PID | `3474:4321` | PROVEN |
| bcdDevice | `2.00` | PROVEN |
| manufacturer | `Thermal Cam Co.,Ltd` | PROVEN |
| product | `Camera` | PROVEN |
| serial | `202206223` | PROVEN for tested unit |
| negotiated speed | `480` Mbit/s / High-Speed | PROVEN |
| UVC revision | UVC `1.10` | PROVEN from kernel enumeration |
| device class | `ef/02/01` | PROVEN |
| Android audio/HID/storage flags | `false/false/false` | PROVEN |

The kernel reported:

```text
usb 1-1: new high-speed USB device number 2 using xhci-mtk
usb 1-1: New USB device found, idVendor=3474, idProduct=4321, bcdDevice=2.00
usb 1-1: Found UVC 1.10 device Camera (3474:4321)
```

This is direct negotiated-speed evidence. The internal camera is neither Full-Speed nor SuperSpeed.

## Interfaces and userspace ownership

The active sysfs snapshot contains two interfaces:

- `1-1:1.0`: class `0e`, subclass `01`, protocol `00` — UVC VideoControl;
- `1-1:1.1`: class `0e`, subclass `02`, protocol `00` — UVC VideoStreaming.

Both show driver `usbfs` during operation. This is consistent with the stock app's bundled libusb/libuvc stack claiming the interfaces from userspace instead of leaving them on the kernel `uvcvideo` driver. Existing APK/native analysis in `qwen_hardware/qwen-thermal/re/usb-transport.md` and the AC020 libraries independently predicts that architecture.

No additional non-UVC interface was enumerated in this capture. Proprietary camera commands may still travel over UVC control transfers or vendor controls; the descriptor evidence does not show a separate proprietary interface.

## Root topology and absence of an internal hub

Active topology:

```text
11201000.usb0 (MTU3 dual-role core)
|
+-- 11200000.xhci0, driver xhci-mtk
    |
    +-- usb1 root hub, 1d6b:0002, 480 Mbit/s
        |
        +-- port 1: 3474:4321, Thermal Cam Co.,Ltd Camera, 480 Mbit/s
```

The device path is `1-1`, not `1-1.1` or another downstream chain, and the snapshot contains no hub-class device between the root hub and camera. Classification: **PROVEN for the observed stock configuration**.

## Power, routing and role transition

At launch, stock logs show:

```text
tiny2c_usb_mode_store: power on: 1
[store_tiny2c_mode] yft_tiny2c_status=1
```

The thermal rail state then becomes:

```text
gpio_1v8=1,gpio_3v3=1,gpio_5v=0,gpio_io3v3=1
```

At the same time:

- the external gadget UDC changes to `current_speed=UNKNOWN`, `state=not attached`;
- `11200000.xhci0` binds to `xhci-mtk`;
- the internal root hub and camera enumerate;
- external wired ADB disappears.

On return Home, the rail GPIOs return to zero, the USB device tree empties and xHCI becomes unbound. The UDC remains physically detached until the external cable is replugged, after which normal 480-Mbit/s gadget operation returns.

The active snapshot reads `tiny2c_mode=0` even though the launch log records a write of `1`. Therefore `tiny2c_mode` must not be treated as a stable camera-power indicator; it is a routing/role transition control whose reported state may be reset after the transition. The rail state and USB enumeration are the authoritative active-state witnesses.

## Relationship to `yft_tiny2c_usb` and I2C `8-003c`

`yft_tiny2c_usb.ko` is not a USB host/device bridge. Its imported-symbol and control-flow evidence shows rail/ID glue, while runtime proves the actual image transport is a normal USB device under xHCI.

- platform node `/yft_tiny2c_usb` controls 1.8-V, 3.3-V and I/O 3.3-V rails;
- live `sensor_id=0x4c59` identifies the module variant;
- DT node `/soc/i2c@11e03000/fm78100@0x3c`, Linux bus/address `8-003c`, binds the `mediatek,tiny2c_usb` companion;
- image/control transport enumerates separately as USB `3474:4321`.

Classification: **PROVEN** that I2C/power glue is not the image-data transport; the exact FM78100 register-level responsibilities remain **UNKNOWN**.

## Shared-fabric conclusion

Normal external gadget operation:

- UDC `11201000.usb0` is configured at High-Speed;
- child `11200000.xhci0` is unbound;
- the Linux host sees the phone at 480 Mbit/s.

Internal thermal operation:

- that same UDC becomes not attached;
- the child `11200000.xhci0` binds as host;
- root hub serial `11200000.xhci0` exposes the camera at port 1;
- external wired ADB disappears.

This proves that external gadget and internal camera operation use mutually switched roles/routes of the same MTU3/USB2 fabric in the tested stock behavior. A second controller is not involved.

## Remaining unknowns

- the exact analog switch/load-switch part numbers behind GPIOs 55 and 152;
- the PCB net names and physical traces between XS-PHY, switch, internal module and Type-C daughterboard;
- whether unused host ports exist electrically despite not appearing in the active topology;
- whether the internal module supports additional alternate settings/endpoints not selected during this capture;
- whether a redesigned board could provide simultaneous internal camera and external USB data.
