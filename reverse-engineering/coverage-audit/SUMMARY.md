# Coverage verdict: NEAR-COMPLETE

Final snapshot: **2026-10-08**, source HEAD `3abc5643e539b3f2c8565d8197091d3bb50856ff`; workspace directories are authoritative. This report is reproducible from committed metadata, not a claim that later concurrent closures never occur.

**Global audit finalized for this stock build.** All registered components and artifact axes are inventoried. One source-actionable ownership hole remains: proposed MALI-GPU-KERNEL. Camera ISP is a split of an already represented scope. NEAR-COMPLETE describes ownership, not open source or daily-driver readiness.

## Measured headline

- Registered components: **133**; DONE **94**, PARTIAL **36**, BLOCKED **3**, TODO **0**.
- Shipped modules: **457** unique names; all accounted, including three explicit GPU E rows.
- DT compatibles: **580**, across **930** nodes; active mapped **571/574** (three GPU E rows).
- HAL/service rows: **525**; non-generic mapped **333/337** (four GPU E rows).
- Physical inventory: **44**; firmware **80**; secure-world boundaries **13**; partition families **61**.
- Android integration **654**; significant native libraries **538**; normalized artifact rows **2952**.
- Unexplained E rows: **0**. All **10** E rows are the one documented Mali scope, not registered owners.

## PARTIAL A–F

- A=6 — Actionable static RE (whole-scope runtime acceptance may still be separate)
- B=11 — Kernel/source closed; broader proprietary boundary remains
- C=8 — Proprietary boundary
- D=6 — Hardware/runtime/teardown gated
- E=0 — Stale/duplicate/wrong scope
- F=5 — Broad umbrella/tracking scope
- Sum: **36**, exactly the current PARTIAL directory count.

## Final decisions

- **Mali:** ACCEPT RECOMMENDATION for one ADD. Source/parity remains work; userspace/CSF stays proprietary.
- **ISP:** ACCEPT RECOMMENDATION for CAMERA-ISP-KERNEL SPLIT from CAMERA-HAL-ISP; not another missing component.
- **RT5133:** bound-device claim RETRACTED; rename REJECTED. Declared client is unbound, zero registered/consumed RT5133 rails, WL2864C supplies camera rails. Static DONE remains. [Evidence](notes/RT5133-CORRECTION.md).
- **Taxonomy:** ADD/SPLIT/MERGE/REMOVE/metadata recommendations only; current component set remains unchanged. [Decisions and conditional count](PROPOSED-CHANGES.md).
- **Readiness:** custom GKI/container baseline is strong, but custom boot/ROM/daily-driver acceptance is not proven. Property definitions and bluetooth_audio.xml were installed externally in 24afa6b; preserve and verify them in the built image, and validate boot, SELinux and HALs. Preserve stock B.

## Corrected next-RE ranking

1. **DTB-DTBO** (PARTIAL; STATIC SOURCE CONTRACT) — Highest: bounded blobs and selection metadata already exist. [Evidence](../../docs/dt-module-matching.md).
2. **FT3680-TOUCH** (PARTIAL; KERNEL MODULE PARITY) — Good but uncertain: bounded, buildable 166-function reconstruction. [Evidence](../display-input/ft3680/parity-report.md).
3. **YFT-DEVINFO** (PARTIAL; KERNEL MODULE PARITY) — Moderate: small residual but unknown enum spelling may resist exact closure. [Evidence](../../kernel/phase4-yft-devinfo-kcfi-typeid.md).
4. **CAMERA-ISP-KERNEL** (PROPOSED; PROPOSED SPLIT / KERNEL MODULE PARITY) — Moderate/lower: source coverage exists, but entire ISP set has not been parity-built. [Evidence](../camera-stack/notes/isp-stack.md).
5. **MALI-GPU-KERNEL** (PROPOSED; PROPOSED ADD / KERNEL MODULE PARITY) — Lowest of this list: ownership absent and matched platform source/parity not established. [Evidence](MISSING-COVERAGE.md).

[Full criteria and separate integration/proprietary/tracking queues](NEXT-RE.md). VINTF-HAL-MANIFEST, VENDOR-PROPERTIES and BOOT-IMAGES are not unfinished RE targets when DONE.

## Manifest hygiene — separate historical result

The 2026-10-07 baseline records 19 stale hash/size entries, 408 unregistered files and one duplicate path; it is not a new current-workspace measurement. No COPY-MANIFEST repair was performed. [Historical details](notes/MANIFEST-HYGIENE.md). This drift does not invalidate the synchronized coverage database.

## Handoff

Use [the master index](../index.md), [PARTIAL triage](PARTIAL-TRIAGE.md), [missing coverage](MISSING-COVERAGE.md), [taxonomy decisions](PROPOSED-CHANGES.md) and [port readiness](PORT-READINESS.md). No further global coverage investigation is needed for this stock build. Remaining work is component RE, ROM integration and physical/runtime validation.
