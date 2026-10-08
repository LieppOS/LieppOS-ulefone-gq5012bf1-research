# Coverage verdict: ACCOUNTED — kernel RE pending

Snapshot: **2026-10-08**, source HEAD `c8de6a1`. Actual workspace directory status is authoritative; scope registration is not kernel reconstruction.

Authorized accelerator preparation fills ownership, not source or runtime parity. All six scopes are accessible; no proprietary firmware payload copied.

- Components **139**: DONE **94**, PARTIAL **42**, BLOCKED **3**, TODO **0**.
- Modules **457**; DT **580** / **930** node instances; active mapped **574/574**.
- HAL/services **525**; firmware **80**; secure-world **13**; partitions **61**.
- Integration **654**; significant libraries **538**; normalized records **2952**; unmapped E **0**.

## PARTIAL A–F

- A=11 — Actionable static RE; runtime acceptance separate
- B=11 — Closed kernel/source boundary; proprietary integration remains
- C=9 — Proprietary boundary
- D=6 — Hardware/runtime/teardown gated
- E=0 — Stale/duplicate/wrong scope
- F=5 — Umbrella/tracking scope

## Accelerator ownership applied

Six registrations own 41 exact stock targets. Preserve 16 camera function/data proof pairs, SCP/ADSP/TinySys and named camera DONE scopes. No new module parity, hardware execution or unrelated taxonomy migration is claimed. [Roadmap](../accelerator-re-roadmap.md).

## Next work

1. **MALI-GPU-KERNEL** — REGISTERED ACCELERATOR / MODULE PARITY; [handoff/evidence](../accelerator-preparation/MALI-GPU-KERNEL/CLAUDE-HANDOFF.md).
2. **APUSYS-NPU-KERNEL** — DONE: public-source deterministic rebuild and full static parity; [reconstruction report](../accelerator-preparation/APUSYS-NPU-KERNEL/RECONSTRUCTION-REPORT.md).
3. **CAMERA-ISP-KERNEL** — REGISTERED ACCELERATOR / MODULE PARITY; [handoff/evidence](../accelerator-preparation/CAMERA-ISP-KERNEL/CLAUDE-HANDOFF.md).
4. **MTK-VCODEC-KERNEL** — REGISTERED ACCELERATOR / MODULE PARITY; [handoff/evidence](../accelerator-preparation/MTK-VCODEC-KERNEL/CLAUDE-HANDOFF.md).
5. **MTK-MDP-KERNEL** — REGISTERED ACCELERATOR / MODULE PARITY; [handoff/evidence](../accelerator-preparation/MTK-MDP-KERNEL/CLAUDE-HANDOFF.md).
6. **GPU-AI-AUX-KERNEL-INTERFACES** — REGISTERED ACCELERATOR / MODULE PARITY; [handoff/evidence](../accelerator-preparation/GPU-AI-AUX-KERNEL-INTERFACES/CLAUDE-HANDOFF.md).
7. **DTB-DTBO** — STATIC SOURCE CONTRACT; [handoff/evidence](../../docs/dt-module-matching.md).
8. **FT3680-TOUCH** — KERNEL MODULE PARITY; [handoff/evidence](../display-input/ft3680/parity-report.md).
9. **YFT-DEVINFO** — KERNEL MODULE PARITY; [handoff/evidence](../../kernel/phase4-yft-devinfo-kcfi-typeid.md).

## Validation/hygiene

Historical audit/manifest records remain historical; the accelerator preparation validation records current scoped registration, exact input checks, manifest drift and reproducibility. [Preparation](../accelerator-preparation/README.md). [RT5133 retraction](notes/RT5133-CORRECTION.md) remains valid. See [PARTIAL triage](PARTIAL-TRIAGE.md), [taxonomy](PROPOSED-CHANGES.md) and [readiness](PORT-READINESS.md). Stop global inventory work; proceed only with component reconstruction and later authorized integration/runtime validation.
