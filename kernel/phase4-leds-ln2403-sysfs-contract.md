# LN2403 sysfs ABI

The three `DEVICE_ATTR` files are created directly under the bound platform
device `/sys/devices/platform/yft_camplight/`:

| file | kernel mode | stock init mode | read | write |
|---|---:|---:|---|---|
| `camplight_mode` | 0644 | 0777 | exact mode name + newline | signed `%d`; modes 0..5 |
| `camplight_set_brightness` | 0644 | 0777 | internal duty + newline | signed `%d`; 0 off, nonzero PWM |
| `leds_ctl` | 0644 | 0777 | exact warning mode name + newline | signed `%d`; modes 0..6 |

All stores return `count`, including parse failure and range errors. There are
no class devices, `/sys/class/leds` entries, ioctls, character devices, input
events, netlink, debugfs, module parameters, or exported symbols.

Stock `vendor_file_contexts` labels all three canonical files
`u:object_r:sysfs_yft_file:s0`. `init.yft.rc` lines 222–224 chmod all three
canonical paths 0777, and intended system/YFT clients receive policy access.
The same rc also chmods legacy
`/sys/devices/platform/soc/soc:gftk_camplight/camplight_mode` at line 113; that
extra path does not match the current `/yft_camplight` DT node and must not
replace the canonical ABI.
