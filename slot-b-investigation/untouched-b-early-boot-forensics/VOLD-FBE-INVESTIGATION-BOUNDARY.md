# Slot-B vold / FBE investigation boundary

The Slot-B investigation has moved from BPF to Android vold/FBE because current
B contains an immediate init reboot policy:

`reboot_on_failure reboot,vold-failed`

## Current-B vold

Current B contains an Android-35 arm64 vold binary:

- path: `/system/bin/vold`
- size: `1006520`
- SHA256:
  `34f452c3890b1633fb1cc51112b821fc43e88bc865368d4162dfe43f96bb6251`
- Build ID:
  `125a1c744e1b5fefce4114e951119b2e`

All direct ELF DT_NEEDED dependencies checked so far were found in the mounted
current-B logical filesystem set.

Therefore an obvious missing direct shared-library dependency is not currently
supported as the cause of a vold startup failure.

## Working Slot A

Working Slot A reports:

- `init.svc.vold=running`
- `ro.crypto.state=encrypted`
- `ro.crypto.type=file`

Its working device fstab uses F2FS for `/metadata` and `/data`.

The working `/data` FBE contract includes:

- file-based encryption;
- `/metadata/vold/metadata_encryption` as metadata-key storage;
- quota;
- filesystem checkpoints;
- fs-verity;
- inline encryption configuration.

## Shared persistent state

Read-only inspection confirms that the shared device state contains:

- `/metadata/vold/metadata_encryption`
- `/metadata/vold/metadata_encryption/key`
- `/data/unencrypted`
- `/data/misc/vold`
- `/data/misc_ce`
- `/data/misc_de`

No encryption key contents were read.

## Exact Android-15 vold semantics

The Android-15 vold executable itself exits nonzero on startup failures such
as:

- failure to obtain SELinux file contexts;
- failure to construct/start VolumeManager;
- failure to construct/start NetlinkManager;
- failure to start VoldNativeService.

Its configuration parser logs a default-fstab read/configuration failure but
continues rather than immediately exiting.

Metadata/FBE helper routines have numerous boolean failure paths, including
metadata-key retrieval, dm-default-key creation, DE/CE key installation, and
user-storage preparation.

A helper returning false does not by itself prove that the long-running vold
process terminates. The exact caller chain and init behavior must therefore be
traced before classifying an FBE incompatibility as a direct
`reboot,vold-failed` mechanism.

## Current question

Determine whether current B consumes the same encryption/fstab contract as
working A and whether any B-specific failure would:

1. terminate vold and directly trigger `reboot,vold-failed`; or
2. fail boot through a different init/fs_mgr path while vold remains alive.

No claim is made yet that vold/FBE caused the Slot-B reboot.
