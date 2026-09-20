# Fixed vendor_b boot postmortem

Observed after installing and verifying the fixed vendor_b/vbmeta_vendor_b pair:

- Slot B was selected successfully.
- B reached the graphical boot/logo screen.
- No usable ADB connection was reached during the observation window.
- B did not reach confirmed `sys.boot_completed`.
- Manual bootloader recovery returned the device to Slot A.
- Slot A is current, active, bootable, and successful.
- Slot B remains bootable but is not marked successful.
- pstore was empty after recovery.

Device-specific bootloader observation:

`fastboot set_active a` returned OKAY while an immediate
`getvar current-slot` still reported `b`. The following reboot entered `_a`,
so this fastboot variable must not be used as confirmation of the pending
next-slot selection on this device.

Current failure class:

`FIXED_VENDOR_B_LOGO_HANG_NO_ADB_NO_PSTORE`
