# Claude executable handoff — MTK-VCODEC-KERNEL

## 1. Exact target and authority

Research repository: `/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research`. Canonical preparation: `/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/reverse-engineering/accelerator-preparation/MTK-VCODEC-KERNEL`. Organized pack: `/home/armol/androido_dalykai/LieppOS custom ROM/Reverse Engineer - PARTIAL/MTK-VCODEC-KERNEL`. Primary ownership is the explicit 5-module set below, not every dependency mentioned in this document.

## 2. Current completion state

PARTIAL. Preparation complete, **no new reconstruction or build performed**. Unchanged-donor binary equivalence and actually functioning exposed codecs are UNKNOWN. XML/config/source capabilities are static declarations only; runtime encode/decode and signed firmware internals are excluded. Existing results are citations; do not erase or reinterpret measured proof operands.

## 3. Exact stock operands

All paths below are repository-relative; all copies of a basename were hash-checked equal. Use these actual files, not arbitrary newest `.ko` files.

| Module | Exact stock paths | SHA-256 | Bytes | Existing measured axes |
|---|---|---|---|---|
| `mtk-vcodec-common.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mtk-vcodec-common.ko` | `09570f1d7a46ddcc339cf09648373d0455e093c92f4d94d1286d744cfc27680e` | 143032 | UNKNOWN / no measured target rebuild parity located |
| `mtk-vcodec-dec-v1.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mtk-vcodec-dec-v1.ko` | `01af3b923c3cde9ac85020a9e26cc40a5f5f8d807ec8ccf63a2b22e8275529d0` | 501760 | UNKNOWN / no measured target rebuild parity located |
| `mtk-vcodec-enc-v1.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mtk-vcodec-enc-v1.ko` | `466da31c3f159ca13de20f9174463bc837baebbf45c21e63fc0213f7197f6f47` | 459424 | UNKNOWN / no measured target rebuild parity located |
| `mtk-vcu.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mtk-vcu.ko` | `2d54781fdc41f76dfdc0ae56dff4322df24e92793512e03456ffef1fbbb116d4` | 157472 | UNKNOWN / no measured target rebuild parity located |
| `clk-mt6878-vcodec.ko` | `workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/clk-mt6878-vcodec.ko` | `9abc181e0087cfc7588da0a8d8d32c97d17e1a70c31d64396a061fccea92bd43` | 14776 | UNKNOWN / no measured target rebuild parity located |

## 4. Source donors

[source-candidates.tsv](source-candidates.tsv) contains exact existing donor paths, local Git pins, input fingerprints and alternate ALPS/patched candidates. [source-lineage.md](source-lineage.md) explains the pins. Best starting points are r44p1 + MT6878 platform candidates for Mali, pinned KDM/ALPS target directories for APU/codec/MDP/aux, and existing grafted camera source for the already exact camera functions/data. Do not edit shared checkouts. Export only to your own space-free scratch tree using `git archive <recorded_commit>`; preserve a patch series and candidate fingerprints.

## 5. Build system/toolchain and first commands

**Build baseline:** Android CI 12901745; `common` `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`; stock vermagic `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64`; Android Clang 17.0.2 `clang-r487747c` (10087095), LLVM integrated assembler/lld, exact GKI/KMI and vendor config. Recorded config: `reverse-engineering/camera-stack/kernel-isp-imgsys/build/vendor-kernel.config`; CI pins: `kernel/exact-gki-build-inputs.md`. Inspect CONFIG_CFI_CLANG/MODVERSIONS and effective per-object LTO/visibility flags. `-faddrsig` was necessary in existing parity builds; verify rather than broadly changing compiler flags. Legacy camera scripts depend on `/tmp/ispenv.sh` and enable modpost warnings; do not call them blindly or count ignored unresolved symbols as success.

From this repository, the first commands are read-only/offline input checks, not fresh discovery:

```sh
R='/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research'
export PATH='/home/armol/kernel-work/gki-12901745-workspace/prebuilts/clang/host/linux-x86/clang-r487747c/bin':"$PATH"
cd "$R"
python3 reverse-engineering/accelerator-preparation/validate.py --scope MTK-VCODEC-KERNEL --inputs-only
# ko-kcfi-typeid.py is an importable prototype oracle, not an ELF CLI.
# Use its kcfi(mangled_type) during type recovery; compare stock/rebuild CFI entries.
```

