# Final taxonomy decision document

Final snapshot: **2026-10-08**, source HEAD `3abc5643e539b3f2c8565d8197091d3bb50856ff`; workspace directories are authoritative. This report is reproducible from committed metadata, not a claim that later concurrent closures never occur.

**Current registered total: 133.** Recommendations only: no ADD/SPLIT/MERGE/REMOVE/RENAME has been applied by this audit. ACCEPT RECOMMENDATION is not migration approval or evidence of implementation.

| Proposal | Operation | Decision | Conditional component-count change |
|---|---|---|---:|
| PC-001 | ADD | ACCEPT RECOMMENDATION | +1 |
| PC-002 | SPLIT | ACCEPT RECOMMENDATION | +1 |
| PC-003 | MERGE | ACCEPT RECOMMENDATION | -4 |
| PC-004 | MERGE | ACCEPT RECOMMENDATION | -1 |
| PC-005 | MERGE | ACCEPT RECOMMENDATION | -1 |
| PC-006 | MERGE | ACCEPT RECOMMENDATION | -1 |
| PC-007 | REMOVE | ACCEPT RECOMMENDATION | -1 |
| PC-008 | REMOVE | ACCEPT RECOMMENDATION | -1 |
| PC-009 | RENAME | REJECT | +0 |
| PC-010 | METADATA | ACCEPT RECOMMENDATION | +0 |

## PC-001: ADD — ACCEPT RECOMMENDATION

- **Components:** MALI-GPU-KERNEL
- **Evidence / rationale:** Ten E rows converge on one active source-actionable kernel/DT/platform scope, not ten components.
- **Consequences and preservation:** Keep proprietary CSF firmware and GPU userspace outside closure; preserve source claims/metadata and add only after approval.
- **Count change if approved and executed:** +1

## PC-002: SPLIT — ACCEPT RECOMMENDATION

- **Components:** CAMERA-HAL-ISP → CAMERA-HAL-ISP + CAMERA-ISP-KERNEL
- **Evidence / rationale:** Existing ISP source/module ledger proves actionable kernel work is mixed with permanently proprietary HAL/3A/tuning/CCU.
- **Consequences and preservation:** Transfer an explicit module/DT ownership ledger to the new child without duplicating primary ownership; retain HAL scope and historical evidence.
- **Count change if approved and executed:** +1
- [ISP module/source and proprietary-boundary evidence](../camera-stack/notes/isp-stack.md).

## PC-003: MERGE — ACCEPT RECOMMENDATION

- **Components:** GZ-IPC-MOD, GZ-MAIN-MOD, GZ-TRUSTY-MOD, GZ-TZ-SYSTEM → GZ-TRANSPORT
- **Evidence / rationale:** Four exact-source transport children and their parent share a coherent normal-world transport boundary.
- **Consequences and preservation:** Preserve all per-module parity/source/ABI subreports and provenance; do not imply signed hypervisor/TA source closure.
- **Count change if approved and executed:** -4

## PC-004: MERGE — ACCEPT RECOMMENDATION

- **Components:** AW36518-V2-FLASH → AW36518-FLASH
- **Evidence / rationale:** Sibling reports distinguish two shipped source variants of the AW36518 family.
- **Consequences and preservation:** Keep both stock module variants, topology, source and parity reports as named subscopes.
- **Count change if approved and executed:** -1

## PC-005: MERGE — ACCEPT RECOMMENDATION

- **Components:** USB3-FEASIBILITY → USB-TYPEC
- **Evidence / rationale:** The resolved-negative SuperSpeed board capability study is a finding under Type-C ownership.
- **Consequences and preservation:** Preserve the USB3-port absence proof and do not discard evidence just because the component is retired.
- **Count change if approved and executed:** -1

## PC-006: MERGE — ACCEPT RECOMMENDATION

- **Components:** VENDOR-ALL-MODULES-READY → INIT-INSMOD
- **Evidence / rationale:** The sole setter/consumer property timeline belongs to module-loader/init ordering.
- **Consequences and preservation:** Keep the complete setter/consumer and boot-phase evidence under INIT-INSMOD; redirect old links.
- **Count change if approved and executed:** -1

## PC-007: REMOVE — ACCEPT RECOMMENDATION

- **Components:** ESIM-EUICC-ABSENCE
- **Evidence / rationale:** A proven absence is a negative hardware finding, not an implementation target.
- **Consequences and preservation:** Archive the original reports and retain an explicit not-fitted finding; reassign the hardware row to negative-inventory ownership before retiring its registered name.
- **Count change if approved and executed:** -1

## PC-008: REMOVE — ACCEPT RECOMMENDATION

- **Components:** WIRELESS-CHARGING-ABSENCE
- **Evidence / rationale:** No fitted wireless-charging implementation scope is established; wired reverse power is separate.
- **Consequences and preservation:** Archive original negative evidence in power/hardware inventory and migrate references/ownership before retirement.
- **Count change if approved and executed:** -1

## PC-009: RENAME — REJECT

- **Components:** RT5133-POWER-IC → RT5133-CAMERA-LDO-INTEGRATION
- **Evidence / rationale:** The claimed successful binding was a client-name misread; no newer success capture exists. The observed client is unbound and camera rails use WL2864C.
- **Consequences and preservation:** Keep the existing name, two-module static DONE scope and GPIO1 safety warning. Physical population needs evidence; do not rename on an inferred reference-board role.
- **Count change if approved and executed:** +0
- [Exact capture chronology and retraction](notes/RT5133-CORRECTION.md). Physical population is NEEDS EVIDENCE; the specific unsupported rename is REJECT, not silently deferred.

## PC-010: METADATA — ACCEPT RECOMMENDATION

- **Components:** OEM-KERNEL-MODULES, VENDOR-DLKM and inventory/umbrella labels
- **Evidence / rationale:** Use the measured module universe and current child closures; tracking is not reconstruction. SYSTEM-DLKM is now DONE for its measured 60-module baseline, not an unfinished umbrella.
- **Consequences and preservation:** Refresh stale metadata/checklists only after approval; preserve all registers/provenance, with no automatic status or ownership move.
- **Count change if approved and executed:** +0

## Conditional count, not current reality

If all **accepted recommendations** are approved and executed: 133 -7 = **126 canonical components**. This conditional number is not the component database total. One ADD and one split-created child are offset by seven merged-away children/findings and two archived absence findings. Rejected RT5133 rename changes nothing.

## Future migration prerequisites

Archive originals first; write old→new path/owner redirects; preserve parity operands, source provenance, negative findings and manifests. Update every affected module/DT/service owner, registered directory, COPY-MANIFEST and status index together **after approval**, outside this final audit. No evidence is to be deleted.
