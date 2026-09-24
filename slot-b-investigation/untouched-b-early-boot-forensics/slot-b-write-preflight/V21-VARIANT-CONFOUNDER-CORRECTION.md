# V21 variant confounder correction

The first V21 Slot-B boot test used a `user` build.

Historical V17 and V20 experiments used `userdebug`.

A userdebug regeneration with the V21 dummy removed reproduced the historical
V17 `vendor_sepolicy.cil` and `precompiled_sepolicy` hashes exactly.

Therefore the first V21 boot result is confounded by build variant and must not
be used to conclude that existing SELinux type renumbering is unnecessary.

The clean V21 experiment is the userdebug build where removing only the V21
dummy type and roletype returns exactly to the historical V17 CIL.

PHONE_MODIFIED=0
