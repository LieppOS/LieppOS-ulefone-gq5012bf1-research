# MT6878 insmod configuration source fix

## Proven blocker

Previous static analysis established:

`SLOT_B_INSMOD_CFG_BOOT_BLOCKER_PROVEN_STATICALLY`

The normal Slot-B chain was:

1. `init.mt6878.rc` sets `vendor.all.modules.ready=1`.
2. Imported `init.mtkgki.rc` later sets it to `0`.
3. It starts `/vendor/bin/init.insmod.sh`.
4. That script expects `/vendor/etc/init.insmod.mt6878.cfg`.
5. The cfg was absent from Slot B.
6. The script therefore exits through its missing-config `exit 2` path.
7. `post-fs-data` later executes
   `wait_for_prop vendor.all.modules.ready 1`.

Android init import/action ordering was independently verified from the local
LineageOS init documentation.

## Source cause

The Ulefone extraction/package source included the MediaTek insmod script and
its init RC consumers but omitted the required
`vendor/etc/init.insmod.mt6878.cfg`.

## Implemented fix

The exact stock configuration is now device-owned at:

`device/ulefone/armol/configs/vendor/init.insmod.mt6878.cfg`

It is installed into:

`/vendor/etc/init.insmod.mt6878.cfg`

through `PRODUCT_COPY_FILES` in `device.mk`.

Verified stock SHA256:

`683d5f45ddf50f6091ce5bbcf4b90d3e92b4bd5ebf05bebab0d59ccf8b112c98`

Device-tree commit:

`ef05e7917c45f1e9619cf340d421138b365bebf6`

## Runtime status

The fix is source-only at this point.

No build, flash, slot change, or phone write was performed.

The next step is to build the vendor image and verify the generated image
contains this exact configuration before preparing an AVB-consistent Slot-B
runtime test.
