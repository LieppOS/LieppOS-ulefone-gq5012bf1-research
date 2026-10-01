# Android 17 HIDL image build continuation

Known HIDL module build from the preceding run succeeded.

This run used:

```
lunch lineage_gq5012bf1 cp2a userdebug
m systemimage systemextimage productimage
```

Resolved:

- TARGET_PRODUCT=lineage_gq5012bf1
- TARGET_RELEASE=cp2a
- TARGET_BUILD_VARIANT=userdebug
- PRODUCT_OUT=/mnt/SamsungSSD/android/lineage-24.0/out/target/product/gq5012bf1

Result:

- BUILD_RC=1
- image build failed

This run was host-only.

- PHONE_MODIFIED=0
- no adb
- no fastboot
- no flashing
- no slot changes
