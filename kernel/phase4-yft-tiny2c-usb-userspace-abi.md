# yft_tiny2c_usb userspace ABI

## Interfaces owned by this module

| path/name | declared mode | stock init mode | show/store contract |
|---|---:|---:|---|
| `/sys/devices/platform/yft_tiny2c_usb/tiny2c_usb_mode` | 0644 (`DEVICE_ATTR_RW`) | chmod 0666 | show four raw GPIO values; store power state |
| `/sys/devices/platform/yft_tiny2c_usb/sensor_id` | 0444 (`DEVICE_ATTR_RO`) | chmod 0666 | show cached chip ID only |

No class/driver attribute, misc device, procfs, debugfs, ioctl, uevent generator, or module
parameter exists. `/sys/class/yft_extcon/tiny2c_mode` is a separate
`extcon-mtk-usb.ko` ABI and must not be attributed to this module.

## Exact formats and parser behavior

### `tiny2c_usb_mode` show

```text
gpio_1v8=%d,gpio_3v3=%d,gpio_5v=%d,gpio_io3v3:%d\n
```

Values are read at show time through `gpiod_get_raw_value(gpio_to_desc(...))`; there is no
cached mode. Buffer limit is 4096. If the passed device pointer is NULL, stock logs
`tiny2c_usb_mode_show. dev is null!!` and returns 0 bytes.

### `tiny2c_usb_mode` store

- Parser: `sscanf(buf, "%d", &en)`; return count is ignored.
- `en=1`: all available rail slots raw-high, then `yft_usb_flag=1`.
- `en=0`: all available rail slots raw-low, then `yft_usb_flag=0`.
- Unparsable input: `en` was initialized to zero, so it performs the power-off path.
- Any other integer: logs `tiny2c_usb_mode_store: fail: %d`, leaves state unchanged.
- Return: always the supplied byte count, including parse failure or unsupported values.
- No lock, delay, GPIO error propagation, or provider acknowledgement.

### `sensor_id` show

```text
0x%x\n
```

It reports the global cached by I2C probe; reading sysfs does not access I2C. NULL device
behavior matches mode show (same log, zero-byte return).

## Stock access-control and clients

- `vendor/etc/init/hw/init.yft.rc` lines 249-251 chmod the two coordinated mode paths 0666;
  line 280 chmods `sensor_id` 0666 despite the kernel attribute being show-only.
- SELinux genfs labels platform mode and extcon mode as `sysfs_yft_file`; platform/radio
  domains receive read/write/open/append permissions. `sensor_id` is labeled
  `yft_fmt_device`, readable by platform/radio/system app domains.
- `M170infDlp.apk` (`com.energy.tc2c.sop`) writes `1\n`/`0\n` to platform mode and then
  extcon mode through `GPIOUtils`.
- `M170infisens.apk` (`com.energy.tc2c`) contains the same two-path `GPIOUtils` and uses it
  in thermal-preview startup/shutdown.
- `FactoryMode.apk` `InfirayEcoTest` writes literal `1` then registers `USBMonitor`; it
  unregisters before writing literal `0`. `InfiraySmtTest` reads `sensor_id` and requires
  trimmed text `0x4c59`.
- `services.jar` ActivityManager crash cleanup writes 0 to both paths when
  `com.energy.tc2c`, `com.energy.tc2c.sop`, or `com.energy.ac020` dies.
- `YftSystemUI.apk` references `sensor_id` for device feature/UI integration; no write to
  this module was found.
