# Source lineage — CAMERA-ISP-KERNEL

The reproducible source of truth is the repository described in [SOURCE.md](SOURCE.md),
not any mutable scratch worktree.

## Public base

| package | upstream commit | subtree / use |
|---|---|---|
| AOSP common kernel | `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09` | exact Android 14 GKI 6.1 baseline |
| Android clang prebuilt | `7775eb113f960bc69a780b621d03a715914d4bca` | `clang-r487747c` |
| NothingOSS kernel modules | `5f75a3b13e8135d45b4b0b70ec893345144f70df` | `mtkcam` base |
| NothingOSS device modules | `957dac185efe46cbf6336b0fff9516d84c8cd78f` | PDA, VMM and shared headers |
| Android CI KMI | build `12901745` | `vmlinux.symvers` |

The recipe checks git tree ids, not just commit names. Expected pristine trees and SHA-256
values are recorded in the source repository and summarized in [SOURCE.md](SOURCE.md).

## Device reconstruction

Three reviewable patches create the GQ5012BF1 source. Their assembled tree ids are fixed:

* `mtkcam`: `4b75fc209a4b8a608aec9dc5b86d29fa095646fe`;
* kdm: `ceab410136a0542d16d3654bb73634cef09ff1f8`.

The largest patch supplies the device's nine imgsensor translation-unit families and
frame-sync/YFT integration. The other changes reconcile the MT6878 camera packages and
vendor headers with measured stock functions, objects, strings, source-line `BUG()`
records, relocations and object layout. See [RECONSTRUCTION-REPORT.md](RECONSTRUCTION-REPORT.md)
§3 for the behavioural groups.

## Unmodified public-source closures

The following stock modules require no device source delta:

* `pda_drv_mt6878.ko`;
* `mtk-vmm-isp71-regulator.ko`;
* `mtk-vmm-notifier.ko`.

Their exact match is useful lineage evidence: the Ulefone build shares those NothingOSS
MT6878 implementations directly.

## Historical candidates

[source-candidates.tsv](source-candidates.tsv) and the previous 133c6c1/ALPS worktrees are
retained as discovery provenance. Candidate name overlap never constituted parity. The
accepted source is only the pinned recipe whose B1/B2 outputs pass the complete ledgers.

## Binary-independent reproduction

Stock modules are comparison operands, not source inputs. Their only build-time use is
outside the build itself: `scripts/verify.py` compares the already-built outputs. External
provider CRC input is either naturally regenerated from public provider source (97 rows)
or explicitly retained from the corresponding stock provider export (10 rows); see
[abi-parity.md](abi-parity.md).
