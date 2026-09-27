# Shared userdata risk: Android 16 A ↔ Android 17 test

## Decision

```text
SHARED_USERDATA_DIRECT_TEST_SAFE=0
```

Direct Slot-B Android 17 boot against A's live userdata is a **KNOWN BLOCKER**,
not merely a caution. Nothing in this pass modified userdata or metadata.

## Proven version transitions

Official Lineage 23.2 files were compared with the synced Lineage 24 source:

| State | A / Android 16 | Android 17 | Return-to-A risk |
|---|---:|---:|---|
| Contacts DB | 1800 | 1800 | no version change |
| CallLog DB | 14 | 14 | no version change |
| MMS/SMS DB | 70 | 73 | Android16 helper sees newer SQLite DB; no proven downgrade path |
| Telephony/APN DB | `74<<16` | `78<<16` | Android downgrade handler can delete/rebuild provider DB and lose settings |
| Settings state | 231 | 236 | Android16 treats mismatch as failed upgrade, removes state and recreates it |
| LineageSettings DB | 24 | 24 | native compatibility; old SDK35 shim is unnecessary |
| MediaProvider DB | 1602 | 1700 | reverse schema depends on downgrade schema support; not proven safe |
| Launcher DB | 32/34 | 32/34 | no source version change under matching flags |
| Accounts CE/DE DB | 10/3 | 10/3 | no source version change |

Android17 Settings 231→236 performs real mutations: HDR brightness conversion,
airplane/watch default, adaptive-connectivity split, Wear default and password
setting migration. The Android16 `upgradeIfNeededLocked()` has no downgrade
branch: with version 236 versus expected 231, it fails to reach its target,
drops Settings state and recreates it. This alone makes rollback unsafe.

Contacts explicitly throws through SQLiteOpenHelper for unsupported downgrade,
although its A16/A17 version happens to match. The previously observed
LineageSettings 24→21 fatal proves these are real shared-data failures, not
hypothetical API concerns.

## Other state

| State | Assessment |
|---|---|
| PackageManager `packages.xml` and package settings | forward scan will rewrite package/component/signature/domain state; old parser tolerance is not rollback assurance |
| permission/access state | API37 raises per-package access version to 19/20 depending flags; A16 may warn on an unexpected future version and skip intended migrations |
| APEX and module data | `/data/apex`, `/data/misc/apexdata` and module-owned data are release-coupled; rollback snapshots exist only when orchestrated by Android rollback infrastructure |
| ART/dalvik cache | API37 recompilation is expected; A16 can often rebuild, but cache behavior is not a data rollback contract |
| keystore/accounts | DB constants are stable, but KeyMint/keystore and account authenticators can update records; raw file restore may not revert secure hardware state |
| launcher/media | launcher schema stable; Media schema advances and is not certified reversible |

## Architecture evaluation

### A. Direct shared userdata

**REJECT / KNOWN BLOCKER.** It can upgrade state before boot completion and can
make A destructive or unable to open providers on return.

### B. Isolated userdata

**BEST if DSU is validated.** Stock/current captures contain `gsid`, `gsi_tool`,
`DynamicSystemInstallationService`, `/metadata/gsi`, and `gsi_tool status`
returns `normal`. AOSP GSID creates separate backing images under
`/data/gsi/dsu/` and defaults to a separate 2 GiB guest userdata image, with a
DSU metadata-encryption key. Android17 then does not mount A's normal userdata
as guest `/data`.

**TEST TO CONFIRM:** the framework does not advertise
`android.software.dynamic_system` and `cmd dynamic_system` has no shell
implementation. Do not assume installation works until a separately authorized
DSU capability test proves it. DSU itself writes host `/data/gsi` and
`/metadata/gsi`; none of that was done here.

### C. Snapshot/backup plus shared use

A verified offline block snapshot of both userdata and metadata is better than a
file backup, but still second choice: live `dd` is inconsistent, FBE/keystore
state is coupled, and secure/RPMB state may not roll back. Android's package
rollback snapshots are not automatically created by an arbitrary slot image.

### D. Other

No second physical userdata partition, supported dual-data fstab, or safe
63-MiB-super solution is proven. Do not invent one, and do not factory-reset or
format metadata.

## Recommendation

Use a DSU GSI with its separate guest userdata image for the first hardware
framework/vendor proof **after DSU support is explicitly validated**. If DSU
cannot be proven, stop: do not perform a direct A16-data Android17 boot. Build a
rehearsed offline snapshot/restore architecture before any slot test.
