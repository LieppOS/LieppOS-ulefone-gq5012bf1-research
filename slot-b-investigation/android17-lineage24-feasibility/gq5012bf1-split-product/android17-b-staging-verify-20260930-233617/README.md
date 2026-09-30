# Android 17 Slot-B userspace staging verification

Android 17 / LineageOS 24.0 userspace was staged only to inactive Slot B.

Written logical partitions:

- system_b
- system_ext_b
- product_b

Slot A remained current throughout the fastbootd write sequence.

Expected Android 17 hashes:

- system_b: d71f720c5edc727249e22a00021e2eb58871555f843f6464a67b267e841b2eef
- system_ext_b: e72441c57fb2727dffce3a3a4626b9716828456a9c3e472fe650fe07f38f51a4
- product_b: e7490f3204b936af49889d8b03e89a87cabbdd7c8e8a55c970920eb041201fde

This verification performs full device-side SHA256 readback from the logical
block devices after rebooting recovery and remapping super.

READBACK_PASS=1

No Slot-B boot was attempted.
No userdata or metadata write was performed.
No vbmeta partition was written during userspace staging.
