# Corrected AVB vendor capacity calculation

The earlier `avbtool add_hashtree_footer --calc_max_image_size` attempt failed
because the AOSP host helper `fec` was not in PATH.

This was a host-tool environment failure, not an image or AVB failure.

AOSP fec used:

`/mnt/SamsungSSD/android/lineage-22.2/out/host/linux-x86/bin/fec`

Current vendor_b allocation:

`816349184`

Current valid vendor original-image size:

`800976896`

Calculated maximum:

`803381248`

Candidate +4096 allocation:

`816353280`

Fixed vendor original-image size:

`800980992`

Calculated maximum:

`803385344`

`CURRENT_MAX_MATCHES_OLD_FS=0`

`PLUS4K_MAX_MATCHES_FIXED_FS=0`

`AVB_BOUNDARY_PROVEN=0`

`AVB_CAPACITY_CLASS=AVB_MAX_IMAGE_SIZE_NEEDS_REVIEW`

No phone, flash, slot, or super-metadata operation occurred.
