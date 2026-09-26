# Controlled vanilla Slot-B boot plan — not executed

This is a future procedure requiring separate explicit authorization. No write,
slot activation, or package-state operation described below was performed in
this task.

## Artifacts

- product:
  `product-b-vanilla-debug.img`
  SHA-256 `e8a6b134a4f32b6f9fbdea337c8384c75ba9c4897f385be51d437be2bc46af8b`
- root vbmeta:
  `vbmeta_b.vanilla-debug.img`
  SHA-256 `39ab5e9e6eabc2fa33e9a8e0aec842fc650828f5f8cb505f9e2ea655fab7c917`

## Procedure

1. Boot normally and prove the runtime is healthy Slot A.
2. Require `sys.boot_completed=1` on A.
3. Require authorized root and record only non-secret identity/status evidence.
4. Hash the shared metadata encryption key in place and require:
   `1eac61edfe777d0c6fa2f2d4f62ec892b6a031b90cb7064e4d6581c0a944fbca`.
   Never print or copy key contents.
5. Read and verify current `system_b` against
   `68b4639959dd189fcc6e6603742a4b4ef57f6106d444da48ef884031a69d1a99`.
6. Read and verify current diagnostic `product_b` against
   `a0a7eb7692dfc27e261d17eef366cd43beff351f5e67979ae35aa1d2e17d329d`.
7. Back up the exact current `product_b` and first 8192 bytes of root
   `vbmeta_b`; hash the backups before any write.
8. Enter the appropriate bootloader/fastbootd modes and write **only** the new
   `product_b` and its paired root `vbmeta_b`. Do not touch A, system,
   system-ext, vendor, userdata, metadata, or super metadata.
9. Read both B targets back and require exact hashes matching the candidate
   artifacts.
10. Activate Slot B once without marking it successful.
11. Capture authorized early ADB through the retained diagnostic
    `ro.adb.secure=0` system.
12. Observe `sys.boot_completed` without clearing any state.
13. Collect PackageManager, `system_server`, zygote, vold, keystore2, storage,
    and full logcat evidence.
14. Confirm these old fatal strings are absent:
    - `Unknown source permission com.google.android.gms.permission.ACTIVITY_RECOGNITION`
    - `Required services extension package is missing`
    - `config_servicesExtensionPackage ... com.google.android.ext.services`
15. Record any distinct next blocker without editing shared `/data` package or
    permission state.
16. Return to A through **BOOTLOADER fastboot**, not recovery and not a wipe.
17. Re-hash the shared metadata key and require the expected hash.
18. Confirm A boots fully and mark A successful if required by slot metadata.
19. Re-read/hash B product and vbmeta to prove the diagnostic artifacts remain
    exact after the test.

## Prohibited during the test

- no factory reset, formatting, repair fsck, or super resize
- no deletion or editing under `/data/system`, permission APEX data, or user
  package state
- no Slot-A partition writes
- no vendor, metadata, calibration, NVRAM, or system writes

Missing-package warnings inherited from shared Slot-A userdata are acceptable
unless direct evidence shows one becomes fatal.
