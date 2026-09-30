# Android 17 Slot-B AVB decision

## Result

Do not flash the generated Android 17 `vbmeta.img` or `vbmeta_system.img`
for the initial Slot-B boot experiment.

The existing Slot-B root vbmeta has flags=3:

- AVB_VBMETA_IMAGE_FLAGS_HASHTREE_DISABLED
- AVB_VBMETA_IMAGE_FLAGS_VERIFICATION_DISABLED

With top-level verification disabled, AVB does not process the root vbmeta
descriptors or chained vbmeta images. Therefore the stale Android 15/16
system/product/system_ext/vendor_boot descriptors are not enforced.

The generated Android 17 root vbmeta instead has flags=0 and a substantially
different trust graph:

- chain: vbmeta_system
- hashtree: product
- hashtree: system_ext

It does not reproduce the existing device graph covering boot, vbmeta_vendor,
dtbo, init_boot, vendor_boot, odm_dlkm, system_dlkm, and vendor_dlkm.

Replacing the permissive current root vbmeta with this narrower enforcing
root vbmeta is unnecessary for initial bring-up and would introduce additional
boot-chain variables.

## Current intended Slot-B bring-up state

Android 17 images are staged and device-side SHA256 verified on:

- system_b
- system_ext_b
- product_b

Keep existing:

- vbmeta_b
- vbmeta_system_b
- vbmeta_vendor_b
- boot_b
- init_boot_b
- vendor_boot_b
- dtbo_b
- vendor_b and DLKM partitions

Slot B must still not be booted against Slot A's shared userdata until an
isolated-data strategy is implemented.
