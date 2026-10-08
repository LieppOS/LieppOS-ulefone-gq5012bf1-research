# Axis 11: canonical component-folder audit

Audit date: 2026-10-08

`components.tsv` is generated from the actual canonical workspace folders, not from
the old typed totals. The measured current workspace is:

| Status | Count |
|---|---:|
| DONE | 94 |
| PARTIAL | 42 |
| BLOCKED | 3 |
| TODO | 0 |
| **Total** | **139** |

This supersedes the 71/59/3 snapshot in the original audit request. The total stayed
139 while 23 folders have since moved from PARTIAL to DONE through
independently verified closures; each moved folder carries its own closure README
with measured parity evidence.

## PARTIAL classification

| Class | Meaning | Count |
|---|---|---:|
| A | actionable / statically closeable | 11 |
| B | kernel/source closed, broader proprietary scope remains | 11 |
| C | proprietary boundary | 9 |
| D | hardware/runtime/teardown gated | 6 |
| E | stale/duplicate/wrong PARTIAL scope | 0 |
| F | intentional umbrella/tracking scope | 5 |

Every PARTIAL row in `components.tsv` has an explicit boundary, next action,
difficulty and dependency list, and each is expanded individually in
[PARTIAL-TRIAGE.md](../PARTIAL-TRIAGE.md). The SCP-owned physical sensors are class
C—not missing Linux drivers—because their register drivers and calibration live in
the signed SCP image.

## DONE audit

DONE is interpreted as **named-scope static closure**, never as a claim that every
proprietary firmware/HAL/runtime behavior is open. The module, DT, HAL/service,
firmware and hardware axes were joined back to every component row to expose
boundaries.

No evidence justifies an automatic DONE → PARTIAL move in this audit. Several DONE
rows still have runtime or physical follow-up, but their READMEs explicitly exclude
it from the closed static scope. Examples include MediaTek DRM runtime validation,
microSD insertion/format behavior and RT5133 physical population confirmation (not an active camera LDO). These
must remain visible as boundaries; they are not silently treated as source gaps.

Taxonomy quality is a separate question. Some DONE folders are valid findings but
poor canonical ownership boundaries (GZ per-module children, negative-absence
findings, USB3 feasibility and the `vendor.all.modules.ready` property). They are
recommendations in [PROPOSED-CHANGES.md](../PROPOSED-CHANGES.md); no folder was
moved or deleted by this audit.

## BLOCKED audit

All 3 blockers still exist:

- `RF-ANTENNAS`: Requires teardown, schematic/board view, continuity or RF measurements.
- `TRUSTKERNEL-ABI-ISLAND`: Required stock ABI functions are absent from available donor/source; private vendor island is unavailable.
- `TRUSTKERNEL-TEE`: Private TA/helper semantics and authorized secure-world runtime evidence are unavailable.

None should be moved automatically.

## Measured joins

`components.tsv` includes, per component:

- directly owned and umbrella-recorded kernel modules from `kernel-modules.tsv`;
- VINTF/HAL interfaces and init services from axes 4–5;
- DT compatibles plus physical devices from axes 2–3;
- firmware/calibration artifacts from axis 6;
- best available research-repository report path;
- recommended taxonomy action, if any.

The generator fails if any current PARTIAL lacks a curated A–F decision. This
prevents a newly added/moved folder from silently disappearing from triage.
