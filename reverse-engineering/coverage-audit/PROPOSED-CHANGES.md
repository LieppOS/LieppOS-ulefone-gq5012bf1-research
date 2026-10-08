# Taxonomy decisions after accelerator preparation

Snapshot: **2026-10-08**, source HEAD `c8de6a1`. Actual workspace directory status is authoritative; scope registration is not kernel reconstruction.

**Current registered total: 139.** Six authorized PARTIAL registrations (including the camera child) are applied. No unrelated merge, removal, rename or DONE promotion was performed.

| Proposal | Operation | Decision | Remaining conditional change |
|---|---|---|---:|
| PC-001 | ADD | APPLIED (AUTHORIZED PREPARATION) | +0 |
| PC-002 | SPLIT | APPLIED (AUTHORIZED PREPARATION) | +0 |
| PC-003 | MERGE | ACCEPT RECOMMENDATION | -4 |
| PC-004 | MERGE | ACCEPT RECOMMENDATION | -1 |
| PC-005 | MERGE | ACCEPT RECOMMENDATION | -1 |
| PC-006 | MERGE | ACCEPT RECOMMENDATION | -1 |
| PC-007 | REMOVE | ACCEPT RECOMMENDATION | -1 |
| PC-008 | REMOVE | ACCEPT RECOMMENDATION | -1 |
| PC-009 | RENAME | REJECT | +0 |
| PC-010 | METADATA | ACCEPT RECOMMENDATION | +0 |
| PC-011 | ADD | APPLIED (AUTHORIZED PREPARATION) | +0 |
| PC-012 | ADD | APPLIED (AUTHORIZED PREPARATION) | +0 |
| PC-013 | ADD | APPLIED (AUTHORIZED PREPARATION) | +0 |
| PC-014 | ADD | APPLIED (AUTHORIZED PREPARATION) | +0 |

## PC-001: ADD — APPLIED (AUTHORIZED PREPARATION)

- **Components:** MALI-GPU-KERNEL
- **Rationale:** Ten E rows converge on one active source-actionable kernel/DT/platform scope, not ten components.
- **Preservation/remaining consequences:** Authorized registration is PARTIAL; eight explicit KMD/platform modules, CSF/userspace algorithms excluded. Historical ten E rows are now assigned; no parity fabricated.
- **Remaining conditional change:** +0

## PC-002: SPLIT — APPLIED (AUTHORIZED PREPARATION)

- **Components:** CAMERA-HAL-ISP → CAMERA-HAL-ISP + CAMERA-ISP-KERNEL
- **Rationale:** Existing ISP source/module ledger proves actionable kernel work is mixed with permanently proprietary HAL/3A/tuning/CCU.
- **Preservation/remaining consequences:** Nineteen explicit kernel modules moved in ownership only; sixteen existing proof pairs and source/evidence paths preserved. HAL parent stays PARTIAL for proprietary userspace/algorithms.
- **Remaining conditional change:** +0

## PC-003: MERGE — ACCEPT RECOMMENDATION

- **Components:** GZ-IPC-MOD, GZ-MAIN-MOD, GZ-TRUSTY-MOD, GZ-TZ-SYSTEM → GZ-TRANSPORT
- **Rationale:** Four exact-source transport children and their parent share a coherent normal-world transport boundary.
- **Preservation/remaining consequences:** Preserve all per-module parity/source/ABI subreports and provenance; do not imply signed hypervisor/TA source closure.
- **Remaining conditional change:** -4

## PC-004: MERGE — ACCEPT RECOMMENDATION

- **Components:** AW36518-V2-FLASH → AW36518-FLASH
- **Rationale:** Sibling reports distinguish two shipped source variants of the AW36518 family.
- **Preservation/remaining consequences:** Keep both stock module variants, topology, source and parity reports as named subscopes.
- **Remaining conditional change:** -1

## PC-005: MERGE — ACCEPT RECOMMENDATION

- **Components:** USB3-FEASIBILITY → USB-TYPEC
- **Rationale:** The resolved-negative SuperSpeed board capability study is a finding under Type-C ownership.
- **Preservation/remaining consequences:** Preserve the USB3-port absence proof and do not discard evidence just because the component is retired.
- **Remaining conditional change:** -1

## PC-006: MERGE — ACCEPT RECOMMENDATION

- **Components:** VENDOR-ALL-MODULES-READY → INIT-INSMOD
- **Rationale:** The sole setter/consumer property timeline belongs to module-loader/init ordering.
- **Preservation/remaining consequences:** Keep the complete setter/consumer and boot-phase evidence under INIT-INSMOD; redirect old links.
- **Remaining conditional change:** -1

