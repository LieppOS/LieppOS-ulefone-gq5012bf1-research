# Slot-B `system_ext` DB-24 provider candidate

## Scope and safety

Offline build plus read-only analysis for the Ulefone Armor 29 Pro
(`gq5012bf1`) Slot-B `system_ext` partition.

Nothing was flashed. Slot B was not activated. Slot A, userdata, the shared
Lineage settings database, metadata, and super metadata were not modified.

Images stay outside Git under
`/mnt/SamsungSSD/TIER3/phase4/controls/system-ext-b-lineagesettings-db24-debug/`.
`BUILD-ARTIFACT-MANIFEST.txt` in that directory is the authoritative hash list;
it is mirrored here as `BUILD-ARTIFACT-MANIFEST.txt`.

## Blocker being addressed

The coherent vanilla Slot-B product removed both Google PackageManager
blockers. The next fatal, proven live, is `system_server` crashing while
installing `org.lineageos.lineagesettings.LineageSettingsProvider`:

`android.database.sqlite.SQLiteException: Can't downgrade database from version 24 to 21`
at `SQLiteOpenHelper.onDowngrade` through
`LineageSettingsProvider.establishDbTracking`.

Slot A is a Lineage 23.2 / SDK 36 userspace whose provider declares
`DATABASE_VERSION = 24` and already created the shared
`/data/user_de/0/org.lineageos.lineagesettings/databases/lineagesettings.db`
at version 24. Slot B is an SDK 35 userspace whose provider declares
`DATABASE_VERSION = 21`, so opening the shared database requests a downgrade and
`SQLiteOpenHelper` aborts. Because `system_server` dies during provider
installation, Slot B never reaches `sys.boot_completed`.

The shared database must not be downgraded or deleted while Slot A is the
daily-boot slot, so the repair has to move Slot B's provider to version 24.

## Repair strategy

Constant-only migration of Slot B's provider rather than a userspace generation
change:

1. `lineage-sdk` at commit `70465a5d433bc8a1a0204c5e9a604b002a39345b` was copied
   into an isolated tree; exactly one hunk changed
   (`DATABASE_VERSION 21 → 24`, `PROVIDER-SOURCE-PATCH.diff`).
2. `m LineageSettingsProvider` in the normal `lineage_armol-bp1a-userdebug`
   configuration produced the replacement APK.
3. The replacement APK was placed into an exact replica of the live
   `system_ext_b` tree and rebuilt with the proven EROFS + AVB procedure.

Upstream `lineage-23.2` reference is recorded in
`UPSTREAM-LINEAGE-DATABASE-HELPER-22.2-vs-23.2.diff` and
`UPSTREAM-21-24-SCHEMA-AUDIT.txt`: the whole `upgradeVersion` path from 21 to 24
contains **no** DDL/DML against the Lineage settings tables (`CREATE/DROP/ALTER`,
indexes, `execSQL`, `compileStatement`, `insert/update/delete` counts all 0). The
22, 23 and 24 steps only call `Settings.Secure`/global default loaders. Therefore
version 21 and version 24 share one schema, and the patched Slot-B provider can
open the existing version-24 database without any schema operation.

## Verification

### Provider APK (`PROVIDER-*.txt`)

- Signing, badging, manifest and resource dumps are byte-identical
  (`apksigner`/`aapt2` output compared pair-wise) — same platform signature, so no
  PackageManager signature-mismatch risk against the stored package record.
- Zip entries: `ADDED=0`, `REMOVED=0`, content changed only in `classes.dex` and
  its three `META-INF` records; `classes.dex` keeps the identical size 40452.
- Decompiled DEX diff (`PROVIDER-JADX-DEX-DIFF.txt`) shows exactly one changed
  statement: the `SQLiteOpenHelper` super-call version constant `21 → 24`.

### Partition image (`TREE-`, `IMAGE-`, `CANDIDATE-*.txt`)

