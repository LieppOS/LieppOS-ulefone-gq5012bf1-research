# Claude executable handoff — GPU-AI-AUX-KERNEL-INTERFACES

## 1. Exact target and authority

Research repository: `/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research`. Canonical preparation: `/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/reverse-engineering/accelerator-preparation/GPU-AI-AUX-KERNEL-INTERFACES`. Organized pack: `/home/armol/androido_dalykai/LieppOS custom ROM/Reverse Engineer - PARTIAL/GPU-AI-AUX-KERNEL-INTERFACES`. Primary ownership is the explicit 3-module set below, not every dependency mentioned in this document.

## 2. Current completion state

PARTIAL. Preparation complete, **no new reconstruction or build performed**. GPUEB/VCP target rebuild parity is not yet measured. Secure firmware internals, runtime message timing and remote algorithm behavior cannot be settled by this static preparation. MCUPM/SSPM client parity is UNKNOWN outside the owned GPU/video targets, not falsely counted as DONE. Existing results are citations; do not erase or reinterpret measured proof operands.

## 3. Exact stock operands

All paths below are repository-relative; all copies of a basename were hash-checked equal. Use these actual files, not arbitrary newest `.ko` files.

| Module | Exact stock paths | SHA-256 | Bytes | Existing measured axes |
|---|---|---|---|---|
| `gpueb.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/gpueb.ko` | `260543bfa2e5ade98efd0dae151a4738be4a58adaddc674ba6cdfedfd7f103bd` | 109016 | UNKNOWN / no measured target rebuild parity located |
| `vcp_status.ko` | `workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/vcp_status.ko` | `47f48dc56094b3fabe829ec3ccfc665d167353ceb37ea9ac23fe9683108b26fa` | 22624 | UNKNOWN / no measured target rebuild parity located |
| `vcp.ko` | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/vcp.ko` | `bc03ecf9402ba4313b23bf18f55e696d0d09f0197e0d21091a50d9bd5fbd5314` | 268776 | UNKNOWN / no measured target rebuild parity located |

## 4. Source donors

[source-candidates.tsv](source-candidates.tsv) contains exact existing donor paths, local Git pins, input fingerprints and alternate ALPS/patched candidates. [source-lineage.md](source-lineage.md) explains the pins. Best starting points are r44p1 + MT6878 platform candidates for Mali, pinned KDM/ALPS target directories for APU/codec/MDP/aux, and existing grafted camera source for the already exact camera functions/data. Do not edit shared checkouts. Export to your own space-free scratch tree. Use `git archive <recorded_commit>` only when that revision actually contains the target files and the exported inputs match their recorded fingerprints. Grafted/private or patched worktree inputs (notably camera) may not be represented by the enclosing Git HEAD: copy the exact validated donor files read-only into isolation, preserving their path/hash manifest and patch lineage, rather than substituting a pristine archive. Preserve a patch series and candidate fingerprints; never modify the shared source.

## 5. Build system/toolchain and first commands

**Build baseline:** Android CI 12901745; `common` `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`; stock vermagic `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64`; Android Clang 17.0.2 `clang-r487747c` (10087095), LLVM integrated assembler/lld, exact GKI/KMI and vendor config. Recorded config: `reverse-engineering/camera-stack/kernel-isp-imgsys/build/vendor-kernel.config`; CI pins: `kernel/exact-gki-build-inputs.md`. Inspect CONFIG_CFI_CLANG/MODVERSIONS and effective per-object LTO/visibility flags. `-faddrsig` was necessary in existing parity builds; verify rather than broadly changing compiler flags. Legacy camera scripts depend on `/tmp/ispenv.sh` and enable modpost warnings; do not call them blindly or count ignored unresolved symbols as success.

From this repository, the first commands are read-only/offline input checks, not fresh discovery:

```sh
R='/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research'
export PATH='/home/armol/kernel-work/gki-12901745-workspace/prebuilts/clang/host/linux-x86/clang-r487747c/bin':"$PATH"
cd "$R"
python3 reverse-engineering/accelerator-preparation/validate.py --scope GPU-AI-AUX-KERNEL-INTERFACES --inputs-only
# ko-kcfi-typeid.py is an importable prototype oracle, not an ELF CLI.
# Use its kcfi(mangled_type) during type recovery; compare stock/rebuild CFI entries.
```

Create an isolated workspace such as `/home/armol/kernel-work/accelerator-gpu-ai-aux-kernel-interfaces`. Use exact GKI `common` plus isolated vendor/Kconfig/header trees; reuse the prepared mixed-build output `/home/armol/kernel-work/gki-12901745-workspace/lieppos/camera-isp/kout` **as a copied baseline, never as a writable shared build output**. Preserve original common/vmlinux symvers and naturally generated provider symvers. Translate the target's existing Kbuild/Makefile or Kleaf definition; do not guess object membership. A module build uses:

```sh
# Claude sets these to the isolated directories just created, not existing shared trees:
: "${COMMON:?isolated exact GKI common}" "${KOUT:?isolated configured output}" "${TARGET_DIR:?isolated target source}"
make -C "$COMMON" O="$KOUT" M="$TARGET_DIR" ARCH=arm64 LLVM=1 LLVM_IAS=1 \
  KBUILD_EXTRA_SYMBOLS="$PROVIDER_SYMVERS" KCFLAGS="-faddrsig" modules