## PC-007: REMOVE — ACCEPT RECOMMENDATION

- **Components:** ESIM-EUICC-ABSENCE
- **Rationale:** A proven absence is a negative hardware finding, not an implementation target.
- **Preservation/remaining consequences:** Archive the original reports and retain an explicit not-fitted finding; reassign the hardware row to negative-inventory ownership before retiring its registered name.
- **Remaining conditional change:** -1

## PC-008: REMOVE — ACCEPT RECOMMENDATION

- **Components:** WIRELESS-CHARGING-ABSENCE
- **Rationale:** No fitted wireless-charging implementation scope is established; wired reverse power is separate.
- **Preservation/remaining consequences:** Archive original negative evidence in power/hardware inventory and migrate references/ownership before retirement.
- **Remaining conditional change:** -1

## PC-009: RENAME — REJECT

- **Components:** RT5133-POWER-IC → RT5133-CAMERA-LDO-INTEGRATION
- **Rationale:** The claimed successful binding was a client-name misread; no newer success capture exists. The observed client is unbound and camera rails use WL2864C.
- **Preservation/remaining consequences:** Keep the existing name, two-module static DONE scope and GPIO1 safety warning. Physical population needs evidence; do not rename on an inferred reference-board role.
- **Remaining conditional change:** +0

## PC-010: METADATA — ACCEPT RECOMMENDATION

- **Components:** OEM-KERNEL-MODULES, VENDOR-DLKM and inventory/umbrella labels
- **Rationale:** Use the measured module universe and current child closures; tracking is not reconstruction. SYSTEM-DLKM is now DONE for its measured 60-module baseline, not an unfinished umbrella.
- **Preservation/remaining consequences:** Refresh stale metadata/checklists only after approval; preserve all registers/provenance, with no automatic status or ownership move.
- **Remaining conditional change:** +0

## PC-011: ADD — APPLIED (AUTHORIZED PREPARATION)

- **Components:** APUSYS-NPU-KERNEL
- **Rationale:** apusys and apu_top are normal-world source-actionable kernel code, not proprietary algorithms. Prior class-C blob-inventory ownership did not establish source parity; APU/MDLA RPMsg nodes were incorrectly attributed to camera consumers.
- **Preservation/remaining consequences:** PARTIAL only; exact module/DT ledger and handoff prepared, no source reconstruction or proprietary algorithm claim.
- **Remaining conditional change:** +0

## PC-012: ADD — APPLIED (AUTHORIZED PREPARATION)

- **Components:** MTK-VCODEC-KERNEL
- **Rationale:** Four codec/VCU normal-world drivers and their dedicated clock provider have donor targets but no complete module-level source/parity owner. Generic coverage was not a measured reconstruction.
- **Preservation/remaining consequences:** PARTIAL only; exact module/DT ledger and handoff prepared, no source reconstruction or proprietary algorithm claim.
- **Remaining conditional change:** +0

## PC-013: ADD — APPLIED (AUTHORIZED PREPARATION)

- **Components:** MTK-MDP-KERNEL
- **Rationale:** mdp_drv and the two MML modules are distinct from mediatek-drm. The DRM DONE scope explicitly closes DRM/panel modules, not MDP/MML; no MDP byte/semantic parity evidence was found. Keep generic CMDQ and reconstructed secure CMDQ outside this component.
- **Preservation/remaining consequences:** PARTIAL only; exact module/DT ledger and handoff prepared, no source reconstruction or proprietary algorithm claim.
- **Remaining conditional change:** +0

## PC-014: ADD — APPLIED (AUTHORIZED PREPARATION)

- **Components:** GPU-AI-AUX-KERNEL-INTERFACES
- **Rationale:** GPUEB and VCP host/status clients were only referenced by MTK-TINYSYS-IPI. Its explicit DONE scope proves the transport module, not these client implementations. SCP and ADSP host code are already DONE elsewhere and are not duplicated.
- **Preservation/remaining consequences:** PARTIAL only; exact module/DT ledger and handoff prepared, no source reconstruction or proprietary algorithm claim.
- **Remaining conditional change:** +0

## Conditional count, not current reality

Only still-unapplied accepted recommendations would yield 139 -9 = **130 canonical components**. This is not current reality; applied additions are not counted twice. All unrelated migrations need separate approval and evidence-preserving redirects/manifest/index changes. RT5133 rename remains rejected.
