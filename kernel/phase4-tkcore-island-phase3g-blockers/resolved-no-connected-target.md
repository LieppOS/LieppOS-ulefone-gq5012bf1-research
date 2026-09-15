# Phase 3G resolved preflight event — target initially absent

Resolution: **RESOLVED**. The authorized device subsequently appeared as serial `5012BF3010001335`; fresh Slot/bootloader/partition evidence and rollback proof were collected. This file preserves the fail-closed stop event and is not an active blocker.

Historical classification while absent: `TKCORE_ISLAND_PHASE3G_BLOCKED_BEFORE_DEVICE`

## Trigger

Read-only host discovery returned:

- `adb devices -l`: 0 targets;
- `fastboot devices`: 0 targets.

Exact output is frozen at:

`workspace/phase4-tkcore-island/phase3g/device-before/connection-state.txt`

## Why this is fail-closed

Without a connected authorized GQ5012BF1 target, Phase 3G cannot freshly prove:

- active slot and slot suffix;
- Slot A bootability/success state;
- Slot B state;
- bootloader unlocked state;
- current partition/AVB state;
- current Slot-B kernel release;
- current stock-B partition backup hashes;
- an immediately available rollback route to untouched Slot A.

The mission's STOP conditions explicitly require stopping before flash when Slot A state is uncertain or rollback is not proven. Historical device captures are useful context but cannot substitute for current pre-write state.

## Actions not performed

- device shell commands: **0**;
- slot switches: **0**;
- reboots: **0**;
- partition reads: **0**;
- partition writes: **0**;
- Slot-A writes: **0**;
- live module operations: **0**;
- RPMB/NVRAM/calibration/secret operations: **0**;
- SELinux changes: **0**;
- bootloader state changes: **0**.

No image was authorized for flash and no runtime gate was entered.

## Cleared static prerequisites

The blocker is not a static ABI or build failure:

- Phase 3F through 3A-R verifiers: exact required counts;
- cache-cleared provider/consumer rebuilds: RC 0, no warning/error/modpost/unresolved output;
- provider SHA unchanged: `caacafd250dc2d6fbfbb1e9a0a3d129b388d31b9851b18666a33a2da90868983`;
- exact three runtime artifacts frozen;
- required installed-stock provider edges: 12/12 compatible;
- retained stock MicroArray to source tkcore edge: 1/1 compatible;
- complete 471-module offline audit: 0 unresolved, 0 version disagreements, 0 conflicting provider symbols;
- offline depmod: RC 0, 0 warnings, 0 errors;
- stock filenames and load order preserved by planned in-place replacement;
- every replacement is smaller than stock.

## Resolution evidence

The device later connected in normal Android/ADB mode. Read-only Fastboot and root Boot Control checks established unlocked/secure-no state, A active/bootable/successful, B bootable/not-successful, and no snapshot merge. Fresh A/B hashes matched all retained backups. An explicitly authorized `fastboot --set-active=a` control test returned to a fully booted, successful A. See `kernel/phase4-tkcore-island-phase3g-rollback.md`.
