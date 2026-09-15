# TrustKernel Phase 3G — Slot-B device trial

Date: `2026-09-15`

Authorized target: `5012BF3010001335` (`GQ5012BF1_EEA`, `k6878v1_64`)

Verdict: **FAIL-CLOSED — G1 NOT REACHED; STOCK B RESTORED EXACTLY**

## Executive result

The three validated Phase-3G images were written only to Slot B and verified byte-for-byte from running Slot A. Exactly one B boot was attempted. B never reached ADB; the bootloader fell back to A after about 124 seconds and marked B unbootable. No second B boot was attempted.

The retained stock B images were then restored under renewed explicit authorization. Final A-side hashing proves all three B partitions are byte-identical to their pre-trial backups. A is active, bootable and successful; B is bootable and not successful; snapshot merge status is `none`.

This trial does **not** establish that source `tkcore` or `tmem_ffa` loads or functions on-device. G1 failed before module evidence could be collected; G2–G7 are blocked failures and G8–G10 remain deferred.

## Written candidate images

| Partition | Candidate SHA-256 | Write result | Post-write A-side hash |
|---|---|---|---|
| `vendor_dlkm_b` | `7612591d67c3042a649dbd08bbd542ed7a16a18fb794303b58be962088d8833c` | Fastbootd `Writing ... OKAY` | exact |
| `vendor_boot_b` | `df684678914292c285d7c37d757a77807d7278889ca503018da97573cd47886f` | bootloader Fastboot `Writing ... OKAY` | exact |
| `vbmeta_b` | `43cd2bb0a71b1f7cdb4619a3d8969363ee36a860289a137a50c68d7372bd5a0f` | bootloader Fastboot `Writing ... OKAY` | exact |

Inactive logical `vendor_dlkm_b` could not be opened directly. The successful bounded procedure temporarily latched still-stock B, rebooted to B Fastbootd, wrote the exact suffixed logical target, and immediately relatched A before writing the two physical B partitions.

## Single boot attempt

1. Confirmed A current, successful and bootable; B bootable; no snapshot merge.
2. Confirmed all three candidate partition hashes from A.
3. Selected B, restarted the bootloader to relatch metadata, and confirmed `current-slot: b` and `slot-unbootable:b: no`.
4. Issued one `fastboot reboot`.
5. No B ADB transport appeared. At 124 seconds ADB appeared on `_a`; at 135 seconds A reported `sys.boot_completed=1`.
6. Explicitly selected A again and restarted the bootloader; `current-slot: a` was confirmed before rebooting Android.

Authoritative control log:

`workspace/phase4-tkcore-island/phase3g/device-after/first-boot-control.txt`

## Failure evidence and bounded interpretation

Immediately after fallback:

- A was current, bootable and successful;
- B was reported unbootable and not successful;
- all three candidate B hashes still exactly matched the validated candidate files;
- `/sys/fs/pstore` contained no files;
- no B-side ADB, kernel log, module list or userspace evidence existed.

The failure is therefore classified as **pre-userspace / physical B boot-chain class**. Available evidence does not distinguish between:

1. rejection or unusability of the locally test-signed top-level `vbmeta_b` despite Fastboot reporting `unlocked=yes`, `secure=no`; and
2. failure during early/recovery loading from the modified `vendor_boot_b`, where `tkcore.ko` is present in `modules.load.recovery`.

The running GSI reports `ro.boot.flash.locked=1`, `ro.boot.vbmeta.device_state=locked` and `ro.boot.verifiedbootstate=green`, while bootloader Fastboot reports unlocked/insecure. The trial demonstrates that the Fastboot indication alone was insufficient proof that this B boot chain would execute.

A useful isolation observation is that B Fastbootd could not expose `vendor_dlkm_b` while the candidate physical boot chain was installed, but exposed it immediately after stock `vendor_boot_b` and stock `vbmeta_b` were restored. This narrows the failure to the physical B boot path but does not identify which of its two changed components failed.

## Exact stock restoration

| Partition | Restored stock SHA-256 | Final result |
|---|---|---|
| `vendor_dlkm_b` | `fce7acfb64956126a03929f085050ab1b300272333e84abf27b9e708aaa40297` | exact |
| `vendor_boot_b` | `c8953d16b7a47976362aa23b53d0a08dde451f25cab4c552fa70c43e56ee0756` | exact |
| `vbmeta_b` | `e14e11e184950d487b31def17a349f4f161e34988825bf35d85fc9bd6c3bde93` | exact |

Because the candidate physical chain could not launch B Fastbootd, restoration order was necessarily:

1. restore stock `vendor_boot_b` and `vbmeta_b` from bootloader Fastboot while A was active;
2. select B only long enough to launch its restored stock Fastbootd;
3. restore stock `vendor_dlkm_b` through the exact suffixed logical target;
4. relatch and boot A without booting B.

Final boot control:

- current slot: A (`0`);
- active next-boot slot: A (`0`);
- A bootable: yes;
- A successful: yes;
- B bootable: yes;
- B successful: no;
- snapshot merge: `none`.

## Evidence index

- pre-write hashes: `workspace/phase4-tkcore-island/phase3g/device-before/current-partition-hashes.tsv`
- candidate logical write: `workspace/phase4-tkcore-island/phase3g/device-before/flash-vendor_dlkm_b-active-mapped.txt`
- candidate physical writes: `workspace/phase4-tkcore-island/phase3g/device-before/flash-vendor_boot_b-vbmeta_b.txt`
- exact candidate post-write hashes: `workspace/phase4-tkcore-island/phase3g/device-before/post-flash-all-b-hashes.tsv`
- first boot control/timeline: `workspace/phase4-tkcore-island/phase3g/device-after/first-boot-control.txt`
- immediate fallback state: `workspace/phase4-tkcore-island/phase3g/device-after/post-fallback-state.txt`
- captured A logs: `workspace/phase4-tkcore-island/phase3g/device-after/{getprop,dmesg,logcat,bootconfig}.txt`
- physical stock restoration: `workspace/phase4-tkcore-island/phase3g/device-after/restore-stock-physical-b.txt`
- logical stock restoration: `workspace/phase4-tkcore-island/phase3g/device-after/restore-stock-logical-b.txt`
- final stock hashes: `workspace/phase4-tkcore-island/phase3g/device-after/post-restore-stock-b.tsv`
- final boot-control state: `workspace/phase4-tkcore-island/phase3g/device-after/post-restore-bootctl.txt`

## Stop condition

No further B boot, AVB-policy change, verification-disable operation or partition write is authorized by this trial. Any future experiment requires a new diagnosis, a separately reviewed image set and fresh explicit authorization. No A partition, userdata, RPMB, calibration, NVRAM or persist partition was written.
