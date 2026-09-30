# OrangeFox fastbootd / BootControl audit

Current facts established before this audit:

- Normal Android has a working AIDL IBootControl service and reports two slots.
- Bootloader fastboot reports slot-count=2 and current-slot=a.
- Current userspace fastbootd reports slot-count=0 and an empty current-slot.
- Current userspace fastbootd cannot open system_b/system_ext_b/product_b.
- Historical fastbootd with factory vendor_boot successfully resized and flashed
  those same direct *_b logical targets.
- vendor_boot DTB is unchanged.
- vendor_boot platform ramdisk is byte-identical to the historical factory image.
- The current recovery fragment is OrangeFox and is dramatically different from
  factory recovery.
- OrangeFox recovery overlays the platform copy of system/bin/fastbootd and
  several related fastboot/VINTF libraries.

This audit determines whether the regression comes from:

1. OrangeFox replacing the fastbootd BootControl client stack, or
2. OrangeFox init/VINTF configuration preventing the unchanged MTK recovery
   BootControl service from registering.

No device writes are performed.
