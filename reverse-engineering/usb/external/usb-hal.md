# Android USB HAL and framework ownership

```text
system_server `usb` service (`android.hardware.usb.IUsbManager`)
  ├─ UsbPortManager
  │    → android.hardware.usb.IUsb/default, AIDL v1
  │       `/vendor/bin/hw/android.hardware.usb-aidl-service.mediatekv1.0`
  │       service `vendor.usb_default`
  │       → Type-C/role/MTU3/power sysfs
  ├─ UsbDeviceManager
  │    → android.hardware.usb.gadget.IUsbGadget/default, AIDL v1
  │       `/vendor/bin/hw/android.hardware.usb.gadget-aidl-service.mediatekv1.0`
  │       service `vendor.usb_gadget_default`
  │       → USB properties + configfs/UDC/FunctionFS readiness
  └─ UsbHostManager
       → usbfs/usbhost monitor → app attach/permission APIs
```

Both VINTF instances are `/default`, version 1. Live binder capture contains both plus the
framework `usb` service.

## `IUsb/default` surfaces

| API responsibility | stock kernel surface |
|---|---|
| query port status | `/sys/class/typec/port0/{data_role,power_role,port_type}`, partner PD status, `/sys/class/usb_role/*/role`, MTU3 `role_mode` |
| switch data/power/mode role | write Type-C class attributes → exact `rt_pd_manager` → TCPC swap/postpone; rc also permits MTU3 `/mode` |
| limit power transfer | extcon `vbus_limit_cur` (1.8 A ↔ 0.5 A source limit); charger `enable_power_path` on sink side |
| enable/disable USB data | configfs `g1/UDC` unbind/rebind |
| reset port | implemented callback; exact internal mechanism not decompiled, bounded to HAL/kernel interfaces |
| contaminant control | reports unsupported/error; kernel MT6375 water detection is autonomous |
| port events | Type-C and usb_role_switch uevents |

Normal automatic attach/detach does **not** wait for the HAL: TCPC/charger/extcon perform
role selection in kernel. HAL role APIs are explicit framework/user requests.

## `IUsbGadget/default` surfaces

- `setCurrentUsbFunctions`: drives `vendor.usb.config`/`sys.usb.config`; init performs
  symlink/PID/UDC actions.
- `getUsbSpeed`: reads UDC `current_speed` (maximum HS).
- reconnect: UDC `soft_connect`.
- MTP/PTP: polls FunctionFS endpoints and publishes `vendor.usb.ffs.{mtp,ptp}.ready`.

SELinux labels the MediaTek HAL executable/domain and the USB/configfs/typec sysfs paths.
Thermal and uSmart control nodes are not HAL APIs; their apps/kernel glue directly alter
the shared role.
