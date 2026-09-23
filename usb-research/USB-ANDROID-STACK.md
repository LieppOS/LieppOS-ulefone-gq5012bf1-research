# Android and vendor USB stack

## AIDL HALs

The stock vendor image declares and runs:

- `android.hardware.usb.IUsb/default` via `/vendor/bin/hw/android.hardware.usb-aidl-service.mediatekv1.0`;
- `android.hardware.usb.gadget.IUsbGadget/default` via `/vendor/bin/hw/android.hardware.usb.gadget-aidl-service.mediatekv1.0`;
- framework `android.hardware.usb.IUsbManager`.

VINTF declarations:

- `vendor/etc/vintf/manifest/android.hardware.usb-aidl-service.mediatek.xml`;
- `vendor/etc/vintf/manifest/android.hardware.usb.gadget-aidl-service.mediatek.xml`.

Both AIDL HALs are version 1/default. Live binder registration and process state are recorded in `evidence/stock-android-usb-services.txt`.

## Gadget construction

`vendor/etc/init/hw/init.mt6878.usb.rc` is the main platform configuration. It:

- imports the common `init.usb.rc`;
- sets `sys.usb.controller` and `vendor.usb.controller` to `11201000.usb0`;
- enables configfs (`sys.usb.configfs=1`);
- creates gadget `g1` with `idVendor=0x0e8d` and `bcdUSB=0x0200`;
- creates FunctionFS ADB/MTP/PTP functions;
- supports accessory, audio source, MediaTek RNDIS, NCM, MIDI, ACM, mass-storage, HID and C2K modem functions;
- binds the selected configuration by writing `${vendor.usb.controller}` to `g1/UDC`.

The captured configuration was ADB-only:

```text
sys.usb.config=adb
sys.usb.state=adb
sys.usb.controller=11201000.usb0
sys.usb.configfs=1
```

Host descriptors confirm `0e8d:201c`, `bcdUSB 2.00`, manufacturer Ulefone, product Armor 29 Pro and one vendor-specific ADB interface.

The configfs `bcdUSB=0x0200` is consistent with USB2 operation but is not, by itself, proof of hardware limits. The stronger evidence is the DT `maximum-speed`, UDC `maximum_speed` and xHCI root-hub runtime.

## USB HAL permissions and role control

`android.hardware.usb-aidl-service.mediatek.rc` grants the system USB HAL access to:

- `/sys/class/typec/port0/{power_role,data_role,port_type}`;
- configfs gadget/UDC;
- charger `enable_power_path`;
- `extcon-usb/vbus_limit_cur`;
- `/sys/devices/platform/soc/${sys.usb.controller}/mode`.

The HAL therefore coordinates Type-C data/power role, gadget binding and charging power-path controls. The kernel endpoint graph and runtime role switch connect those operations to MTU3.

The gadget HAL rc grants access to UDC `current_speed` and `soft_connect`, enabling Android to report speed and reconnect the gadget without changing DT.

## Ulefone thermal-camera integration

`vendor/etc/init/hw/init.yft.rc` makes these stock ABI surfaces writable:

```text
/sys/devices/platform/yft_tiny2c_usb/tiny2c_usb_mode
/sys/class/yft_extcon/tiny2c_mode
```

It also grants read/write access to `extcon-usb/uvc_insert_status`. The same rc file contains a chmod for `/sys/devices/platform/soc/11211000.usb1/mode`; no such live DT/platform device exists. That line is a dead inherited userspace path, not evidence of a second controller.

The stock system app `M170infisens/M170infisens.apk` (`com.energy.tc2c`, ThermoVue Pro) launches its dual-fusion activity, powers the thermal rails and requests the internal route. On attachment, Android sends `android.hardware.usb.action.USB_DEVICE_ATTACHED` back to its splash activity. Native AC020/libusb/libuvc code claims both UVC interfaces through `usbfs` and streams at about 25 sensor frames/s.

## SELinux integration

Stock vendor policy includes:

- executable label `mtk_hal_usb_exec` for the MediaTek AIDL USB service;
- `sysfs_usb_nonplat` labels for MTU3 UDC, role/mode and xHCI root-hub paths;
- `sysfs_yft_file` for `/class/yft_extcon/tiny2c_mode`;
- HAL server-domain membership for `mtk_hal_usb`.

The policy contains generic labels for possible `usb1`, `usb2` and `usb3` root-hub names below `11200000.xhci0`. Those predeclared labels do not prove three physical buses or SuperSpeed support. In the controlled thermal-host runtime, only the 480-Mbit/s `usb1` root hub existed.

## Lineage device-tree implications

The current device tree at `/mnt/SamsungSSD/android/lineage-22.2/device/ulefone/armol` is minimal and relies heavily on stock proprietary files. A complete LieppOS integration must preserve:

- both AIDL HAL declarations and rc files;
- `init.mt6878.usb.rc` configfs setup;
- controller property `11201000.usb0`;
- Ulefone thermal sysfs permissions;
- matching vendor SELinux types/rules;
- the ThermoVue APK/native libraries if stock thermal functionality is required;
- USB function modules and vendor-ramdisk load order.

Deleting the seemingly stale YFT controls or replacing the USB HAL with a generic implementation can leave the thermal path powered but unrouted, route it without rails, or fail to recover external gadget mode.
