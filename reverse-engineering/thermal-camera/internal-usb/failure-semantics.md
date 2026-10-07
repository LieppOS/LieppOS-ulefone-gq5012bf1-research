# Failure semantics (static)

| failure | kernel behaviour | userspace behaviour | evidence |
|---|---|---|---|
| boot I2C ID read returns 0 (module absent/dead) | I2C probe −1 (8-003c unbound); platform probe continues: rails off, `tiny2c_usb_mode`/`sensor_id` still created; `sensor_id` = `0x0` | FactoryMode SMT test fails; thermal apps do **not** check `sensor_id` → power/role writes still work; USB enumeration does not depend on the I2C result | yft_tiny2c_usb source; app sources |
| I2C read nonzero but ≠ 0x4c59 | treated as success (any nonzero) | `sensor_id` shows that value; SMT test fails | source |
| `i2c_add_driver` fails | probe returns before rails-off and before sysfs creation → rails left **on**, no `tiny2c_usb_mode` node (thermal unusable) | – | source (stock quirk) |
| DT GPIO parse failure | probe −1, no sysfs | thermal unusable | source |
| power write with other integer | "fail: %d", rails/flag unchanged | – | source |
| rails on but module never connects | role stays HOST, flag 1 | `StartPreviewTask` gives up after 500 ms + 9 s; 25 s restart timer → `DEVICE_RESTART` dialog; rails/role stay on until stop/app death | app sources |
| wrong VID/PID / other device on the host | no kernel filter | no VID/PID filter in M170infisens `USBMonitor`; the SDK opens whatever device it is given; stream fails at format negotiation (exact 256×386 YUY2 match, −51) or vdcmd status; first-frame/frame-data timers then restart | AC020-UVC `uvc-capabilities.md`; app sources |
| permission denied | – | `processCancel`; never `onConnect` → wait loop times out | `USBMonitor` |
| uvcvideo detach / claim failure | usbfs `DISCONNECT_CLAIM` error ("disconnect-and-claim failed errno") | `uvc_open` fails → `initHandle` `onFail` → `DeviceState.OPEN_FAILED` | libusbuvccamera020 |
| role-switch failure | `set_role` only fails on `kzalloc` (−ENOMEM, ignored by the store); worker has no error path | no readback (`tiny2c_mode` reads 0) | extcon source |
| no frames after stream start | – | 3 s frame-data check → stop + start preview; mirror/flip vdcmd failure on first frame → `DEVICE_RESTART` | app sources |
| unexpected USB disconnect | usbcore removes `1-1`; role/flag/rails unchanged | `USB_DEVICE_DETACHED` → `UsbControlBlock.close`, `mUSBDeviceConnected=false`, listeners only log; recovery via the frame/first-frame timers | `USBMonitor`, `Tiny2cDualPreviewFragment` |
| app crash / kill | – | AMS writes 0/0 for `com.energy.tc2c`, `.sop`, `com.energy.ac020` (not one of the shipped thermal apps); **FactoryMode crash leaves rails on, flag 1 and role HOST** | services.jar |
| external Type-C contention | flag suppresses external role events during the session; external role not restored after it | `external-usb-interaction.md` |
| uSmart inserted during session | detect work returns early (flag) → GPIO 55/152 and `uvc_insert_status` may be stale until another event | extcon source |
