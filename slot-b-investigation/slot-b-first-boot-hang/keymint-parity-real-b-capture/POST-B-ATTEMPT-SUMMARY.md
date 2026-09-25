# Slot B parity boot — post-attempt evidence

## Confirmed behavior

The parity Slot B candidate was selected through the MediaTek BootControl HAL.

During the B boot attempt, USB ADB was absent initially and then appeared as
`unauthorized` at approximately 30 seconds. It remained unauthorized for the
remainder of the observed boot attempt.

This proves the B boot reached Android userspace far enough to start adbd.

The persistent unauthorized state is compatible with adbd being unable to use
the normal authorized-host state from /data/misc/adb. Because earlier Slot B
tests showed vold/KeyMint/FBE failures, failure to mount or decrypt /data remains
a primary hypothesis. This is not considered proven until corroborated by
pstore or other retained logs.

## Post-attempt A state

- Runtime slot: _a
- bootctl current slot: 0
- A bootable: 1
- B bootable: 1
- A successful: 0
- B successful: 0

## Shared metadata key

Post-B SHA-256:

`1eac61edfe777d0c6fa2f2d4f62ec892b6a031b90cb7064e4d6581c0a944fbca`

Expected known-good SHA-256:

`1eac61edfe777d0c6fa2f2d4f62ec892b6a031b90cb7064e4d6581c0a944fbca`

Unchanged:

`YES`

## Evidence files

- misc-pre-b.bin
- misc-post-set-b.bin
- misc-after-b-attempt.bin
- slot-b-real-boot-capture-v2.txt
- post-b-attempt-a-capture.txt
- pstore-after-b-attempt.txt
- last-kmsg-after-b.txt
- metadata-encryption-inventory-after-b.txt
- bootstat-after-b.txt
- dropbox-list-after-b.txt

## Safety

No factory reset was performed.

Slot A partitions were not modified by this investigation.

userdata and metadata were not formatted, fscked, or intentionally modified.
