# Source lineage — GPU-AI-AUX-KERNEL-INTERFACES

Every donor directory/file exists. Commits and complete relevant-file fingerprints are in [source-candidates.tsv](source-candidates.tsv). The ALPS snapshot local commit `2ae742fda9cd461bfe8cf8a5c04f95e212f8e699` identifies a pristine archive of upstream MT6878 ALPS `5e415e059253`; it is not misrepresented as the upstream Git commit. The Nothing donor import and the patched mixed-build tree are distinct candidates. Do not reset or edit any of these shared checkouts.

| Module | Local donor | Local Git commit | Starting state |
|---|---|---|---|
| `gpueb.ko` | `/home/armol/androido_dalykai/LieppOS custom ROM/kernel-research/nothing-mt6878/device_modules/drivers/gpu/mediatek/gpueb` | `957dac185efe46cbf6336b0fff9516d84c8cd78f` | LOCAL SOURCE CANDIDATE; parity not implied |
| `gpueb.ko` | `/home/armol/kernel-work/gki-12901745-workspace/lieppos/tinysys/trees/5e41/drivers/gpu/mediatek/gpueb` | `2ae742fda9cd461bfe8cf8a5c04f95e212f8e699` | ALTERNATIVE PINNED LOCAL CANDIDATE; ALPS archive origin 5e415e059253 |
| `gpueb.ko` | `/home/armol/kernel-work/gki-12901745-workspace/kernel_device_modules-6.1/drivers/gpu/mediatek/gpueb` | `ca8b550b75e8b49f403f0097e8323c4a930bad79` | EXISTING PATCHED WORKSPACE; read-only candidate, do not edit |
| `vcp_status.ko` | `/home/armol/androido_dalykai/LieppOS custom ROM/kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/vcp/rv` | `957dac185efe46cbf6336b0fff9516d84c8cd78f` | LOCAL SOURCE CANDIDATE; parity not implied |
| `vcp_status.ko` | `/home/armol/kernel-work/gki-12901745-workspace/lieppos/tinysys/trees/5e41/drivers/misc/mediatek/vcp/rv` | `2ae742fda9cd461bfe8cf8a5c04f95e212f8e699` | ALTERNATIVE PINNED LOCAL CANDIDATE; ALPS archive origin 5e415e059253 |
| `vcp_status.ko` | `/home/armol/kernel-work/gki-12901745-workspace/kernel_device_modules-6.1/drivers/misc/mediatek/vcp/rv` | `ca8b550b75e8b49f403f0097e8323c4a930bad79` | EXISTING PATCHED WORKSPACE; read-only candidate, do not edit |
| `vcp.ko` | `/home/armol/androido_dalykai/LieppOS custom ROM/kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/vcp/rv` | `957dac185efe46cbf6336b0fff9516d84c8cd78f` | LOCAL SOURCE CANDIDATE; parity not implied |
| `vcp.ko` | `/home/armol/kernel-work/gki-12901745-workspace/lieppos/tinysys/trees/5e41/drivers/misc/mediatek/vcp/rv` | `2ae742fda9cd461bfe8cf8a5c04f95e212f8e699` | ALTERNATIVE PINNED LOCAL CANDIDATE; ALPS archive origin 5e415e059253 |
| `vcp.ko` | `/home/armol/kernel-work/gki-12901745-workspace/kernel_device_modules-6.1/drivers/misc/mediatek/vcp/rv` | `ca8b550b75e8b49f403f0097e8323c4a930bad79` | EXISTING PATCHED WORKSPACE; read-only candidate, do not edit |

**Build baseline:** Android CI 12901745; `common` `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`; stock vermagic `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64`; Android Clang 17.0.2 `clang-r487747c` (10087095), LLVM integrated assembler/lld, exact GKI/KMI and vendor config. Recorded config: `reverse-engineering/camera-stack/kernel-isp-imgsys/build/vendor-kernel.config`; CI pins: `kernel/exact-gki-build-inputs.md`. Inspect CONFIG_CFI_CLANG/MODVERSIONS and effective per-object LTO/visibility flags. `-faddrsig` was necessary in existing parity builds; verify rather than broadly changing compiler flags. Legacy camera scripts depend on `/tmp/ispenv.sh` and enable modpost warnings; do not call them blindly or count ignored unresolved symbols as success.

GPUEB/VCP target rebuild parity is not yet measured. Secure firmware internals, runtime message timing and remote algorithm behavior cannot be settled by this static preparation. MCUPM/SSPM client parity is UNKNOWN outside the owned GPU/video targets, not falsely counted as DONE.

Input fingerprints identify actual local donor bytes, including grafted/patch worktree files. The enclosing Git pin alone does not prove every donor file is committed; archive only verified tracked inputs, or copy exact fingerprint-checked inputs into isolated scratch space without touching the source.

Exact source candidates, build targets and object composition remain subject to stock function/data/CRC/KCFI evidence; namespace/name overlap is triage, never parity.
