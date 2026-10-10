# Cross-component ABI: actual edges, not a guessed multimedia dependency list

Authoritative source: existing458-identity DEPENDENCY-EDGES.tsv and shipped consumers;
reused accelerator acceptance evidence, not rebuilt DONE modules. Existing owners stay
unchanged. No registered component added for this source-audit group.

## Direct imports into targets (all seven checked)

| Consumer | Existing owner | Target | Symbols |
|---|---|---|---|
| mediatek-drm.ko |MEDIATEK-DRM|mmqos-common|4 HRT/query/notifier calls|
| mtk-cam-isp7sp.ko |CAMERA-ISP-KERNEL|mmqos-common|mtk_mmqos_wait_throttle_done|
| mmqos-mt6878.ko |COVERED-GENERIC|mmqos-common|v2_probe/remove function pointers|

CROSS-COMPONENT-ABI.tsv records exact identities, CRCs, GPL export type, source/stock
callee prefix, consumer absolute type IDs when present, actual consumer relocations and
full target function hash. All match. Two platform pointer type IDs equal callee hashes;
direct branch callers are not falsely required to have an indirect CFI check. No stock
module imports an exported interface from mtk-emi or mmqos-mt6878: they export none.
Actual request execution and caller health are not inferred from relocations.

## Private ICC transport from completed accelerators

Existing CAMERA-ISP-KERNEL (8 slots), MTK-MDP-KERNEL (4), MTK-VCODEC-KERNEL (4) import
of_mtk_icc_get/mtk_icc_set_bw/related functions from **mtk-icc-core**, not this group.
ACCELERATOR-ICC-TRANSPORT.tsv verifies all16 CRCs against complete real core.o genksyms
and stock/source callee prefixes. Board paths in DT-INTERCONNECT-PATHS map their requests
into the accepted MMQoS tables. Framework provider itself remains separately uncertified.

MALI-GPU-KERNEL, APUSYS-NPU-KERNEL and GPU-AI-AUX-KERNEL-INTERFACES have **zero direct
imports into the three targets** in the complete inventory. Absence of direct imports
is not proof of no DVFS/bandwidth coupling: OPP/DVFSRC/firmware or programmatic paths
may be involved. GPU/VPU/MDLA/UFS EMI table entries prove available node implementation,
not routing or active requests. Do not invent larbs for them from another platform.

## Providers consumed by this group

33 true external slots span DVFSRC, VCP status, TinySys IPI, MMDVFS variants, SMI/debug,
DRAMC, emi, mrdump and private ICC. Twelve unchanged public objects reproduce CRC and
licence witnesses; function KCFI prefixes agree with their actual shipped providers.
Core imports use immutable public GKI12901745 metadata; platform's2 imports resolve
inside the owned build. Provider ABI proofs do not promote their D/G source classes.

Ordering: common must be loadable before platform; private ICC/SMI/clock/regulator/
DVFSRC and relevant power-domain/OPP suppliers must be available to successful probing
or handled through deferral. VCP firmware readiness is distinct from status module
symbol availability; DT initially disables MMQoS VCP offload. Module list order alone
cannot establish actual preload chronology when dependency resolution intervenes.

## Existing evidence reused

- [MALI-GPU-KERNEL](../../accelerator-preparation/MALI-GPU-KERNEL/FINAL-REPORT.md): kernel ABI, dependencies, DT/power and source acceptance.
- [APUSYS-NPU-KERNEL](../../accelerator-preparation/APUSYS-NPU-KERNEL/RECONSTRUCTION-REPORT.md): accepted apu_top/apusys and DT/proprietary boundaries.
- [MTK-VCODEC-KERNEL](../../accelerator-preparation/MTK-VCODEC-KERNEL/RECONSTRUCTION-REPORT.md) and [MTK-MDP-KERNEL](../../accelerator-preparation/MTK-MDP-KERNEL/RECONSTRUCTION-REPORT.md): accepted CRC/relocation/consumer contracts.
- [CAMERA-ISP-KERNEL](../../accelerator-preparation/CAMERA-ISP-KERNEL/RECONSTRUCTION-REPORT.md): nineteen-module acceptance and source-to-userspace contract.
- [GPU-AI-AUX-KERNEL-INTERFACES](../../accelerator-preparation/GPU-AI-AUX-KERNEL-INTERFACES/abi-parity.md): VCP status/host split and natural provider recipes.

Those packages remain untouched. Their real media/GPU/NPU firmware and userspace runtime
qualification is not expanded by this source closure.
