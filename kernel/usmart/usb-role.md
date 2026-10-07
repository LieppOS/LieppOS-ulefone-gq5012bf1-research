# uSmart USB role behavior

GPIO28 classification is binary and unconditional:

```text
insert LOW → power/route/status → mtk_usb_extcon_set_role(HOST)
remove HIGH → power/route/status → mtk_usb_extcon_set_role(NONE)
```

`mtk_usb_extcon_set_role` allocates a role record and queues zero-delay work on the
single-thread `extcon_usb` workqueue. The worker updates EXTCON_USB_HOST and calls the
existing `usb_role_switch_set_role`; MTU3 then creates/removes xHCI. No accessory VID,
class, current capability or successful enumeration is consulted.

| event | outcome |
|---|---|
| insertion from NONE | HOST; xHCI/root hub appears; usbcore enumerates whatever responds |
| insertion while DEVICE | DEVICE→HOST; external gadget/ADB is disconnected |
| repeated insertion/current HOST | HOST request is queued; worker records HOST |
| removal | always requests NONE, never restores a prior external DEVICE/HOST role |
| role allocation failure | GPIO/status already changed; return ignored, old role remains |
| underlying role-switch failure | worker ignores return and still caches target role |
| `yft_usb_flag=1` | role request skipped after GPIO/status changes |

uSmart itself never sets `yft_usb_flag`; that flag belongs to the internal thermal power
path. No uSmart-specific ownership flag prevents later Type-C events from changing the
role while GPIO55 remains on uSmart.
