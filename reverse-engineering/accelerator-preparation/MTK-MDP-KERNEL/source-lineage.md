# Source lineage — MTK-MDP-KERNEL

> **Resolved.** The exact source of all four shipped modules is the public ALPS release
> `5e415e059253ce0d2e61c97108e5f5785d71f06f` (tree `9c61acc3cb0d9bb7f5dbabb51adc2b3fd993810c`),
> with **no C or header modification**. The NothingOSS donor `957dac18` is identical for
> `mdp_drv_mt6878`, `mtk-mml-mt6878` and `clk-mt6878-mdpsys` but differs in 18 of the 31
> files compiled into `mtk-mml.ko`, so it is not the stock source; it is retained for the
> vendor Kconfig/defconfig only. The patched worktree `ca8b550b75e8` is unused. See
> [SOURCE.md](SOURCE.md) and [stale-claims.md](stale-claims.md). The table below is the
> original triage record.

Every donor directory/file exists. Commits and complete relevant-file fingerprints are in [source-candidates.tsv](source-candidates.tsv). The ALPS snapshot local commit `2ae742fda9cd461bfe8cf8a5c04f95e212f8e699` identifies a pristine archive of upstream MT6878 ALPS `5e415e059253`; it is not misrepresented as the upstream Git commit. The Nothing donor import and the patched mixed-build tree are distinct candidates. Do not reset or edit any of these shared checkouts.

| Module | Local donor | Local Git commit | Starting state |
|---|---|---|---|
| `mdp_drv_mt6878.ko` | `/home/armol/androido_dalykai/LieppOS custom ROM/kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/mdp` | `957dac185efe46cbf6336b0fff9516d84c8cd78f` | LOCAL SOURCE CANDIDATE; parity not implied |
| `mdp_drv_mt6878.ko` | `/home/armol/kernel-work/gki-12901745-workspace/lieppos/tinysys/trees/5e41/drivers/misc/mediatek/mdp` | `2ae742fda9cd461bfe8cf8a5c04f95e212f8e699` | ALTERNATIVE PINNED LOCAL CANDIDATE; ALPS archive origin 5e415e059253 |
| `mdp_drv_mt6878.ko` | `/home/armol/kernel-work/gki-12901745-workspace/kernel_device_modules-6.1/drivers/misc/mediatek/mdp` | `ca8b550b75e8b49f403f0097e8323c4a930bad79` | EXISTING PATCHED WORKSPACE; read-only candidate, do not edit |
| `mtk-mml.ko` | `/home/armol/androido_dalykai/LieppOS custom ROM/kernel-research/nothing-mt6878/device_modules/drivers/gpu/drm/mediatek/mml` | `957dac185efe46cbf6336b0fff9516d84c8cd78f` | LOCAL SOURCE CANDIDATE; parity not implied |
| `mtk-mml.ko` | `/home/armol/kernel-work/gki-12901745-workspace/lieppos/tinysys/trees/5e41/drivers/gpu/drm/mediatek/mml` | `2ae742fda9cd461bfe8cf8a5c04f95e212f8e699` | ALTERNATIVE PINNED LOCAL CANDIDATE; ALPS archive origin 5e415e059253 |
| `mtk-mml.ko` | `/home/armol/kernel-work/gki-12901745-workspace/kernel_device_modules-6.1/drivers/gpu/drm/mediatek/mml` | `ca8b550b75e8b49f403f0097e8323c4a930bad79` | EXISTING PATCHED WORKSPACE; read-only candidate, do not edit |
| `mtk-mml-mt6878.ko` | `/home/armol/androido_dalykai/LieppOS custom ROM/kernel-research/nothing-mt6878/device_modules/drivers/gpu/drm/mediatek/mml` | `957dac185efe46cbf6336b0fff9516d84c8cd78f` | LOCAL SOURCE CANDIDATE; parity not implied |
| `mtk-mml-mt6878.ko` | `/home/armol/kernel-work/gki-12901745-workspace/lieppos/tinysys/trees/5e41/drivers/gpu/drm/mediatek/mml` | `2ae742fda9cd461bfe8cf8a5c04f95e212f8e699` | ALTERNATIVE PINNED LOCAL CANDIDATE; ALPS archive origin 5e415e059253 |
| `mtk-mml-mt6878.ko` | `/home/armol/kernel-work/gki-12901745-workspace/kernel_device_modules-6.1/drivers/gpu/drm/mediatek/mml` | `ca8b550b75e8b49f403f0097e8323c4a930bad79` | EXISTING PATCHED WORKSPACE; read-only candidate, do not edit |
| `clk-mt6878-mdpsys.ko` | `/home/armol/androido_dalykai/LieppOS custom ROM/kernel-research/nothing-mt6878/device_modules/drivers/clk/mediatek/clk-mt6878-mdpsys.c` | `957dac185efe46cbf6336b0fff9516d84c8cd78f` | LOCAL SOURCE CANDIDATE; parity not implied |
| `clk-mt6878-mdpsys.ko` | `/home/armol/kernel-work/gki-12901745-workspace/lieppos/tinysys/trees/5e41/drivers/clk/mediatek/clk-mt6878-mdpsys.c` | `2ae742fda9cd461bfe8cf8a5c04f95e212f8e699` | ALTERNATIVE PINNED LOCAL CANDIDATE; ALPS archive origin 5e415e059253 |
| `clk-mt6878-mdpsys.ko` | `/home/armol/kernel-work/gki-12901745-workspace/kernel_device_modules-6.1/drivers/clk/mediatek/clk-mt6878-mdpsys.c` | `ca8b550b75e8b49f403f0097e8323c4a930bad79` | EXISTING PATCHED WORKSPACE; read-only candidate, do not edit |

**Build baseline:** Android CI 12901745; `common` `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`; stock vermagic `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64`; Android Clang 17.0.2 `clang-r487747c` (10087095), LLVM integrated assembler/lld, exact GKI/KMI and vendor config. Recorded config: `reverse-engineering/camera-stack/kernel-isp-imgsys/build/vendor-kernel.config`; CI pins: `kernel/exact-gki-build-inputs.md`. Inspect CONFIG_CFI_CLANG/MODVERSIONS and effective per-object LTO/visibility flags. `-faddrsig` was necessary in existing parity builds; verify rather than broadly changing compiler flags. Legacy camera scripts depend on `/tmp/ispenv.sh` and enable modpost warnings; do not call them blindly or count ignored unresolved symbols as success.

No existing complete MDP/MML source-parity owner or measured rebuild was found. Public donor availability is not proof that hardware behavior or shipped module bytes match.

Input fingerprints identify actual local donor bytes, including grafted/patch worktree files. The enclosing Git pin alone does not prove every donor file is committed; archive only verified tracked inputs, or copy exact fingerprint-checked inputs into isolated scratch space without touching the source.

Exact source candidates, build targets and object composition remain subject to stock function/data/CRC/KCFI evidence; namespace/name overlap is triage, never parity.
