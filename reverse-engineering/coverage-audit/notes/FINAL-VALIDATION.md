# Final audit validation record — PASS

Final snapshot: **2026-10-08**, research source HEAD `3abc5643e539b3f2c8565d8197091d3bb50856ff`; external device integration commit `24afa6b`. [Snapshot metadata](../audit-evidence/final-snapshot.json). The local final-audit commit containing this record completes the handoff; no push.

## Measured snapshot

- **133 registered components**, each indexed exactly once: **94 DONE / 36 PARTIAL / 3 BLOCKED / 0 TODO**. Actual directories—not an anticipated 99/31 batch outcome.
- Current PARTIAL classes: **A=6 / B=11 / C=8 / D=6 / E=0 / F=5**, sum **36**. No DONE row is classified as PARTIAL. Camera's unfinished ISP kernel subset is A pending the split; runtime OTA/recovery acceptance is D.
- **457 unique shipped modules**, complete set equality with extracted stock `.ko` names.
- **580 compatibles / 930 node instances**. Of **574** enabled compatibles, **571** have registered/generic accounting and **3** remain explicit Mali ownership gaps. DT enablement is not proof of hardware binding.
- **525 HAL/service rows** (272 interface/backend rows + 253 init-service/exec rows). Of **337 non-generic** rows, **333** have owners and **4** are the explicit GPU service boundary.
- **44** physical inventory rows, **80** firmware metadata records, **13** secure-world boundaries, **61** partition families, **654** integration artifacts, **538** significant libraries.
- **2,952 normalized records** reconcile individually with every source axis. **10 E rows**, all explained by **one** proposed missing scope, MALI-GPU-KERNEL; **0 unexplained E rows**. Camera ISP is already represented, not another orphan.

## Commands and results

From the research repository root:

```sh
python3 reverse-engineering/coverage-audit/scripts/check-audit.py
python3 reverse-engineering/coverage-audit/scripts/test-final-audit.py -v
git diff --check
```

**All PASS. Seven regression tests pass.** Checked workspace/table/index set and status equality; current source/workspace paths and harvested evidence-source existence; relative and percent-encoded links; singleton A–F assignments/totals; every normalized axis join; explicit module/DT/HAL/service GPU E sets; status-filtered ranked targets; RT5133 false-binding/rename regression; and conditional, unapplied taxonomy consequences. No proprietary firmware/module/library/image payload file was copied into `coverage-audit/`.

## Determinism

Two consecutive executions of the six changed builders (`build-kernel-modules`, `build-devicetree`, `build-hardware`, `build-integration`, `build-components`, `build-reports`) produced **identical SHA-256 hashes for 25 generated files**. Unchanged HAL/service, firmware, secure-world and partition metadata were reused rather than re-investigated.

Combined generated-output digest:

```text
9d9afba18a91f877a4adbad15af4b1f5d389a6b6257a2c42f2909532a189fc08
```

Digest method: sort repository-relative paths, hash each file, then SHA-256 the concatenated `path<TAB>file_sha256<LF>` lines. Scope: all `coverage-audit/*.tsv`, all `coverage-audit/*.md`, the master `reverse-engineering/index.md`, and generated `notes/{KERNEL-MODULES,DEVICE-TREE,COMPONENT-AUDIT,MANIFEST-HYGIENE}.md`. This hand-written validation record and other hand-written correction evidence are excluded to avoid self-referential hashes.

## Concurrency and integration

The final reconciliation retained Claude's new research commit `3abc564` and device `24afa6b`; no directory status differed from the 94/36/3 measured snapshot. Property definitions (327 installed keys with 16 documented exclusions/one EGL rewrite) and the Bluetooth audio fragment are now statically installed **outside this audit**. VINTF's refreshed instance ledger is 146 PRESENT / 48 SKU-only / 5 SOURCE-BUILT / 0 DROPPED. Emitted-image, build, SELinux and actual HAL/runtime acceptance are still outstanding; no such test was claimed here.

## Separate hygiene and handoff limits

The [2026-10-07 historical manifest baseline](MANIFEST-HYGIENE.md) records 19 hash mismatches, 408 unregistered files and one duplicate path. It is not a new current-workspace measurement or a coverage-database failure. No manifest/status-file repair was attempted. Stage only the master index and audit directory; do not amend/revert other commits or touch active reconstruction.

No ADD/SPLIT/MERGE/REMOVE/RENAME is implemented. Current registry remains 133; the accepted migration recommendations would conditionally yield 126, after approval and evidence-preserving migration. The unsupported RT5133 rename is rejected.

**Audit handoff complete:** remaining work is the ranked component RE, ROM integration and physical/runtime validation—not another global coverage investigation for this stock build.