Create an isolated workspace such as `/home/armol/kernel-work/accelerator-mtk-vcodec-kernel`. Use exact GKI `common` plus isolated vendor/Kconfig/header trees; reuse the prepared mixed-build output `/home/armol/kernel-work/gki-12901745-workspace/lieppos/camera-isp/kout` **as a copied baseline, never as a writable shared build output**. Preserve original common/vmlinux symvers and naturally generated provider symvers. Translate the target's existing Kbuild/Makefile or Kleaf definition; do not guess object membership. A module build uses:

```sh
# Claude sets these to the isolated directories just created, not existing shared trees:
: "${COMMON:?isolated exact GKI common}" "${KOUT:?isolated configured output}" "${TARGET_DIR:?isolated target source}"
make -C "$COMMON" O="$KOUT" M="$TARGET_DIR" ARCH=arm64 LLVM=1 LLVM_IAS=1 \
  KBUILD_EXTRA_SYMBOLS="$PROVIDER_SYMVERS" KCFLAGS="-faddrsig" modules
```

Use the recorded vendor config, exact include/KCONFIG_EXT_PREFIX/DEVICE_MODULES paths and target Kconfig selectors from donor Kbuild. Snapshot all effective flags and headers. Reject modpost errors, unknown symbols or changed CRC/KCFI; do not suppress them to get a green build. For camera mixed-tree wiring, read existing `camera-stack/kernel-isp-imgsys/build/` recipes and replace ephemeral paths with your isolated manifest. The above is an executable build pattern, **not a claim that unmodified donors already build or match**.

## 6. Required reconstruction sequence

1. Close dedicated vcodec clock module and common IRQ/DMA/power/provider helpers.
2. Reconstruct decoder and encoder object composition, FOURCC/control tables, buffer state machines and VCP message layouts independently.
3. Close VCU character-device/userspace bridge, compat translation and firmware-channel lifecycle.
4. Trace interrupt, fence/completion, failure/timeout/abort and reset recovery across both directions.
5. Accept five modules and source-visible Codec2/V4L2/DT interface equivalence; retain declared XML limits without claiming hardware success.

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

MediaTek V4L2 decoder/encoder and common driver; VCU bridge and VCP firmware ABI, native/compat ioctls, video device registration, input/output buffer ownership, DMA/IOMMU, interrupt completion, stream-on/off/abort and timeout recovery. Stock codec XML declarations and donor FOURCC evidence are recorded separately: neither proves codec execution or that the unchanged generic donor reproduces shipped binaries. Codec2/userspace consumer candidates are listed without asserting a complete call graph. Use [dt-nodes.tsv](dt-nodes.tsv), provider resolutions and [kernel-abi.md](kernel-abi.md). Decode source macros only after fixing type/layout evidence; numeric IOCTLs/IRQ numbers unsupported by stock remain UNKNOWN.

## 10. Proven hardware behavior

Only existing stock captures, module presence/loading, merged DT and published source/parity results are cited. This pass executes no hardware. MT6878 decoder vdec@16000000, encoder venc@17000000, dedicated vcodec clocks and VCP codec IOMMU domains. Exact registers, interrupts and power/clock/domain references are in dt-nodes.tsv. JPEG and display/MDP blocks are distinct, not silently added to this scope. DT `okay`, Android libraries and config capabilities are not successful accelerator operation or inference/video/graphics performance tests.

## 11. Proprietary exclusions

VCP host/status modules belong to the auxiliary component; VCP firmware algorithms and Codec2/vendor codec implementations are proprietary. Shared CMDQ/IOMMU/SMI/power providers are not duplicated. Existing generic source triage was not module-level source/parity closure.

## 12. Definition of DONE

Every owned target independently passes all [parity axes](../PARITY-STANDARD.md), reproducible clean B1/B2, documented source/type/provenance deltas, and complete observable normal-world DT/ABI/error/lifetime behavior. Any semantic equivalence has symbol-specific proof. No aggregate DONE based on one successful build or a function-count table. Firmware algorithms/userspace and later physical/runtime acceptance remain separate.

## 13. Safety restrictions

Offline static analysis and source builds only when Claude starts reconstruction. No adb, boot, reboot, flash, experimental driver load, accelerator/device command, secure-world invocation, firmware or calibration change, or partition write. Preserve stock Slot B and shared metadata. Do not reset/amend another agent's Git work or modify shared/private reconstruction. Check current HEAD/status before edits and use isolated source/build outputs.

## 14. Required research commits

Commit locally to the authoritative research repository in bounded groups: input/donor baseline → source/patch and ABI reconstruction → per-module complete parity evidence → scoped status/manifest/coverage synchronization. No push. Commit all GQ5012BF1 findings; preserve existing historical evidence. Stop on an explicitly documented blocker rather than stamping CRCs, inventing interfaces or claiming unmeasured progress.
