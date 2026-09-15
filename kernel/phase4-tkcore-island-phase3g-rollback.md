# TrustKernel Phase 3G — rollback gate

Current result: **PASS — FAILED B TRIAL RETURNED TO A; ALL B PARTITIONS RESTORED STOCK-EXACT**.

## Fresh pre-write state

- authorized target: `5012BF3010001335`, product `GQ5012BF1_EEA` / `k6878v1_64`;
- Fastboot: `unlocked=yes`, `secure=no`, two slots;
- current/active: A;
- A: bootable=yes, successful=yes;
- B: bootable=yes, successful=no;
- snapshot merge: `none`;
- current Android kernel: `6.1.115-android14-11-g6b18f0b574ab-ab12901745`.

Fastboot is authoritative for unlock state: the running GSI normalizes Android properties to `flash.locked=1`, `vbmeta.device_state=locked`, `verifiedbootstate=green`; the same discrepancy was recorded in the prior read-only Slot-B investigation.

## Backup proof

Fresh root read-only hashes of current `boot_{a,b}`, `vendor_boot_{a,b}`, `vbmeta_{a,b}`, `vbmeta_vendor_{a,b}` and `vendor_dlkm_{a,b}` are all byte-for-byte equal in both size and SHA-256 to the retained images under `slot-b-investigation/device-dumps/`. Thus those files are current backups, not stale assumptions. Exact values are frozen in `workspace/phase4-tkcore-island/phase3g/device-before/current-partition-hashes.tsv`.

## Tested return-to-A procedure

With A already active, the explicitly authorized recovery-control test performed:

1. confirm Android `_a` and A successful;
2. enter bootloader Fastboot;
3. confirm `current-slot: a` and `slot-successful:a: yes`;
4. issue exactly `fastboot --set-active=a`;
5. confirm `current-slot: a`, `slot-unbootable:a: no`;
6. reboot;
7. wait for `sys.boot_completed=1`;
8. root `bootctl` reconfirmed A active, bootable and successful; B remained bootable/not-successful.

No image partition was written. This proves the exact active-slot selection mechanism that will be used to return from a failed B boot.

## Failure procedure

On a first-boot failure: capture safe logs once if possible; enter bootloader; issue `fastboot --set-active=a`; reboot A; do not retry B. If restoration is required, use only the ledgered retained B backup images. No shared userdata mutation is required to return to A.

## Executed trial and restoration

The procedure was exercised after exactly one authorized B boot attempt. B never reached ADB, the bootloader fell back to A, and the monitor explicitly relatched A without retrying B. The retained backup images were then restored under renewed authorization.

Because the candidate physical B boot chain could not launch a B-mapped Fastbootd, restoration required stock `vendor_boot_b` and stock `vbmeta_b` first. B's restored stock Fastbootd then exposed `vendor_dlkm_b`, allowing its exact stock backup to be restored. B was never booted during restoration.

Final proof:

- A current and active-next-boot;
- A bootable and successful;
- B bootable and not successful;
- snapshot merge `none`;
- `vendor_boot_b`, `vendor_dlkm_b`, and `vbmeta_b` each byte-identical to the retained stock backup.

Evidence: `workspace/phase4-tkcore-island/phase3g/device-after/post-restore-stock-b.tsv` and `post-restore-bootctl.txt`. Full trial report: `kernel/phase4-tkcore-island-phase3g-device-trial.md`.
