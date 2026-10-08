#!/usr/bin/env python3
"""Render useful scoped plans from measured inventories; does not reconstruct kernel source."""
import csv
import json
from pathlib import Path
from inventory import HERE, REPO, GKI, WS, rows

DETAIL = {
'MALI-GPU-KERNEL': {
 'hardware':'Valhall/CSF KMD on MT6878; merged DT has mali@13000000 and g3d-brisket@13fb0000. Exact GPU_ID/revision/core count is UNKNOWN from this static pass; do not substitute a marketing GPU designation. Register ranges, raw GIC interrupt cells, clocks, power domains and provider arguments are recorded per node.',
 'abi':'Kbase memory/context/queue management and mmap/ioctl paths; MGM memory groups and protected allocator; GED, GPU HAL callbacks, GPU QoS and gpufreq wrapper/platform interfaces. Trace kbase context creation → GPU VA allocation/import/map → CSF scheduling → completion/fault cleanup; then protected allocation and normal-world secure-heap calls. `/dev/mali0` is the expected Kbase ABI, not a newly observed binding. Numeric commands and layouts must be checked against stock handlers; source definitions alone are not parity.',
 'boundary':'Do not absorb mtk_gpu_power_throttling (THERMAL-POWER-HAL), mtk_sec_heap/tmem_ffa (TMEM-FFA), GenieZone transport/secure memory (existing GZ scopes), or the DONE mailbox/IPI providers. GPUEB host client belongs to GPU-AI-AUX-KERNEL-INTERFACES. mali_dmabuf_test is diagnostic stock baggage, not an additional unfinished accelerator. Retain Mali EGL/GLES/Vulkan blobs and stock mali_csffw.bin; their algorithms are not kernel parity.',
 'steps':['Freeze MGM/protected allocator and GPU HAL exported interfaces; compare r44p1 baseline to r44p0 only as an alternative, not an assumed match.','Build MGM and protected allocator; recover resource/provider callbacks and data tables.','Close GPU HAL → gpufreq wrapper → mt6878 platform → GPU QoS → GED, resolving actual import cycles at ABI level with stock providers as initial operands.','Close Kbase object composition, CSF firmware-loading API, memory/VA/mmap/ioctl, scheduling, IRQ/fault/recovery and protected-mode paths.','Accept every owned module independently and then prove provider/consumer CRC/KCFI/DT compatibility across the assembled stack.'],
 'unknown':'GPU runtime model/revision, OEM donor deltas, secure/protected execution and real frame performance remain unproved. No measured target source build exists for these eight modules.'},
'APUSYS-NPU-KERNEL': {
 'hardware':'MT6878 APU RV complex at apusys-rv@190e1000, apu-top-3@1c000000, APUMMU, APU IOMMU banks and MDLA/MVPU/EDMA/RPMsg channel declarations. The monolithic apusys.ko contains multiple IP generations: alias presence does not mean every generation is enabled. Separate board DT instances from dormant code.',
 'abi':'apu_top power/DVFS callbacks; apusys middleware command submission, buffer/shared-memory management, APUMMU/reviser translation, RPMsg/mailbox/interrupt transport, EDMA/MDLA/MVPU completion and recovery. Extract APUSYS ioctl command numbers and native/compat layouts from source witnesses and compare stock switch paths. Recover ownership of each buffer through allocation, map, submit, ACK, abort/reset and release. APUSYS uses its own RPMsg implementation; do not assign it to TinySys IPI merely because both exchange messages.',
 'boundary':'All APU/MDLA/MVPU RPMsg accelerator nodes previously attributed to CAMERA-HAL-ISP move to this kernel owner. Camera AIE/FD hardware stays CAMERA-ISP-KERNEL. GenieZone trusty-sapu remains the existing secure transport. Shared generic IOMMU/QoS/SSPM providers remain dependencies. APUware/NeuroPilot/neuron/NNAPI libraries and signed apusys firmware algorithms are retained binaries, not a claim of proven model execution.',
 'steps':['Close apu_top power initialization, OPP/DVFS/thermal callbacks, unwind and suspend/reset state machine.','Split the existing apusys Kbuild object list into middleware, remoteproc/RPMsg, APUMMU/reviser, EDMA, MDLA and MVPU work units; do not invent standalone mdla.ko or mvpu.ko.','Reconstruct shared-memory and command-submit/complete/error ABI, including compat ioctls and secure-boundary calls.','Close interrupt, mailbox, RPMsg readiness, timeout, recovery/reset and teardown paths against stock.','Accept both modules and verify every exposed provider/callback against stock consumers.'],
 'unknown':'Dedicated NPU model execution, actual exposed inference throughput, signed payload algorithms and secure internals are UNKNOWN. DT enablement, loaded apusys and runtime library presence are not inference-execution proof.'},
'CAMERA-ISP-KERNEL': {
 'hardware':'ISP7sp FE/RAW/YUV/RMS/MRAW/CAMSV and P2 DIP/TRAW/WPE/ME/PQDIP, SENINF/CSI, CCD/CCU, AIE/FD, DPE, PDA and VMM interfaces. Existing camera-stack/notes/isp-stack.md specifies four CSI ports, nvmem PHY tuning and camera power domains. Sensor dies, EEPROMs, lens/VCM/OIS and camera rails retain their named DONE owners.',
 'abi':'Camsys/media/V4L2 scheduling, request/buffer DMA lifecycle and camera IOMMU integration; IMG_SYS/HCP command/tuning buffers and CMDQ; CCD/CCU normal-world communication; DPE/PDA/AIE vendor ioctls; VMM voltage/notifier ABI; imgsensor framework/glue and C2PS scheduling hooks. Sensor TUs are named subscopes inside imgsensor.ko, not duplicate whole-module ownership. Stock .modinfo includes legacy CCU dependency names; actual CRC-resolved exports point to mtk_ccuv.ko—do not invent mtk_ccu.ko or mtk_ccu_mssv.ko absent from the 457-module universe.',
 'boundary':'CAMERA-HAL-ISP stays PARTIAL for proprietary CameraProvider/HAL, 3A, tuning, calibration interpretation and CCU/ISP firmware algorithms. The child owns the explicit 19-module ledger only. Keep all parent historical evidence and source material where it is; its references become historical/cross-links, not a second primary owner. CAMERA-EEPROMS/VCMS/OIS/flash/LDO and closed sensor TUs are dependencies, never restarted.',
 'steps':['Read the 16 published function/data proof pairs first; match their stock hashes and preserve the existing grafted mtkcam 133c6c1 source. Do not replace byte-exact work with a pristine donor.','Prioritize PDA and VMM regulator/notifier: no function/data proof pair exists for these three owned targets. Recover their source/struct/callback deltas and compile separately.','Certify the already reconstructed HCP → imgsys command/ISP/V4L2 → CCD/RPMsg → CCU → camsys → AIE/DPE stack on full module axes, not function tables alone.','Certify imgsensor framework/glue and C2PS without reopening closed sensor TUs; preserve the one documented imgsensor semantic-equivalence residual.','Close CSI/SENINF, power/IRQ/DMA/IOMMU/media/IOCTL and HAL-consumer boundaries with the preserved stock contract.'],
 'unknown':'Existing camera reports prove measured function/data axes, not a complete full-module acceptance packet for every owned target. No new camera parity is claimed here. On-device streaming, tuning/quality and firmware algorithms remain outside static DONE.'},
'MTK-VCODEC-KERNEL': {
 'hardware':'MT6878 decoder vdec@16000000, encoder venc@17000000, dedicated vcodec clocks and VCP codec IOMMU domains. Exact registers, interrupts and power/clock/domain references are in dt-nodes.tsv. JPEG and display/MDP blocks are distinct, not silently added to this scope.',
 'abi':'MediaTek V4L2 decoder/encoder and common driver; VCU bridge and VCP firmware ABI, native/compat ioctls, video device registration, input/output buffer ownership, DMA/IOMMU, interrupt completion, stream-on/off/abort and timeout recovery. Stock codec XML declarations and donor FOURCC evidence are recorded separately: neither proves codec execution or that the unchanged generic donor reproduces shipped binaries. Codec2/userspace consumer candidates are listed without asserting a complete call graph.',
 'boundary':'VCP host/status modules belong to the auxiliary component; VCP firmware algorithms and Codec2/vendor codec implementations are proprietary. Shared CMDQ/IOMMU/SMI/power providers are not duplicated. Existing generic source triage was not module-level source/parity closure.',
 'steps':['Close dedicated vcodec clock module and common IRQ/DMA/power/provider helpers.','Reconstruct decoder and encoder object composition, FOURCC/control tables, buffer state machines and VCP message layouts independently.','Close VCU character-device/userspace bridge, compat translation and firmware-channel lifecycle.','Trace interrupt, fence/completion, failure/timeout/abort and reset recovery across both directions.','Accept five modules and source-visible Codec2/V4L2/DT interface equivalence; retain declared XML limits without claiming hardware success.'],
 'unknown':'Unchanged-donor binary equivalence and actually functioning exposed codecs are UNKNOWN. XML/config/source capabilities are static declarations only; runtime encode/decode and signed firmware internals are excluded.'},
'MTK-MDP-KERNEL': {
 'hardware':'MT6878 MDP/MML data-processing RDMA, resizer, WROT, color/HDR/AAL/TDSHP and mutex/config blocks in the 0x1f000000 region. MDP and MML are not the ISP, codec engines or DRM scanout driver. The exact DT node list provides real blocks rather than invented module names.',
 'abi':'mdp_drv plus generic/platform MML interfaces; command construction/tile scheduling, buffer/fence lifecycle, DMA/IOMMU/SMI bandwidth, power/clock control and CMDQ execution. Distinguish generic command-queue engine from MDP clients, DRM attachment from full MDP reconstruction, and vendor PQ userspace from kernel block programming. Recover tile geometry, plane offsets/strides, job submit/complete/cancel/error handling and teardown.',
 'boundary':'MEDIATEK-DRM remains DONE for its explicitly proved DRM/panel modules; that result does not close mdp_drv or either MML binary. Generic mtk-cmdq-drv-ext/cmdq-platform/helpers remain platform dependencies; cmdq-sec-drv remains the existing GZ-TZ-SYSTEM scope. Do not absorb video codec or camera ISP owners. Preserve userspace PQ algorithms as proprietary.',
 'steps':['Close clk-mt6878-mdpsys and mdp_drv object/target composition against stock.','Close mtk-mml common interfaces, job/tile/config lifetime and shared-resource arbitration.','Close mtk-mml-mt6878 block tables, per-engine clock/IRQ programming, platform quirks and command generation.','Verify CMDQ, SMI/IOMMU, DRM and optional VCP boundary contracts without reconstructing their already owned modules.','Accept four module parity packets and complete the observable submit/buffer/fence/error ABI.'],
 'unknown':'No existing complete MDP/MML source-parity owner or measured rebuild was found. Public donor availability is not proof that hardware behavior or shipped module bytes match.'},
'GPU-AI-AUX-KERNEL-INTERFACES': {
 'hardware':'GPUEB and VCP are the unfinished GPU/video host clients. SCP sensor/audio/CHRE host is already reconstructed; ADSP source is closed but the board has no instantiated ADSP DT node. MCUPM/SSPM are CPU/system-power dependencies, not silently bundled as GPU firmware projects. SAP/CPUEB capability names are not proof of instantiated processors.',
 'abi':'GPUEB shared-memory/mailbox/11 IPI channel setup and GPU-frequency consumer callbacks; VCP/status readiness, feature reference counts, reserved/shared memory, IPI/mailboxes, loader/boot, suspend, reset and recovery. SCP/ADSP contracts are reused, not reconstructed. Each channel has distinct client-visible payload and ownership; no single universal co-processor protocol is inferred. See processors.tsv and existing tinysys protocol ledgers.',
 'boundary':'MTK-MBOX, MTK-RPMSG-MBOX and MTK-TINYSYS-IPI remain DONE for their exact transport modules. SENSOR-HUB-KERNEL keeps scp/hf_manager/sensorhub; AUDIO-DSP-KERNEL keeps adsp/audio host modules. CCU belongs to CAMERA-ISP-KERNEL and APUSYS to APUSYS-NPU-KERNEL. Firmware algorithms, signing, secure-boot loader internals and per-channel remote implementations are excluded.',
 'steps':['Reuse DONE mailbox/RPMsg/IPI source and exact provider CRC/KCFI evidence; freeze all client-facing headers.','Close gpueb probe/shared-memory/IRQ/channel table/power/readiness/reset/recovery and exported callback interfaces.','Close vcp_status early provider and vcp host boot/reserved-memory/mailbox/feature/suspend/recovery code in dependency order.','Check GPU, codec, camera and MDP client imports/callbacks against the reconstructed providers.','Accept three independent full-module packets; do not change SCP/ADSP DONE status or promise firmware parity.'],
 'unknown':'GPUEB/VCP target rebuild parity is not yet measured. Secure firmware internals, runtime message timing and remote algorithm behavior cannot be settled by this static preparation. MCUPM/SSPM client parity is UNKNOWN outside the owned GPU/video targets, not falsely counted as DONE.'}}

