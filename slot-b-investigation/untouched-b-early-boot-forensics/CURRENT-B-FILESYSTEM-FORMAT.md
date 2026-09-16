# Current Slot-B logical filesystem format

The current Slot-B logical partition dumps are raw EROFS filesystems:

- `system_b.img`
- `system_ext_b.img`
- `product_b.img`
- `vendor_b.img`

All report EROFS with LZ4 zero-padding support.

Host tooling currently present:

- `debugfs`: present, but ext2/3/4 only
- `simg2img`: present, but not applicable because these images are already raw
  EROFS rather than Android sparse images
- `dump.erofs`: absent
- `fsck.erofs`: absent
- `erofsfuse`: absent

Next step: use the host kernel's EROFS support for read-only loop mounts, or
locate an existing erofs-utils binary in the Android build tree.
