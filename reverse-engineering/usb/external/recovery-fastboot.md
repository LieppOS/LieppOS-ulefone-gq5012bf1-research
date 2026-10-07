# Recovery / fastbootd / bootloader boundary

Static evidence from stock recovery vendor ramdisk
`workspace/gq5012bf1/stock/vendor-ramdisks/recovery.cpio` (6,038,528 bytes,
SHA256 `fbfa50e3863e3c6a9f1443c5dfcf8ebf713ecfd9f8355ec54b016100a75f9a3a`):

| item | recovered value | class |
|---|---|---|
| recovery init | `sys.usb.configfs=1`, `sys.usb.controller=11201000.usb0` | PROVEN |
| recovery VID | `ro.recovery.usb.vid=18D1` | PROVEN property |
| recovery ADB PID | `ro.recovery.usb.adb.pid=D001` | PROVEN property |
| recovery fastboot/fastbootd PID | `ro.recovery.usb.fastboot.pid=4EE0` | PROVEN property |
| ADB security | `ro.adb.secure=1` | PROVEN property |
| fastbootd support | recovery UI contains `fastbootd.png`; fastboot PID/config properties present | STRONGLY SUPPORTED statically |

Recovery/fastbootd are device-mode gadget uses of the same `11201000.usb0` UDC and same
external D+/D− physical path; host/xHCI is irrelevant. Therefore the hardware USB2
High-Speed ceiling applies in recovery too. Recovery has its own init/property contract,
not the normal Android gadget HAL lifecycle.

The exact pre-Android bootloader fastboot implementation/descriptors were not recovered
from the available artifacts and are not inferred from recovery. It necessarily uses the
same receptacle and U2-only controller hardware, but its VID/PID, service policy and
recovery behavior are outside normal Android EXTERNAL-USB closure. No bootloader or
recovery mode was started during this offline pass.
