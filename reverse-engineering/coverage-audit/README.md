# GQ5012BF1 reverse-engineering coverage audit — FINAL

Final snapshot: **2026-10-08**, source HEAD `3abc5643e539b3f2c8565d8197091d3bb50856ff`; workspace directories are authoritative. This report is reproducible from committed metadata, not a claim that later concurrent closures never occur.

Reproducible database behind [the authoritative index](../index.md). **NEAR-COMPLETE ownership**: one confirmed missing scope (MALI-GPU-KERNEL), no unexplained artifact gap. No taxonomy changes applied.

## Reports

- [SUMMARY.md](SUMMARY.md) — final measured verdict
- [PARTIAL-TRIAGE.md](PARTIAL-TRIAGE.md) — all 36 current PARTIAL components, A–F
- [NEXT-RE.md](NEXT-RE.md) / [next-re.tsv](next-re.tsv) — status-filtered static ranking and separate work queues
- [MISSING-COVERAGE.md](MISSING-COVERAGE.md) — one Mali gap; camera ISP already covered, proposed split
- [PROPOSED-CHANGES.md](PROPOSED-CHANGES.md) — decisions and conditional count, not an implemented migration
- [PORT-READINESS.md](PORT-READINESS.md) — seven readiness assessments and remaining integration actions
- [RT5133 correction](notes/RT5133-CORRECTION.md) — capture chronology and bound-device retraction
- [Final corrections](notes/FINAL-CORRECTIONS.md) and [validation](notes/FINAL-VALIDATION.md)
- [Historical manifest hygiene](notes/MANIFEST-HYGIENE.md) — separate unresolved baseline drift

## Machine tables

- [components.tsv](components.tsv): 133 rows
- [kernel-modules.tsv](kernel-modules.tsv): 457 rows
- [device-tree.tsv](device-tree.tsv): 580 rows
- [hardware.tsv](hardware.tsv): 44 rows
- [hals-services.tsv](hals-services.tsv): 272 rows
- [vendor-services.tsv](vendor-services.tsv): 253 rows
- [firmware.tsv](firmware.tsv): 80 rows
- [secure-world.tsv](secure-world.tsv): 13 rows
- [boot-storage.tsv](boot-storage.tsv): 61 rows
- [android-integration.tsv](android-integration.tsv): 654 rows
- [userspace-libraries.tsv](userspace-libraries.tsv): 538 rows
- [artifact-map.tsv](artifact-map.tsv): 2952 rows

## Reproduce from committed evidence

From the research repository root (builders locate their files relative to themselves):

```sh
python3 reverse-engineering/coverage-audit/scripts/build-kernel-modules.py
python3 reverse-engineering/coverage-audit/scripts/build-devicetree.py
python3 reverse-engineering/coverage-audit/scripts/build-hardware.py
python3 reverse-engineering/coverage-audit/scripts/build-services.py
python3 reverse-engineering/coverage-audit/scripts/build-integration.py
python3 reverse-engineering/coverage-audit/scripts/build-components.py
python3 reverse-engineering/coverage-audit/scripts/build-reports.py
python3 reverse-engineering/coverage-audit/scripts/check-audit.py
python3 reverse-engineering/coverage-audit/scripts/test-final-audit.py -v
```

Do not redo the 457-module investigation. For a legitimate new workspace snapshot, refresh only changed pack identity/claims with the existing harvesters and rebuild the dependent axes. Do not reharvest unchanged stock firmware/integration payloads. The final snapshot record is metadata, not permission to modify component packs.

`check-audit.py` checks current workspace membership/status, all A–F assignments and displayed totals, source/workspace paths, relative Markdown links, axis/normalized joins and the explicit GPU orphan sets. Determinism is verified by hashing generated outputs across a second build. Committed audit evidence contains metadata/claims only, no proprietary firmware/library/module payloads.

The final report's snapshot date/source HEAD is explicit in [final-snapshot.json](audit-evidence/final-snapshot.json). All corrections are committed in the final audit commit; no push is required. Further work is component RE, ROM integration and physical/runtime validation, not another global coverage investigation.
