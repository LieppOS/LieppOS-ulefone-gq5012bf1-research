# Fixed vendor init.insmod cfg metadata audit

The previous metadata audit was manually interrupted during a recursive grep
over the entire out/soong tree. That search strategy was abandoned.

No flash or slot operation occurred.

## Final image

SHA256:

`7abbeb81e68ab4e9afd5847ea788b0c6bcdc48f9d6fc049d4b1b81d0e84c71ba`

## Working Slot-A reference

Content SHA256:

`UNKNOWN`

SELinux context:

`UNKNOWN`

Metadata:

`UNKNOWN`

`WORKING_A_REFERENCE_CONTENT_EXACT=0`

## Slot-B-fit image

Content SHA256:

`UNKNOWN`

UID:

`UNKNOWN`

GID:

`UNKNOWN`

Mode:

`UNKNOWN`

Observed EROFS SELinux xattr:

`UNKNOWN`

## Build file-context resolution

matchpathcon result:

`u:object_r:vendor_configs_file:s0`

## Classification

`CFG_CONTENT_EXACT=0`

`POSIX_METADATA_EXACT=0`

`SELINUX_CONTEXT_EXACT=0`

`METADATA_GATE=0`
