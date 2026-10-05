# USB init / property flow (stock, static)

The files involved are all stock:
- `system/etc/init/hw/init.usb.rc` and `init.usb.configfs.rc` (AOSP);
- `system_ext/etc/init/hw/init.usb.rc` (MTK: `kpoc_adbd` service);
- `vendor/etc/init/hw/init.mt6878.usb.rc` (948 lines, MTK platform; imports the system_ext rc);
- `vendor/etc/init/android.hardware.usb{,.gadget}-aidl-service.mediatek.rc`;
- `vendor/etc/init/hw/init.yft.rc` (Ulefone thermal additions).

```text
early boot
  system init.usb.rc  on init: sys.usb.configfs=0
  vendor  init.mt6878.usb.rc on post-fs: vendor.usb.vid=0x0E8D, build configfs g1 (see gadget/configfs.md),
                       mount functionfs adb/mtp/ptp
                       on post-fs-data: via_* (C2K) functions
                       on boot: sys.usb.configfs=1, sys.usb.controller=vendor.usb.controller="11201000.usb0",
                                vendor.usb.acm_cnt=0, acm_enable=0, chmod android_usb iSerial
  system init.usb.rc  on boot && persist.sys.usb.config=* : sys.usb.config=${persist.sys.usb.config}

property sys.usb.config = <cfg>          (set by UsbDeviceManager / USB gadget HAL / boot)
  ├─ AOSP init.usb.configfs.rc: none → UDC "none", stop adbd, ffs.ready=0;
  │                             adb / mtp,adb / ptp,adb … → start adbd
  ├─ vendor init.mt6878.usb.rc:  <cfg> && acm_cnt=N → setprop vendor.usb.pid <PID>
  └─ when sys.usb.ffs.ready=1 (adbd/MTP FunctionFS ready), or immediately for non-FFS configs:
        write configs/b.1/strings/0x409/configuration "<name>"
        write idProduct ${vendor.usb.pid}
        [write /sys/class/udc/11201000.usb0/device/saving 1  (some debug configs)]
        symlink functions/<f> configs/b.1/fN
        write /config/usb_gadget/g1/UDC ${vendor.usb.controller}   ← UDC bind
        setprop sys.usb.state ${sys.usb.config}
```

Gadget HAL (`vendor.usb_gadget_default`, AIDL `IUsbGadget/default` v1) drives:
- `setCurrentUsbFunctions` → `vendor.usb.config` / `sys.usb.config`;
- `/config/usb_gadget/g1/UDC`;
- the `/sys/class/udc/11201000.usb0/{current_speed,soft_connect}` reconnect path (made accessible by its rc `on boot` chown/chmod);
- MTP/PTP FunctionFS endpoint readiness (`vendor.usb.ffs.{mtp,ptp}.ready`).

## Property inventory

| property | set by | meaning |
|---|---|---|
| `persist.sys.usb.config` | framework (persisted) | default function set at boot |
| `sys.usb.config` | framework / gadget HAL / init | requested function set |
| `sys.usb.state` | init (after the UDC write) | applied set |
| `sys.usb.configfs` | vendor rc `on boot` = 1 | selects the configfs triggers (0 = legacy android_usb paths) |
| `sys.usb.controller`, `vendor.usb.controller` | vendor rc = `11201000.usb0` | UDC name |
| `sys.usb.ffs.ready` | adbd / MTP | FunctionFS descriptors written |
| `vendor.usb.vid` / `vendor.usb.pid` | vendor rc | `0x0E8D` / per config (functions.tsv) |
| `vendor.usb.acm_cnt`, `acm_enable`, `acm_port0/1` | MTK engineering mode | ACM add-ons |
| `vendor.usb.config`, `vendor.usb.ffs.{mtp,ptp}.ready` | gadget HAL | HAL-side state |
| `vendor.usb.device.wakeup` | USB HAL | MTU3 device-wakeup control |
| `ro.vendor.usb.kpoc_adb` | vendor build.prop = 0 | KPOC: midi rather than adb |
| `sys.usb.typec.mode` | AOSP legacy | writes `/sys/class/dual_role_usb/otg_default/mode`. **Dead** on this kernel (no dual_role_usb class) |
| `vendor.sys.usb.adb.disabled` → `sys.usb.adb.disabled` | AOSP | adb gate |

The YFT/Ulefone paths (`init.yft.rc`) are:
- `/sys/class/yft_extcon/tiny2c_mode` and `/sys/devices/platform/extcon-usb/uvc_insert_status`, used by the ThermoVue app for the internal-camera host role;
- `/sys/devices/platform/soc/11211000.usb1/mode`, which does not exist (a dead line for an `usb1` the DT never instantiates).
