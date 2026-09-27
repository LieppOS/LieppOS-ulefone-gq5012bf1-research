# Safest Android 17 first-boot architecture — not executed

This is a future plan. It does not authorize a phone write.

## Recommendation

`RECOMMENDED_FIRST_BOOT_ARCHITECTURE=VALIDATED_DSU_WITH_SEPARATE_GUEST_USERDATA`

The official GSI's folded partition layout fits DSU naturally, and GSID creates
a separate guest userdata backing image (2 GiB default) under `/data/gsi/dsu`.
That prevents API37 providers from upgrading A's mounted Android16 userdata.

## Gate 0 — host completion

1. Provide at least 110 GB additional free SSD space (150 GB preferred).
2. Build a vanilla ARM64 EROFS `lineage_gsi_arm64 cp2a userdebug`.
3. Hash it, inspect filesystem/AVB, run host VINTF checks and record exact size.
4. Do not inject SDK35 compatibility edits. Debugging, if needed, must be a
   separately named temporary variant.

## Gate 1 — DSU capability proof

Read-only facts already proven: stock/current system contains `gsid`, `gsi_tool`,
`DynamicSystemInstallationService`; `/metadata/gsi` exists; status is `normal`.
The framework feature `android.software.dynamic_system` is absent, so actual
installation is **UNKNOWN**.

Under separate explicit authorization, first verify service/API availability,
no existing DSU, free userdata capacity and recovery behavior. DSU installation
writes `/data/gsi` and `/metadata/gsi` and creates a DSU encryption key; do not
run it under this report's authorization.

## Gate 2 — isolated proof

If DSU is proven:

1. Install only the hashed Android17 GSI plus a dedicated guest userdata image.
2. One-shot boot; do not mark or modify physical Slot B.
3. Capture early init/vold/VINTF/SELinux/BPF/HAL and `sys.boot_completed`.
4. Test only framework/vendor/kernel compatibility first; do not enroll accounts
   or migrate personal content.
5. Disable/wipe the DSU through its supported mechanism and prove A returns with
   its provider database/settings hashes and metadata-key hash invariant intact.

## If DSU is unavailable

**STOP.** Do not fall back to direct shared userdata. Before a physical B boot,
build and rehearse an offline, consistent block snapshot/restore procedure for
both userdata and metadata and assess secure/RPMB state that cannot be restored.
A normal file backup is insufficient. No factory reset or metadata format is
acceptable.

## Later physical Slot-B proof

Only after DSU userspace success:

- build separate system/system_ext/product images that each fit current extents;
- complete host VINTF, SELinux, ELF, filesystem and size gates;
- resolve all AVB descriptors into a flags-0 fully verified B chain;
- back up/read back every B target, write B only, boot once, capture, and return
  through bootloader control without touching A;
- keep shared-userdata boot prohibited until data compatibility is solved.

## Rejected architectures

- **direct B with A userdata:** known destructive/fatal downgrade risk;
- **factory reset or metadata format:** prohibited and destroys the daily anchor;
- **invented second userdata partition in super:** unsupported and only ~63.45
  MiB free;
- **live userdata `dd` as backup:** inconsistent and not a rollback guarantee.

Nothing in this plan was executed.
