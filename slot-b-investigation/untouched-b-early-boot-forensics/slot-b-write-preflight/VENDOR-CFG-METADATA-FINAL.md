# Final fixed-vendor cfg metadata closure

The earlier targeted audit resolved the compiled Android SELinux context but
could not inspect the image because the phone was disconnected and the host
mount required sudo.

This audit is host-only.

## Final Slot-B image

SHA256:

`7abbeb81e68ab4e9afd5847ea788b0c6bcdc48f9d6fc049d4b1b81d0e84c71ba`

The first `800980992` bytes of the original fixed vendor image and
the Slot-B-sized AVB-resized image are byte-identical.

`EROFS_PAYLOAD_IDENTICAL_AFTER_AVB_RESIZE=1`

## Actual EROFS cfg inode

Path:

`/vendor/etc/init.insmod.mt6878.cfg`

SHA256:

`683d5f45ddf50f6091ce5bbcf4b90d3e92b4bd5ebf05bebab0d59ccf8b112c98`

UID:

`0`

GID:

`0`

Mode:

`644`

`CFG_CONTENT_EXACT=1`

`POSIX_METADATA_EXACT=1`

## SELinux

Final compiled path resolution:

`u:object_r:vendor_configs_file:s0`

Required generic vendor/etc context:

`u:object_r:vendor_configs_file:s0`

`SELINUX_BUILD_CONTEXT_EXACT=1`

Actual extracted security.selinux xattr, when the host LSM allowed it:

`UNAVAILABLE`

`ACTUAL_SELINUX_XATTR_OBSERVED=0`

The actual xattr observation is supplemental because host desktop kernels may
reject materializing Android security.selinux xattrs during extraction.

## Final gate

`METADATA_GATE=1`

No phone, flash, slot, or super-metadata operation occurred.
