# First boot after fixed vendor_b + vbmeta_vendor_b

The fixed Slot-B vendor/AVB pair had been verified before activation.

Observed runtime result:

- Slot B was successfully selected before reboot.
- Device reached and remained on the boot/logo screen.
- No usable ADB connection was reached during the observation period.
- Therefore the test harness could not arm Slot A from B userspace.
- Recovery to Slot A was performed manually through bootloader Fastboot.
- No further Slot-B boot was attempted.

Recovered Android state:

- slot: _a
- boot completed: 1

Provisional class:

`FIXED_VENDOR_B_LOGO_HANG_NO_ADB`

This differs from claiming Android userspace success: there is currently no
evidence that B reached stable ADB or sys.boot_completed.
