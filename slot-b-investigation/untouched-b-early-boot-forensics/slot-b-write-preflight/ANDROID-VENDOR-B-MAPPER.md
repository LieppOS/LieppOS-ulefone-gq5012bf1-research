# Android-A vendor_b device-mapper audit

The OEM fastbootd path is not usable for the inactive vendor partition:

- fastbootd reports slot-count 0
- has-slot:vendor is no
- --slot=b is rejected by host fastboot because the device reports no slots
- unsuffixed vendor resolves to a partition whose size is 0x4C812000,
  matching vendor_a
- explicit vendor_b is reported logical but cannot be opened by fastbootd
- an explicit vendor_b flash failed before making any persistent change

Android A independently exposes:

`/dev/block/mapper/vendor_b -> /dev/block/dm-11`

## Mapping

dm name:

`vendor_b`

Size:

`816349184`

Expected:

`816349184`

`MAPPER_SIZE_EXACT=1`

blockdev read-only:

`1`

sysfs read-only:

`1`

`MAPPER_WRITABLE_FLAG=0`

Mount references:

`1`

`MAPPER_UNMOUNTED=0`

Holders:

`0`

`MAPPER_NO_HOLDERS=1`

## Content identity

Mapper SHA256:

`9f3dfe3fe5ef025b667b8181bddfedaf6b08dace4b7cd6c4e05a4fde0d16aa98`

Known super extent SHA256:

`9f3dfe3fe5ef025b667b8181bddfedaf6b08dace4b7cd6c4e05a4fde0d16aa98`

Expected rollback SHA256:

`9f3dfe3fe5ef025b667b8181bddfedaf6b08dace4b7cd6c4e05a4fde0d16aa98`

`MAPPER_CONTENT_EXACT=1`

`MAPPER_TO_EXTENT_EXACT=1`

## Gate

`ANDROID_DIRECT_WRITE_PATH_READY=0`

This audit performed no writes, flashes, slot changes, or reboots.
