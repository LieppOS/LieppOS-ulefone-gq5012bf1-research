# Claude executable handoff — CAMERA-ISP-KERNEL

## 1. Exact target and authority

Research repository: `/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research`. Canonical preparation: `/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/reverse-engineering/accelerator-preparation/CAMERA-ISP-KERNEL`. Organized pack: `/home/armol/androido_dalykai/LieppOS custom ROM/Reverse Engineer - PARTIAL/CAMERA-ISP-KERNEL`. Primary ownership is the explicit 19-module set below, not every dependency mentioned in this document.

## 2. Current completion state

PARTIAL. Preparation complete, **no new reconstruction or build performed**. Existing camera reports prove measured function/data axes, not a complete full-module acceptance packet for every owned target. No new camera parity is claimed here. On-device streaming, tuning/quality and firmware algorithms remain outside static DONE. Existing results are citations; do not erase or reinterpret measured proof operands.

## 3. Exact stock operands

All paths below are repository-relative; all copies of a basename were hash-checked equal. Use these actual files, not arbitrary newest `.ko` files.

| Module | Exact stock paths | SHA-256 | Bytes | Existing measured axes |
|---|---|---|---|---|
| `mtk_hcp.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mtk_hcp.ko` | `2d58b9802107c82af95adb7dbec1b038db802b27f643ddf6c3264a3871437e9b` | 237640 | function: EXACT=169 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/mtk_hcp.function-parity.tsv); data: EXACT=53 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/mtk_hcp.data-parity.tsv) |
| `mtk-ipesys-me.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mtk-ipesys-me.ko` | `cb3a3fb932684a551e218fed6725f6bd98d75e80b922288c7711b791f065e15c` | 22856 | function: EXACT=14 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/mtk-ipesys-me.function-parity.tsv); data: EXACT=8 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/mtk-ipesys-me.data-parity.tsv) |
| `mtk_imgsys_cmdq.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mtk_imgsys_cmdq.ko` | `daefc888c27639800e1a8435d9d63a25b5f71a60d3ad73f403348a5b8ad5f6cc` | 562768 | function: EXACT=165 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/mtk_imgsys_cmdq.function-parity.tsv); data: EXACT=171 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/mtk_imgsys_cmdq.data-parity.tsv) |
| `mtk_imgsys_v4l2.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mtk_imgsys_v4l2.ko` | `06e6707e84347053dcef95a744b98f16a4592c99c3ac88b5e9a1bb773759d371` | 344376 | function: EXACT=185 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/mtk_imgsys_v4l2.function-parity.tsv); data: EXACT=139 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/mtk_imgsys_v4l2.data-parity.tsv) |
| `mtk_imgsys_isp7sp.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mtk_imgsys_isp7sp.ko` | `ec40d0e3e727b86e52dee78707dad344352f1e5a92a1017b9c48c0cd73f1dfd9` | 241704 | function: EXACT=85 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/mtk_imgsys_isp7sp.function-parity.tsv); data: EXACT=119 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/mtk_imgsys_isp7sp.data-parity.tsv) |
| `ccd_rpmsg.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/ccd_rpmsg.ko` | `87728684e86598e79c2152d1c4c80c9f1e43a9b9360cc0581fe960bf0b88c719` | 50840 | function: EXACT=29 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/ccd_rpmsg.function-parity.tsv); data: EXACT=13 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/ccd_rpmsg.data-parity.tsv) |
| `mtk_ccd_remoteproc.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mtk_ccd_remoteproc.ko` | `8ba14226b2badbbe6538b3d7395cf6656749919360cc7770f7b5e4384ac82acb` | 52424 | function: EXACT=25 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/mtk_ccd_remoteproc.function-parity.tsv); data: EXACT=13 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/mtk_ccd_remoteproc.data-parity.tsv) |
| `mtk_ccuv.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mtk_ccuv.ko` | `430d7b0cfe560de3296e117f93b68f15d9d0e9f491c38960eff62448c53bb806` | 74248 | function: EXACT=45 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/mtk_ccuv.function-parity.tsv); data: EXACT=22 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/mtk_ccuv.data-parity.tsv) |
| `mtk-cam-isp7sp.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mtk-cam-isp7sp.ko` | `c25b2d66b69dc16855fa2c0e20beffb8a2915f9d57a82aa1127c33465f9b6ac5` | 1530424 | function: EXACT=1220 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/mtk-cam-isp7sp.function-parity.tsv); data: EXACT=579 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/mtk-cam-isp7sp.data-parity.tsv) |
| `mtk_aie.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mtk_aie.ko` | `5d74d10d0e3fbbc8e426fa20f6af13c04ff0755afdfc58efa09b9675d5b96d14` | 283128 | function: EXACT=135 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/mtk_aie.function-parity.tsv); data: EXACT=116 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/mtk_aie.data-parity.tsv) |
| `mtk_aie_debug_7sp_2.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mtk_aie_debug_7sp_2.ko` | `dbb3bbef82c51be7170bb04fc10884f4e527920dcfdf5deab38b6f2c79188b68` | 15968 | function: EXACT=6 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/mtk_aie_debug_7sp_2.function-parity.tsv); data: EXACT=4 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/mtk_aie_debug_7sp_2.data-parity.tsv) |
| `camera_dpe_isp7sp.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/camera_dpe_isp7sp.ko` | `78f0a5f0a15acc2669ea9b0432e1342f8c79bc2ee37c9cb6c0b41e931730267e` | 301232 | function: EXACT=96 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/camera_dpe_isp7sp.function-parity.tsv); data: EXACT=118 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/camera_dpe_isp7sp.data-parity.tsv) |
| `pda_drv_mt6878.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/pda_drv_mt6878.ko` | `d0b09a5d6c6825134c7b6e9a59b3efe89c3f95a5000f074b559a9688f52e713e` | 116576 | UNKNOWN / no measured target rebuild parity located |
| `mtk-vmm-isp71-regulator.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mtk-vmm-isp71-regulator.ko` | `44f71bdc995c2dee4f80559e3b1e9e65113648af9e0cf684957ec0da0b04fb6e` | 62752 | UNKNOWN / no measured target rebuild parity located |
| `mtk-vmm-notifier.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mtk-vmm-notifier.ko` | `c51a910a3df3db3d56f93d60e13c6b08f3263087f67c693dec1923a0bea96e37` | 19040 | UNKNOWN / no measured target rebuild parity located |
| `imgsensor-glue.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/imgsensor-glue.ko` | `e21d8e0074f8440dcbb58b9558c3724ed0d45f3f6471c92f51aa86f8c01a04b9` | 13888 | function: EXACT=4 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/imgsensor-glue.function-parity.tsv); data: EXACT=3 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/imgsensor-glue.data-parity.tsv) |
| `imgsensor.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/imgsensor.ko` | `9243061cec77e96e3072b19f14a4d0f893e768586585830fa86f0a5129ce3558` | 1140880 | function: DIFF=1, EXACT=620 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/imgsensor.function-parity.tsv); data: EXACT=396 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/imgsensor.data-parity.tsv) |
| `c2ps_perf_ioctl.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/c2ps_perf_ioctl.ko` | `bc99873254826f5370b211b69e19a4b454ba9808a894ae20dc921ae28444632f` | 22192 | function: EXACT=6 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/c2ps_perf_ioctl.function-parity.tsv); data: EXACT=16 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/c2ps_perf_ioctl.data-parity.tsv) |
| `mtk_c2ps.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mtk_c2ps.ko` | `2a47b709d8edc8e8be6e662289f1f7e13d42be682cfc2b571fd2303446f35574` | 137744 | function: EXACT=106 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/mtk_c2ps.function-parity.tsv); data: EXACT=144 (reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module/mtk_c2ps.data-parity.tsv) |

