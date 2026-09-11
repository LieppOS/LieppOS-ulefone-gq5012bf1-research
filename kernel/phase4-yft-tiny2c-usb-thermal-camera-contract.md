# yft_tiny2c_usb thermal-camera relationship

## Stock chain

```text
ThermoVue Pro (`com.energy.tc2c`) / TC2C SOP (`com.energy.tc2c.sop`)
FactoryMode InfirayEcoTest / InfiraySmtTest
       │ writes rail mode; reads cached ID
       ▼
/sys/devices/platform/yft_tiny2c_usb/{tiny2c_usb_mode,sensor_id}
       │
       ├─ GPIO 192/191/149 low-voltage enables
       └─ I2C8 address 0x3c ID registers 0/1

same applications coordinate /sys/class/yft_extcon/tiny2c_mode
       ▼
extcon-mtk-usb / MT6375 / USB1 routing and VBUS
       ▼
internal InfiRay/InfiSense AC020-family UVC device
       ▼
USBMonitor + libusbuvccamera020/libAC020sdk + thermal processing/radiometry libraries
```

## Exact stock userspace evidence

- `system/app/M170infisens/M170infisens.apk`: thermal app package
  `com.energy.tc2c`, label ThermoVue Pro, with AC020/UVC native stack.
- `system/app/M170infDlp/M170infDlp.apk`: SOP/manufacturing package
  `com.energy.tc2c.sop`. Its `GPIOUtils` writes platform `tiny2c_usb_mode` first,
  then extcon `tiny2c_mode`, with 1 for power-up and 0 for power-down.
- `system/app/FactoryMode/FactoryMode.apk`: `InfirayEcoTest` performs the same ordered
  two-node writes, then registers `USBMonitor`. It unregisters the monitor before writing
  both nodes to 0. `InfiraySmtTest` reads `sensor_id` and accepts exact text `0x4c59`.
- `system/framework/services.jar`: `ActivityManagerService.handleAppDiedLocked` catches
  death of `com.energy.tc2c`, `com.energy.tc2c.sop`, or `com.energy.ac020` and writes 0 to
  both nodes as crash cleanup.
- Native libraries include `libusbuvccamera020.so`, `libAC020sdk.so`, command/parse/image
  and radiometry libraries. Imaging traffic is through Android USB/libusb UVC, not the
  module's I2C transfers.
- No thermal VID/PID is safely instance-proven by this static module/DT corpus; bundled SDK
  descriptor tables are multi-product and are not treated as the attached device identity.

## Control conclusion

ThermoVue-related applications **directly control this module's power sysfs node**; USB
enumeration alone is not sufficient because userspace first turns on the low-voltage rails
and selects the paired extcon mode. Conversely, `yft_tiny2c_usb` does not stream frames,
implement UVC, provide Android Camera HAL integration, or calculate temperatures.

`tiny2c_usb_i2c_probe` caches a chip ID. The preferred production value is `0x4c59`; after
up to three wrapper reads, stock accepts any nonzero final cached value and fails only on
zero. FactoryMode is stricter and enables its Pass button only for formatted `0x4c59`.
