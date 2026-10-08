# Claude executable handoff — MTK-MDP-KERNEL

## 1. Exact target and authority

Research repository: `/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research`. Canonical preparation: `/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/reverse-engineering/accelerator-preparation/MTK-MDP-KERNEL`. Organized pack: `/home/armol/androido_dalykai/LieppOS custom ROM/Reverse Engineer - PARTIAL/MTK-MDP-KERNEL`. Primary ownership is the explicit 4-module set below, not every dependency mentioned in this document.

## 2. Current completion state

PARTIAL. Preparation complete, **no new reconstruction or build performed**. No existing complete MDP/MML source-parity owner or measured rebuild was found. Public donor availability is not proof that hardware behavior or shipped module bytes match. Existing results are citations; do not erase or reinterpret measured proof operands.

## 3. Exact stock operands

All paths below are repository-relative; all copies of a basename were hash-checked equal. Use these actual files, not arbitrary newest `.ko` files.

| Module | Exact stock paths | SHA-256 | Bytes | Existing measured axes |
|---|---|---|---|---|
| `mdp_drv_mt6878.ko` | `workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/mdp_drv_mt6878.ko` | `ec0aa807803912a5747aa64ebedd76204de5f4042c8b404fa96578057f97a32b` | 763384 | UNKNOWN / no measured target rebuild parity located |
| `mtk-mml.ko` | `workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/mtk-mml.ko` | `f8f7c2c72d2feec9884a754fc5d08db93daac3b0425c5388cbe83991319dfe76` | 1894280 | UNKNOWN / no measured target rebuild parity located |
| `mtk-mml-mt6878.ko` | `workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/mtk-mml-mt6878.ko` | `b5accb2acde460ad90df40dd1c6d1a13a365e10b61bab841b9fba76630d83114` | 23128 | UNKNOWN / no measured target rebuild parity located |
| `clk-mt6878-mdpsys.ko` | `workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/clk-mt6878-mdpsys.ko` | `f6b976ff3e5fc364485161823bdc52bb402f2726237069133aee5a2cf750c62f` | 15176 | UNKNOWN / no measured target rebuild parity located |

## 4. Source donors

[source-candidates.tsv](source-candidates.tsv) contains exact existing donor paths, local Git pins, input fingerprints and alternate ALPS/patched candidates. [source-lineage.md](source-lineage.md) explains the pins. Best starting points are r44p1 + MT6878 platform candidates for Mali, pinned KDM/ALPS target directories for APU/codec/MDP/aux, and existing grafted camera source for the already exact camera functions/data. Do not edit shared checkouts. Export to your own space-free scratch tree. Use `git archive <recorded_commit>` only when that revision actually contains the target files and the exported inputs match their recorded fingerprints. Grafted/private or patched worktree inputs (notably camera) may not be represented by the enclosing Git HEAD: copy the exact validated donor files read-only into isolation, preserving their path/hash manifest and patch lineage, rather than substituting a pristine archive. Preserve a patch series and candidate fingerprints; never modify the shared source.

## 5. Build system/toolchain and first commands

**Build baseline:** Android CI 12901745; `common` `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`; stock vermagic `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64`; Android Clang 17.0.2 `clang-r487747c` (10087095), LLVM integrated assembler/lld, exact GKI/KMI and vendor config. Recorded config: `reverse-engineering/camera-stack/kernel-isp-imgsys/build/vendor-kernel.config`; CI pins: `kernel/exact-gki-build-inputs.md`. Inspect CONFIG_CFI_CLANG/MODVERSIONS and effective per-object LTO/visibility flags. `-faddrsig` was necessary in existing parity builds; verify rather than broadly changing compiler flags. Legacy camera scripts depend on `/tmp/ispenv.sh` and enable modpost warnings; do not call them blindly or count ignored unresolved symbols as success.

From this repository, the first commands are read-only/offline input checks, not fresh discovery:

```sh
R='/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research'
export PATH='/home/armol/kernel-work/gki-12901745-workspace/prebuilts/clang/host/linux-x86/clang-r487747c/bin':"$PATH"
cd "$R"
python3 reverse-engineering/accelerator-preparation/validate.py --scope MTK-MDP-KERNEL --inputs-only
# ko-kcfi-typeid.py is an importable prototype oracle, not an ELF CLI.
# Use its kcfi(mangled_type) during type recovery; compare stock/rebuild CFI entries.
```

Create an isolated workspace such as `/home/armol/kernel-work/accelerator-mtk-mdp-kernel`. Use exact GKI `common` plus isolated vendor/Kconfig/header trees; reuse the prepared mixed-build output `/home/armol/kernel-work/gki-12901745-workspace/lieppos/camera-isp/kout` **as a copied baseline, never as a writable shared build output**. Preserve original common/vmlinux symvers and naturally generated provider symvers. Translate the target's existing Kbuild/Makefile or Kleaf definition; do not guess object membership. A module build uses:

