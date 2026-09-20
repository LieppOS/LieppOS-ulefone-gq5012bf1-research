# Final pre-write topology correction

The previous fastboot ownership probe stopped because userspace fastboot
returned an empty value for `current-slot`.

That was a probing-script assumption, not evidence of a slot change.

Immediately before entering fastbootd Android reported Slot A and
`sys.boot_completed=1`. No slot-changing command was issued. The cleanup
returned the phone to Android, where this follow-up audit again proved Slot A.

## Previously proven in fastbootd

`is-userspace=yes`

`vendor_b`:

- type raw
- logical yes

`vbmeta_vendor_b`:

- size 0x800000
- type raw
- logical no

`vbmeta_b`:

- size 0x800000
- type raw
- logical no

Therefore absence of a fastbootd `current-slot` value is treated as an
unsupported/blank variable, not as a failed Slot-A safety condition.

## Current B baseline

The preceding audits established:

- vendor_b equals rollback image exactly
- vbmeta_vendor_b equals rollback image exactly
- vbmeta_b equals the complete expected 8192-byte root image exactly
- root AVB metadata is identical
- snapshot update state is none
- current Android slot is A
- fixed vendor metadata gate passed

`CURRENT_B_BASELINE_READY=1`

## Bootloader fastboot

`is-userspace=no`

`current-slot=a`

`vbmeta_vendor_b size=800000`

`vbmeta_vendor_b logical=UNKNOWN`

`vbmeta_b size=800000`

`vbmeta_b logical=UNKNOWN`

## Write topology

`vendor_b` is a dynamic logical partition and its intended write environment
is fastbootd.

`vbmeta_vendor_b` is a physical 8 MiB partition and is visible from
bootloader fastboot when:

`BOOTLOADER_VBMETA_VENDOR_B_VISIBLE=0`

The top-level `vbmeta_b` will remain unchanged.

`WRITE_TOPOLOGY_READY=0`

No flash or slot-changing operation occurred during this probe.
