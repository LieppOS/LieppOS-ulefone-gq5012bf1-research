# Slot-B vold / FBE direct-reboot path demoted

The Slot-B investigation previously identified the current-B vold service as
an immediate init reboot authority because its service definition contains:

`reboot_on_failure reboot,vold-failed`

Further source analysis substantially narrows what this means.

## FBE failures do not directly equal vold process death

Android 15 exposes the important FBE operations through VoldNativeService.

Examples include:

- `fscrypt_init_user0()`
- `fscrypt_mount_metadata_encrypted()`

These calls return through `translateBool(...)` into Binder status handling.

Therefore failures such as:

- metadata-key retrieval failure;
- dm-default-key creation failure;
- DE/CE key installation failure;
- user-storage preparation failure;

can return errors to the caller without terminating the long-running vold
process.

Such failures therefore do not automatically activate:

`reboot_on_failure reboot,vold-failed`

That init target requires the vold service process itself to terminate
unsuccessfully.

## Current-B vold executable

The current-B Android-35 vold binary has already been identified and all of its
direct DT_NEEDED libraries checked by the investigation were present in the
current-B logical filesystem set.

No obvious direct linker failure has been found.

## Shared FBE state

Read-only inspection confirms normal-looking shared persistent FBE structure,
including:

- `/metadata/vold/metadata_encryption`
- `/metadata/vold/metadata_encryption/key`
- `/data/unencrypted`
- `/data/misc/vold`
- user 0 CE key directory
- user 0 DE key directory
- `/data/misc_ce`
- `/data/misc_de`
- `/data/system_ce`
- `/data/system_de`
- `/data/vendor_ce`
- `/data/vendor_de`

No encryption key contents were read.

## Historical evidence caveat

The TIER3 search found vold/FBE messages in:

`run-20260812T094157Z/fallback/logcat-all.stdout`

including:

- vold startup;
- metadata-encrypted `/data` setup;
- systemwide-key initialization;
- `fscrypt_init_user0`.

Because these records are explicitly under a `fallback` capture, they must not
be attributed to the failed Slot-B runtime without independent slot-identity
evidence.

They are not direct evidence that current/failed B completed FBE setup.

## Direct vold-failed evidence

No preserved evidence currently identifies:

- `vold-failed`;
- a vold process crash;
- a vold process exit;
- a linker failure starting vold.

Conclusion:

The direct `reboot,vold-failed` hypothesis is demoted.

An FBE or mount failure remains theoretically possible as a boot failure
through the fs_mgr/init call chain, but it must not be conflated with vold
daemon death.

Investigation should prioritize other explicit second-stage reboot authorities
unless new direct vold evidence appears.
