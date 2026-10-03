# Controlled Slot-B logo-hang post-rescue forensics

The controlled plain A -> B test produced a graphical logo hang with no ADB
or fastboot transport during the 120-second observation period.

The device was manually returned to Slot A.

The first pstore analysis of that failed attempt was non-diagnostic for two
independent reasons:

1. the three files copied from `/sys/fs/pstore` were only approximately
   62-65 bytes each and were not retained kernel-console logs;
2. the initial host extraction used malformed grep expressions and emitted
   repeated `Trailing backslash` errors.

Accordingly, the earlier classification:

    DEEPEST_BOOT_STAGE=NO_LINUX_PROGRESS_PROVEN

must not be interpreted as evidence that Linux failed to start.

The correct interpretation is:

    the failed Slot-B boot stage was not recovered from that pstore capture.

This follow-up remained entirely on safe Slot A and checked alternate
read-only forensic sources:

- Android previous-boot logcat (`logcat -L`);
- `/proc/last_kmsg` variants;
- current pstore;
- MediaTek AEE/mtklog inventories;
- Android DropBox;
- persistent logd directories;
- boot-reason history.

No new Slot-B boot was performed and no partition content was modified.
