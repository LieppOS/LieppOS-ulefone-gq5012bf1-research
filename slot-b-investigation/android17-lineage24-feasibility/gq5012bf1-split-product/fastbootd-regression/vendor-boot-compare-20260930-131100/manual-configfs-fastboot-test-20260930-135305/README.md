# Manual configfs same-boot fastbootd test

OrangeFox creates and mounts the fastboot FunctionFS transport correctly.

The earlier direct `sys.usb.config=fastboot` experiment attempted to switch
while the live configfs gadget was still bound to ffs.adb.

This test:

1. verifies the MTK AIDL BootControl service is already healthy
2. starts fastbootd after that service exists
3. switches the volatile configfs gadget from ffs.adb to ffs.fastboot
4. queries slot and logical-partition variables only
5. reboots to known-good Slot A

No flash, erase, resize, create, delete, or partition write operation is used.
