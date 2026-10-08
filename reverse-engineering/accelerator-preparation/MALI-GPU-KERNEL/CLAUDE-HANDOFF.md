# Claude executable handoff — MALI-GPU-KERNEL

## 1. Exact target and authority

Research repository: `/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research`. Canonical preparation: `/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/reverse-engineering/accelerator-preparation/MALI-GPU-KERNEL`. Organized pack: `/home/armol/androido_dalykai/LieppOS custom ROM/Reverse Engineer - PARTIAL/MALI-GPU-KERNEL`. Primary ownership is the explicit 8-module set below, not every dependency mentioned in this document.

## 2. Current completion state

PARTIAL. Preparation complete, **no new reconstruction or build performed**. GPU runtime model/revision, OEM donor deltas, secure/protected execution and real frame performance remain unproved. No measured target source build exists for these eight modules. Existing results are citations; do not erase or reinterpret measured proof operands.

## 3. Exact stock operands

All paths below are repository-relative; all copies of a basename were hash-checked equal. Use these actual files, not arbitrary newest `.ko` files.

| Module | Exact stock paths | SHA-256 | Bytes | Existing measured axes |
|---|---|---|---|---|
| `mali_kbase_mt6878_r44.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mali_kbase_mt6878_r44.ko` | `1633e3169242255a5714a4e3f4cfc525a5bbcc5393a3f7e7c6d8d76a1cf17092` | 2202264 | UNKNOWN / no measured target rebuild parity located |
| `mali_mgm_mt6878_r44.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mali_mgm_mt6878_r44.ko` | `20c7c978860b40dbf4beee6ab30c779bc01661203dd32803a1d9739922af5ce8` | 57232 | UNKNOWN / no measured target rebuild parity located |
| `mali_prot_alloc_mt6878_r44.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mali_prot_alloc_mt6878_r44.ko` | `970aa7d7ab217ca47db40b67f3ac1adda80fa497156b05e4ee60a341c3e1952a` | 22872 | UNKNOWN / no measured target rebuild parity located |
| `ged.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/ged.ko` | `174d067296d66ad733ebb62e7cdea1e0798e12ac053900862b801ee7ed6211d3` | 712328 | UNKNOWN / no measured target rebuild parity located |
| `mtk_gpu_hal.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mtk_gpu_hal.ko` | `447ae8199bd3ad10647dfbbeaab0846b72002894dad4a72818d879d934bc5066` | 59208 | UNKNOWN / no measured target rebuild parity located |
| `mtk_gpu_qos.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mtk_gpu_qos.ko` | `bd73206abe478aa8c944cd37163df48ffd439eb69e3e866f91f0eecd08030775` | 27888 | UNKNOWN / no measured target rebuild parity located |
| `mtk_gpufreq_wrapper.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mtk_gpufreq_wrapper.ko` | `7b047caf1a491693376d3b0f1f67240a202e5522c2211626d8857a6aaafc3139` | 164552 | UNKNOWN / no measured target rebuild parity located |
| `mtk_gpufreq_mt6878.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mtk_gpufreq_mt6878.ko` | `54428c82358cc794f43c9fb3b62586766f9b892518a3f7fdbfcfaa1977f62ea4` | 68064 | UNKNOWN / no measured target rebuild parity located |

## 4. Source donors

[source-candidates.tsv](source-candidates.tsv) contains exact existing donor paths, local Git pins, input fingerprints and alternate ALPS/patched candidates. [source-lineage.md](source-lineage.md) explains the pins. Best starting points are r44p1 + MT6878 platform candidates for Mali, pinned KDM/ALPS target directories for APU/codec/MDP/aux, and existing grafted camera source for the already exact camera functions/data. Do not edit shared checkouts. Export to your own space-free scratch tree. Use `git archive <recorded_commit>` only when that revision actually contains the target files and the exported inputs match their recorded fingerprints. Grafted/private or patched worktree inputs (notably camera) may not be represented by the enclosing Git HEAD: copy the exact validated donor files read-only into isolation, preserving their path/hash manifest and patch lineage, rather than substituting a pristine archive. Preserve a patch series and candidate fingerprints; never modify the shared source.

## 5. Build system/toolchain and first commands

