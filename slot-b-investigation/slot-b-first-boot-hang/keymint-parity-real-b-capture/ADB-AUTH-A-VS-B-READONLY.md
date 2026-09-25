# Slot A vs Slot B ADB authorization investigation

This investigation compares the working Slot A runtime with the Slot B parity
candidate without modifying Slot B.

Motivation:

- Slot B reliably starts adbd roughly 30 seconds after boot.
- The host sees Slot B as `unauthorized`.
- Working Slot A has a zero-length `/data/misc/adb/adb_keys`.
- Therefore the B unauthorized state alone does not prove that `/data` failed
  to mount or decrypt.
- The next discriminator is whether Slot A and Slot B use different
  `ro.adb.secure`, `ro.debuggable`, build type, ADB APEX, USB-init, or ADB-key
  policy.

See `adb-auth-a-vs-b-readonly-analysis.txt` for the raw evidence.

All Slot B filesystem mounts in this investigation were read-only.
