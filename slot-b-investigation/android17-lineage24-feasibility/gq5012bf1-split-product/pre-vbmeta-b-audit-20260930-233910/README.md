# Pre-vbmeta Slot-B AVB audit

Android 17 userspace staging has already been verified byte-for-byte on:

- system_b
- system_ext_b
- product_b

Before replacing vbmeta_system_b and vbmeta_b, this audit records the complete
current Slot-B physical boot/AVB chain and the descriptors in the candidate
Android 17 vbmeta images.

A specific point requiring verification is vendor_boot_b, whose current SHA256
does not match the previously recorded exact-stock B vendor_boot baseline.

Physical Slot-B backups were written outside the research repository to:

/mnt/WDBlue/TIER3-phase5-android17/pre-vbmeta-b-backup-20260930-233910

This audit performs reads only. No partition, slot metadata, userdata, metadata,
device-mapper table, or AVB partition is modified.