- Reproduction control: rebuilding the untouched tree reproduced the live image to
  within 7 bytes, all of them non-semantic EROFS superblock bookkeeping
  (`sb+0x04` crc32c superblock checksum, `sb+0x20` `build_time_nsec`). Every
  semantic superblock attribute from `dump.erofs` matches: magic, blocksize,
  total blocks 87874, meta start, root nid 39, inode count 3860, creation time
  `Wed Aug 12 02:07:51 2026`, features `sb_csum mtime xattr_filter 0padding`,
  UUID `ed639924-966e-5159-8c17-be23b62cf6c6`.
- Candidate vs live image over all 3860 paths: added 0, removed 0, content
  differences 1 (`priv-app/LineageSettingsProvider/LineageSettingsProvider.apk`),
  and 0 differences in type, mode, owner, mtime, nlink, rdev, regular size,
  directory size, xattrs, symlink targets.
- Final image keeps the exact existing partition size 366891008 bytes, the first
  359931904 bytes (the whole EROFS payload) are byte-identical to the validated
  raw image, `fsck.erofs` passes.

### AVB (`SYSTEM-EXT-CANDIDATE-AVB-*`, `VBMETA-B-*.txt`)

- New hashtree footer: sha1, `fec_num_roots 2`, salt
  `b6497d…24aa6`, same three `com.android.build.system_ext.*` props, new root
  digest `46988ddf233c2ab42b3711085da86dcd45cdaefb`; `avbtool verify_image`
  verifies the hashtree.
- The `system_ext` hashtree descriptor lives only in **root `vbmeta_b`**
  (`vbmeta_system_b` carries only `system`, `vbmeta_vendor_b` only `vendor`), so a
  rebuilt root `vbmeta_b` is the complete and sufficient metadata change; this
  mirrors the proven product control.
- Root `vbmeta_b` rebuilt with the same key, algorithm `SHA256_RSA2048`, rollback
  index 0/0, flags 3, padding 4096, same chain partitions and the same eight
  included images except the new `system_ext`. Its `info_image` output differs
  from the current one in exactly two lines: the `system_ext` root digest.
- `avbtool verify_image` on the new root vbmeta reaches exactly the same state as
  on the current live root vbmeta (`VBMETA-B-VERIFY-*`): the vbmeta struct itself
  verifies against `root.pem`, all three chain partitions match, `dtbo` verifies,
  and both runs stop at the same pre-existing `init_boot` hash-descriptor
  mismatch of the dumped live image. Verified outcome is identical.

## Candidate artifacts

- `system_ext`:
  `/mnt/SamsungSSD/TIER3/phase4/controls/system-ext-b-lineagesettings-db24-debug/system-ext-b-lineagesettings-db24-debug.img`
  SHA-256 `41140a783a0417c3c91f9688cd71aa98e58fb31d9c4e2e2b488c3286814acd79`,
  size `366891008`
- root vbmeta:
  `/mnt/SamsungSSD/TIER3/phase4/controls/system-ext-b-lineagesettings-db24-debug/vbmeta_b.system-ext-db24-debug.img`
  SHA-256 `98fc5ca45f78f2a3d8bd01a07d21fff82c70b5b9e9583e7be87fd8eb7707551b`,
  size `8192`

## Classification

### PROVEN

- Slot A provider is version 24, Slot B provider is version 21; the shared DB is
  version 24 and Slot B provably crashes on it.
- The patched provider differs from the shipped one only in the DB version
  constant plus its re-signature, with identical manifest, resources, and signer.
- The 21→24 upstream upgrade path performs no schema or table-level SQL.
- The candidate image differs from the live image in exactly one file and
  preserves every metadata attribute and the exact partition size.
- Root `vbmeta_b` is the only verifier of the `system_ext` hashtree and the new
  copy changes only that digest.

### INFERRED

Slot B should get past provider installation: opening the existing version-24
database becomes a same-version open, so `onDowngrade` is never reached. The
three settings normalizations belonging to versions 22-24 do not run on Slot B
(its provider carries no 21→24 upgrade bodies); they are data-level defaults that
Slot A already applied to the same shared database, so this is a cosmetic gap and
not a boot dependency.

### TEST TO CONFIRM

Only a separately authorized controlled Slot-B boot can show that
`LineageSettingsProvider` installs, `system_server` survives provider startup,
and the next distinct blocker is revealed. **This report does not claim that the
candidate boots.** See `LIVE-BOOT-PLAN.md` — not executed.
