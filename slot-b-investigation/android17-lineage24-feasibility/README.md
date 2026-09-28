# LineageOS 24.0 / Android 17 host feasibility

Host-side source and build feasibility pass for the Ulefone Armor 29 Pro
(`gq5012bf1`, MT6878 family). Research baseline was
`fc662645511dd03052f87cba9d57efb66f886e19`.

> **Build continuation:** the storage blocker was later resolved and the EROFS
> GSI build succeeded. Actual artifacts, folded-payload measurements and Slot-B
> fit results are in [`build-and-measure/`](build-and-measure/). That directory
> supersedes the pre-build size/build-status statements below while preserving
> this original feasibility snapshot.
>
> **Split-product continuation:** a real `lineage_gq5012bf1` target now builds
> separate system/system_ext/product images, all three fit the current B extents,
> and host VINTF/AVB validation passes. See
> [`gq5012bf1-split-product/`](gq5012bf1-split-product/). That directory is the
> authoritative current Android 17 result.

## Executive result

| Question | Answer | Classification |
|---|---|---|
| Does official `lineage-24.0` exist and configure? | Yes. Manifest `f16772cb8c33a15e970abe42d7bb120e2dc84f33`; Android 17/API 37; `lineage_gsi_arm64 cp2a userdebug` lunches and `m nothing` succeeds. | **PROVEN** |
| Did a complete image build run? | No. Sync plus build-graph generation left 57,484,259,328 bytes free. The 150 GB build-space planning allowance was short by 92,515,740,672 bytes, so the massive build was not started. | **BLOCKER** |
| Can current vendor/kernel plausibly reach an initial Android 17 boot? | Yes, plausibly: vendor FCM 8/NDK 34/sepolicy 34.0 remain supported; the exact 6.1 config satisfies the retained Android-U/6.1 requirements. Runtime is untested. | **INFERRED** |
| Do unmodified official GSI artifacts fit B? | The official target emits one system image with `product` and `system_ext` folded into it, not the required three-image B layout. No image exists to measure. It is not directly flashable as a coherent B set. | **PROVEN / UNKNOWN size** |
| Is direct use of A's shared userdata safe? | No. Android 17 moves Settings 231→236, MMS/SMS 70→73, APN 74→78 and Media 1602→1700. Returning to Android 16 has destructive/fatal downgrade paths. | **KNOWN BLOCKER** |
| Safest first hardware architecture | Validate DSU and use its separate userdata image before any B-partition build; otherwise do not boot Android 17 on this shared data. | **TEST TO CONFIRM** |

## Important direction

The SDK35 B chain is a proven bring-up/rollback reference only. Its release
property edit, insecure-ADB edit, DB24 constant shim and selective Google config
removal are **not** Android 17 production inputs. Lineage 24 supplies its native
API-37 framework, providers and configuration.

## Current proven B reference

| Partition | SHA-256 | Extent |
|---|---|---:|
| `system_b` | `68b4639959dd189fcc6e6603742a4b4ef57f6106d444da48ef884031a69d1a99` | 665391104 |
| `product_b` | `e8a6b134a4f32b6f9fbdea337c8384c75ba9c4897f385be51d437be2bc46af8b` | 337686528 |
| `system_ext_b` | `41140a783a0417c3c91f9688cd71aa98e58fb31d9c4e2e2b488c3286814acd79` | 366891008 |
| `vbmeta_b` | `98fc5ca45f78f2a3d8bd01a07d21fff82c70b5b9e9583e7be87fd8eb7707551b` | 8192 |

The shared metadata-key invariant remains hash-only:
`1eac61edfe777d0c6fa2f2d4f62ec892b6a031b90cb7064e4d6581c0a944fbca`.
Its contents were never read or printed.

## Files

- [`UPSTREAM-STATUS.md`](UPSTREAM-STATUS.md), [`HOST-ENVIRONMENT.md`](HOST-ENVIRONMENT.md), [`SOURCE-SYNC.md`](SOURCE-SYNC.md)
- [`BUILD-TARGETS.md`](BUILD-TARGETS.md), [`BUILD-RESULT.md`](BUILD-RESULT.md), [`BUILD-ARTIFACTS.tsv`](BUILD-ARTIFACTS.tsv), [`ANDROID17-PARTITION-FIT.tsv`](ANDROID17-PARTITION-FIT.tsv)
- [`MT6878-ANDROID17-COMPATIBILITY.md`](MT6878-ANDROID17-COMPATIBILITY.md), [`KERNEL-COMPATIBILITY.md`](KERNEL-COMPATIBILITY.md), [`VINTF-VENDOR-COMPATIBILITY.md`](VINTF-VENDOR-COMPATIBILITY.md)
- [`SIZE-REDUCTION-PLAN.md`](SIZE-REDUCTION-PLAN.md), [`CURRENT-B-VS-LINEAGE24.md`](CURRENT-B-VS-LINEAGE24.md)
- [`SHARED-USERDATA-RISK.md`](SHARED-USERDATA-RISK.md), [`FIRST-BOOT-PLAN.md`](FIRST-BOOT-PLAN.md)
- [`AVB-PLAN.md`](AVB-PLAN.md), [`DEVICE-TREE-MIGRATION-PLAN.md`](DEVICE-TREE-MIGRATION-PLAN.md)

## Safety result

**PROVEN:** no phone command was issued. Nothing was flashed; no slot was
activated; A, B, userdata, metadata and super metadata were untouched. No super
resize or source-tree deletion occurred.
