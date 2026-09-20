# Failed fastbootd vendor_b write

The first attempted fixed-vendor write failed in userspace fastboot.

Fastboot output:

```
Resizing 'vendor_b' OKAY
Invalid sparse file format at header magic
Sending sparse 'vendor_b' 1/4 ... OKAY
Writing 'vendor_b' FAILED (remote: 'No such file or directory')
```

The procedure stopped immediately.

`vbmeta_vendor_b` was not flashed.

Slot B was not activated.

## Post-failure Android state

Slot:

`_a`

Boot completed:

`1`

## vendor_b geometry

Start sector:

`17098384`

Sectors:

`1594432`

Bytes:

`816349184`

`VENDOR_B_GEOMETRY_UNCHANGED=1`

`LP_METADATA_IDENTICAL=1`

## vendor_b content

Current SHA256:

`9f3dfe3fe5ef025b667b8181bddfedaf6b08dace4b7cd6c4e05a4fde0d16aa98`

Old expected SHA256:

`9f3dfe3fe5ef025b667b8181bddfedaf6b08dace4b7cd6c4e05a4fde0d16aa98`

New candidate SHA256:

`7abbeb81e68ab4e9afd5847ea788b0c6bcdc48f9d6fc049d4b1b81d0e84c71ba`

`VENDOR_B_STATE=ROLLBACK_IMAGE_INTACT`

## AVB physical partitions

vbmeta_vendor_b:

`cedd477ccca28a7358bfd4f20b744658cb706ab2037d1489d64b72a189191ddc`

`VBMETA_VENDOR_B_UNCHANGED=1`

vbmeta_b:

`bb2c7cb52dd15ee636cdb27b60f3fa5ed8fd6f774fe4acfc0a77301cbb4b17fb`

`ROOT_VBMETA_B_UNCHANGED=1`

## Dynamic partition state

Update state:

`none`

Current slot:

`_a`

## Classification

`FAILED_FLASH_EFFECT=NO_PERSISTENT_CHANGE`

`RECOVERY_REQUIRED=0`

No writes were performed by this post-failure audit.
