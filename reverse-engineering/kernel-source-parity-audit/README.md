# Kernel source-parity audit

A complete **read-only** inventory/evidence audit, not another kernel reconstruction project.

- [Summary and exact counts](SUMMARY.md)
- [All identities](ALL-457-MODULES.tsv): 458 binary identities / 457 filenames / 471 occurrences
- [Source gaps](SOURCE-GAPS.tsv): all 271 uncertified/unexcluded identities, including G
- [Canonical audit source ownership](SOURCE-OWNERSHIP.tsv)
- [Finite reconstruction/preservation queue](RECONSTRUCTION-QUEUE.md)
- [Machine project map](RECONSTRUCTION-PROJECTS.tsv)
- [Clock-core assignment (completed 2026-10-09)](NEXT-CLAUDE-TASK.md) and [result](../kernel-source-reconstruction/BOOT-CLOCK-CORE/README.md)
- PRESERVE:STORAGE (completed 2026-10-09): [result](../kernel-source-reconstruction/STORAGE/README.md)
- PINCTRL (completed 2026-10-09): [result](../kernel-source-reconstruction/PINCTRL/README.md)
- REGULATORS (completed 2026-10-09): [result](../kernel-source-reconstruction/REGULATORS/README.md)
- INTERCONNECT-EMI (completed 2026-10-09): [result](../kernel-source-reconstruction/INTERCONNECT-EMI/README.md)
- IOMMU (mtk_iommu only, completed 2026-10-10): [result](../kernel-source-reconstruction/IOMMU/README.md)
- PLATFORM-BATCH-01 (35 compiled;31 certified,4 explicit C blockers): [result](../kernel-source-reconstruction/PLATFORM-BATCH-01/BATCH-SUMMARY.md)
- PLATFORM-BATCH-02 (27/27 certified A,21D/6G→A): [result](../kernel-source-reconstruction/PLATFORM-BATCH-02/BATCH-SUMMARY.md)
- [Stale claims](STALE-CLAIMS.md)
- [All import/provider/CRC edges](DEPENDENCY-EDGES.tsv)
- [Actual partition-specific load-list evidence](LOAD-LIST-EVIDENCE.tsv)
- [All fifteen optional/reference reviews](OPTIONAL-15-REVIEW.tsv)
- [Historical reproduction input risks](REPRODUCIBILITY-RISKS.tsv)
- [DONE-associated modules needing source evidence](DONE-SOURCE-EVIDENCE-DISCREPANCIES.tsv)

`source_status` and `runtime_status` are independent. No component status changed. G remains
explicitly unresolved; a validator PASS does not convert it to A, missing code or an exclusion.
Source project names are audit groups, not newly created workspace components.

Reproduce/validate with the five commands in SUMMARY.md. Input and source/evidence hashes,
stock metadata, baseline drift and machine counts are retained in `evidence/`. Existing
stock/source/provenance payloads are referenced, not overwritten or recopied.