def write(path,text):path.write_text(text.rstrip()+'\n')
def links():
 return ('[stock modules](stock-modules.tsv), [DT nodes](dt-nodes.tsv), [source candidates](source-candidates.tsv), '
         '[parity gaps](parity-gaps.tsv), [imports](imports.tsv), [exports](exports.tsv), '
         '[functions](functions.tsv), [data symbols](data-symbols.tsv), [donor ABI witnesses](abi-source-witnesses.tsv).')

def main():
 cfg=json.loads((HERE/'scopes.json').read_text());road=[]
 for scope in cfg['scopes']:
  n=scope['component']; d=HERE/n; detail=DETAIL[n]; inv=rows(d/'stock-modules.tsv'); donors=rows(d/'source-candidates.tsv')
  modulelist=', '.join('`'+m+'`' for m in scope['modules']); proof_count=sum(not x['published_parity'].startswith('UNKNOWN') for x in inv)
  pre='; '.join(dict.fromkeys(x['modinfo_depends'] for x in inv if x['modinfo_depends']))
  write(d/'README.md',f'# {n} — PARTIAL preparation\n\nStatus: PARTIAL\n\n- **Subsystem:** Accelerators / {scope["title"]}\n- **Hardware identity:** {detail["hardware"]}\n- **Stock artifact:** {modulelist}\n- **Interfaces:** {detail["abi"]}\n- **Still required:** Complete per-module source/parity and observable DT/ABI acceptance; proprietary algorithms excluded\n\n**Purpose:** {scope["title"]} normal-world kernel source/parity closure, not firmware reconstruction.\n\n**Decision:** {scope["decision"]}. {scope["justification"]}\n\n**Entry point:** [CLAUDE-HANDOFF.md](CLAUDE-HANDOFF.md). Canonical research: `reverse-engineering/accelerator-preparation/{n}/`. Workspace pack: `Reverse Engineer - PARTIAL/{n}/`.\n\n**Exclusive primary kernel modules ({len(inv)}):** {modulelist}. Dependencies are references, not additional ownership.\n\n{links()}\n\n{detail["boundary"]}\n\nNo module rebuilt, hardware command executed or parity result created by this preparation. Published proof rows are preserved and labeled by axis; the component starts PARTIAL, never DONE.')
  write(d/'STATUS.md',f'# {n} status — {cfg["date"]}\n\n**PARTIAL / actionable kernel RE (class A).** {len(inv)} exact stock targets located; {len(donors)} pinned donor candidates. {proof_count} modules have existing published function/data evidence, reproduced as citations—not new measurements.\n\n{detail["unknown"]}\n\n{scope["justification"]}\n\n**Next action:** {detail["steps"][0]}\n\n**Blockers:** full acceptance packet and target-specific donor/config/ABI reconciliation. Signed algorithms and runtime tests are excluded, not a reason to fake static closure.\n\n**Definition of DONE:** all owned modules satisfy the complete [parity standard](../PARITY-STANDARD.md), plus the normal-world DT/ABI contract; retained firmware and userspace boundaries remain explicit.\n\nNo ADD elsewhere, merge, removal, rename or unrelated status move is authorized by this pack.')
  provider_link='[dt-providers.tsv](dt-providers.tsv) resolves clock/power/IOMMU/mailbox/reset phandles where declared.' if (d/'dt-providers.tsv').exists() else 'No clock/power/IOMMU/mailbox/reset phandle array was declared on these selected nodes; provider lookup through supplies/other platform nodes remains to trace. No empty provider table is fabricated.'
  write(d/'hardware-contract.md',f'# Hardware contract — {n}\n\n{detail["hardware"]}\n\n**Evidence:** [dt-nodes.tsv](dt-nodes.tsv) is decoded from `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dtb` (stock selected base+overlay). Each row retains all properties, exact parent-bus reg ranges, interrupt cells and resolved provider arguments. {provider_link} Addresses are parent-bus addresses; verify `ranges` translations before calling them physical CPU addresses. Numeric IRQ cells are DT specs, not observed Linux IRQ numbers.\n\n{detail["abi"]}\n\n**UNKNOWN:** missing register names, IRQ servicing semantics, electrical enablement, execution or throughput not evidenced by these static rows. `okay` and module loading never establish successful probe or execution. Runtime libraries only establish consumers/capability.')
  source_md='\n'.join(f'| `{x["module"]}` | `{x["donor"]}` | `{x["commit"]}` | {x["availability"]} |' for x in donors)
  write(d/'source-lineage.md',f'# Source lineage — {n}\n\nEvery donor directory/file exists. Commits and complete relevant-file fingerprints are in [source-candidates.tsv](source-candidates.tsv). The ALPS snapshot local commit `2ae742fda9cd461bfe8cf8a5c04f95e212f8e699` identifies a pristine archive of upstream MT6878 ALPS `5e415e059253`; it is not misrepresented as the upstream Git commit. The Nothing donor import and the patched mixed-build tree are distinct candidates. Do not reset or edit any of these shared checkouts.\n\n| Module | Local donor | Local Git commit | Starting state |\n|---|---|---|---|\n{source_md}\n\n{name_build_note(n)}\n\n{detail["unknown"]}\n\nInput fingerprints identify actual local donor bytes, including grafted/patch worktree files. The enclosing Git pin alone does not prove every donor file is committed; archive only verified tracked inputs, or copy exact fingerprint-checked inputs into isolated scratch space without touching the source.\n\nExact source candidates, build targets and object composition remain subject to stock function/data/CRC/KCFI evidence; namespace/name overlap is triage, never parity.')
  write(d/'kernel-abi.md',f'# Kernel/userspace ABI — {n}\n\n{detail["abi"]}\n\n**Static witnesses:** [functions.tsv](functions.tsv) identifies each exact symbol/section/offset/size; [imports.tsv](imports.tsv) pins modversion CRCs and known stock providers; [exports.tsv](exports.tsv) pins export buckets/CRCs; [abi-source-witnesses.tsv](abi-source-witnesses.tsv) gives precise source file/line/hash for IOCTLs, fops, buffers, IRQ, power, recovery, firmware and transport candidates. Source lines are explicitly DONOR—not accepted stock behavior.\n\n**Remaining contract work:** enumerate each device node, ioctl direction/number/struct size and compat layout, mmap offset/cache behavior, poll/fence semantics, queue states, buffer ownership, error returns and teardown. Recover stock call sites and data/relocations before asserting numerical equivalence. Read the [userspace consumer list](userspace-consumers.tsv); it is not proof of every edge or live use.\n\nKernel release is the exact stock GKI/KMI baseline, not the host kernel. Do not replace natural CRC/KCFI generation with forced constants or CRC stamping as a proof of reconstructed types.')
  write(d/'dependencies.md',f'# Dependencies and singleton ownership — {n}\n\n**Prerequisites:** {scope["prerequisites"]}.\n\n**Owned modules:** {modulelist}.\n\n{detail["boundary"]}\n\n[Master dependency edges](../dependency-edges.tsv) resolve stock imports by symbol and CRC; each row carries consumer/provider/owner. The load order and legacy modinfo dependencies are recorded separately in stock-modules.tsv. `modules.dep` can be transitive and legacy modinfo can name obsolete provider identities; neither overrides the actual export/CRC graph.\n\nRaw direct modinfo dependency sets: `{pre}`. These names are not a list of new targets. UNKNOWN provider/type provenance must be resolved against existing stock export/KMI ledgers, not fabricated. Preserve generic platform providers and explicitly closed modules.\n\nFor cycles, freeze mutually shared headers/provider ABI, use unchanged stock provider operands during initial isolation, then verify the assembled reconstructed graph; copied stock symvers is an oracle, not source/type proof.')
  fwlink='[firmware metadata](firmware-boundaries.tsv)' if (d/'firmware-boundaries.tsv').exists() else 'No standalone firmware artifact proved for this scope; exact payload is UNKNOWN.'
  write(d/'proprietary-boundary.md',f'# Proprietary boundary — {n}\n\n{detail["boundary"]}\n\n{fwlink} records paths, sizes and hashes only. Its historical coverage-loader labels are not loader implementation proofs; trace each real source/stock host loader separately. A signed scatter image is not necessarily loaded by Linux `request_firmware`. Code/data in remote images, secure-world functions, model/3A/tuning/PQ algorithms, per-unit calibration and signing keys are outside kernel-source parity.\n\nNo proprietary `.ko`, `.bin`, `.img`, calibration, Android HAL/library payload or raw dump enters this preparation tree or Git. Reuse private local artifacts by exact path/hash.\n\n{detail["unknown"]}')
  steps='\n'.join(f'{i}. {v}' for i,v in enumerate(detail['steps'],1))
  write(d/'RE-PLAN.md',f'# Source-parity reconstruction sequence — {n}\n\n{steps}\n\nFor **each** target in stock-modules.tsv, create its own function/data/ABI/residual ledger and isolated source patch series. Do not bulk-mark a scope DONE after compiling one binary. Preserve existing exact camera data/function proofs and closed provider source.\n\nApply [PARITY-STANDARD.md](../PARITY-STANDARD.md) completely, then verify imports/exports across the source-built provider graph and DT/observable ABI. Report new results in authoritative research commits before scoped workspace synchronization. Runtime tests are a separate, later authorized phase; none is permitted by this preparation assignment.')
  write(d/'CLAUDE-HANDOFF.md',handoff(scope,detail,inv,steps))
  (d/'evidence').mkdir(exist_ok=True);(d/'notes').mkdir(exist_ok=True)
  write(d/'evidence/EVIDENCE-INDEX.md',f'# Evidence index — {n}\n\nAuthoritative source: `ulefone-gq5012bf1-research/reverse-engineering/accelerator-preparation/{n}/`. All TSV files at the pack root are derived metadata, not payloads.\n\nDiscovery source HEAD `{cfg["discovery_head"]}`. Inputs: coverage-audit tables, stock ELF modules and merged DT; existing camera/tinysys/sensors/GKI reports; pinned source candidates and file fingerprints. See [handoff](../CLAUDE-HANDOFF.md), [module inventory](../stock-modules.tsv), [source lineage](../source-lineage.md). Original per-module camera reports and private source trees remain in place; no historical file is moved/deleted.')
  write(d/'notes/PROVENANCE.md',f'# Provenance — {n}\n\nPrepared {cfg["date"]}, from measured stock metadata and source HEAD `{cfg["discovery_head"]}`. Canonical files live in research `reverse-engineering/accelerator-preparation/{n}/`; the organized PARTIAL pack is a verified copy. `COPY-MANIFEST.tsv` records each actual copied file/hash/size and research commit.\n\nThis package proves preparation/ownership only. Existing parity reports are explicitly cited by axis; no new kernel reconstruction, firmware source or live hardware result is asserted.')
  road.append(f'| {scope["priority"]} | {scope["title"]} | New registered PARTIAL{ " child" if n=="CAMERA-ISP-KERNEL" else ""}: `{n}` | {len(inv)}: {modulelist} | {proof_count} existing function/data report pairs; pinned local candidates, full acceptance pending | {scope["difficulty"]}; {scope["effort"]} | {scope["prerequisites"]} | {detail["steps"][0]} | [Claude handoff](accelerator-preparation/{n}/CLAUDE-HANDOFF.md) |')
 write(HERE.parent/'accelerator-re-roadmap.md', '# GQ5012BF1 accelerator RE roadmap\n\nFinite offline preparation for the captured stock build, 2026-10-08. Six names were checked in DONE/PARTIAL/BLOCKED/TODO and none existed. All six justify distinct normal-world kernel work: generic donor coverage was not reconstruction; referenced client modules were not inside TinySys transport DONE. No fully closed component is reopened. Six new PARTIAL scopes own 41 exact shipped modules, without duplicate primary ownership.\n\n| Rank | Scope | Registration/current primary owner | Exact owned modules | Source readiness | Difficulty / qualitative effort | Prerequisites | Best next action | Handoff |\n|---|---|---|---|---|---|---|---|---|\n'+'\n'.join(road)+'\n\n## Dependency-aware execution\n\nRetain requested Mali → APUSYS → camera → VCodec → MDP → auxiliary priority. First reuse the already DONE GKI, mailbox/IPI, secure-memory and display providers and freeze GPUEB/VCP headers. Aux host parity can be advanced in parallel or before its blocked consumers if source-header/CRC tests require it; no need to delay Mali discovery or repeat inventory. Camera starts with PDA/VMM residuals and full-module acceptance, **not** a rewrite of 16 published function/data proof pairs.\n\n## Ownership correction rules\n\nThe explicit [module transfer ledger](accelerator-preparation/ownership-changes.tsv), [DT transfer ledger](accelerator-preparation/dt-ownership.tsv) and [dependency graph](accelerator-preparation/dependency-edges.tsv) are authoritative for this preparation. Camera HAL/3A/tuning stays CAMERA-HAL-ISP PARTIAL; sensor TUs/EEPROM/VCM/OIS/flash/rails remain closed child subscopes. APU/MDLA/RPMsg accelerator nodes are not camera-owned just because camera consumes inference. MDP is distinct from DRM DONE; GPUEB/VCP host code is distinct from TinySys IPI DONE. Generic shared CMDQ/SMI/IOMMU/clock/power infrastructure remains referenced, never silently called reconstructed. SCP and ADSP source owners remain DONE. No unrelated merge, removal or rename was performed.\n\n## Evidence and limitations\n\n[Preparation README](accelerator-preparation/README.md), [parity standard](accelerator-preparation/PARITY-STANDARD.md), [aux processor identities](accelerator-preparation/GPU-AI-AUX-KERNEL-INTERFACES/processors.tsv). Static DT enablement/module loading/config declarations are not hardware-execution proof. Proprietary algorithms, secure-world execution, signing keys, calibration and performance tests are excluded. No rebuild, driver load, hardware command, adb, boot, flash or partition write belongs to this assignment.\n')
 print('Rendered six scoped plans and accelerator-re-roadmap.md')

