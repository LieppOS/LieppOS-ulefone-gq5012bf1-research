# Controlled Slot-B DB-24 boot plan — not executed

Future procedure requiring separate explicit authorization. No write, slot
activation, or package-state operation described here was performed in this task.

## Artifacts

- `system_ext`:
  `/mnt/SamsungSSD/TIER3/phase4/controls/system-ext-b-lineagesettings-db24-debug/system-ext-b-lineagesettings-db24-debug.img`
  SHA-256 `41140a783a0417c3c91f9688cd71aa98e58fb31d9c4e2e2b488c3286814acd79`
  (exact current partition size, `366891008` bytes)
- paired root vbmeta:
  `/mnt/SamsungSSD/TIER3/phase4/controls/system-ext-b-lineagesettings-db24-debug/vbmeta_b.system-ext-db24-debug.img`
  SHA-256 `98fc5ca45f78f2a3d8bd01a07d21fff82c70b5b9e9583e7be87fd8eb7707551b`
  (8192 bytes)

These two must always be written as a pair; the new `system_ext` root digest
`46988ddf233c2ab42b3711085da86dcd45cdaefb` exists only in this vbmeta copy.

## Preflight expectations (read-only, must already hold)

1. Healthy Slot A: `ro.boot.slot_suffix=_a`, `sys.boot_completed=1`.
2. Authorized root available for capture only; record non-secret identity/status.
3. Shared metadata encryption key hashed in place equals
   `1eac61edfe777d0c6fa2f2d4f62ec892b6a031b90cb7064e4d6581c0a944fbca`;
   never print or copy its contents.
4. Current B logical partitions hash as:
   - `system_b` `68b4639959dd189fcc6e6603742a4b4ef57f6106d444da48ef884031a69d1a99`
   - `product_b` `e8a6b134a4f32b6f9fbdea337c8384c75ba9c4897f385be51d437be2bc46af8b`
   - `system_ext_b` `a63bd6e22cc8a451a7ffb0d8c9f026957c9ea03f89f032fd408134805865af4a`
   - root `vbmeta_b` `39ab5e9e6eabc2fa33e9a8e0aec842fc650828f5f8cb505f9e2ea655fab7c917`
5. Shared Lineage settings database hashes to
   `4cb61014c32ba48f86c7fac68e6059cdd2eebf78fade9e86b339ba8e1e0ef7a7`
   (`/data/user_de/0/org.lineageos.lineagesettings/databases/lineagesettings.db`,
   53248 bytes) and its SHA-256 is recorded.

Any mismatch stops the test before a write.

## Procedure

1. Back up the exact current `system_ext_b` and root `vbmeta_b`; hash both backups
   before any write.
2. Write root `vbmeta_b` in bootloader fastboot and `system_ext_b` in
   userspace fastboot (dynamic partition). Write **only** those two B targets.
3. Read both back and require the exact candidate hashes above.
4. Activate Slot B once without marking it successful.
5. Capture authorized early ADB through the retained diagnostic `ro.adb.secure=0`
   system.
6. Observe `sys.boot_completed` without clearing any state.
7. Require `LineageSettingsProvider` to be installed and to resolve to the DB-24
   provider, and require `system_server` to survive provider installation; collect
   PackageManager, `system_server`, zygote, vold, keystore2, storage, and full
   logcat evidence.
8. Require that the previous fatals remain absent:
   - `Unknown source permission com.google.android.gms.permission.ACTIVITY_RECOGNITION`
   - `Required services extension package is missing`
   - `config_servicesExtensionPackage ... com.google.android.ext.services`
   - `Can't downgrade database from version 24 to 21`
9. Record any distinct next blocker without editing shared `/data` package,
   permission, or settings state.
10. Return to Slot A through **bootloader fastboot**, not recovery and not a wipe.
11. Re-hash the shared metadata key (expect the preflight value) and re-hash the
    shared Lineage settings database, attributing any change to Slot-A writes
    only after Slot A is booted again.
12. Confirm A boots fully, mark A successful if slot metadata requires it, then
    re-read and re-hash B `system_ext` and `vbmeta` to prove the diagnostic
    artifacts remain exact.

## Prohibited

- no factory reset, format, repair/fsck, or super resize
- no downgrade, deletion, rename, or hand-edit of the shared Lineage settings
  database or its journal
- no writes to A partitions, `/data`, `metadata`, NVRAM, or calibration regions
- no slot-successful marking of B before the evidence is captured
