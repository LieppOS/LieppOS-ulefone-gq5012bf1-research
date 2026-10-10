# First-stage loading and deferred runtime contract

All three identities are REQUIRED_BY_RETAINED_FIRST_STAGE_LOAD_CONTRACT in the audit,
recorded loaded but with UNKNOWN successful probe/binding. Preserve that distinction.
No module is excluded merely because an enabled DT node has no current binding capture.

| Module | Actual normal list | Recovery list | Stale audit field corrected |
|---|---:|---:|---|
| mtk-emi.ko |51|50|47→51|
| mmqos-common.ko |61|59|67→61|
| mmqos-mt6878.ko |62|60|68→62|

Hashed actual files and all related entries are in evidence/inventory/LOAD-ORDER.tsv.
Lists are unchanged. Other modules' stale metadata is outside this scope.

Normal declarations place pinctrl20/21, boot clocks22/23 (bus/peri/VLP later), PMIC
regulator38, SCPSYS41/42, DVFSRC44 and regulator45 before EMI51. DRAMC53, SMI54,
SMI-debug55, private ICC56 and MMDVFS58-60 precede common61/platform62. IOMMU65 and
CMDQ69 are separately declared; do not invent direct target imports of those drivers.
Clock/provider/PMIC source closures remain completed; their runtime validation is not
redone here. Uncertified SMI/DVFSRC/private ICC/MMDVFS/power-domain source gaps remain.

VCP status166, TinySys IPI88 and emi169 appear **later** in the declaration despite
common's imports. That proves declaration position, not literal successful chronological
insmod order: dependency loading/preloading and saved loaded records are separate.
Do not silently reorder the list. DRAMC appears twice (53/119); preserve duplicates.
The MMQoS DT initial VCP-offload bit is clear, but required symbols still must resolve.

Probe requirements: parent DVFSRC child/provider and Linux EMI paths; private ICC nodes;
available larbs/common devices; mm clock; OPP/vcore supply/power-domain dependencies;
DRAMC/channel-query state and notifier registration. A bound provider, non-null paths and
nondeferred client are runtime requirements, not consequences of binary equivalence.

## Future controlled runtime/Slot B validation — not performed

Separate authorization and recovery/rollback readiness are necessary before any deployment.
1. Check shipped-order dependency resolution, unknown-symbol/CRC/CFI failures and deferrals.
2. Prove parent/EMI/private-MMQoS/SMI/client probes and resolved interconnect paths.
3. Observe controlled normal/HRT and read/write votes, aggregation and zero-vote release;
   distinguish requested/software counters from measured memory throughput.
4. Observe clock/OPP/regulator/power-domain interactions and actual DRAM type/channel state.
5. Exercise separately authorized media use, close/unbind, suspend/resume and retry paths.
6. Validate provider errors, missing resources, failed allocations, stale handles and teardown;
   preserve exact stock error handling risks rather than claiming it safe by inspection.
7. If VCP offload is separately enabled, verify firmware readiness, IPI/shared-memory
   ownership, timeout/restart/suspend handling and feature refcount balance.

No GPIO/register/vote/voltage/frequency operation, stress test, firmware action, reboot,
flash, slot switch, module load, ADB access or push occurred in this offline task.