## 4. Source donors

[source-candidates.tsv](source-candidates.tsv) contains exact existing donor paths, local Git pins, input fingerprints and alternate ALPS/patched candidates. [source-lineage.md](source-lineage.md) explains the pins. Best starting points are r44p1 + MT6878 platform candidates for Mali, pinned KDM/ALPS target directories for APU/codec/MDP/aux, and existing grafted camera source for the already exact camera functions/data. Do not edit shared checkouts. Export to your own space-free scratch tree. Use `git archive <recorded_commit>` only when that revision actually contains the target files and the exported inputs match their recorded fingerprints. Grafted/private or patched worktree inputs (notably camera) may not be represented by the enclosing Git HEAD: copy the exact validated donor files read-only into isolation, preserving their path/hash manifest and patch lineage, rather than substituting a pristine archive. Preserve a patch series and candidate fingerprints; never modify the shared source.

## 5. Build system/toolchain and first commands

**Build baseline:** Android CI 12901745; `common` `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`; stock vermagic `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64`; Android Clang 17.0.2 `clang-r487747c` (10087095), LLVM integrated assembler/lld, exact GKI/KMI and vendor config. Recorded config: `reverse-engineering/camera-stack/kernel-isp-imgsys/build/vendor-kernel.config`; CI pins: `kernel/exact-gki-build-inputs.md`. Inspect CONFIG_CFI_CLANG/MODVERSIONS and effective per-object LTO/visibility flags. `-faddrsig` was necessary in existing parity builds; verify rather than broadly changing compiler flags. Legacy camera scripts depend on `/tmp/ispenv.sh` and enable modpost warnings; do not call them blindly or count ignored unresolved symbols as success.

