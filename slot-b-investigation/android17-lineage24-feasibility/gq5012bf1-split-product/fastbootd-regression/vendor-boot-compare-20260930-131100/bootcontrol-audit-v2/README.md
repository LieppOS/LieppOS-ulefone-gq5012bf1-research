# Corrected OrangeFox fastbootd / BootControl audit

The previous audit aborted while trying to materialize a CPIO directory entry
as a file. Its recovery-side extraction was therefore incomplete.

This corrected audit distinguishes regular files, directories, and symlinks
and compares the complete selected BootControl/fastbootd client stack.

Already established independently:

- normal Android BootControl works and exposes two slots
- bootloader fastboot exposes two slots and current slot A
- OrangeFox fastbootd exposes slot-count 0 and empty current-slot
- stock/factory fastbootd previously resized and flashed Slot-B logical
  partitions successfully
- vendor_boot DTB is unchanged
- vendor_boot platform fragment is byte-identical to factory
- current recovery fragment is OrangeFox
- OrangeFox recovery overlays fastbootd and numerous boot/binder/VINTF
  libraries from the otherwise unchanged platform fragment

This directory contains only research evidence intended for source control.
Extracted ELF binaries remain local derived artifacts and are not committed.