**Build baseline:** Android CI 12901745; `common` `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`; stock vermagic `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64`; Android Clang 17.0.2 `clang-r487747c` (10087095), LLVM integrated assembler/lld, exact GKI/KMI and vendor config. Recorded config: `reverse-engineering/camera-stack/kernel-isp-imgsys/build/vendor-kernel.config`; CI pins: `kernel/exact-gki-build-inputs.md`. Inspect CONFIG_CFI_CLANG/MODVERSIONS and effective per-object LTO/visibility flags. `-faddrsig` was necessary in existing parity builds; verify rather than broadly changing compiler flags. Legacy camera scripts depend on `/tmp/ispenv.sh` and enable modpost warnings; do not call them blindly or count ignored unresolved symbols as success.

From this repository, the first commands are read-only/offline input checks, not fresh discovery:

```sh
R='/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research'
export PATH='/home/armol/kernel-work/gki-12901745-workspace/prebuilts/clang/host/linux-x86/clang-r487747c/bin':"$PATH"
cd "$R"
python3 reverse-engineering/accelerator-preparation/validate.py --scope MALI-GPU-KERNEL --inputs-only
# ko-kcfi-typeid.py is an importable prototype oracle, not an ELF CLI.
# Use its kcfi(mangled_type) during type recovery; compare stock/rebuild CFI entries.
```

Create an isolated workspace such as `/home/armol/kernel-work/accelerator-mali-gpu-kernel`. Use exact GKI `common` plus isolated vendor/Kconfig/header trees; reuse the prepared mixed-build output `/home/armol/kernel-work/gki-12901745-workspace/lieppos/camera-isp/kout` **as a copied baseline, never as a writable shared build output**. Preserve original common/vmlinux symvers and naturally generated provider symvers. Translate the target's existing Kbuild/Makefile or Kleaf definition; do not guess object membership. A module build uses:

```sh
# Claude sets these to the isolated directories just created, not existing shared trees:
: "${COMMON:?isolated exact GKI common}" "${KOUT:?isolated configured output}" "${TARGET_DIR:?isolated target source}"
make -C "$COMMON" O="$KOUT" M="$TARGET_DIR" ARCH=arm64 LLVM=1 LLVM_IAS=1 \
  KBUILD_EXTRA_SYMBOLS="$PROVIDER_SYMVERS" KCFLAGS="-faddrsig" modules
```

Use the recorded vendor config, exact include/KCONFIG_EXT_PREFIX/DEVICE_MODULES paths and target Kconfig selectors from donor Kbuild. Snapshot all effective flags and headers. Reject modpost errors, unknown symbols or changed CRC/KCFI; do not suppress them to get a green build. For camera mixed-tree wiring, read existing `camera-stack/kernel-isp-imgsys/build/` recipes and replace ephemeral paths with your isolated manifest. The above is an executable build pattern, **not a claim that unmodified donors already build or match**.

## 6. Required reconstruction sequence

1. Freeze MGM/protected allocator and GPU HAL exported interfaces; compare r44p1 baseline to r44p0 only as an alternative, not an assumed match.
2. Build MGM and protected allocator; recover resource/provider callbacks and data tables.
3. Close GPU HAL → gpufreq wrapper → mt6878 platform → GPU QoS → GED, resolving actual import cycles at ABI level with stock providers as initial operands.
4. Close Kbase object composition, CSF firmware-loading API, memory/VA/mmap/ioctl, scheduling, IRQ/fault/recovery and protected-mode paths.
5. Accept every owned module independently and then prove provider/consumer CRC/KCFI/DT compatibility across the assembled stack.

## 7. Function/data parity tests

For each exact module, compare A=listed shipped ELF with B=isolated source rebuild, then independently build B1 and B2. Example after setting exact operands:

```sh
: "${STOCK_KO:?path from stock-modules.tsv}" "${B1_KO:?isolated rebuild}" "${B2_KO:?second clean rebuild}" "${REPORT_DIR:?new report directory}"
mkdir -p "$REPORT_DIR"
python3 "$R/reverse-engineering/scripts/ko-pair-parity.py" "$STOCK_KO" "$B1_KO" > "$REPORT_DIR/full-parity.txt"
python3 "$R/reverse-engineering/scripts/ko-func-diff.py" --summary "$STOCK_KO" "$B1_KO" > "$REPORT_DIR/function-diff.txt"
python3 "$R/reverse-engineering/scripts/ko-residue-diff.py" "$STOCK_KO" "$B1_KO" > "$REPORT_DIR/residue-diff.txt"
cmp "$B1_KO" "$B2_KO"
```

