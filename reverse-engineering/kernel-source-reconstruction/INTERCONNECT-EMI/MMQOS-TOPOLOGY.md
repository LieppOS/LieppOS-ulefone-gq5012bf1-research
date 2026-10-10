# Actual MT6878 MMQoS implementation and topology

Evidence is accepted stock code/data plus the independently decoded GQ5012BF1 DT,
not features borrowed from another SoC. Full table: evidence/hardware/MMQOS-NODES.tsv.
All 166 24-byte source records agree field-for-field with compiled stock; exact compiler
record layouts and source expansion hash are retained. All links terminate without cycles.

## Module ownership

**mmqos-mt6878** contains the166 node descriptors, platform/HRT policies, OF match
mediatek,mt6878-mmqos and platform-driver registration. It delegates probe/remove to
common and defines no exported API or separate suspend/resume implementation.

**mmqos-common** links four real C units: common/provider policies (mmqos-mtk), HRT
budget/throttle/sysfs (mmqos-hrt), VCP host/IPI/shared-memory integration (mmqos-vcp),
and compiled test/diagnostic helpers (mmqos-test). These helpers were analyzed, not run.

IDs encode type in bits31:16: common1, common-port2, larb3, master-port4. Low bits
encode common/port or larb/port. This is **not** the EMI provider's onecell index space.
There is1 common0,9 common ports,24 logical larbs and132 master ports. Board supplier
list resolves21 physical larbs plus1 common. Logical5/8 and virtual39 have no board
supplier instance, even though their software nodes/DT vote paths exist.

## Functional request flow

Clients use of_mtk_icc_get/mtk_icc_set_bw through the separate mtk-icc-core registry.
That framework invokes common's aggregate/set/path_is_write/xlate callbacks. Average
and peak aggregation in common uses sums (including max-OSTD sentinel policy), not the
Linux EMI driver's sum-average/max-peak policy. V2 read/write/channel state is updated
for the exact compiled nodes; channel labels are accounting classes, not measured DRAM
channels. Common caches prior votes under locks to avoid redundant programming.

A master-port→larb edge calculates/clamps outstanding transactions using its ratio,
avg/peak/mixed request and camera/display policy; OSTD_ENABLE controls the actual
mtk_smi_larb_bw_set call. Larb→common-port can program SMI common bandwidth and
read/write outstanding limits through mtk_smi_common_bw_set/common_ostdl_set. Missing
larb devices cause the corresponding hardware branch to skip, not a fabricated binding.
Common-port→common maintains channel totals and, with DVFSRC_ENABLE, issues Linux ICC
normal/HRT EMI votes and updates HRT accounting.

Common obtains clock mm from the DT and reads its rate; MMDVFS notifier updates cached
frequency. OPP/regulator, MMDVFS and VMMRC frequency-vote modes exist in exact code.
Default frequency mode is BY_REGULATOR (0); parameters/policy may change it. No operating
frequency or active mode was measured. mmdvfs-dvfsrc-vcore supply and OPP helpers are
separate framework dependencies; REGULATORS source closure does not certify DVFSRC.

## HRT and board policy

Platform descriptors distinguish display, camera, SRT VDEC/VENC and other common-port
classes; max_ratio0x3f and max_disp_ostdl0x3f are capability ceilings, not live settings.
Camera admission accounting applies weighted budgets/ratios, delayed camera increases,
wait/throttle state and blocking notifier chains. DRM consumes four HRT/query/notifier
exports; camera waits for throttle completion. Readout includes software records, not
independent throughput measurements. DRAMC type/step frequency and emi channel count
are queried dynamically; source fallback totals are not hardware measurements.

Board interconnect node declares mmqos-state **0xc8d**: OSTD, DVFSRC, common OSTD,
DPC, CAM_NO_MAX_OSTDL and DYNA_URATE bits. BWL, VCP, VMMRC/VMMRC_VCP bits are initially
clear. This is DT initialization, not a read of mutable current module parameters.
VMMRC/MMINFRA ranges are still mapped by v2 probe when their DT properties are present;
mapping a range does not establish that VMMRC voting is active.

## Initialization, error handling and lifecycle

Probe allocates bookkeeping, resolves/creates available larb devices (may defer), adds
the private provider/nodes/links, obtains clock/EMI paths, registers MMDVFS/SMI notifiers,
HRT sysfs and /proc/mmqos/{mmqos_bw,last_mmqos}. Common library has no own board probe;
the platform module invokes it. Allocation/provider/node failures have the exact stock
cleanup paths. Preserve the observed limits: v2 setup runs after probe_ret without an
early return; removal drops nodes/provider and some HRT/MMDVFS state but does not visibly
clean every persistent proc/VCP/SMI resource. No speculative fixes were introduced.

Neither target platform driver declares dev_pm_ops/runtime-PM callbacks. Bus/domain
frameworks, MMDVFS notifiers, client vote release and VCP host suspend/notifier handling
provide related lifecycle boundaries. VCP code supports readiness/timeouts, feature
refcounts, reserved/shared memory, IPI sync and diagnostics; firmware algorithms remain
outside source scope and VCP bit is initially off on this DT.

Writable module parameters include state/frequency/trace/test controls; HRT exposes
sysfs handlers and software diagnostics. Those interfaces can alter votes or initiate
tests and were **not exercised**. Tracepoint/proc/sysfs availability is source capability,
not proof of a created runtime path, sustained bandwidth or correct fault recovery.