From this repository, the first commands are read-only/offline input checks, not fresh discovery:

```sh
R='/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research'
export PATH='/home/armol/kernel-work/gki-12901745-workspace/prebuilts/clang/host/linux-x86/clang-r487747c/bin':"$PATH"
cd "$R"
python3 reverse-engineering/accelerator-preparation/validate.py --scope CAMERA-ISP-KERNEL --inputs-only
# ko-kcfi-typeid.py is an importable prototype oracle, not an ELF CLI.
# Use its kcfi(mangled_type) during type recovery; compare stock/rebuild CFI entries.
```

Create an isolated workspace such as `/home/armol/kernel-work/accelerator-camera-isp-kernel`. Use exact GKI `common` plus isolated vendor/Kconfig/header trees; reuse the prepared mixed-build output `/home/armol/kernel-work/gki-12901745-workspace/lieppos/camera-isp/kout` **as a copied baseline, never as a writable shared build output**. Preserve original common/vmlinux symvers and naturally generated provider symvers. Translate the target's existing Kbuild/Makefile or Kleaf definition; do not guess object membership. A module build uses:

```sh
# Claude sets these to the isolated directories just created, not existing shared trees:
: "${COMMON:?isolated exact GKI common}" "${KOUT:?isolated configured output}" "${TARGET_DIR:?isolated target source}"
make -C "$COMMON" O="$KOUT" M="$TARGET_DIR" ARCH=arm64 LLVM=1 LLVM_IAS=1 \
  KBUILD_EXTRA_SYMBOLS="$PROVIDER_SYMVERS" KCFLAGS="-faddrsig" modules
```

Use the recorded vendor config, exact include/KCONFIG_EXT_PREFIX/DEVICE_MODULES paths and target Kconfig selectors from donor Kbuild. Snapshot all effective flags and headers. Reject modpost errors, unknown symbols or changed CRC/KCFI; do not suppress them to get a green build. For camera mixed-tree wiring, read existing `camera-stack/kernel-isp-imgsys/build/` recipes and replace ephemeral paths with your isolated manifest. The above is an executable build pattern, **not a claim that unmodified donors already build or match**.

## 6. Required reconstruction sequence

