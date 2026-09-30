# Live OrangeFox TCP fastbootd test

Device-specific recovery behavior established during testing:

- OrangeFox R12.0 does not reliably expose ADB automatically after recovery boot.
- ADB may need to be manually enabled from the OrangeFox UI.
- `adb get-state` reports `recovery` while connected to OrangeFox, not `device`.

This test was therefore performed after manual ADB enablement without another
recovery reboot.

Fastbootd is started only after the MediaTek AIDL BootControl service reports
two slots and current slot A. Transport is TCP port 5554 tunneled through ADB.

No partition write, flash, resize, erase, slot activation, userdata operation,
or metadata operation is performed.