```

Use the recorded vendor config, exact include/KCONFIG_EXT_PREFIX/DEVICE_MODULES paths and target Kconfig selectors from donor Kbuild. Snapshot all effective flags and headers. Reject modpost errors, unknown symbols or changed CRC/KCFI; do not suppress them to get a green build. For camera mixed-tree wiring, read existing `camera-stack/kernel-isp-imgsys/build/` recipes and replace ephemeral paths with your isolated manifest. The above is an executable build pattern, **not a claim that unmodified donors already build or match**.

## 6. Required reconstruction sequence

1. Reuse DONE mailbox/RPMsg/IPI source and exact provider CRC/KCFI evidence; freeze all client-facing headers.
2. Close gpueb probe/shared-memory/IRQ/channel table/power/readiness/reset/recovery and exported callback interfaces.
3. Close vcp_status early provider and vcp host boot/reserved-memory/mailbox/feature/suspend/recovery code in dependency order.
4. Check GPU, codec, camera and MDP client imports/callbacks against the reconstructed providers.
5. Accept three independent full-module packets; do not change SCP/ADSP DONE status or promise firmware parity.

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

GPUEB shared-memory/mailbox/11 IPI channel setup and GPU-frequency consumer callbacks; VCP/status readiness, feature reference counts, reserved/shared memory, IPI/mailboxes, loader/boot, suspend, reset and recovery. SCP/ADSP contracts are reused, not reconstructed. Each channel has distinct client-visible payload and ownership; no single universal co-processor protocol is inferred. See processors.tsv and existing tinysys protocol ledgers. Use [dt-nodes.tsv](dt-nodes.tsv), provider resolutions and [kernel-abi.md](kernel-abi.md). Decode source macros only after fixing type/layout evidence; numeric IOCTLs/IRQ numbers unsupported by stock remain UNKNOWN.

## 10. Proven hardware behavior

Only existing stock captures, module presence/loading, merged DT and published source/parity results are cited. This pass executes no hardware. GPUEB and VCP are the unfinished GPU/video host clients. SCP sensor/audio/CHRE host is already reconstructed; ADSP source is closed but the board has no instantiated ADSP DT node. MCUPM/SSPM are CPU/system-power dependencies, not silently bundled as GPU firmware projects. SAP/CPUEB capability names are not proof of instantiated processors. DT `okay`, Android libraries and config capabilities are not successful accelerator operation or inference/video/graphics performance tests.

## 11. Proprietary exclusions

MTK-MBOX, MTK-RPMSG-MBOX and MTK-TINYSYS-IPI remain DONE for their exact transport modules. SENSOR-HUB-KERNEL keeps scp/hf_manager/sensorhub; AUDIO-DSP-KERNEL keeps adsp/audio host modules. CCU belongs to CAMERA-ISP-KERNEL and APUSYS to APUSYS-NPU-KERNEL. Firmware algorithms, signing, secure-boot loader internals and per-channel remote implementations are excluded.

## 12. Definition of DONE

Every owned target independently passes all [parity axes](../PARITY-STANDARD.md), reproducible clean B1/B2, documented source/type/provenance deltas, and complete observable normal-world DT/ABI/error/lifetime behavior. Any semantic equivalence has symbol-specific proof. No aggregate DONE based on one successful build or a function-count table. Firmware algorithms/userspace and later physical/runtime acceptance remain separate.

## 13. Safety restrictions

Offline static analysis and source builds only when Claude starts reconstruction. No adb, boot, reboot, flash, experimental driver load, accelerator/device command, secure-world invocation, firmware or calibration change, or partition write. Preserve stock Slot B and shared metadata. Do not reset/amend another agent's Git work or modify shared/private reconstruction. Check current HEAD/status before edits and use isolated source/build outputs.

## 14. Required research commits

Commit locally to the authoritative research repository in bounded groups: input/donor baseline → source/patch and ABI reconstruction → per-module complete parity evidence → scoped status/manifest/coverage synchronization. No push. Commit all GQ5012BF1 findings; preserve existing historical evidence. Stop on an explicitly documented blocker rather than stamping CRCs, inventing interfaces or claiming unmeasured progress.