1. Read the 16 published function/data proof pairs first; match their stock hashes and preserve the existing grafted mtkcam 133c6c1 source. Do not replace byte-exact work with a pristine donor.
2. Prioritize PDA and VMM regulator/notifier: no function/data proof pair exists for these three owned targets. Recover their source/struct/callback deltas and compile separately.
3. Certify the already reconstructed HCP → imgsys command/ISP/V4L2 → CCD/RPMsg → CCU → camsys → AIE/DPE stack on full module axes, not function tables alone.
4. Certify imgsensor framework/glue and C2PS without reopening closed sensor TUs; preserve the one documented imgsensor semantic-equivalence residual.
5. Close CSI/SENINF, power/IRQ/DMA/IOMMU/media/IOCTL and HAL-consumer boundaries with the preserved stock contract.

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

Camsys/media/V4L2 scheduling, request/buffer DMA lifecycle and camera IOMMU integration; IMG_SYS/HCP command/tuning buffers and CMDQ; CCD/CCU normal-world communication; DPE/PDA/AIE vendor ioctls; VMM voltage/notifier ABI; imgsensor framework/glue and C2PS scheduling hooks. Sensor TUs are named subscopes inside imgsensor.ko, not duplicate whole-module ownership. Stock .modinfo includes legacy CCU dependency names; actual CRC-resolved exports point to mtk_ccuv.ko—do not invent mtk_ccu.ko or mtk_ccu_mssv.ko absent from the 457-module universe. Use [dt-nodes.tsv](dt-nodes.tsv), provider resolutions and [kernel-abi.md](kernel-abi.md). Decode source macros only after fixing type/layout evidence; numeric IOCTLs/IRQ numbers unsupported by stock remain UNKNOWN.

## 10. Proven hardware behavior

Only existing stock captures, module presence/loading, merged DT and published source/parity results are cited. This pass executes no hardware. ISP7sp FE/RAW/YUV/RMS/MRAW/CAMSV and P2 DIP/TRAW/WPE/ME/PQDIP, SENINF/CSI, CCD/CCU, AIE/FD, DPE, PDA and VMM interfaces. Existing camera-stack/notes/isp-stack.md specifies four CSI ports, nvmem PHY tuning and camera power domains. Sensor dies, EEPROMs, lens/VCM/OIS and camera rails retain their named DONE owners. DT `okay`, Android libraries and config capabilities are not successful accelerator operation or inference/video/graphics performance tests.

## 11. Proprietary exclusions

CAMERA-HAL-ISP stays PARTIAL for proprietary CameraProvider/HAL, 3A, tuning, calibration interpretation and CCU/ISP firmware algorithms. The child owns the explicit 19-module ledger only. Keep all parent historical evidence and source material where it is; its references become historical/cross-links, not a second primary owner. CAMERA-EEPROMS/VCMS/OIS/flash/LDO and closed sensor TUs are dependencies, never restarted.

## 12. Definition of DONE

Every owned target independently passes all [parity axes](../PARITY-STANDARD.md), reproducible clean B1/B2, documented source/type/provenance deltas, and complete observable normal-world DT/ABI/error/lifetime behavior. Any semantic equivalence has symbol-specific proof. No aggregate DONE based on one successful build or a function-count table. Firmware algorithms/userspace and later physical/runtime acceptance remain separate.

## 13. Safety restrictions

Offline static analysis and source builds only when Claude starts reconstruction. No adb, boot, reboot, flash, experimental driver load, accelerator/device command, secure-world invocation, firmware or calibration change, or partition write. Preserve stock Slot B and shared metadata. Do not reset/amend another agent's Git work or modify shared/private reconstruction. Check current HEAD/status before edits and use isolated source/build outputs.

## 14. Required research commits

Commit locally to the authoritative research repository in bounded groups: input/donor baseline → source/patch and ABI reconstruction → per-module complete parity evidence → scoped status/manifest/coverage synchronization. No push. Commit all GQ5012BF1 findings; preserve existing historical evidence. Stop on an explicitly documented blocker rather than stamping CRCs, inventing interfaces or claiming unmeasured progress.
