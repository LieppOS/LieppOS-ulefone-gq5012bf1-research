# Final Slot-B write topology

The previous ownership classifier incorrectly required the bootloader
partition size to contain a 0x prefix.

Bootloader fastboot actually reported:

- is-userspace: no
- current-slot: a
- vbmeta_vendor_b partition-size: 800000
- vbmeta_vendor_b partition-type: raw
- vbmeta_b partition-size: 800000
- vbmeta_b partition-type: raw

800000 is the bootloader's hexadecimal rendering of 0x800000, or 8388608
bytes.

Fastbootd independently reported:

- is-userspace: yes
- vendor_b is-logical: yes
- vbmeta_vendor_b is-logical: no
- vbmeta_b is-logical: no

Therefore:

- vendor_b write environment: fastbootd
- vbmeta_vendor_b write environment: bootloader fastboot
- vbmeta_b remains unchanged

CURRENT_B_BASELINE_READY=1
WRITE_TOPOLOGY_READY=1
