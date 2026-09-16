# Post-untouched-B persistent-state conclusion

A bounded read-only inspection from working Slot A found no direct persisted
Linux/Android crash record attributable to the untouched Slot-B attempt.

Observed:

- pstore: empty
- bounded AEE `db.fatal.*.KE` query: no records returned
- `/metadata/watchdog`: no apparent crash record; only unrelated KSU metadata
- current A `/proc/pl_lk`:
  - AEE exception type `0x0`
  - WDT status `0x800`
  - reports `last is full pmic reset`
  - current A KPOC check has `charger_boot_switch = 0`
  - current A proceeds to Linux normally

The `full pmic reset` and WDT status cannot yet be attributed to failed Slot B
because current A was reached through later bootloader/reboot activity. They
must be compared with historical known-good A-only PL/LK captures.

The initial bootstat capture contained metadata timestamps only, not bootstat
file contents. Actual boot-reason values require a separate read-only capture.

No evidence from this capture currently establishes kernel panic, AEE fatal
exception, or Android watchdog as the Slot-B reset initiator.