def name_build_note(n):
 return ('**Build baseline:** Android CI 12901745; `common` '+
 '`6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`; stock vermagic '+
 '`6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64`; '+
 'Android Clang 17.0.2 `clang-r487747c` (10087095), LLVM integrated assembler/lld, exact GKI/KMI and vendor config. '+
 'Recorded config: `reverse-engineering/camera-stack/kernel-isp-imgsys/build/vendor-kernel.config`; '+
 'CI pins: `kernel/exact-gki-build-inputs.md`. Inspect CONFIG_CFI_CLANG/MODVERSIONS and effective per-object LTO/visibility flags. '+
 '`-faddrsig` was necessary in existing parity builds; verify rather than broadly changing compiler flags. '+
 'Legacy camera scripts depend on `/tmp/ispenv.sh` and enable modpost warnings; do not call them blindly or count ignored unresolved symbols as success.')

def handoff(s,d,inv,steps):
 n=s['component']; tabletext='\n'.join(f'| `{x["module"]}` | `{x["stock_paths"]}` | `{x["sha256"]}` | {x["bytes"]} | {x["published_parity"]} |' for x in inv)
 return f'''# Claude executable handoff — {n}

## 1. Exact target and authority

Research repository: `{REPO}`. Canonical preparation: `{HERE/n}`. Organized pack: `{WS}/Reverse Engineer - PARTIAL/{n}`. Primary ownership is the explicit {len(inv)}-module set below, not every dependency mentioned in this document.

## 2. Current completion state

PARTIAL. Preparation complete, **no new reconstruction or build performed**. {d['unknown']} Existing results are citations; do not erase or reinterpret measured proof operands.

## 3. Exact stock operands

All paths below are repository-relative; all copies of a basename were hash-checked equal. Use these actual files, not arbitrary newest `.ko` files.

| Module | Exact stock paths | SHA-256 | Bytes | Existing measured axes |
|---|---|---|---|---|
{tabletext}

## 4. Source donors

[source-candidates.tsv](source-candidates.tsv) contains exact existing donor paths, local Git pins, input fingerprints and alternate ALPS/patched candidates. [source-lineage.md](source-lineage.md) explains the pins. Best starting points are r44p1 + MT6878 platform candidates for Mali, pinned KDM/ALPS target directories for APU/codec/MDP/aux, and existing grafted camera source for the already exact camera functions/data. Do not edit shared checkouts. Export to your own space-free scratch tree. Use `git archive <recorded_commit>` only when that revision actually contains the target files and the exported inputs match their recorded fingerprints. Grafted/private or patched worktree inputs (notably camera) may not be represented by the enclosing Git HEAD: copy the exact validated donor files read-only into isolation, preserving their path/hash manifest and patch lineage, rather than substituting a pristine archive. Preserve a patch series and candidate fingerprints; never modify the shared source.

## 5. Build system/toolchain and first commands

{name_build_note(n)}

From this repository, the first commands are read-only/offline input checks, not fresh discovery:

```sh
R='{REPO}'
export PATH='{GKI}/prebuilts/clang/host/linux-x86/clang-r487747c/bin':"$PATH"
cd "$R"
python3 reverse-engineering/accelerator-preparation/validate.py --scope {n} --inputs-only
# ko-kcfi-typeid.py is an importable prototype oracle, not an ELF CLI.
# Use its kcfi(mangled_type) during type recovery; compare stock/rebuild CFI entries.
```

Create an isolated workspace such as `/home/armol/kernel-work/accelerator-{n.lower()}`. Use exact GKI `common` plus isolated vendor/Kconfig/header trees; reuse the prepared mixed-build output `{GKI}/lieppos/camera-isp/kout` **as a copied baseline, never as a writable shared build output**. Preserve original common/vmlinux symvers and naturally generated provider symvers. Translate the target's existing Kbuild/Makefile or Kleaf definition; do not guess object membership. A module build uses:

```sh
# Claude sets these to the isolated directories just created, not existing shared trees:
: "${{COMMON:?isolated exact GKI common}}" "${{KOUT:?isolated configured output}}" "${{TARGET_DIR:?isolated target source}}"
make -C "$COMMON" O="$KOUT" M="$TARGET_DIR" ARCH=arm64 LLVM=1 LLVM_IAS=1 \\
  KBUILD_EXTRA_SYMBOLS="$PROVIDER_SYMVERS" KCFLAGS="-faddrsig" modules
```

Use the recorded vendor config, exact include/KCONFIG_EXT_PREFIX/DEVICE_MODULES paths and target Kconfig selectors from donor Kbuild. Snapshot all effective flags and headers. Reject modpost errors, unknown symbols or changed CRC/KCFI; do not suppress them to get a green build. For camera mixed-tree wiring, read existing `camera-stack/kernel-isp-imgsys/build/` recipes and replace ephemeral paths with your isolated manifest. The above is an executable build pattern, **not a claim that unmodified donors already build or match**.

## 6. Required reconstruction sequence

{steps}

## 7. Function/data parity tests

For each exact module, compare A=listed shipped ELF with B=isolated source rebuild, then independently build B1 and B2. Example after setting exact operands:

```sh
: "${{STOCK_KO:?path from stock-modules.tsv}}" "${{B1_KO:?isolated rebuild}}" "${{B2_KO:?second clean rebuild}}" "${{REPORT_DIR:?new report directory}}"
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

{d['abi']} Use [dt-nodes.tsv](dt-nodes.tsv), provider resolutions and [kernel-abi.md](kernel-abi.md). Decode source macros only after fixing type/layout evidence; numeric IOCTLs/IRQ numbers unsupported by stock remain UNKNOWN.

## 10. Proven hardware behavior

Only existing stock captures, module presence/loading, merged DT and published source/parity results are cited. This pass executes no hardware. {d['hardware']} DT `okay`, Android libraries and config capabilities are not successful accelerator operation or inference/video/graphics performance tests.

## 11. Proprietary exclusions

{d['boundary']}

## 12. Definition of DONE

Every owned target independently passes all [parity axes](../PARITY-STANDARD.md), reproducible clean B1/B2, documented source/type/provenance deltas, and complete observable normal-world DT/ABI/error/lifetime behavior. Any semantic equivalence has symbol-specific proof. No aggregate DONE based on one successful build or a function-count table. Firmware algorithms/userspace and later physical/runtime acceptance remain separate.

## 13. Safety restrictions

Offline static analysis and source builds only when Claude starts reconstruction. No adb, boot, reboot, flash, experimental driver load, accelerator/device command, secure-world invocation, firmware or calibration change, or partition write. Preserve stock Slot B and shared metadata. Do not reset/amend another agent's Git work or modify shared/private reconstruction. Check current HEAD/status before edits and use isolated source/build outputs.

## 14. Required research commits

Commit locally to the authoritative research repository in bounded groups: input/donor baseline → source/patch and ABI reconstruction → per-module complete parity evidence → scoped status/manifest/coverage synchronization. No push. Commit all GQ5012BF1 findings; preserve existing historical evidence. Stop on an explicitly documented blocker rather than stamping CRCs, inventing interfaces or claiming unmeasured progress.
'''

if __name__=='__main__':main()
