# Thermal userspace control path (stock)

No HAL, no vendor daemon, no init service, no binder interface, no ioctl and no I2C access
exist for the thermal camera. Everything is app-level:

| actor | package | path | access |
|---|---|---|---|
| M170infisens | `com.energy.tc2c` (system app) | `GPIOUtils.powerUpControl/powerDownControl` | W `tiny2c_usb_mode` then `tiny2c_mode` (1 / 0) |
| M170infDlp | `com.energy.tc2c.sop` | `sop.utils.GPIOUtils` | same; also firmware/system_cfg update over USB |
| FactoryMode | `com.yft.factorymode` | `InfirayEcoTest(2)` / `InfiraySmtTest` / `VernoInfo` | W both nodes; R `sensor_id` (pass = `0x4c59`) |
| YftSystemUI | system_ext priv-app | — | R `sensor_id`, `uvc_insert_status` |
| ActivityManager | `services.jar` | crash cleanup | W 0 to both nodes when `com.energy.tc2c`, `com.energy.tc2c.sop`, `com.energy.ac020` die |
| USB | all thermal apps | `USBMonitor` → `UsbManager` fd → `libusbuvccamera020.so` (libusb/usbfs) | `/dev/bus/usb/001/NNN` |

Permissions: `init.yft.rc` chmod 0666 `tiny2c_usb_mode`, `tiny2c_mode`, `sensor_id`;
0777 `uvc_insert_status`; SELinux `sysfs_yft_file` (mode nodes), `yft_fmt_device`
(`sensor_id`, `uvc_insert_status`). Dead entries: `/sys/bus/i2c/drivers/fm78100-sensor/*`.
