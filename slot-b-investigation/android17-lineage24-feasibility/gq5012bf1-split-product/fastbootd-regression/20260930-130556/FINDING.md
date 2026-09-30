# Current fastbootd BootControl regression

Observed current state:

- bootloader fastboot reports slot-count=2 and current-slot=a
- Android bootctl reports a valid Slot A
- userspace fastbootd reports slot-count=0
- userspace fastbootd reports an empty current-slot
- fastbootd still identifies system_b/system_ext_b/product_b as logical
- fastbootd cannot open those logical partitions
- Android inactive B mapper devices exist but are read-only
- historical August 12 fastbootd provisioning succeeded on direct *_b targets

AOSP behavior strongly indicates the current fastbootd environment does not
have a usable BootControl HAL/service. This prevents fastbootd from obtaining
the current slot and breaks its logical-partition mapping/open path.

Next investigation: compare the current A boot/init_boot/vendor_boot chain with
the August 12 known-working chain and isolate which recovery/fastbootd component
changed.
