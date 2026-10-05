# Android USB HAL boundary (interface level only)

| HAL | VINTF | executable (sha256 prefix, size) | rc service | links |
|---|---|---|---|---|
| `android.hardware.usb.IUsb/default` **AIDL v1** | `vendor/etc/vintf/manifest/android.hardware.usb-aidl-service.mediatek.xml` | `/vendor/bin/hw/android.hardware.usb-aidl-service.mediatekv1.0` (`2a4aa9eea147c408`, 111 144 B) | `vendor.usb_default`, class hal, user/group system | `android.hardware.usb-V1-ndk`, libbase, libbinder_ndk, libcutils, liblog, libutils. **No vendor-private libraries** |
| `android.hardware.usb.gadget.IUsbGadget/default` **AIDL v1** | `…usb.gadget-aidl-service.mediatek.xml` | `/vendor/bin/hw/android.hardware.usb.gadget-aidl-service.mediatekv1.0` (`ff1ce34b3501a202`, 37 696 B) | `vendor.usb_gadget_default`, class hal, user system, groups system mtp shell | `android.hardware.usb.gadget-V1-ndk`, `android.frameworks.stats-V1-ndk`, libhidlbase, libhardware, … |

## IUsb kernel touch-points (from strings + rc permissions)

| API | kernel surface |
|---|---|
| `queryPortStatus` / port status callback | `/sys/class/typec/port*` (`data_role`, `power_role`, `port_type`, `-partner/supports_usb_power_delivery`), `/sys/class/usb_role/*-role-switch/role` (`getDataRoleFromRoleSwitch`), MTU3 `role_mode`, uevents `DEVTYPE=typec_*` and `DEVTYPE=usb_role_switch` |
| `switchRole` (data/power/mode) | write `/sys/class/typec/port0/{data_role,power_role,port_type}` → `rt_pd_manager` `dr_set`/`pr_set`/`port_type_set` → TCPC DR/PR swap or role postpone. `/sys/devices/platform/soc/${sys.usb.controller}/mode` (MTU3 `mode_store`: 0 OFF / 1 DUAL / 2 HOST / 3 DEVICE operation mode) is made writable by its rc |
| `limitPowerTransfer` | `/sys/devices/platform/extcon-usb/vbus_limit_cur` (extcon: OTG VBUS current 1.8 A ↔ 0.5 A). The sink side also uses `/sys/devices/platform/charger/enable_power_path` |
| `enableUsbData` / `enableUsbDataWhileDocked` | `/config/usb_gadget/g1/UDC` (unbind/rebind). The callbacks are implemented (`notifyEnableUsbDataStatus`) |
| `enableContaminantPresenceDetection` | callback reports error/not supported (string `enableContaminantPresenceDetection error`). **No HAL control** of the TCPC water detection, which runs autonomously in the kernel (`tcpc,en-wd`) |
| device wakeup | `vendor.usb.device.wakeup` → "enable device wakeup %s" |
| `resetUsbPort` | implemented ("Userspace reset USB Port", `notifyResetUsbPortStatus`). The mechanism is not decompiled (likely UDC unbind/rebind) |
| compliance warnings, DisplayPort alt-mode status | no strings found: not implemented (AIDL v1 has no such API) |

## IUsbGadget

- Function selection is through `vendor.usb.config` / `sys.usb.config` properties (see `init-property-flow.md`) and `/config/usb_gadget/g1/UDC`.
- `getUsbSpeed` reads `/sys/class/udc/11201000.usb0/current_speed`. The maximum is HS on this device.
- The reconnect uses `soft_connect`, and MTP/PTP readiness comes from the `/dev/usb-ffs/{mtp,ptp}/ep1..3` poll.

## Boundary statement

Both HALs are thin, proprietary MediaTek AOSP-derivative services. Every kernel interface they use is provided by the exactly-rebuilt modules (`mtu3`, `extcon-mtk-usb`, `rt_pd_manager`) or by GKI (typec class, usb_role class, configfs, UDC class). A replacement HAL (for example AOSP `android.hardware.usb-service.example` with a gadget HAL) needs only these sysfs paths. The Ulefone thermal paths are driven by the ThermoVue app, not by the HAL.
