# Coverage verdict: ACCOUNTED — remaining kernel/runtime work explicit

Snapshot: **2026-10-08**, source HEAD `c8de6a1`. Actual workspace directory status is authoritative; scope registration is not kernel reconstruction.

Authorized accelerator preparation fills ownership, not source or runtime parity. All six scopes are accessible; no proprietary firmware payload copied.

- Canonical component ledger **139**: DONE **99**, PARTIAL **37**, BLOCKED **3**, TODO **0**.
- Actual organized workspace after camera promotion: DONE **100**, PARTIAL **36**,
  BLOCKED **3**, TODO **0**. The pre-existing Mali canonical-PARTIAL/workspace-DONE
  discrepancy is documented and left outside this component's changes.
- Modules **457**; DT **580** / **930** node instances; active mapped **574/574**.
- HAL/services **525**; firmware **80**; secure-world **13**; partitions **61**.
- Integration **654**; significant libraries **538**; normalized records **2952**; unmapped E **0**.

## PARTIAL A–F

- A=6 — Actionable static RE; runtime acceptance separate
- B=11 — Closed kernel/source boundary; proprietary integration remains
- C=9 — Proprietary boundary
- D=6 — Hardware/runtime/teardown gated
- E=0 — Stale/duplicate/wrong scope
- F=5 — Umbrella/tracking scope

## Accelerator ownership applied

Six accelerator registrations own 41 exact stock targets and are now workspace-DONE;
CAMERA-ISP-KERNEL closes the final nineteen modules with clean B1/B2 and complete machine
ledgers. Mali's older canonical PARTIAL row is stale and is not a new task. Hardware
execution and proprietary firmware/HAL algorithms remain explicit boundaries.
[Roadmap](../accelerator-re-roadmap.md).

## Next work

1. **MALI-GPU-KERNEL** — already workspace-DONE; older canonical registration/handoff is historical. No reopening in this camera task.
2. **APUSYS-NPU-KERNEL** — DONE: public-source deterministic rebuild and full static parity; [reconstruction report](../accelerator-preparation/APUSYS-NPU-KERNEL/RECONSTRUCTION-REPORT.md).
3. **CAMERA-ISP-KERNEL** — DONE: nineteen public-source module rebuilds, clean B1/B2 and complete static parity; [reconstruction report](../accelerator-preparation/CAMERA-ISP-KERNEL/RECONSTRUCTION-REPORT.md).
4. **MTK-VCODEC-KERNEL** — DONE: public-source deterministic rebuild and full static parity; [reconstruction report](../accelerator-preparation/MTK-VCODEC-KERNEL/RECONSTRUCTION-REPORT.md).
7. **DTB-DTBO** — STATIC SOURCE CONTRACT; [handoff/evidence](../../docs/dt-module-matching.md).
8. **FT3680-TOUCH** — KERNEL MODULE PARITY; [handoff/evidence](../display-input/ft3680/parity-report.md).
9. **YFT-DEVINFO** — KERNEL MODULE PARITY; [handoff/evidence](../../kernel/phase4-yft-devinfo-kcfi-typeid.md).

## Validation/hygiene

Historical audit/manifest records remain historical; the accelerator preparation validation records current scoped registration, exact input checks, manifest drift and reproducibility. [Preparation](../accelerator-preparation/README.md). [RT5133 retraction](notes/RT5133-CORRECTION.md) remains valid. See [PARTIAL triage](PARTIAL-TRIAGE.md), [taxonomy](PROPOSED-CHANGES.md) and [readiness](PORT-READINESS.md). Stop global inventory work; proceed only with component reconstruction and later authorized integration/runtime validation.