These tools report differences; a zero exit alone is **not** complete parity. Preserve per-function full coverage, byte/semantic evidence, all data objects and section padding, imports/exports and their CRCs, relocation target/addend semantics, symbols, strings, .modinfo, vermagic and build IDs. Review [PARITY-STANDARD.md](../PARITY-STANDARD.md). Keep build-provenance exceptions separate; no blanket normalization hides behavior changes.

## 8. CRC/KCFI/relocation requirements

Stock [imports.tsv](imports.tsv), [exports.tsv](exports.tsv), [functions.tsv](functions.tsv) and data inventory are fixed operands. Generate CRCs naturally from recovered source types/headers; copied CRC constants or patched symvers are not type reconstruction. Match address-taken KCFI IDs and call-site type checks. Match relocation `(section, offset, type, symbol-name, addend)` multisets; explain raw-order/symbol-index differences independently. Verify provider/consumer edges with the master graph, including already DONE providers.

## 9. DT and ABI work remaining

Kbase memory/context/queue management and mmap/ioctl paths; MGM memory groups and protected allocator; GED, GPU HAL callbacks, GPU QoS and gpufreq wrapper/platform interfaces. Trace kbase context creation → GPU VA allocation/import/map → CSF scheduling → completion/fault cleanup; then protected allocation and normal-world secure-heap calls. `/dev/mali0` is the expected Kbase ABI, not a newly observed binding. Numeric commands and layouts must be checked against stock handlers; source definitions alone are not parity. Use [dt-nodes.tsv](dt-nodes.tsv), provider resolutions and [kernel-abi.md](kernel-abi.md). Decode source macros only after fixing type/layout evidence; numeric IOCTLs/IRQ numbers unsupported by stock remain UNKNOWN.

## 10. Proven hardware behavior

Only existing stock captures, module presence/loading, merged DT and published source/parity results are cited. This pass executes no hardware. Valhall/CSF KMD on MT6878; merged DT has mali@13000000 and g3d-brisket@13fb0000. Exact GPU_ID/revision/core count is UNKNOWN from this static pass; do not substitute a marketing GPU designation. Register ranges, raw GIC interrupt cells, clocks, power domains and provider arguments are recorded per node. DT `okay`, Android libraries and config capabilities are not successful accelerator operation or inference/video/graphics performance tests.

## 11. Proprietary exclusions

Do not absorb mtk_gpu_power_throttling (THERMAL-POWER-HAL), mtk_sec_heap/tmem_ffa (TMEM-FFA), GenieZone transport/secure memory (existing GZ scopes), or the DONE mailbox/IPI providers. GPUEB host client belongs to GPU-AI-AUX-KERNEL-INTERFACES. mali_dmabuf_test is diagnostic stock baggage, not an additional unfinished accelerator. Retain Mali EGL/GLES/Vulkan blobs and stock mali_csffw.bin; their algorithms are not kernel parity.

## 12. Definition of DONE

Every owned target independently passes all [parity axes](../PARITY-STANDARD.md), reproducible clean B1/B2, documented source/type/provenance deltas, and complete observable normal-world DT/ABI/error/lifetime behavior. Any semantic equivalence has symbol-specific proof. No aggregate DONE based on one successful build or a function-count table. Firmware algorithms/userspace and later physical/runtime acceptance remain separate.

## 13. Safety restrictions

Offline static analysis and source builds only when Claude starts reconstruction. No adb, boot, reboot, flash, experimental driver load, accelerator/device command, secure-world invocation, firmware or calibration change, or partition write. Preserve stock Slot B and shared metadata. Do not reset/amend another agent's Git work or modify shared/private reconstruction. Check current HEAD/status before edits and use isolated source/build outputs.

## 14. Required research commits

Commit locally to the authoritative research repository in bounded groups: input/donor baseline → source/patch and ABI reconstruction → per-module complete parity evidence → scoped status/manifest/coverage synchronization. No push. Commit all GQ5012BF1 findings; preserve existing historical evidence. Stop on an explicitly documented blocker rather than stamping CRCs, inventing interfaces or claiming unmeasured progress.
