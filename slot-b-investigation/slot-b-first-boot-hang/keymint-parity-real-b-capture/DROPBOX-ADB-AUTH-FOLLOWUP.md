# Slot B postmortem: DropBox and ADB authorization

## Known facts

The Slot B parity candidate reaches adbd approximately 30 seconds after reboot,
but appears to the development host as unauthorized.

Two files in /data/system/dropbox have timestamps during the Slot B attempt:

- data_app_crash@1790330521368.txt
- data_app_crash@1790330530977.txt

Their contents are captured beside this report.

If these records identify the Slot B LineageOS runtime, they demonstrate that
Slot B had writable access to at least part of /data. In that case, persistent
ADB unauthorized status cannot be explained simply as "userdata was not
mounted" and the ADB authorization path must be investigated separately.

The current working Slot A ADB key files were inspected by metadata and SHA-256
only; their key contents were not copied into this report.

Slot A was confirmed fully booted before bootctl mark-boot-successful was used.
This restores Slot A's known-good successful flag after set_active a reset it.

No factory reset or filesystem formatting was performed.