```sh
# Claude sets these to the isolated directories just created, not existing shared trees:
: "${COMMON:?isolated exact GKI common}" "${KOUT:?isolated configured output}" "${TARGET_DIR:?isolated target source}"
make -C "$COMMON" O="$KOUT" M="$TARGET_DIR" ARCH=arm64 LLVM=1 LLVM_IAS=1 \
  KBUILD_EXTRA_SYMBOLS="$PROVIDER_SYMVERS" KCFLAGS="-faddrsig" modules
```

Use the recorded vendor config, exact include/KCONFIG_EXT_PREFIX/DEVICE_MODULES paths and target Kconfig selectors from donor Kbuild. Snapshot all effective flags and headers. Reject modpost errors, unknown symbols or changed CRC/KCFI; do not suppress them to get a green build. For camera mixed-tree wiring, read existing `camera-stack/kernel-isp-imgsys/build/` recipes and replace ephemeral paths with your isolated manifest. The above is an executable build pattern, **not a claim that unmodified donors already build or match**.

## 6. Required reconstruction sequence

1. Close clk-mt6878-mdpsys and mdp_drv object/target composition against stock.
2. Close mtk-mml common interfaces, job/tile/config lifetime and shared-resource arbitration.
3. Close mtk-mml-mt6878 block tables, per-engine clock/IRQ programming, platform quirks and command generation.
4. Verify CMDQ, SMI/IOMMU, DRM and optional VCP boundary contracts without reconstructing their already owned modules.
5. Accept four module parity packets and complete the observable submit/buffer/fence/error ABI.

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

mdp_drv plus generic/platform MML interfaces; command construction/tile scheduling, buffer/fence lifecycle, DMA/IOMMU/SMI bandwidth, power/clock control and CMDQ execution. Distinguish generic command-queue engine from MDP clients, DRM attachment from full MDP reconstruction, and vendor PQ userspace from kernel block programming. Recover tile geometry, plane offsets/strides, job submit/complete/cancel/error handling and teardown. Use [dt-nodes.tsv](dt-nodes.tsv), provider resolutions and [kernel-abi.md](kernel-abi.md). Decode source macros only after fixing type/layout evidence; numeric IOCTLs/IRQ numbers unsupported by stock remain UNKNOWN.

## 10. Proven hardware behavior

Only existing stock captures, module presence/loading, merged DT and published source/parity results are cited. This pass executes no hardware. MT6878 MDP/MML data-processing RDMA, resizer, WROT, color/HDR/AAL/TDSHP and mutex/config blocks in the 0x1f000000 region. MDP and MML are not the ISP, codec engines or DRM scanout driver. The exact DT node list provides real blocks rather than invented module names. DT `okay`, Android libraries and config capabilities are not successful accelerator operation or inference/video/graphics performance tests.

## 11. Proprietary exclusions

MEDIATEK-DRM remains DONE for its explicitly proved DRM/panel modules; that result does not close mdp_drv or either MML binary. Generic mtk-cmdq-drv-ext/cmdq-platform/helpers remain platform dependencies; cmdq-sec-drv remains the existing GZ-TZ-SYSTEM scope. Do not absorb video codec or camera ISP owners. Preserve userspace PQ algorithms as proprietary.

## 12. Definition of DONE

Every owned target independently passes all [parity axes](../PARITY-STANDARD.md), reproducible clean B1/B2, documented source/type/provenance deltas, and complete observable normal-world DT/ABI/error/lifetime behavior. Any semantic equivalence has symbol-specific proof. No aggregate DONE based on one successful build or a function-count table. Firmware algorithms/userspace and later physical/runtime acceptance remain separate.

## 13. Safety restrictions

Offline static analysis and source builds only when Claude starts reconstruction. No adb, boot, reboot, flash, experimental driver load, accelerator/device command, secure-world invocation, firmware or calibration change, or partition write. Preserve stock Slot B and shared metadata. Do not reset/amend another agent's Git work or modify shared/private reconstruction. Check current HEAD/status before edits and use isolated source/build outputs.

## 14. Required research commits

Commit locally to the authoritative research repository in bounded groups: input/donor baseline → source/patch and ABI reconstruction → per-module complete parity evidence → scoped status/manifest/coverage synchronization. No push. Commit all GQ5012BF1 findings; preserve existing historical evidence. Stop on an explicitly documented blocker rather than stamping CRCs, inventing interfaces or claiming unmeasured progress.
