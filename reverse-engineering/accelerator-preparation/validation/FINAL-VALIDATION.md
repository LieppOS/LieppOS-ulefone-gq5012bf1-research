# Accelerator preparation final validation — 2026-10-08

This is offline **preparation**, not source reconstruction or hardware validation. Discovery baseline `3bb6db32de2c5f312be31265482a7f8539145b62`; inventories committed as `3c48e19`, initial packs/handoffs as `c8de6a1`. The coverage/registration correction commit contains this report. Final source-pin/manifest attestation is recorded by the following local validation commit; no push.

## Measured result

- All six scopes are newly registered **PARTIAL**, with 146 useful metadata/doc files copied to their organized packs, individually registered in COPY-MANIFEST. No new DONE or unrelated status migration.
- Workspace: **139 = 94 DONE + 42 PARTIAL + 3 BLOCKED + 0 TODO**. Camera HAL remains PARTIAL and its preserved README now points to the kernel child. All prior source and historical evidence stays in place.
- Exact targets: **41 singleton primary modules**: Mali 8, APU 2, camera 19, codec 5, MDP 4, auxiliary 3. Existing SCP/ADSP, mailbox/IPI and named camera source closures are not duplicated.
- DT ledger: **108 node-compatible rows / 91 unique accelerator compatibles**; generic shared syscon stays generic. Additional seven PMIC infrastructure compatibles are removed from incorrect camera HAL ownership and remain shared generic dependencies.
- All **166** normalized ownership/class changes are explained against the pinned discovery baseline: 57 module, 98 compatible, 5 firmware, 2 VINTF family, 2 service, 2 integration. Artifact universe is unchanged; no unexplained ownership change.
- Coverage: **457 modules, 580 compatibles / 930 node instances, 525 HAL/services, 80 firmware, 654 integration, 538 significant libraries, 2,952 normalized records**. No current E ownership gaps. This is accounting, not kernel parity or runtime readiness.
- Existing camera **16 function/data proof pairs** are preserved with exact paths and class counts; new parity is not claimed. PDA/VMM and each module's complete acceptance packet remain actionable.

## Commands and acceptance

Run from the authoritative research repository:

```sh
python3 reverse-engineering/accelerator-preparation/validate.py
python3 reverse-engineering/accelerator-preparation/ownership-delta.py
python3 reverse-engineering/accelerator-preparation/validate-replay.py
python3 reverse-engineering/coverage-audit/scripts/check-audit.py
python3 reverse-engineering/coverage-audit/scripts/test-final-audit.py
python3 reverse-engineering/scripts/manifest-audit.py .. --json reverse-engineering/accelerator-preparation/validation/manifest-after.json
```

Preparation validator: **PASS** on exact stock hashes/sizes, donor fingerprints, all fourteen handoff sections, required nonempty files, singleton PARTIAL directories and primary module/DT owners, manifest rows, links and no firmware/source payload files.

Coverage check: **PASS** on live directories, measured totals/notes, complete normalized reconciliation, no duplicate whole-module component ownership, links, taxonomy state and retained RT5133 retraction. Ten regression tests pass, including DONE filtering, deterministic reports, rejected duplicate kernel-parent ownership, preventing `ccd` from matching PMIC `accdet`, GED DT discovery, and excluding closed transports/hosts from the new target set.

Replay: **PASS — 183 generated files byte-identical across 16 offline commands**, including preparation inventories, ABI witnesses, handoffs, coverage generators and tests. See [machine result](reproducibility.json) and [command log](replay.log). This is metadata reproducibility, not module B1/B2 acceptance.

## Global manifest is not clean — unchanged pre-existing drift

The standard manifest audit intentionally still exits **1**. Before/after:

| Measure | Before | After |
|---|---:|---:|
| Rows / resolved | 4251 / 4251 | 4397 / 4397 |
| Missing / malformed | 0 / 0 | 0 / 0 |
| Hash / size mismatches | 19 / 19 | 19 / 19 |
| Unregistered files | 408 | 408 |
| Duplicate paths | 1 | 1 |

All nonempty drift buckets, all unregistered paths and the duplicate path are unchanged. Empty buckets for the six new directories are not drift. The duplicate is `Reverse Engineer - DONE/HAPTICS/notes/haptics.md`. Existing hash/size drift belongs to CAMERA-IMX989, FT3680-TOUCH, HAPTICS, SENSOR-HUB and YFT-DEVINFO. None was silently repaired or incorporated into new accelerator ownership. **All 146 newly registered files are clean**, as is our explicitly corrected camera parent README. See [before](manifest-before.json), [after](manifest-after.json), [registration](../registration.json) and [scoped refresh](../manifest-refresh.json).

## Remaining boundaries and safety

Local donor availability does not establish stock equivalence. Grafted/private/patch worktree bytes are fingerprinted independently of enclosing Git HEAD; Claude must copy verified inputs into isolated scratch, not assume a pristine archive contains them. Natural type-derived CRCs/KCFI, function/data, relocation/symbol/string/modinfo/vermagic, deterministic clean builds and observable DT/ABI behavior remain reconstruction work.

CSF, APU, GPUEB/VCP, SCP/DSP and CCU algorithms/signatures, proprietary HAL/3A/PQ/model implementations, secure-world internals, calibration and keys are not reconstructed. Actual probe, inference, graphics/video/streaming, quality/performance, timing and power/reset behavior need later separately authorized runtime acceptance; DT `okay`, module presence and XML libraries are not execution proof.

No adb, reboot, flash, driver load, accelerator command, secure-world operation, firmware/calibration/partition write, destructive Git operation, module rebuild or push was performed. Shared source work and stock Slot B remain untouched. Finite preparation is complete; start only the scoped Claude handoffs next.
