# Source initialization and sync

## Isolation

```text
existing tree: /mnt/SamsungSSD/android/lineage-22.2   (untouched)
new tree:      /mnt/SamsungSSD/android/lineage-24.0
logs:          /mnt/SamsungSSD/TIER3/phase5/android17/logs/
reports:       /mnt/SamsungSSD/TIER3/phase5/android17/reports/
```

No existing source tree was deleted, cleaned or modified.

## Init

**PROVEN successful:** exact requested official initialization command:

```sh
repo init -u https://github.com/LineageOS/android.git -b lineage-24.0 --git-lfs
```

Manifest before sync:
`f16772cb8c33a15e970abe42d7bb120e2dc84f33`.

## Sync

Initial command used current-branch, no-tags, no-clone-bundle, optimized fetch,
prune and 16 jobs. It ran from `20:36:28` to `22:13:36` local time and fetched
most projects, then Android GoB returned `RESOURCE_EXHAUSTED` for seven projects.
This was an upstream quota/transient fetch failure, not a source edit.

A safe serial retry was limited to those seven projects:

```text
external/hyphenation-patterns
external/icu
external/jackson-annotations
external/jackson-core
external/libese
external/linux-firmware
external/toolchain-utils
```

`repo sync -c -j1 --fail-fast ...` completed successfully at `22:21:14`.
A final local-only checkout pass succeeded.

## Result

| Check | Result |
|---|---|
| final manifest commit | `f16772cb8c33a15e970abe42d7bb120e2dc84f33` |
| resolved projects | 1238 |
| missing worktrees | 0 |
| sync success | **1** |
| source tree usage | 203965796352 bytes (190 GiB) |
| resolved manifest | `/mnt/SamsungSSD/TIER3/phase5/android17/reports/manifest-resolved.xml` |

Full logs stay outside Git. No source patch was applied to make sync finish.
