# Direct service-state V3 Slot-B result

Slot B was booted with the V3 diagnostic vendor pair.

No usable ADB transport appeared. The device was manually recovered to
safe Slot A through bootloader fastboot.

The persistent metadata markers capture direct service-property snapshots
from fs, post-fs and late-fs event actions, avoiding dependence on
property-trigger delivery.

See `hwsm-v3-test-result.txt` for exact values and timestamps.
