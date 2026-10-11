# Source lineage and local reconstruction commits

## Immutable public inputs

| Input | Commit | Verified tree |
|---|---|---|
| GKI common / modpost | `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09` | `710eb859513863cda0204995a411d5795ad3fe92` |
| Clang-r487747c | `7775eb113f960bc69a780b621d03a715914d4bca` | `8eb8e3afb00a52d48b29381d73daf352362231ad` |
| NothingOSS vendor Kconfig | `957dac185efe46cbf6336b0fff9516d84c8cd78f` | `05f9c65d40ef9e4bdbe17397a90edd303a5da6dd` |
| ALPS/Nothing implementation | `5e415e059253ce0d2e61c97108e5f5785d71f06f` | `9c61acc3cb0d9bb7f5dbabb51adc2b3fd993810c` |
| MiCode TCPC 2.0.31 subtree | `2d6f27aa19d521409f443c8d821e2d475bdc72b6` | `5166ca2ab7fba22712731484a80657f27641818c` |

Repositories: Android Googlesource `kernel/common`, `platform/prebuilts/clang/host/linux-x86`; NothingOSS `android_kernel_device_modules_6.1_nothing_mt6878`; MiCode `MTK_kernel_device_modules`, branch `bsp-chagall-w-oss`. No network fetch was made: bootstraps use the dedicated nonwritable mirror, local pinned commits and retained TCPC archive.

The TCPC public archive's SHA256 is `f7c290219fc86ca8dd5091602965be0bf6e2aabb73ce351f0c4239b2009eb41d`. The shared configuration remains pinned to the original vendor configuration, Clang 17.0.2 build 10087095, GKI artifact 12901745 and kernel release `6.1.115-android14-11-g945dff7bc1bf`. Full configuration/symvers hashes and source-only external ABI producer witnesses are preserved by independent build records; no provider CRC transplants.

## Baselines and new local commits

- Canonical research base: `f61ebf03275ba2d3f6aa4f9d5aebe18e12922263`, 245 certified / 213 remaining / 458 identities.
- Charging source baseline: `44ce4ff57556bba462772f4b164c2650b9caa0e3`.
- Type-C source baseline: `d41a2436c15fc53c25061dd9cd19d0e08f11ffbb`.
- Type-C source reconstruction commit: `a78b931945e87fe85aaa01c6d9c1766e0d450946`; final maintained debug-reproducible source **`758f9edc78c7a50d07b8629126438a3674845911`**.
- Charging/shared reconstruction commit: `feba82e92855aa3043e6bade9c1bc22f6b682242`; final maintained debug-reproducible source **`b2a343a9d8664b77a63dc16835b5af0fd0e55cf1`**.
- Dedicated source/research branch: `codex/usb-typec-closure`; source worktrees have the `-usb-typec-closure` suffix, research worktree `ulefone-gq5012bf1-research-codex-usb-typec-closure`.

Existing `0001`/`0002` patches and failed Batch04 experiments are retained. New `0003-stock-observed-tcpc-code-and-timers.patch` is identical in both independent engines. Full assembled tree changes from `ee1ba4f1b00915b54e0a207c3daa454da2ea0de1` to `2f08a85f28379aff76414c01ec8b6d3fc6ba5af1`; the old tree pin is retained as `reference/pre-closure-kdm-tree.txt`. Charging C/headers and `rt_pd_manager.c` are unchanged.

The initial four independent workspace builds compiled correctly and preserved 25 accepted/five rejected outputs, but failed raw determinism because DWARF retained workspace-specific compilation/source paths. Their bundles, workspaces and failure report remain preserved. Final commits add only standard `-fdebug-prefix-map` flags for KDM/common/KOUT; the pre-existing macro-prefix map is unchanged. These compiler flags canonicalize debug paths during compilation, not by ELF rewriting. All stock source/metadata acceptance remains unchanged.

## What is and is not authentic recovery

The bases, historical patches, source files/Git commits scanned, dependency graphs, compiler and sumversion implementation are real preserved inputs. The new selected-stock source algorithms/timer scalars are **reconstructions supported by complete stock machine-code/data comparisons**. They are not represented as a newly discovered original OEM release or exact OEM textual token stream. Six-field source diagnostics, BUG source-line values, original counter/include lineage and natural stock fingerprints are not fabricated.

Recoverable source bundles in `evidence/bundles/` were verified, cloned and checked with `git fsck --full` before independent compilation. Their hashes and full commits are recorded in `evidence/fresh-clones/source-commits.json`. No push was performed. Source changes are not integrated into canonical checkouts and do not modify runtime/component ownership.
