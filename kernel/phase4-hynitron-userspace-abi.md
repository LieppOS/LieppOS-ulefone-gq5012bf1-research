# Hynitron userspace ABI

Live stock exposes exactly this root kobject and files:

```
/sys/hynitron_debug/
  hyntpfwver          0644
  hynfwupdate         0644
  hyntprwreg          0644
  hynfwupgradeapp     0644
  hyntpfactorytest    0644
  hyn_gesture_mode    0644
  hyn_gesture_buf     0644
```

Five base attributes are created first; two gesture attributes are added as a
second group on the same kobject. Every `device_attribute` stock object stores
mode 0644.

- `hyntpfwver` show performs a fresh 0xa6 read under mutex and prints
  `chip_version: 0x%02X,module_version:0x%02X,project_version:0x%02X,chip_type:0x%02X,checksum:0x%02X .\n`.
- `hynfwupdate`/`hynfwupgradeapp` are update entrypoints; reconstruction keeps
  names/parsers but default-safe stores return `-EPERM` and never program.
- `hyntprwreg` is the raw debug register parser in stock and is write-capable;
  reconstruction's default-safe store returns `-EPERM` (read usage text only).
- `hyntpfactorytest` invokes stock factory/reset scaffolding; no separate misc
  device/ioctl/proc/debugfs node exists.
- `hyn_gesture_mode` shows/sets gesture framework mode; `hyn_gesture_buf` shows
  last gesture ID/count/points.

No procfs, debugfs, misc device, ioctl, raw character device, or firmware_class
request exists in Hynitron. The stock tiny LCD's misc/sysfs ABI is a separate
driver. Static userspace search found no dedicated Hynitron client; generic
factory/root tooling could access these world-readable/root-writable files.
