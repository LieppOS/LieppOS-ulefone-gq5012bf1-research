# Final current Slot-B baseline before writes

This audit was read-only.

No flash, partition write, slot change, or reboot occurred.

## Working slot

Android slot: _a

Boot completed: 1

bootctl: UNKNOWN

## Current vendor_b geometry

Single extent:

`1`

Start sector in super:

`17098384`

Sector count:

`1594432`

Byte size:

`816349184`

## Current B identities

vendor_b SHA256:

`9f3dfe3fe5ef025b667b8181bddfedaf6b08dace4b7cd6c4e05a4fde0d16aa98`

Expected rollback SHA256:

`9f3dfe3fe5ef025b667b8181bddfedaf6b08dace4b7cd6c4e05a4fde0d16aa98`

`CURRENT_VENDOR_B_MATCHES_ROLLBACK=1`

vbmeta_vendor_b first 4096 bytes SHA256:

`cedd477ccca28a7358bfd4f20b744658cb706ab2037d1489d64b72a189191ddc`

Expected:

`cedd477ccca28a7358bfd4f20b744658cb706ab2037d1489d64b72a189191ddc`

`CURRENT_VBMETA_VENDOR_B_MATCHES_ROLLBACK=1`

vbmeta_b first 4096 bytes SHA256:

`768e992decaf8ea13235f6ef9e5c675e8263f061b16326b3568d65c5c5ba4e4d`

Expected unchanged root:

`bb2c7cb52dd15ee636cdb27b60f3fa5ed8fd6f774fe4acfc0a77301cbb4b17fb`

`CURRENT_ROOT_VBMETA_B_MATCHES_EXPECTED=0`

## New pair prepared for later write

vendor_b candidate:

`7abbeb81e68ab4e9afd5847ea788b0c6bcdc48f9d6fc049d4b1b81d0e84c71ba`

vbmeta_vendor_b candidate:

`1ac2a85791813b70f7a901c73d43a19d1358ba0c4158a7e20688f32a2ffe783f`

## Snapshot state

`UNKNOWN`

## Gate

`CURRENT_B_BASELINE_READY=0`
