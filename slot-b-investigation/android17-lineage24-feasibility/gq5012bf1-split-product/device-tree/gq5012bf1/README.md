# GQ5012BF1 Android 17 split userspace target

This is the first host-only LineageOS 24 product for the Ulefone Armor 29 Pro.
It builds separate `system`, `system_ext`, and `product` EROFS images against the
current Slot-B extent limits. It deliberately does not build or replace the
kernel, boot/init_boot/vendor_boot, dtbo, vendor, or DLKM partitions.

Configure with:

```bash
source build/envsetup.sh
lunch lineage_gq5012bf1 cp2a userdebug
```

Artifacts are host research outputs only and are not authorized for flashing.
