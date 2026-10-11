# USB/Type-C five-blocker investigation

**Partial source improvement; all five remain C.** All original TCPC class instruction mismatches and runtime timer data are recovered; fingerprints/counter/diagnostic lineage still prevent complete acceptance. Zero new certifications, no canonical audit edit or push. Integration is additionally blocked by unrelated live canonical stock-identity drift; preserved source-build/fixture tests are not a live audit PASS.

- [Closure summary and five-module matrix](CLOSURE-SUMMARY.md)
- [Machine-readable module parity](MODULE-PARITY.tsv)
- [Experiments and negative outcomes](EXPERIMENTS.tsv)
- [Exact blocker table](BLOCKERS.tsv)
- [Source-version inputs and actual MD4](SRCVERSION-INVESTIGATION.md)
- [MT6375 metadata/counters](TCPC-METADATA-INVESTIGATION.md)
- [All eight TCPC function comparisons](TCPC-CLASS-FUNCTION-DIFFS.md)
- [Source lineage/commits](SOURCE-LINEAGE.md)
- [Four independent builds and23 mutation tests](BUILD-REPRODUCTION.md)
- [Field-level audit proposal](AUDIT-DELTA.tsv) — unapplied, all five remain C
- [Safe merge preconditions and instructions](MERGE-INSTRUCTIONS.md)
- [Remaining blockers](REMAINING-BLOCKERS.md)
- [Stale claims](stale-claims.md)
- [Precise next task](NEXT-TASK.md)

Retained-artifact verification: `PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate-preserved-evidence.py`. The result in `evidence/final-validation.json` explicitly verifies source-build files, tables, compiled archives and bundle recovery while keeping full closure/live audit blocked.

Complete ledgers: `evidence/final/full-acceptance/`. Actual source-build proofs: `evidence/fresh-clones/`. Preserved experiments: `evidence/{baseline,E1,E2,E3,E4}`, `evidence/tcpc-*`; first nondeterministic build proof: `evidence/fresh-clones-first-attempt/`; compiled operands/source bundles are comparison/recovery evidence, never stock binary build inputs.
