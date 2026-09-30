# Live OrangeFox BootControl runtime inspection

Purpose:

Determine why OrangeFox fastbootd has no usable BootControl interface despite
the stock MTK recovery AIDL service definition remaining present in the merged
vendor_boot ramdisk.

Checks include:

- init service state
- AIDL service registration
- HIDL service registration
- bootctl behavior
- MTK BootControl process state
- actual dynamically loaded libraries
- linker errors
- SELinux AVCs
- one init-controlled retry if vendor.boot-default was already stopped

No partition flash/write command is used.
